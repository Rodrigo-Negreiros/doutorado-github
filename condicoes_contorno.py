from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes

import numpy as np
from dolfinx import mesh, fem

class Condicoes_contorno:
    
    def __init__(self, domain, V, como_prender):
        
        self.como_prender = como_prender
        self.null_vector = fem.Function(V)
        self.null_vector.vector.set(0.0)

        self.tdim = domain.topology.dim
        self.fdim = self.tdim - 1
        
        if como_prender == 'solte-1':
            self.condicao_fronteira = lambda x: np.logical_or(x[0] == 0.0, np.logical_or(x[0] == 1.0, x[1] == 0.0))
            self.boundary_facets = mesh.locate_entities_boundary(domain, self.fdim, self.condicao_fronteira)
        
        if como_prender == 'prenda-as-quatro':
            self.condicao_fronteira = lambda x: np.logical_or(x[0] == 0.0, np.logical_or(x[0] == 1.0, np.logical_or(x[1] == 0.0, x[1] == 1.0)))
            self.boundary_facets = mesh.locate_entities_boundary(domain, self.fdim, self.condicao_fronteira)

        self.boundary_dofs = fem.locate_dofs_topological(V, self.fdim, self.boundary_facets)
        self.bc = fem.dirichletbc(self.null_vector, self.boundary_dofs)
    
    def vetor_nulo(self):
        return self.null_vector
    
    def bc(self):
        return self.bc
    
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
    
    num_elementos = 10
    
    como_criar_malha = 'gmsh'
    furo = True
    
    if furo == False or como_criar_malha == 'quadrada-normal':
        problema = Dados_Entrada(**valores)
        domain, V, elementos_x = Malhas(problema, num_elementos, num_elementos, como_criar_malha).gerando_malha()
        como_prender = 'solte-1'
    
    elif furo == True and como_criar_malha == 'gmsh': 
        problema = Dados_Entrada(**valores)
        centro = input('Centro: ')
        centro = float(centro)
        domain, V, elementos_x = Malhas(problema, num_elementos, num_elementos, como_criar_malha, furo, centro).gerando_malha()
        como_prender = input("Como fazer nas bordas? ")
        while como_prender not in ['solte-1', 'prenda-as-quatro']:
            como_prender = input("Como fazer nas bordas? ")
    
    funcoes = Funcoes(problema, domain, V)
    
    condicoes_contorno = Condicoes_contorno(domain, V, como_prender)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    