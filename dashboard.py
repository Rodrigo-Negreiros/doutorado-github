from forma_variacional import FormaVariacional

import numpy as np
import os
import base64
from dash import Dash, dcc, html, Input, Output
import pickle
import numpy as np
import math
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

folder_path_gif = "videos"
folder_path_png = "graficos_energias"
def modelo_nome(condicao_contorno, elementos, num_passos, delta, grau):
    string_padrao = f'-tipo-malha-quadrada-normal-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}'
    return string_padrao

numero_de_elementos = [10, 20]
numero_de_passos = [100, 200, 400]
delta = [format(0, '.1f'), 0.01, 0.05]
grau_dos_polinomios = [2, 4]
condicoes_contorno = ['solte-1', 'presa']

def read_and_encode_file(file_path):
    with open(file_path, 'rb') as file:
        encoded_file = base64.b64encode(file.read()).decode('utf-8')
    return encoded_file

app = Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Dashboard de soluções", className="titulo"),
    html.Div([
    html.H2("Problema:", className="word-problema"),
    html.Img(src='assets/equacao.png', alt='equacao',className="img-problema"),
    html.H2("Função exata:", id = 'funcao-exata',className="word-problema"),
    html.Img(src='assets/funcao_exata.png', alt='funcao-exata', id = 'img-exata',className="img-problema")],  className="problema"),
    
    html.Ul([ 
    
        html.Li([
        html.H3("Número de passos:"),
        dcc.Dropdown(numero_de_passos, value=100, id='dropdown-1', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        html.Li([
        html.H3("Número de elementos:"),
        dcc.Dropdown(numero_de_elementos, value=10, id='dropdown-2', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        html.Li([
        html.H3("Tamanho do delta:"),
        dcc.Dropdown(delta, value= 0.01, id='dropdown-3', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),  
        ]),
        
        html.Li([
        html.H3("Grau dos polinômios:"),
        dcc.Dropdown(grau_dos_polinomios, value=2, id='dropdown-4', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        html.Li([
        html.H3("Condição de contorno:"),
        dcc.Dropdown(condicoes_contorno, value='solte-1', id='dropdown-5', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        
        
    ], className="opcoes"),
    
    
    html.Div([
        
        html.Div([
            html.H2("Gráfico da energia em escala Logarítmica", id = 'grafico-titulo'),
            
            html.Div([
                html.Img(id='png-display')
            ]),
        ], className="imagem"),
        
    html.Div([
        html.Div([
        html.H3("Valor máximo da energia", className='num_max'),
        html.Div(id='valor_max')], id = 'caixa_max'),
        
        html.Div([
        html.H3("Tempo de execução", className='tempo'),
        html.Div(id='tempo_exe')], id = 'caixa_tempo')
        
    ],className="caixa_de_valores"),
        
    html.Div([
            html.H2("Comportamento da solução", className='gif-title'),
       
            html.Div([
                html.Img(id='gif-display')
                ]),
        ], className="gif"),
            
    ], className="solucao"),
    
    
    html.Div([
        html.H2("Comparação entre os graus", id='comparacao-title'),
        dcc.Graph(id='grafico-tempo-valores'),
    ], className="comparacao"),
    
    
], className = 'corpo') 

@app.callback(
    Output('valor_max', 'children'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value')]
)
def update_output(num_passos, elementos, delta, grau, condicao_contorno):
    print(condicao_contorno)
 
    #result_string = f'vetores_energia-tipo-malha-quadrada-normal-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.pkl'
    
    string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if condicao_contorno == 'solte-1':
        result_string = 'vetores_energia' + string_padrao + '.pkl'
    else:
        result_string = 'vetores_energia' + string_padrao + f'-centro-{None}.pkl'
    
    # Obtém o caminho completo do arquivo .pkl
    caminho_completo = os.path.join('vetores_energia', result_string)
    
    # Abre o arquivo no modo de leitura binária ('rb') usando o with statement
    with open(caminho_completo, 'rb') as arquivo:
        # Carrega os dados do arquivo
        lista_dados = pickle.load(arquivo)
    
    # Calcula o maior valor na lista usando numpy.max
    maior_valor =float(format(np.max(lista_dados), '.2f'))

    if maior_valor == 0:
        exp = maior_valor
    else:
        exp = (format(maior_valor, '.2f'))
    
    return exp

@app.callback(
    Output('tempo_exe', 'children'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value')]
)
def update_output(num_passos, elementos, delta, grau, condicao_contorno):
    
    string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if condicao_contorno == 'solte-1':
        result_string = 'vetor_tempo' + string_padrao + '.pkl'
    else:
        result_string = 'vetor_tempo' + string_padrao + f'-centro-{None}.pkl'
    
    
    #result_string = f'vetor_tempo-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.pkl'
    
    # Obtém o caminho completo do arquivo .pkl
    caminho_completo = os.path.join('vetores_tempo_geral', result_string)
    
    # Abre o arquivo no modo de leitura binária ('rb') usando o with statement
    with open(caminho_completo, 'rb') as arquivo:
        # Carrega os dados do arquivo
        lista_dados = pickle.load(arquivo)
    
    # Calcula o maior valor na lista usando numpy.max
    maior_valor =str(format(np.max(lista_dados), '.2f')) + ' s'
    
    return maior_valor

   
@app.callback(
    Output('png-display', 'src'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value')]
)
def update_output(num_passos, elementos, delta, grau, condicao_contorno):
    string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if condicao_contorno == 'solte-1':
        result_string = 'vetores_un' + string_padrao + '.png'
    else:
        result_string = 'vetores_un' + string_padrao + f'-centro-{None}.png'
    
    #result_string = f'vetores_un-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.png'
    png_path = os.path.join(folder_path_png, result_string)
    encoded_png = read_and_encode_file(png_path)
    
    return f'data:image/png;base64,{encoded_png}'

@app.callback(
    Output('gif-display', 'src'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'), 
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value')]
)
def update_output(num_passos, elementos, delta, grau, condicao_contorno):
    result_string = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    result_string = result_string[1:]
    
    #result_string = f'tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}'
    png_path = os.path.join(folder_path_png, result_string)
    gif_path = os.path.join(folder_path_gif, f'vetores_un-{result_string}.gif')
    
    # Inicializa a variável para o caso de o arquivo GIF não existir
    encoded_gif = None

    # Tenta ler e codificar o conteúdo do arquivo GIF
    try:
        with open(gif_path, 'rb') as gif_file:
            gif_data = gif_file.read()
            encoded_gif = f'data:image/gif;base64,{base64.b64encode(gif_data).decode("utf-8")}' if gif_data else None
    except Exception as e:
        print(f"Erro ao ler o arquivo GIF: {e}")

    # Retorna as representações em base64 dos arquivos para exibição
    return encoded_gif
    
    return gif_path

@app.callback(
    Output('grafico-tempo-valores', 'figure'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value')]
)
def update_output(num_passos, elementos, delta, grau, condicao_contorno):
    
    vetores = []    

    for i, valor in enumerate(grau_dos_polinomios):
        vetor_tempo = np.linspace(0, 4*np.pi , num_passos)
        #result_string = f'vetores_energia-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{valor}.pkl'
        
        string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, valor)
        
        if condicao_contorno == 'solte-1':
            result_string = 'vetores_energia' + string_padrao + '.pkl'
        else:
            result_string = 'vetores_energia' + string_padrao + f'-centro-{None}.pkl'
        
        caminho_completo = os.path.join('vetores_energia', result_string)
        
        valores = pd.read_pickle(caminho_completo)
        valores = pd.DataFrame({f'Grau {valor}': valores})
        vetores.append(valores)

    df = pd.concat(vetores, axis=1)
    df['tempo'] = vetor_tempo
    
    figure = px.line(df, x='tempo', y = df.columns[:])
    figure.update_layout(plot_bgcolor='#e5e5e5', 
                         paper_bgcolor='#4C4C4C', 
                         legend=dict(font=dict(color='#dfdfdf')), 
                         xaxis=dict(title_font=dict(color='#dfdfdf'), tickfont=dict(color='#dfdfdf')),
                         yaxis=dict(title_font=dict(color='#dfdfdf'), tickfont=dict(color='#dfdfdf'))
                         )
    
    return figure


# Executa o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
