from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes
from forma_variacional import FormaVariacional
from condicoes_contorno import Condicoes_contorno
from imprimir_resultados import Imprime_Resultados
import time

start_time = time.time()
numeros_passos = [100, 200, 400]
numero_elementos = [10, 20]

for n_p in numeros_passos:
    for n_e in numero_elementos: 
        print(f'Número de passos: {n_p}, Numero de elementos: {n_e}')
        problema = Dados_Entrada(n_p, 1, 0.25, 0.5, 0.01, 1, 2, 4)
        malha = Malhas(problema, n_e, n_e, 'quadrada-normal')
        domain, V, elementos_x = malha.gerando_malha()
        funcoes = Funcoes(problema, domain, V)
        condicoes_contorno = Condicoes_contorno(domain, V, 'solte-1')
        
        # Execução do Lopping:
        forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, malha, V, domain, elementos_x)
        a_n = forma_variacional.a_n()
        vetor_energia = forma_variacional.retorna_vetor_energia
        vetor_tempo = forma_variacional.retorna_vetor_tempo
        
        #Retorna Resultados:
        nome_arquivo = f'vetores_un-tipo-malha-{malha.tipo_malha}-condicoes-contorno-{condicoes_contorno.como_prender}-elementos-{elementos_x}-num_steps-{problema.num_steps}-delta-{problema.delta}-grau-{problema.grau}.pkl'   
        resultado = Imprime_Resultados(problema, malha, condicoes_contorno, V, elementos_x, vetor_energia, vetor_tempo, nome_arquivo)
        resultado.mostra_grafico_energia()
        resultado.mostra_video()
        
        time.sleep(3)
    
    if n_p == numeros_passos[-1]:
        print(f'Foram finalizados todos os testes com tempo: {(time.time() - start_time)/60} minutos')
