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

    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1, 4)
    domain, V = Malhas(problema, 'quadrada-normal', 10, 10).gerando_malha()
    funcoes = Funcoes(problema, domain, V)
    condicoes_contorno = Condicoes_contorno(domain, V, 'prenda-as-quatro')