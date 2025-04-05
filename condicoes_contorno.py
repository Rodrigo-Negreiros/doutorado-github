from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes

import numpy as np
from dolfinx import mesh, fem

class Condicoes_contorno:
    
    def __init__(self, domain, V, como_prender):
        
        self.como_prender = como_prender
        self.null_vector = fem.Function(V)
        self.null_vector.x.array[:] = 0.0

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
    
    valores_malha = {'elementos_x': 10,
                     'elementos_y': 10,
                     'furo': True}
    
    if valores_malha['furo'] == False:
        como_criar_malha = 'quadrada-normal'
        problema = Dados_Entrada(**valores)
        domain, V, elementos_x = Malhas(problema, **valores_malha, tipo_malha = como_criar_malha).gerando_malha()
        como_prender = 'solte-1'
    
    elif valores_malha['furo'] == True:
        como_criar_malha = 'gmsh'
        problema = Dados_Entrada(**valores)
        centro = float(input('Centro: '))
        raio = float(input('Raio: '))
        domain, V, elementos_x = Malhas(problema, **valores_malha, tipo_malha = como_criar_malha, centro = centro, raio = raio).gerando_malha()
        como_prender = input("Como fazer nas bordas? ")
        while como_prender not in ['solte-1', 'prenda-as-quatro']:
            como_prender = input("Como fazer nas bordas? ")
    
    k, l = 2, 2.5
    funcoes = Funcoes(problema, domain, V, k, l)
    condicoes_contorno = Condicoes_contorno(domain, V, como_prender)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    