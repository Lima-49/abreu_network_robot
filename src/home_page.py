"""
Pagina criada utilizando o streamlit, para mostrar os dados
e ativar algumas ferrametnas da empresa Abreu Networks
"""
import os
import pandas as pd
import streamlit as st
import header
import extracao_dados as ed

OUTPUT_PATH = os.getcwd() + "/" + 'files' + '/log_view.csv'

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

    #header da pagina
    header.main()

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
        st.markdown(f"""<h1 style='text-align:center;font-size:80px;'>{qtd_em}</h1>""",
        unsafe_allow_html=True)

    #contas que mais madaram email x ação realizada
    # Filtra o DF com a opção selecionada
    df_filt = df_data.loc[df_data['To'] == option]

    # Conta a ocorrencia de emails recebidos
    serie = df_filt['From'].value_counts()
    email_series = serie.loc[serie > 0].index.to_list()

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
