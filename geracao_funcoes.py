from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas

import ufl
from ufl import sin, cos
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh, fem, plot, io, nls, log
import numpy as np


class Funcoes:
    
    def __init__(self, dados_entrada, domain, V, k, l, t0 = 0, pi = np.pi): # u_exa, t,
        self.V = V
        self.domain = domain
        self.dados_entrada = dados_entrada
        beta = dados_entrada.beta
        p = dados_entrada.p
        
        self.p = p
        self.t_ini = fem.Constant(self.domain, PETSc.ScalarType(t0))
        
        
        #self.t = fem.Constant(self.domain, PETSc.ScalarType(t0))
        self.tv = fem.Constant(self.domain, PETSc.ScalarType(t0))
        

        #tv = ufl.variable(ufl.Constant(self.domain))
        t = ufl.variable(ufl.Constant(self.domain))
        
        
        self.x = ufl.SpatialCoordinate(self.domain)
        
        #self.u_exa = u_exa
        #u = beta * ufl.cos(tv) * ufl.sin(k * pi * self.x[0]) * ufl.sin(l * pi * self.x[1])
        #u = self.u_exa
        
        ####################################################################################
        # Funcao teste
        ####################################################################################
        u = beta * ufl.cos(t) * ufl.sin(k * pi * self.x[0]) * ufl.sin(l * pi * self.x[1])
        
        
        #self.u = ufl.replace(u, {tv: self.t})
        self.u = ufl.replace(u, {t: self.tv})
        
        
        #self.u0 = ufl.replace(u, {tv: self.t_ini})
        self.u0 = ufl.replace(u, {t: self.t_ini})
        

        #u_t = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u, tv))
        u_t = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u, t))
        
        
        
        #self.u_t = ufl.replace(u_t, {tv: self.t})
        self.u_t = ufl.replace(u_t, {t: self.tv})
        
        
        #u_tt = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u_t, tv))
        u_tt = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u_t, t))
        
        
        
        #self.u_tt = ufl.replace(u_tt, {tv: self.t})
        self.u_tt = ufl.replace(u_tt, {t: self.tv})
        
        

        #self.u0_t = ufl.replace(u_t, {tv: self.t_ini})
        self.u0_t = ufl.replace(u_t, {t: self.t_ini})
        
        

        qe = self.q(self.u, self.p)
        fq = qe * ufl.grad(u) + dados_entrada.delta * ufl.grad(self.u_t)
        #self.f = ufl.replace(u_tt - ufl.div(fq), {tv: self.t})
        self.f = ufl.replace(u_tt - ufl.div(fq), {t: self.tv})
        
        
        ne = ufl.as_vector((0, 1))
        #self.g = ufl.replace(u_tt + ufl.dot(fq, ne), {tv: self.t})
        self.g = ufl.replace(u_tt + ufl.dot(fq, ne), {t: self.tv})
          
        
    def q(self, u, p):
        return 1 + self.dados_entrada.epsilon * ufl.dot(ufl.grad(u), ufl.grad(u))**(0.5*p)    
   
    def u_exa(self):
        return fem.Expression(self.u, self.V.element.interpolation_points())
    
    def v_exa(self):
        return fem.Expression(self.u_t, self.V.element.interpolation_points())

    def a_exa(self):
        return fem.Expression(self.u_tt, self.V.element.interpolation_points())

    def u_ini(self):
        return fem.Expression(self.u0, self.V.element.interpolation_points())

    def v_ini(self):
        return fem.Expression(self.u0_t, self.V.element.interpolation_points())
    
    
    
    def f(self):
        return fem.Expression(self.f, self.V.element.interpolation_points())
    def g(self):
        return fem.Expression(self.g, self.V.element.interpolation_points())   
    

if __name__ == "__main__":
    
    valores = {'num_steps' : 100, 
               'alpha' : 1, 
               'beta' : 0.25, 
               'gama' : 0.5, 
               'delta' : 0.002, 
               'epsilon': 1, 
               'p' : 4, 
               'grau':2
               }
    
    valores_malha = {'elementos_x': 10,
                     'elementos_y': 10,
                     'furo': False}
    #num_elementos = 10
    #furo = True
    
    if valores_malha['furo'] == False:
        como_criar_malha = 'quadrada-normal'
        problema = Dados_Entrada(**valores)
        domain, V, elementos_x = Malhas(problema, **valores_malha).gerando_malha()
    
    elif valores_malha['furo'] == True:
        como_criar_malha = 'gmsh'
        problema = Dados_Entrada(**valores)
        centro = float(input('Centro: '))
        raio = float(input('Raio: '))
        domain, V, elementos_x = Malhas(problema, **valores_malha, centro = centro, raio = raio).gerando_malha()
    
    num_steps, alpha, beta, gama, delta, epsilon, p, grau, t0, pi = problema.retorna_dados()
    #x = ufl.SpatialCoordinate(domain)
    #t = ufl.variable(ufl.Constant(domain))
    k, l = 2, 2.5
    
    #u_exa = beta * cos(t) * sin(k * pi * x[0]) * ufl.sin(l * pi * x[1])
    funcoes = Funcoes(problema, domain, V,  k, l) # u_exa, t,
    

    
    
    
    
    
