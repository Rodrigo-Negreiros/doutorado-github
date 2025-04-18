from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes
from forma_variacional import FormaVariacional
from condicoes_contorno import Condicoes_contorno

from dolfinx import plot
import dolfinx
import pyvista as pv
import pickle
import os
import matplotlib.pyplot as plt
import time

class Imprime_Resultados:
    
    def __init__(self, dados_entrada, malha, furo, condicoes_contorno, V, elementos_x, forma_variacional, retorna_vetor_energia, retorna_vetor_tempo, nome_pasta, **kwargs):
        self.dados_entrada = dados_entrada
        self.malha = malha
        self.furo = furo
        self.condicoes_contorno = condicoes_contorno
        self.V = V
        self.elementos_x = elementos_x
        
        self.retorna_vetor_energia = retorna_vetor_energia
        self.retorna_vetor_tempo = retorna_vetor_tempo
        self.nome_pasta = nome_pasta
        #self.nome_arquivo = nome_arquivo
        self.caminho = forma_variacional.retorna_estrutura_caminho()
    
    def carregar_arquivo_por_nome(self, furo, malha):
        
        # Crie o caminho completo para o arquivo desejado
        if furo == False:
            nome_arquivo = 'vetores_un' + self.caminho + '.pkl'
            caminho_completo = os.path.join(self.nome_pasta, nome_arquivo)
            
        else:
            
            nome_arquivo = 'vetores_un' + self.caminho + f'-centro-{malha.centro}-raio-{malha.raio}.pkl'
            caminho_completo = os.path.join(self.nome_pasta, nome_arquivo)
        
        # Verifique se o arquivo existe
        if os.path.exists(caminho_completo):
            with open(caminho_completo, 'rb') as arquivo_pickle:
                dados = pickle.load(arquivo_pickle)
            return dados
    
    def mostra_grafico_energia(self, furo, malha):
        
        
        params = {"ytick.color" : "#dfdfdf",
          "xtick.color" : "#dfdfdf",
          "axes.labelcolor" : "#dfdfdf",
          "axes.edgecolor" : "#dfdfdf"}
        plt.rcParams.update(params)
        
        fig, ax = plt.subplots()
        fig.set_facecolor('#4C4C4C')
        ax.set_facecolor('#4C4C4C')
        ax.grid()
        
        y_energia = list(self.retorna_vetor_energia())
        x_tempo = list(self.retorna_vetor_tempo())
        ax.plot(x_tempo, y_energia, color = '#2B8B6F')
        
        #ax.set_title(f'Gráfico de energia (nx:{self.elementos_x}, grau:{self.dados_entrada.grau}, passos: {self.dados_entrada.num_steps}, delta = {self.dados_entrada.delta})', fontweight ="bold")
        ax.set_xlabel("Período: 4π", fontsize = 12)
        ax.set_ylabel("Energia em escala logarítmica", fontsize = 12)
        
        pasta_graficos_energia = 'graficos_energias'
        if furo == False:
            nome_arquivo = 'vetores_un' + self.caminho + '.png'
        else:
            nome_arquivo = 'vetores_un' + self.caminho + f'-centro-{malha.centro}-raio-{malha.raio}.png'
        #nome_arquivo = f'vetores_un-tipo-malha-{self.malha.tipo_malha}-condicoes-contorno-{self.condicoes_contorno.como_prender}-elementos-{self.elementos_x}-num_steps-{self.dados_entrada.num_steps}-delta-{self.dados_entrada.delta}-grau-{self.dados_entrada.grau}.png'
        caminho_completo = os.path.join(pasta_graficos_energia, nome_arquivo)
        
        
        if not os.path.exists(pasta_graficos_energia):
            os.makedirs(pasta_graficos_energia)
        
        fig.savefig(caminho_completo, format='png')
        #ax.set_yscale('log')
        
        return plt.show()
         
        
    def mostra_video(self, furo, malha):
        vetores = self.carregar_arquivo_por_nome(furo, malha)
        #print(vetores[0])
        plotear = True #False  # Faça plotear = True para salvar no arquivo "waves.gif"
        
        if plotear == True:
            cells, types, x = plot.vtk_mesh(self.V)
            grid = pv.UnstructuredGrid(cells, types, x)
            grid.point_data["u"] = vetores[0]
            grid.set_active_scalars("u")
        
            plotter = pv.Plotter(off_screen=True)
            pasta_videos = 'videos'
            if furo == False:
                nome_arquivo = 'vetores_un' + self.caminho + '.gif'
            else:
                nome_arquivo = 'vetores_un' + self.caminho + f'-centro-{malha.centro}-raio-{malha.raio}.gif'
            #nome_arquivo = f"waves-tipo-malha-{self.malha.tipo_malha}-condicoes-contorno-{self.condicoes_contorno.como_prender}-elementos-{self.elementos_x}-num_steps-{self.dados_entrada.num_steps}-delta-{self.dados_entrada.delta}-grau-{self.dados_entrada.grau}.gif"
            caminho_completo = os.path.join(pasta_videos, nome_arquivo)
            
            if not os.path.exists(pasta_videos):
                os.makedirs(pasta_videos)
            
            plotter.open_gif(caminho_completo, fps=5)
        
            warped = grid.warp_by_scalar()
            warped.set_active_scalars("u")
        
            # Add mesh to plotter and visualize
            plotter.add_mesh(warped, clim=[-self.dados_entrada.beta, self.dados_entrada.beta])#, show_edges=False, lighting=False)
            plotter.add_text(str.format("Tempo: {:.3g}", self.retorna_vetor_tempo()[0]), name='time-label')
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
                    plotter.add_text(str.format("Tempo: {:.3g}", self.retorna_vetor_tempo()[n]), name='time-label')
                    #plotter.show_axes()
                    plotter.show_bounds(bounds=bnds, location='all')
                    # Write a frame. This triggers a render.
                    plotter.write_frame()


            # Be sure to close the plotter when finished
            if plotear == True:
                plotter.close()


