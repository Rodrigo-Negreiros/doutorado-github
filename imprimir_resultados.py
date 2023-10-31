from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas

from dolfinx import plot
import pyvista as pv
import pickle
import os
import matplotlib.pyplot as plt

class Imprime_Resultados:
    
    def __init__(self, dados_entrada, V, retorna_vetor_energia, retorna_vetor_tempo, nome_pasta = 'vetores', nome_arquivo = 'vetores_un.pkl'):
        self.V = V
        self.dados_entrada = dados_entrada
        self.retorna_vetor_energia = retorna_vetor_energia
        self.retorna_vetor_tempo = retorna_vetor_tempo
        self.nome_pasta = nome_pasta
        self.nome_arquivo = nome_arquivo
    
    def carregar_arquivo_por_nome(self):
        # Crie o caminho completo para o arquivo desejado
        caminho_completo = os.path.join(self.nome_pasta, self.nome_arquivo)
        
        # Verifique se o arquivo existe
        if os.path.exists(caminho_completo):
            with open(caminho_completo, 'rb') as arquivo_pickle:
                dados = pickle.load(arquivo_pickle)
            return dados
    
    def mostra_grafico_energia(self):
        y_energia = self.retorna_vetor_energia()
        x_tempo = self.retorna_vetor_tempo()
        plt.plot(x_tempo, y_energia)
        plt.title(f'Gráfico de energia (nx:{10}, grau:{self.dados_entrada.grau}, passos: {self.dados_entrada.num_steps}, delta = {self.dados_entrada.delta})')
        plt.legend(loc="upper right")
        plt.xlabel("Período: 8π")
        plt.ylabel("Energia em escala logarítmica")
        return plt.show()
    
        
        
    def mostra_video(self):
        #gmsh.initialize()
        vetores = self.carregar_arquivo_por_nome()
        
        plotear = True #False  # Faça plotear = True para salvar no arquivo "waves.gif"
        
        if plotear == True:
            cells, types, x = plot.create_vtk_mesh(self.V)
            grid = pv.UnstructuredGrid(cells, types, x)
            grid.point_data["u"] = vetores[0]
            grid.set_active_scalars("u")
        
            plotter = pv.Plotter()
            plotter.open_gif("waves.gif", fps=5)
        
            warped = grid.warp_by_scalar()
            warped.set_active_scalars("u")
        
            # Add mesh to plotter and visualize
            plotter.add_mesh(warped, clim=[-self.dados_entrada.beta, self.dados_entrada.beta])#, show_edges=False, lighting=False)
            #plotter.add_text(str.format("Tempo: {:.3g}", mm.t.value), name='time-label')
            #plotter.show_axes()
            bnds = [0, 1, 0, 1, -1.2 * self.dados_entrada.beta, 1.2 * self.dados_entrada.beta]
            plotter.show_bounds(bounds=bnds, location='all')
            plotter.write_frame()  # write initial data
            #plotter.show(auto_close=False)  # only necessary for an off-screen movie
            
            for n in range(self.dados_entrada.num_steps):
                
                if plotear == True and n % 2 == 0:
                    #warped.set_active_scalars("u")
                    plotter.update_scalars(vetores[n])
                    print(vetores[n])
                    warped = grid.warp_by_scalar()
                    plotter.update_coordinates(warped.points.copy(), render=False)
                    #plotter.add_text(str.format("Tempo: {:.3g}", mm.t.value), name='time-label')
                    #plotter.show_axes()
                    plotter.show_bounds(bounds=bnds, location='all')
                    # Write a frame. This triggers a render.
                    plotter.write_frame()


            # Be sure to close the plotter when finished
            if plotear == True:
                plotter.close()

'''
if __name__ == "__main__":
    problema = Dados_Entrada(100, 1, 0.25, 0.5, 0.002, 1, 4)
    domain, V = Malhas(problema, 'quadrada-normal', 10, 10).gerando_malha()
    funcoes = Funcoes(problema, domain, V)
    condicoes_contorno = Condicoes_contorno(domain, V, 'solte-1')
    forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, V, domain)
    vetor_energia = forma_variacional.retorna_vetor_energia
    vetor_tempo = forma_variacional.retorna_vetor_tempo
    vetores = Imprime_Resultados(problema, V, vetor_energia, vetor_tempo)
 '''   

  
    
    
    
    
    
    
    
    
    
    