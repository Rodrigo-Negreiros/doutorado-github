from dados_entrada import Dados_Entrada

import ufl
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh, fem, plot, io, nls, log
import gmsh
from dolfinx.io import gmshio
from dolfinx.mesh import create_unit_square

class Malhas:
    
    def __init__(self, dados_entrada, tipo_malha, elementos_x, elementos_y):
        self.dados_entrada = dados_entrada
        self.tipo_malha = tipo_malha
        self.elementos_x = elementos_x
        self.elementos_y = elementos_y
        
    
    def gerando_malha(self):
        
        if self.tipo_malha == 'quadrada-normal':
            self.domain = create_unit_square(MPI.COMM_WORLD, self.elementos_x, self.elementos_y)
            self.V = fem.FunctionSpace(self.domain, ("CG", self.dados_entrada.grau))
            
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
            
            self.V = fem.FunctionSpace(self.domain, ("CG", self.dados_entrada.grau))
            
            return self.domain, self.V

if __name__ == "__main__":

    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1, 4)
    domain, V = Malhas(problema, 'quadrada-normal', 10, 10).gerando_malha()
    
    
    
    