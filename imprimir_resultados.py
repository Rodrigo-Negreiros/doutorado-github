from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas

from dolfinx import plot
import pyvista as pv
import pickle
import os
import matplotlib.pyplot as plt
import time

class Imprime_Resultados:
    
    def __init__(self, dados_entrada, V, retorna_vetor_energia, retorna_vetor_tempo, nome_arquivo, nome_pasta = 'vetores'):
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
        fig, ax = plt.subplots()
        
        y_energia = list(self.retorna_vetor_energia())
        x_tempo = list(self.retorna_vetor_tempo())
        ax.plot(x_tempo, y_energia)
        
        ax.set_title(f'Gráfico de energia (nx:{10}, grau:{self.dados_entrada.grau}, passos: {self.dados_entrada.num_steps}, delta = {self.dados_entrada.delta})', fontweight ="bold")
        ax.set_xlabel("Período: 8π", fontsize = 12)
        ax.set_ylabel("Energia em escala logarítmica", fontsize = 12)
        
        pasta_graficos_energia = 'graficos_energias'
        nome_arquivo = f'grafico-energia-nx-{10}-grau-{self.dados_entrada.grau}-passos-{self.dados_entrada.num_steps}-delta-{self.dados_entrada.delta}.png'
        caminho_completo = os.path.join(pasta_graficos_energia, nome_arquivo)
        
        if not os.path.exists(pasta_graficos_energia):
            os.makedirs(pasta_graficos_energia)
        
        fig.savefig(caminho_completo, format='png')
        #ax.set_yscale('log')
        
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
            pasta_videos = 'videos'
            nome_arquivo = f"waves-{time.strftime('%H-%M-%S', time.localtime())[:8]}.gif"
            caminho_completo = os.path.join(pasta_videos, nome_arquivo)
            
            if not os.path.exists(pasta_videos):
                os.makedirs(pasta_videos)
            
            plotter.open_gif(caminho_completo, fps=5)
        
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

  
    
    
    
    
    
    
    
    
    
    