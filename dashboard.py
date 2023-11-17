import os
import base64
from dash import Dash, dcc, html, Input, Output

folder_path_gif = "videos"
folder_path_png = "graficos_energias"


numero_de_elementos = [10, 20]
numero_de_passos = [100, 200, 400]
delta = [0, 0.01, 0.05]
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
    
    html.Ul([ 
    
    html.Li([
    html.H3("Número de passos:"),
    dcc.Dropdown(numero_de_passos, value=100, id='dropdown-1', className="seletor"),
    ]),
    
    html.Li([
    html.H3("Número de elementos:"),
    dcc.Dropdown(numero_de_elementos, value=10, id='dropdown-2', className="seletor"),
    ]),
    
    html.Li([
    html.H3("Tamanho do delta:"),
    dcc.Dropdown(delta, value=0, id='dropdown-3', className="seletor"),  
    ]),
    
    html.Li([
    html.H3("Grau dos polinômios:"),
    dcc.Dropdown(grau_dos_polinomios, value=2, id='dropdown-4', className="seletor"),
    ]),
    
    html.Li([
    html.H3("Condição de contorno:"),
    dcc.Dropdown(condicoes_contorno, value='solte-1', id='dropdown-5', className="seletor"),
    ]),
    
    ], className="opcoes"),
    
    html.Div([
    
    html.Div([
    html.H2("Gráfico em escala Logarítmica"),
    
    html.Div([
        html.Img(id='png-display', style={'width': '100%'})
    ]),
    ], className="imagem"),
    
    html.Div([
    html.H2("Comportamento da solução"),
   
    html.Div([
        html.Img(id='gif-display', style={'width': '100%'})
    ]),
    ]),
    ], className="solucoes")

])


@app.callback(
    Output('png-display', 'src'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'),
     Input('dropdown-4', 'value')]
)
def update_output(num_passos, elementos, delta, grau):
    result_string = f'vetores_un-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}.png'
    png_path = os.path.join(folder_path_png, result_string)
    encoded_png = read_and_encode_file(png_path)
    
    return f'data:image/png;base64,{encoded_png}'

@app.callback(
    Output('gif-display', 'src'),
    [Input('dropdown-1', 'value'),
     Input('dropdown-2', 'value'),
     Input('dropdown-3', 'value'), 
     Input('dropdown-4', 'value')]
)
def update_output(num_passos, elementos, delta, grau):
    result_string = f'tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-{elementos}-num_steps-{num_passos}-delta-{delta}-grau-{grau}'
    png_path = os.path.join(folder_path_png, result_string)
    gif_path = os.path.join(folder_path_gif, f'waves-{result_string}.gif')
    
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


# Executa o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
