import os
import base64
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

# Obtém a lista de arquivos GIF na pasta "videos" e PNG na pasta "graficos_energias"
folder_path_gif = "videos"
folder_path_png = "graficos_energias"
gif_files = [f for f in os.listdir(folder_path_gif) if f.endswith(".gif")]
png_files = [f for f in os.listdir(folder_path_png) if f.endswith(".png")]

# Função para extrair parte do nome do arquivo sem a extensão .gif ou .png
def extract_partial_name(file_name):
    # Exemplo: 'vetores_un-tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-10-num_steps-100-grau-4.png'
    # Resultado: 'tipo-malha-quadrada-normal-condicoes-contorno-solte-1-elementos-10-num_steps-100-grau-4'
    parts = file_name[:-4].split('-')[1:]
    return '-'.join(parts)

# Função para ler e codificar um arquivo para base64
def read_and_encode_file(file_path):
    with open(file_path, 'rb') as file:
        encoded_file = base64.b64encode(file.read()).decode('utf-8')
    return encoded_file

# Inicializa o aplicativo Dash
app = Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1("Dashboard de Arquivos"),
    
    # Componente Dropdown para selecionar o arquivo
    dcc.Dropdown(
        id='file-dropdown',
        options=[{'label': extract_partial_name(file), 'value': file} for file in png_files],
        value=png_files[0]
    ),
    
    # Div para exibir o arquivo PNG selecionado (com tamanho 50%)
    html.Div([
        html.Img(id='png-display', style={'width': '50%'})
    ]),
    
    # Div para exibir o arquivo GIF correspondente (com tamanho 50%)
    html.Div([
        html.Img(id='gif-display', style={'width': '50%'})
    ])
])

# Callback para atualizar a exibição dos arquivos com base na seleção do Dropdown
@app.callback(
    [Output('png-display', 'src'),
     Output('gif-display', 'src')],
    [Input('file-dropdown', 'value')]
)
def update_files(selected_file):
    # Extrai a parte do nome do arquivo sem a extensão .png
    partial_name = extract_partial_name(selected_file)
    
    # Caminho completo para o arquivo PNG selecionado na pasta "graficos_energias"
    png_path = os.path.join(folder_path_png, selected_file)
    # Caminho completo para o arquivo GIF correspondente na pasta "videos"
    gif_path = os.path.join(folder_path_gif, f'waves-{partial_name}.gif')
    
    # Lê e codifica o conteúdo dos arquivos em base64
    encoded_png = read_and_encode_file(png_path)
    
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
    return f'data:image/png;base64,{encoded_png}', encoded_gif

# Executa o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)












































