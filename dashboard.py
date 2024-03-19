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

def modelo_nome(condicao_contorno, elementos, num_passos, delta, p, grau, possui_furo):
    if possui_furo == 'não':
        string_padrao = f'-tipo-malha-quadrada-normal-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-p-{p}-grau-{grau}'
    else:
        string_padrao = f'-tipo-malha-gmsh-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-p-{p}-grau-{grau}'
    return string_padrao

numero_de_elementos = [10, 20]
numero_de_passos = [100, 200, 400]
delta = [format(0, '.1f'), 0.01, 0.05]
valor_p = [2, 4]
grau_dos_polinomios = [1, 2, 4]
condicoes_contorno = ['solte-1', 'prenda-as-quatro']
centro = [0.25, 0.5, 0.75]
raio = [0.125]

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
        html.H3("Valor de p:"),
        dcc.Dropdown(valor_p, value=4, id='dropdown-4', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        html.Li([
        html.H3("Grau dos polinômios:"),
        dcc.Dropdown(grau_dos_polinomios, value=2, id='dropdown-5', className="seletor", style={'backgroundColor': '#4C4C4C', 'color': '#838383'}),
        ]),
        
        html.Li([
        html.H3('Possui furo?:'),
        dcc.Dropdown(
            id='dropdown-condicao',
            options=[
                {'label': 'sim', 'value': 'sim'},
                {'label': 'não', 'value': 'não'}
            ],
            value='não',
            style={'backgroundColor': '#4C4C4C', 'color': '#838383'}
        ),
        ]),
        dcc.Loading(
            id="loading-dropdown",
            type="circle",
            children=[
                html.Div([
                    html.H3('Centro:', id='label-condicao1', style={'display': 'none'}),
                    dcc.Dropdown(centro, value = 0.25, id='dropdown-condicao1', style={'display': 'none'}),
                    
                    html.H3('Raio:', id='label-condicao2', style={'display': 'none'}),
                    dcc.Dropdown(raio, value = 0.125, id='dropdown-condicao2', style={'display': 'none'}),
                    
                    html.H3('Borda:', id='label-condicao3', style={'display': 'none'}),
                    dcc.Dropdown(condicoes_contorno, value = 'solte-1', id='dropdown-condicao3', style={'display': 'none'}),
                    
                    html.H1(id='output-h1', style={'display': 'none'})
                ])
            ]
        ),
        
        
        
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
    [Output('dropdown-condicao1', 'style'),
     Output('dropdown-condicao2', 'style'),
     Output('dropdown-condicao3', 'style'),
     Output('label-condicao1', 'style'),
     Output('label-condicao2', 'style'),
     Output('label-condicao3', 'style'),
     Output('output-h1', 'children')],
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value'),
     Input('dropdown-5', 'value'),
     Input('dropdown-condicao', 'value'),
     Input('dropdown-condicao1', 'value'),
     Input('dropdown-condicao2', 'value'),
     Input('dropdown-condicao3', 'value')]
)
def update_dropdown_and_h1(num_passos, elementos, delta, p, grau, possui_furo, centro, raio, condicao):
    dropdown_condicao1_style = {'backgroundColor': '#4C4C4C', 'display': 'block' if possui_furo == 'sim' else 'none'}
    dropdown_condicao2_style = {'backgroundColor': '#4C4C4C', 'display': 'block' if possui_furo == 'sim' else 'none'}
    dropdown_condicao3_style = {'backgroundColor': '#4C4C4C', 'display': 'block' if possui_furo == 'sim' else 'none'}
    label_condicao1_style = {'display': 'block' if possui_furo == 'sim' else 'none'}
    label_condicao2_style = {'display': 'block' if possui_furo == 'sim' else 'none'}
    label_condicao3_style = {'display': 'block' if possui_furo == 'sim' else 'none'}
    
    
    if possui_furo == 'sim':
        result_string = f'-tipo-malha-gmsh-condicoes-contorno-{condicao}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-p-{p}-grau-{grau}'
        
    else:
        result_string = f'-tipo-malha-quadrada-normal-condicoes-contorno-{condicao}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-p-{p}-grau-{grau}'
        
        
    
    # Obtém o caminho completo do arquivo .pkl
    #caminho_completo = os.path.join('vetores_energia', result_string)

    return dropdown_condicao1_style, dropdown_condicao2_style,dropdown_condicao3_style, label_condicao1_style, label_condicao2_style, label_condicao3_style, result_string