if __name__ == "__main__":
    valores = {'num_steps' : 10, 
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
        malha = Malhas(problema, **valores_malha, tipo_malha= como_criar_malha)
        malha.tipo_malha = 'quadrada-normal'
        domain, V, elementos_x = Malhas(problema, **valores_malha).gerando_malha()
        como_prender = 'solte-1'
        
    elif valores_malha['furo'] == True:
        como_criar_malha = 'gmsh'
        problema = Dados_Entrada(**valores)
        centro = float(input('Centro: '))
        raio = float(input('Raio: '))
        malha = Malhas(problema, **valores_malha, tipo_malha = como_criar_malha, centro = centro, raio = raio)
        domain, V, elementos_x = malha.gerando_malha()
        como_prender = input("Como fazer nas bordas? ")
        while como_prender not in ['solte-1', 'prenda-as-quatro']:
            como_prender = input("Como fazer nas bordas? ")
    
    k, l = 2, 2.5
    funcoes = Funcoes(problema, domain, V, k, l)
    condicoes_contorno = Condicoes_contorno(domain, V, como_prender)
    forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, malha, V, domain, elementos_x)
    a_n = forma_variacional.a_n()
    vetor_energia = forma_variacional.retorna_vetor_energia
    vetor_tempo = forma_variacional.retorna_vetor_tempo
    caminho = forma_variacional.retorna_estrutura_caminho()
    
    informacoes = {'nome_pasta': 'vetores',
                   'caminho': caminho}
    #dados_entrada, malha, condicoes_contorno, V, elementos_x, retorna_vetor_energia, retorna_vetor_tempo, nome_arquivo, nome_pasta = 'vetores', **kwargs):   
    resultado = Imprime_Resultados(problema, malha, valores_malha['furo'], condicoes_contorno, V, elementos_x, forma_variacional, vetor_energia, vetor_tempo, **informacoes)
    resultado.mostra_grafico_energia(valores_malha['furo'], malha)
    resultado.mostra_video(valores_malha['furo'], malha)

    
    
    
    
    
    
    
    
    
    