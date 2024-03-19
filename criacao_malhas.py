from dados_entrada import Dados_Entrada

import ufl
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh, fem, plot, io, nls, log
import gmsh
from dolfinx.io import gmshio
from dolfinx.mesh import create_unit_square

class Malhas(Dados_Entrada):
    
    def __init__(self, dados_entrada, elementos_x = None, elementos_y = None, furo = None, tipo_malha = '', centro = None, raio = None):
        self.dados_entrada = dados_entrada
        self.elementos_x = elementos_x
        self.elementos_y = elementos_y
        self.tipo_malha = tipo_malha
        self.furo = furo
        self.centro = centro
        self.raio = raio
        
    def gerando_malha(self):
        
        if self.furo == False:
            self.tipo_malha = 'quadrada-normal'
            self.domain = create_unit_square(MPI.COMM_WORLD, self.elementos_x, self.elementos_y)
            self.V = fem.FunctionSpace(self.domain, ("CG", self.dados_entrada.grau))
            
            return self.domain, self.V, self.elementos_x
        
        else:
            self.tipo_malha = 'gmsh'
            gmsh.initialize()
            
            if self.furo == True:
                L = 1
                H = 1
                
                c_x = c_y = self.centro
                r = self.raio
                gdim = 2
                elementos = self.elementos_x 
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
            
            self.V = fem.FunctionSpace(self.domain, ("CG", self.dados_entrada.grau))
            
            gmsh.finalize()
            
            return self.domain, self.V, self.elementos_x

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
    
    if valores_malha['furo'] == False:
        como_criar_malha = 'quadrada-normal'
        problema = Dados_Entrada(**valores)
        domain, V, elementos_x = Malhas(problema, **valores_malha, tipo_malha = como_criar_malha).gerando_malha()
    
    elif valores_malha['furo'] == True:
        como_criar_malha = 'gmsh'
        problema = Dados_Entrada(**valores)
        centro = float(input('Centro: '))
        raio = float(input('Raio: '))
        domain, V, elementos_x = Malhas(problema, **valores_malha, tipo_malha = como_criar_malha, centro = centro, raio = raio).gerando_malha()
    
    
    
    
    
    