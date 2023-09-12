"""
The `main()` function generates a markdown report with the current date, a centered title, and a
logo.

:param img_path: The `img_path` parameter is the path to the image file that you want to convert to
HTML. It should be a string representing the file path, including the file name and extension
:return: The `main()` function does not return any value. It generates a markdown report with the
current date, a centered title, and a logo.
"""
import datetime
import os
from pathlib import Path
import base64
import streamlit as st
import pytz
OUTPUT_PATH = os.getcwd() + "/" + 'images'
LOGO_PATH = OUTPUT_PATH + '/logo.png'

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

def main():
    """
    The `main()` generates a markdown report with the current date and a centered title and
    logo.
    """
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
