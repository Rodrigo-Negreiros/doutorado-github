from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes
from forma_variacional import FormaVariacional
from condicoes_contorno import Condicoes_contorno
from imprimir_resultados import Imprime_Resultados
import time

start_time = time.time()

valores = {'alpha' : 1, 
           'beta' : 0.25, 
           'gama' : 0.5, 
           'delta' : 1, 
           'epsilon': 1, 
           'p' : 2, 
           'grau': 2
           }

furo = False

numeros_passos = [200]
numero_elementos = [40]

valor_centro = 0
valor_raio = 0

for i, n_p in enumerate(numeros_passos):
    for j, n_e in enumerate(numero_elementos):
        
        if furo == False:
            como_criar_malha = 'quadrada-normal'
            como_prender = 'solte-1'
            centro = None
            raio = None
        
        elif furo == True:
            como_criar_malha = 'gmsh'
            if i == 0 and j == 0:
                centro = float(input('Centro: '))
                raio = float(input('Raio: '))
                valor_centro += centro
                valor_raio += raio
                como_prender = input("Como fazer nas bordas? ")
                while como_prender not in ['solte-1', 'prenda-as-quatro']:
                    como_prender = input("Como fazer nas bordas? ") 
            else:
                centro = valor_centro
                raio = valor_raio
        
        print(f'Número de passos: {n_p}, Numero de elementos: {n_e}')
        problema = Dados_Entrada(n_p, **valores)
        
        
        malha = Malhas(problema, n_e, n_e, furo, como_criar_malha, centro, raio)
        domain, V, elementos_x = malha.gerando_malha()
        k, l = 2, 2
        funcoes = Funcoes(problema, domain, V, k, l)
        condicoes_contorno = Condicoes_contorno(domain, V, como_prender)
        
        # Execução do Lopping:   
        forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, malha, V, domain, elementos_x)
        a_n = forma_variacional.a_n()
        vetor_energia = forma_variacional.retorna_vetor_energia
        vetor_tempo = forma_variacional.retorna_vetor_tempo
        
        caminho = forma_variacional.retorna_estrutura_caminho()
        
        informacoes = {'nome_pasta': 'vetores',
                       'caminho': caminho}

        #dados_entrada, malha, condicoes_contorno, V, elementos_x, retorna_vetor_energia, retorna_vetor_tempo, nome_arquivo, nome_pasta = 'vetores', **kwargs):   
        resultado = Imprime_Resultados(problema, malha, furo, condicoes_contorno, V, elementos_x, forma_variacional, vetor_energia, vetor_tempo, **informacoes)
        resultado.mostra_grafico_energia(furo, malha)
        resultado.mostra_video(furo, malha)
      
        
        time.sleep(3)
    
    if n_p == numeros_passos[-1]:
        print(f'Foram finalizados todos os testes com tempo: {(time.time() - start_time)/60} minutos')
        

        
        
        



