@app.callback(
    Output('valor_max', 'children'),
    [Input('output-h1', 'children'),
    Input('dropdown-condicao', 'value'),
    Input('dropdown-condicao1', 'value'),
    Input('dropdown-condicao2', 'value')]
)
def update_output(result_string, possui_furo, centro, raio):
    #result_string = f'vetores_energia-tipo-malha-quadrada-normal-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.pkl'
    
    #string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if possui_furo == 'não':
        result_string = 'vetores_energia' + result_string + '.pkl'
    else:
        result_string = 'vetores_energia' + result_string + f'-centro-{centro}-raio-{raio}.pkl'
    
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
    [Input('output-h1', 'children'),
     Input('dropdown-condicao', 'value'),
     Input('dropdown-condicao1', 'value'),
     Input('dropdown-condicao2', 'value')]
)
def update_output(result_string, possui_furo, centro, raio):
    #string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if possui_furo == 'não':
        result_string = 'vetor_tempo' + result_string + '.pkl'
    else:
        result_string = 'vetor_tempo' + result_string + f'-centro-{centro}-raio-{raio}.pkl'
    
    
    #result_string = f'vetor_tempo-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.pkl'
    
    # Obtém o caminho completo do arquivo .pkl
    caminho_completo = os.path.join('vetores_tempo_geral', result_string)
    # print('oi', caminho_completo)
    # Abre o arquivo no modo de leitura binária ('rb') usando o with statement
    with open(caminho_completo, 'rb') as arquivo:
        # Carrega os dados do arquivo
        lista_dados = pickle.load(arquivo)
    
    # Calcula o maior valor na lista usando numpy.max
    maior_valor =str(format(np.max(lista_dados), '.2f')) + ' s'
    
    return maior_valor


@app.callback(
    Output('png-display', 'src'),
    [Input('output-h1', 'children'),
     Input('dropdown-condicao', 'value'),
     Input('dropdown-condicao1', 'value'),
     Input('dropdown-condicao2', 'value')]
)
def update_output(result_string, possui_furo, centro, raio):

    #string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    
    if possui_furo == 'não':
        result_string = 'vetores_un' + result_string + '.png'
    else:
        result_string = 'vetores_un' + result_string + f'-centro-{centro}-raio-{raio}.png'
    
    #result_string = f'vetores_un-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.png'
    png_path = os.path.join(folder_path_png, result_string)
    encoded_png = read_and_encode_file(png_path)
    
    return f'data:image/png;base64,{encoded_png}'

@app.callback(
    Output('gif-display', 'src'),
    [Input('output-h1', 'children'),
     Input('dropdown-condicao', 'value'),
     Input('dropdown-condicao1', 'value'),
     Input('dropdown-condicao2', 'value')]
)
def update_output(result_string, possui_furo, centro, raio):
    
    #result_string = modelo_nome(condicao_contorno, elementos, num_passos, delta, grau)
    result_string = result_string[1:]
    
    #result_string = f'tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}'
    png_path = os.path.join(folder_path_png, result_string)
    
    if possui_furo == 'não':
        gif_path = os.path.join(folder_path_gif, f'vetores_un-{result_string}.gif')
    else:
        gif_path = os.path.join(folder_path_gif, f'vetores_un-{result_string}-centro-{centro}-raio-{raio}.gif')
    
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
     Input('dropdown-5', 'value'),
     Input('dropdown-condicao3', 'value'),
     Input('dropdown-condicao','value'),
     Input('dropdown-condicao1', 'value'),
     Input('dropdown-condicao2', 'value')]
)
def update_output(num_passos, elementos, delta, p, grau, condicao_contorno, possui_furo, centro, raio):
    
    vetores = []    

    for i, valor in enumerate(grau_dos_polinomios):
        vetor_tempo = np.linspace(0, 4*np.pi , num_passos)
        
        #result_string = f'vetores_energia-tipo-malha-quadrada-normal-condicoes-contorno-{condicao_contorno}-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{valor}.pkl'
        
        if possui_furo == 'não':
            condicao_contorno = 'solte-1'
            
            string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, p, valor, possui_furo)
            
            result_string = 'vetores_energia' + string_padrao + '.pkl'
        else:
            string_padrao = modelo_nome(condicao_contorno, elementos, num_passos, delta, p, valor, possui_furo)
            
            result_string = 'vetores_energia' + string_padrao + f'-centro-{centro}-raio-{raio}.pkl'
        
        
        caminho_completo = os.path.join('vetores_energia', result_string)
        
        valores = pd.read_pickle(caminho_completo)
        valores = pd.DataFrame({f'Grau {valor}': valores})
        vetores.append(valores)

    df = pd.concat(vetores, axis=1)
    
    df['tempo'] = vetor_tempo
    
    colors = ['#2B8B6F', '#FDE030', '#45075B']
    figure = px.line(df, x='tempo', y = df.columns[:], color_discrete_sequence=colors)
    
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
