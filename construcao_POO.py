#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 18:47:03 2023

@author: rodrigonegreiros
"""
from datetime import datetime
import pickle
import ufl
import time
import math
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh, fem, plot, io, nls, log
import gmsh
import numpy as np
import matplotlib.pyplot as plt
from dolfinx.io import gmshio
from dolfinx.mesh import create_unit_square

start_time = time.time()

#nome_arquivo = input('Nome do arquivo:') + ".txt"

#arquivo = open(nome_arquivo, "a")
#elementos_vetor = list()
        
class Malhas:
    
    def __init__(self, tipo_malha, elementos_x, elementos_y, problema):
        self.tipo_malha = tipo_malha
        self.elementos_x = elementos_x
        self.elementos_y = elementos_y
        
    
    def gerando_malha(self):
        
        if self.tipo_malha == 'quadrada-normal':
            self.domain = create_unit_square(MPI.COMM_WORLD, self.elementos_x, self.elementos_y)
            self.V = fem.FunctionSpace(self.domain, ("CG", problema.grau))
            
            return self.domain, self.V
            
        
        if self.tipo_malha == 'gmsh':
            gmsh.initialize()
            
            L = 1
            H = 1
            c_x = c_y =0.25
            r = 0.125
            gdim = 2
            elementos = 20  
            nx = ny = L / elementos
    
            mesh_comm = MPI.COMM_WORLD
            model_rank = 0
            if mesh_comm.rank == model_rank:
                rectangle = gmsh.model.occ.addRectangle(0, 0, 0, L, H, tag = 1)
                obstacle = gmsh.model.occ.addDisk(c_x, c_y, 0, r, r)
    
            if mesh_comm.rank == model_rank:
                fluid = gmsh.model.occ.cut([(gdim, rectangle)], [(gdim, obstacle)])
                gmsh.model.occ.synchronize()
                gmsh.model.addPhysicalGroup(gdim, [rectangle])
                gmsh.model.addPhysicalGroup(gdim, [obstacle])
    
            if mesh_comm.rank == model_rank:
                gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 2)
                gmsh.option.setNumber("Mesh.CharacteristicLengthMin",nx)
                gmsh.option.setNumber("Mesh.CharacteristicLengthMax",ny)
                gmsh.model.mesh.generate(gdim)
                gmsh.model.mesh.setOrder(2)
                gmsh.model.mesh.optimize("Netgen")
    
            self.domain, cell_markers, facet_markers = gmshio.model_to_mesh(gmsh.model, mesh_comm, model_rank, gdim=gdim)
            facet_markers.name = "Facet markers"
            
            self.V = fem.FunctionSpace(self.domain, ("CG", problema.grau))
            
            return self.domain, self.V

class Funcoes:
    
    def __init__(self, domain, V, k = 2, l = 2.5, t0 = 0, pi = np.pi, p = 4):
        beta = problema.beta
        
        self.p = p
        self.t_ini = fem.Constant(domain, PETSc.ScalarType(t0))
        self.t = fem.Constant(domain, PETSc.ScalarType(t0))

        tv = ufl.variable(ufl.Constant(domain))
        self.x = ufl.SpatialCoordinate(domain)

        u = beta * ufl.cos(tv) * ufl.sin(k * pi * self.x[0]) * ufl.sin(l * pi * self.x[1])
        self.u = ufl.replace(u, {tv: self.t})
        
        self.u0 = ufl.replace(u, {tv: self.t_ini})

        u_t = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u, tv))
        self.u_t = ufl.replace(u_t, {tv: self.t})
        u_tt = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u_t, tv))
        self.u_tt = ufl.replace(u_tt, {tv: self.t})

        self.u0_t = ufl.replace(u_t, {tv: self.t_ini})

        qe = self.q(self.u)
        fq = qe * ufl.grad(u) + problema.delta * ufl.grad(u_t)
        self.f = ufl.replace(u_tt - ufl.div(fq), {tv: self.t})
        ne = ufl.as_vector((0, 1))
        self.g = ufl.replace(u_tt + ufl.dot(fq, ne), {tv: self.t})
        
    def q(self, u):
        return 1 + problema.epsilon * ufl.dot(ufl.grad(self.u), ufl.grad(self.u))**(0.5*self.p)    
   
    def u_exa(self):
        return fem.Expression(self.u, V.element.interpolation_points())
    
    def v_exa(self):
        return fem.Expression(self.u_t,V.element.interpolation_points())

    def a_exa(self):
        return fem.Expression(self.u_tt, V.element.interpolation_points())

    def u_ini(self):
        return fem.Expression(self.u0, V.element.interpolation_points())

    def v_ini(self):
        return fem.Expression(self.u0_t, V.element.interpolation_points())
 
class Condicoes_contorno:
    
    def __init__(self, como_prender):
        
        self.null_vector = fem.Function(V)
        self.null_vector.vector.set(0.0)

        self.tdim = domain.topology.dim
        self.fdim = self.tdim - 1
        
        if como_prender == 'solta':
            self.condicao_fronteira = lambda x: np.logical_or(x[0] == 0.0, np.logical_or(x[0] == 1.0, x[1] == 0.0))
            self.boundary_facets = mesh.locate_entities_boundary(domain, self.fdim, self.condicao_fronteira)

        self.boundary_dofs = fem.locate_dofs_topological(V, self.fdim, self.boundary_facets)
        self.bc = fem.dirichletbc(self.null_vector, self.boundary_dofs)
    
    def vetor_nulo(self):
        return self.null_vector
    
    def bc(self):
        return  self.bc

class FormaVariacional:
    def __init__(self, V, domain):
        self.vetor_tempo = []
        
        self.u_0 = fem.Function(V)
        self.u_0.interpolate(classe_funcoes.u_ini())
    
        self.v_0 = fem.Function(V)
        self.v_0.interpolate(classe_funcoes.v_ini())
        
        
        self.f = fem.Constant(domain, PETSc.ScalarType(0))
        self.g = fem.Constant(domain, PETSc.ScalarType(0))

        self.a0 = ufl.TrialFunction(V)
        self.v = ufl.TestFunction(V)
        
        
        self.energia_y = []

        self.u_11 = fem.Function(V)
        self.u_11.interpolate(classe_funcoes.u_exa())

        self.v_1_t = fem.Function(V)
        self.v_1_t.interpolate(classe_funcoes.v_exa())
        
    
    def retorna_vetor_tempo(self) -> list:
        return self.vetor_tempo
    
    
    def retorna_vetor_energia(self) -> list:
        return self.energia_y
    
    
    def calculo_energia(self, u , u_t):#, tempo):
        return 0.5 * ufl.dot(u_t ,u_t)*ufl.dx + \
                        0.5 * (1 + problema.epsilon * pow(ufl.dot(ufl.grad(u),ufl.grad(u)),(0.5*classe_funcoes.p))/((classe_funcoes.p/2) + 1))*ufl.dot(ufl.grad(u),ufl.grad(u))*ufl.dx\
                            + 0.5*ufl.dot(u_t , u_t)*ufl.ds
      
    def a_0(self):
        
        bc = condicoes_contorno.bc
        
        
        F = self.a0 * self.v * ufl.dx + Funcoes(domain, V).q(self.u_0) * ufl.dot(ufl.grad(self.u_0), ufl.grad(self.v)) * ufl.dx\
            + problema.delta * (ufl.dot(ufl.grad(self.v_0), ufl.grad(self.v)) * ufl.dx)\
                - self.f * self.v * ufl.dx - (self.g - self.a0) * self.v * ufl.ds

        a = ufl.lhs(F)
        L = ufl.rhs(F)

        problem = fem.petsc.LinearProblem(a, L, bcs=[bc], petsc_options={"ksp_type": "preonly", "pc_type": "lu"})
        #print("Achando a0 ...")
        a0 = problem.solve()
        #print("a0 calculado")
        
        return a0

    def a_n(self, t0 = 0):
        a_inicial = self.a_0()
        null_vector = condicoes_contorno.null_vector
        bc = condicoes_contorno.bc
        num_steps = problema.num_steps
        
        ener_0 = self.calculo_energia(self.u_11 , self.v_1_t)#, t0)
        energia_0 = fem.assemble_scalar(fem.form(ener_0))
        
        # -----------------------------------------------
        # Definindo Functions auxiliares
        # -----------------------------------------------
        a_0 = fem.Function(V)
        a_0.interpolate(a_inicial)

        u_1 = fem.Function(V)
        v_1 = fem.Function(V)
        a_1 = fem.Function(V)

        u_1 = self.u_0 + problema.dt * self.v_0 + (problema.dt**2 / 2) * ( (1 - 2 * problema.beta) * a_0 + 2 * problema.beta * a_1 )
        v_1 = self.v_0 + problema.dt * ((1 - problema.gama) * a_0 + problema.gama * a_1)

                 
        # -------------------------------------------------------
        # Definindo a forma variacional para descobrir o a_(n+1)
        # -------------------------------------------------------
        F = a_1 * self.v * ufl.dx + ufl.dot(classe_funcoes.q(u_1)*ufl.grad(u_1) + problema.delta*ufl.grad(v_1), ufl.grad(self.v)) * ufl.dx\
            - self.f * self.v * ufl.dx - (self.g - a_1) * self.v * ufl.ds

        problem = fem.petsc.NonlinearProblem(F, a_1, bcs=[bc])
        solver = nls.petsc.NewtonSolver(domain.comm, problem)


        # Set Newton solver options
        solver.atol = 1e-8
        solver.rtol = 1e-8
        solver.convergence_criterion = "incremental"

        u_11 = fem.Function(V)
        u_11.name = "u_11"
        u_11.interpolate(Funcoes(domain, V).u_exa())

        v_1_t = fem.Function(V)
        v_1_t.name = "v_1_t"
        v_1_t.interpolate(Funcoes(domain, V).v_exa())


        for n in range(num_steps):
            
            dt = problema.dt
            t = t0 + (n+1)*dt
            
            # Atribuindo os valores da energia
            ener = self.calculo_energia(self.u_0 , self.v_0)
            energia = fem.assemble_scalar(fem.form(ener))
            self.energia_y += [math.log(energia/energia_0)]
            #elementos_vetor.append(str(math.log(energia/energia_0))+",")
            
            classe_funcoes.t.value = t
            self.vetor_tempo += [t]
            
            util = self.u_0.x.array + dt * self.v_0.x.array + (dt ** 2 / 2) * (1 - 2 * problema.beta) * a_0.x.array
            null_vector.x.array[:] = - util / (problema.beta * dt**2)
            
            num_its, converged = solver.solve(a_1)
            assert(converged)
            
            # Atualização dos passos de Newmark
            self.u_0.x.array[:] =  util + (dt ** 2 / 2) * 2 * problema.beta * a_1.x.array
            self.v_0.x.array[:] = self.v_0.x.array + dt * ((1 - problema.gama) * a_0.x.array + problema.gama * a_1.x.array)
            a_0.x.array[:] = a_1.x.array
            
            
            print(str.format("Time step {:}, Número de iteracoes: {:}, vetor= {:}", n, num_its, a_0.x.array[10:15]))
                

if __name__ == "__main__":

    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1)
    
    domain, V = Malhas('quadrada-normal', 10, 10, problema).gerando_malha()
    
    classe_funcoes = Funcoes(domain, V) 
    
    condicoes_contorno = Condicoes_contorno('solta')
    
    forma_variacional = FormaVariacional(V, domain)
    a_no_tempo = forma_variacional.a_n()

    
    


















