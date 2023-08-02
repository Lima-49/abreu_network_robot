import pandas as pd
import streamlit as st
import os
import datetime
from pathlib import Path
import base64
import pytz
import extracao_dados as ed

OUTPUT_PATH = os.getcwd() + "\\" + 'files' + '\\log_view.csv'
LOGO_PATH = 'logo.png'

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path, width='200px'):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid' width='{}'>".format(
        img_to_bytes(img_path), width
    )
    return img_html

if os.path.isfile(OUTPUT_PATH):
    df_data = pd.read_csv(OUTPUT_PATH, sep=',')
    customer_list = df_data['To'].sort_values().drop_duplicates()
else:
    st.subheader("Clique em Atualizar os dados para os gráficos carregarem")
    st.text(os.listdir(os.getcwd()))
    
if st.button('Atualizar Dados '):
    with st.spinner('Carregando Dados'):
        ed.run()
        
st.text(os.listdir(os.getcwd() + "\\" + 'files'))
df_data = pd.read_csv(OUTPUT_PATH, sep=',')
customer_list = df_data['To'].sort_values().drop_duplicates()

# Set the timezone to São Paulo, Brazil (UTC-3)
saopaulo_tz = pytz.timezone('America/Sao_Paulo')

# Get the current date and time in the São Paulo timezone
current_date = datetime.datetime.now(saopaulo_tz).strftime("%d/%m/%Y")

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
col1, col2 = st.columns(2)

with col1:
    #Grafico de quantidade de email por acao realizada
    df_action = df_data.loc[df_data['To']==option]
    chart_data = df_action['Action'].value_counts()
    st.bar_chart(chart_data)

with col2:
    #Quantidade de emails recebidos pela conta
    st.markdown("<h3 align='center'>Quantidade de emails recebidos</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{str(df_action.shape[0])}</h1>", unsafe_allow_html=True)

#contas que mais madaram email x ação realizada
# Filtra o DF com a opção selecionada
df_filt = df_data.loc[df_data['To'] == option]

# Conta a ocorrencia de emails recebidos 
serie = df_filt['From'].value_counts()
email_series = serie.loc[serie > 2].index.to_list()

# filtra o df baseado nas ccontas de emails recebidos
df_from = df_filt.loc[df_filt['From'].isin(email_series)]

# Conta as ocorrecnais e as ações realizadas por email recebido
qtd_series = df_from['From'].value_counts()
unique_actions = df_from.drop_duplicates(subset=['From'])['Action']

# Cria um novo dataframe
df_tres = pd.DataFrame({'From': qtd_series.index, 'Qtd': qtd_series.values, 'Actions': unique_actions})

# Cria um grafico com essas informações
st.bar_chart(df_tres.set_index('From')['Qtd'])