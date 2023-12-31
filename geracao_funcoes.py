from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas

import ufl
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh, fem, plot, io, nls, log
import numpy as np

class Funcoes:
    
    def __init__(self, dados_entrada, domain, V, k = 2, l = 2.5, t0 = 0, pi = np.pi):
        self.V = V
        self.domain = domain
        self.dados_entrada = dados_entrada
        beta = dados_entrada.beta
        p = dados_entrada.p
        
        self.p = p
        self.t_ini = fem.Constant(self.domain, PETSc.ScalarType(t0))
        self.t = fem.Constant(self.domain, PETSc.ScalarType(t0))

        tv = ufl.variable(ufl.Constant(self.domain))
        self.x = ufl.SpatialCoordinate(self.domain)
        
        u = beta * ufl.cos(tv) * ufl.sin(k * pi * self.x[0]) * ufl.sin(l * pi * self.x[1])
        self.u = ufl.replace(u, {tv: self.t})
        
        self.u0 = ufl.replace(u, {tv: self.t_ini})

        u_t = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u, tv))
        self.u_t = ufl.replace(u_t, {tv: self.t})
        u_tt = ufl.algorithms.apply_derivatives.apply_derivatives(ufl.diff(u_t, tv))
        self.u_tt = ufl.replace(u_tt, {tv: self.t})

        self.u0_t = ufl.replace(u_t, {tv: self.t_ini})

        qe = self.q(self.u, self.p)
        fq = qe * ufl.grad(u) + dados_entrada.delta * ufl.grad(self.u_t)
        self.f = ufl.replace(u_tt - ufl.div(fq), {tv: self.t})
        ne = ufl.as_vector((0, 1))
        self.g = ufl.replace(u_tt + ufl.dot(fq, ne), {tv: self.t})
        
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
    
    
if __name__ == "__main__":

    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1, 4)
    domain, V = Malhas(problema, 'quadrada-normal', 10, 10).gerando_malha()
    funcoes = Funcoes(problema, domain, V)