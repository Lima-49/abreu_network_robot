"""
Pagina criada utilizando o streamlit, para mostrar os dados
e ativar algumas ferrametnas da empresa Abreu Networks
"""
import os
import datetime
from pathlib import Path
import base64
import pandas as pd
import streamlit as st
import pytz
import extracao_dados as ed

OUTPUT_PATH = os.getcwd() + "/" + 'files' + '/log_view.csv'
LOGO_PATH = 'logo.png'

def img_to_bytes(img_path):
    """
    A função img_to_bytes recebe como entrada o caminho de um arquivo de imagem,
    lê o arquivo de imagem como bytes, codifica os bytes usando a codificação base64
    e retorna a string codificada.

    :param img_path: O parâmetro img_path é uma sequência de caracteres
    que representa o caminho para um arquivo de imagem.
    :return: a imagem codificada como uma string.
    """
    #Le o caminho da imagem em bytes
    img_bytes = Path(img_path).read_bytes()

    #decodifica os bytes para base64
    encoded = base64.b64encode(img_bytes).decode()

    #Retorna a imagem decodificada
    return encoded

def img_to_html(img_path, width='200px'):
    """
    The function takes an image path and an optional width parameter and returns an HTML
    string that displays the image with the specified width.
    
    :param img_path: The `img_path` parameter is the path to the image file that you want to convert 
    to HTML. It should be a string representing the file path, including the file name and extension
    :param width: The `width` parameter is used to specify the width of the image in the HTML output
    It is set to a default value of '200px', but you can change it to any valid CSS width value that 
    you prefer, defaults to 200px (optional)
    :return: an HTML string that contains an image tag. The image source is set to a base64-encoded
    representation of the image located at the specified img_path. The image is displayed with a
    class of 'img-fluid' and a width specified by the width parameter (defaulting to '200px').
    """
    img_src = f"'data:image/png;base64,{img_to_bytes(img_path)}'"
    html_img = f"<img src= {img_src} class='img-fluid' width='{width}'>"
    return html_img

def amostragem_dados():
    """
    The `main_view` function displays a main view of a mail security report, including graphs and
    statistics based on email data.
    """

    #Se o arquivo extraido do portal ja existir
    if os.path.isfile(OUTPUT_PATH):

        #Abre o arquivo existente
        df_data = pd.read_csv(OUTPUT_PATH, sep=',')

        #Transforma em uma lista a quantidade de emails da coluna To
        customer_list = df_data['To'].sort_values().drop_duplicates()

    #Se o arquivo não existir, pede para o usuario clicar no botao
    else:
        st.subheader("Clique em Atualizar os dados para os gráficos carregarem")

    #Clica no botão atualizar os dados
    if st.button('Atualizar Dados '):

        #Enquanto rodar o robo para extrair os arquivos, fica carregando
        with st.spinner('Carregando Dados'):
            ed.run()

    #Le o arquivo com os emails do dia atual
    df_data = pd.read_csv(OUTPUT_PATH, sep=',')

    #Transforma em uma lista a quantidade de emails da coluna To
    customer_list = df_data['To'].sort_values().drop_duplicates()

    #salva na variavel o fuso horario de sao paulo
    saopaulo_tz = pytz.timezone('America/Sao_Paulo')

    #pega a data atual, formatando como string
    current_date = datetime.datetime.now(saopaulo_tz).strftime("%d/%m/%Y")

    #Cria um markdown para centralizar os itens na pagina
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: center;">
            <h1 style="text-align: center;">MAIL SECURITY REPORT</h1>
            {img_to_html(LOGO_PATH, width='100px')}
        </div>
            <p style="text-align: center; font-size: 20px;">{current_date}</p>
        """,
        unsafe_allow_html=True
    )

    #Lista de clientes que será utilizada para filtrar os graficos
    option = st.selectbox('Selecione o cliente',(customer_list))

    #Cria dois conteiners para organizar os itens na tela
    col1, col2 = st.columns(2)

    with col1:
        #Grafico de quantidade de email por acao realizada
        df_action = df_data.loc[df_data['To']==option]
        chart_data = df_action['Action'].value_counts()
        st.bar_chart(chart_data)

    with col2:
        #Quantidade de emails recebidos pela conta
        titulo1 = 'Quantidade de emails recebidos'
        st.markdown(f"<h3 align='center'>{titulo1}</h3>", unsafe_allow_html=True)

        qtd_em = str(df_action.shape[0])
        st.markdown(f"<h1 style='text-align:center;font-size:80px;'>{qtd_em}</h1>")

    #contas que mais madaram email x ação realizada
    # Filtra o DF com a opção selecionada
    df_filt = df_data.loc[df_data['To'] == option]

    # Conta a ocorrencia de emails recebidos
    serie = df_filt['From'].value_counts()
    email_series = serie.loc[serie > 1].index.to_list()

    # filtra o df baseado nas contas de emails recebidos
    df_from = df_filt.loc[df_filt['From'].isin(email_series)]

    # Conta as ocorrencias e as ações realizadas por email recebido
    qtd_series = df_from['From'].value_counts()
    unique_actions = df_from.drop_duplicates(subset=['From'])['Action']

    # Cria um novo dataframe
    df_tres = pd.DataFrame(
        {
            'From': qtd_series.index, 
            'Qtd': qtd_series.values, 
            'Actions': unique_actions
        }
    )

    # Cria um grafico com essas informações
    df_tres.set_index('From', inplace=True)
    st.bar_chart(df_tres['Qtd'])

if __name__ == '__main__':
    amostragem_dados()
