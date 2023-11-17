from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes
from condicoes_contorno import Condicoes_contorno

import math
import ufl
from petsc4py import PETSc
import pickle
import os
import numpy as np

from dolfinx import mesh, fem, nls

class FormaVariacional:
    def __init__(self, dados_entrada, classe_funcoes, condicoes_contorno, malha, V, domain, elementos_x):
        
        self.malha = malha
        self.elementos_x = elementos_x 
        self.V = V
        self.domain = domain
        p = dados_entrada.p
        
        self.dados_entrada = dados_entrada
        self.classe_funcoes = classe_funcoes
        self.condicoes_contorno = condicoes_contorno
        self.p = p
        
        self.vetor_tempo = []
        
        self.u_0 = fem.Function(V)
        self.u_0.interpolate(classe_funcoes.u_ini())
    
        self.v_0 = fem.Function(V)
        self.v_0.interpolate(classe_funcoes.v_ini())
        
        
        self.f = fem.Constant(domain, PETSc.ScalarType(0))
        self.g = fem.Constant(domain, PETSc.ScalarType(0))

        self.a0 = ufl.TrialFunction(V)
        self.v = ufl.TestFunction(V)

        self.u_11 = fem.Function(V)
        self.u_11.interpolate(classe_funcoes.u_exa())

        self.v_1_t = fem.Function(V)
        self.v_1_t.interpolate(classe_funcoes.v_exa())
        
        self.energia_y = []
        
        # Serve para gerar videos
        #self.vetores_un = [self.u_0.x.array.real]
        
  
    def retorna_vetor_tempo(self) -> list:
        return self.vetor_tempo
    
    
    def retorna_vetor_energia(self) -> list:
        return self.energia_y
    
    
    def calculo_energia(self, u , u_t) -> list:
        
        return 0.5 * ufl.dot(u_t ,u_t)*ufl.dx + \
                        0.5 * (1 + self.dados_entrada.epsilon * pow(ufl.dot(ufl.grad(u),ufl.grad(u)),(0.5 * self.classe_funcoes.p))/((self.classe_funcoes.p/2) + 1))*ufl.dot(ufl.grad(u),ufl.grad(u))*ufl.dx\
                            + 0.5*ufl.dot(u_t , u_t)*ufl.ds
       
    def a_0(self):
        
        bc = self.condicoes_contorno.bc
        
        F = self.a0 * self.v * ufl.dx + self.classe_funcoes.q(self.u_0, self.p) * ufl.dot(ufl.grad(self.u_0), ufl.grad(self.v)) * ufl.dx\
            + self.dados_entrada.delta * (ufl.dot(ufl.grad(self.v_0), ufl.grad(self.v)) * ufl.dx)\
                - self.f * self.v * ufl.dx - (self.g - self.a0) * self.v * ufl.ds
        
        a = ufl.lhs(F)
        L = ufl.rhs(F)

        problem = fem.petsc.LinearProblem(a, L, bcs=[bc], petsc_options={"ksp_type": "preonly", "pc_type": "lu"})
        #print("Achando a0 ...")
        a00 = problem.solve()
        #print("a0 calculado")
        
        return a00
    

    def a_n(self, t0 = 0):
    
        a_inicial = self.a_0()
        
        null_vector = self.condicoes_contorno.null_vector
        bc = self.condicoes_contorno.bc
        num_steps = self.dados_entrada.num_steps
        
        ener_0 = self.calculo_energia(self.u_11 , self.v_1_t)#, t0)
        energia_0 = fem.assemble_scalar(fem.form(ener_0))
        
        # -----------------------------------------------
        # Definindo Functions auxiliares
        # -----------------------------------------------
        a_0 = fem.Function(self.V)
        a_0.interpolate(a_inicial)

        u_1 = fem.Function(self.V)
        v_1 = fem.Function(self.V)
        a_1 = fem.Function(self.V)

        u_1 = self.u_0 + self.dados_entrada.dt * self.v_0 + (self.dados_entrada.dt**2 / 2) * ( (1 - 2 * self.dados_entrada.beta) * a_0 + 2 * self.dados_entrada.beta * a_1 )
        v_1 = self.v_0 + self.dados_entrada.dt * ((1 - self.dados_entrada.gama) * a_0 + self.dados_entrada.gama * a_1)

                 
        # -------------------------------------------------------
        # Definindo a forma variacional para descobrir o a_(n+1)
        # -------------------------------------------------------
        F = a_1 * self.v * ufl.dx + ufl.dot(self.classe_funcoes.q(u_1, self.p)*ufl.grad(u_1) + self.dados_entrada.delta*ufl.grad(v_1), ufl.grad(self.v)) * ufl.dx\
            - self.f * self.v * ufl.dx - (self.g - a_1) * self.v * ufl.ds

        problem = fem.petsc.NonlinearProblem(F, a_1, bcs=[bc])
        solver = nls.petsc.NewtonSolver(self.domain.comm, problem)
        

        # Set Newton solver options
        solver.atol = 1e-8
        solver.rtol = 1e-8
        solver.convergence_criterion = "incremental"

        u_11 = fem.Function(self.V)
        u_11.name = "u_11"
        u_11.interpolate(self.classe_funcoes.u_exa())

        v_1_t = fem.Function(self.V)
        v_1_t.name = "v_1_t"
        v_1_t.interpolate(self.classe_funcoes.v_exa())

        # Serve para gerar videos
        pasta_vetores = 'vetores'
        vetores_un = [self.u_0.x.array.real]
        
        for n in range(self.dados_entrada.num_steps):
            
            dt = self.dados_entrada.dt
            t = t0 + (n+1)*dt
            self.vetor_tempo += [t]
            
            # Atribuindo os valores da energia
            ener = self.calculo_energia(self.u_0 , self.v_0)
            energia = fem.assemble_scalar(fem.form(ener))
            self.energia_y += [math.log(energia/energia_0)]
            
            util = self.u_0.x.array + dt * self.v_0.x.array + (dt ** 2 / 2) * (1 - 2 * self.dados_entrada.beta) * a_0.x.array
            null_vector.x.array[:] = - util / (self.dados_entrada.beta * dt**2)
            
            num_its, converged = solver.solve(a_1)
            assert(converged)
            
            # Atualização dos passos de Newmark
            self.u_0.x.array[:] =  util + (dt ** 2 / 2) * 2 * self.dados_entrada.beta * a_1.x.array
            u_teste = self.u_0.x.array
            self.v_0.x.array[:] = self.v_0.x.array + dt * ((1 - self.dados_entrada.gama) * a_0.x.array + self.dados_entrada.gama * a_1.x.array)
            a_0.x.array[:] = a_1.x.array
            
            soma = np.zeros(len(self.u_0.x.array)) + self.u_0.x.array
            vetores_un.append(soma)
            
            print(str.format("Time step {:}, Número de iteracoes: {:}", n, num_its))
            #print('')
        
        
        nome_arquivo = f'vetores_un-tipo-malha-{self.malha.tipo_malha}-condicoes-contorno-{self.condicoes_contorno.como_prender}-elementos-{self.elementos_x}-num_steps-{self.dados_entrada.num_steps}-delta-{self.dados_entrada.delta}-grau-{self.dados_entrada.grau}.pkl'
        caminho_completo = os.path.join(pasta_vetores, nome_arquivo)
        
        if not os.path.exists(pasta_vetores):
            os.makedirs(pasta_vetores)
        
        with open(caminho_completo, 'wb') as arquivo_pickle:
            pickle.dump(vetores_un, arquivo_pickle)



if __name__ == "__main__":

    problema = Dados_Entrada(10, 1, 0.25, 0.5, 0.002, 1, 4)
    malha = Malhas(problema, 20, 20, 'quadrada-normal', True, 0.5)
    domain, V, elementos_x = malha.gerando_malha()
    funcoes = Funcoes(problema, domain, V)
    condicoes_contorno = Condicoes_contorno(domain, V, 'solte-1')
    forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, malha, V, domain, elementos_x)
    
    
    
    
    
    

