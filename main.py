from dados_entrada import Dados_Entrada
from criacao_malhas import Malhas
from geracao_funcoes import Funcoes
from forma_variacional import FormaVariacional
from condicoes_contorno import Condicoes_contorno
from imprimir_resultados import Imprime_Resultados


if __name__ == "__main__":
    problema = Dados_Entrada(10, 1, 0.25, 0.5, 0.002, 1, 4)
    domain, V, elementos_x = Malhas(problema, 10, 10, 'quadrada-normal', True, 0.5).gerando_malha()
    funcoes = Funcoes(problema, domain, V)
    condicoes_contorno = Condicoes_contorno(domain, V, 'solte-1')
    
    # Execução do Lopping:
    forma_variacional = FormaVariacional(problema, funcoes, condicoes_contorno, V, domain, elementos_x)
    a_n = forma_variacional.a_n()
    vetor_energia = forma_variacional.retorna_vetor_energia
    vetor_tempo = forma_variacional.retorna_vetor_tempo
    
    #Retorna Resultados:
        
    nome_arquivo = f'vetores_un-elementos-{elementos_x}-num_steps-{problema.num_steps}-grau-{problema.grau}.pkl'
    resultado = Imprime_Resultados(problema, V, vetor_energia, vetor_tempo, nome_arquivo)