"""
Pagina criada utilizando o streamlit, para mostrar os dados
e ativar algumas ferrametnas da empresa Abreu Networks
"""
import os
import pandas as pd
import altair as alt
import streamlit as st
import header
import extracao_dados as ed

OUTPUT_PATH = os.getcwd() + "/" + 'files' + '/log_view.csv'
LOG_PATH = r'database\log_execucao.xlsx'

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

def dount_chart_execution(df_filt):
    """
    The function `donut_chart_execution` takes a filtered DataFrame as input, combines the
    'DATA_EXECUCAO' and 'HORA_EXECUCAO' columns into a single 'DATA_HORA_EXECUCAO' column, sorts the
    DF by 'DATA_HORA_EXECUCAO' in descending order, creates a donut chart based on the 'STATUS'
    column, and adds the total number of rows in the center of the chart.
    
    :param df_filt: The parameter `df_filt` is a DataFrame that contains the data to be used for
    creating the donut chart. It should have the following columns:
    :return: a donut chart visualization created using the Altair library.
    The donut chart represents
    the count of successful and failed executions in a DataFrame. The chart also includes the total
    number of rows in the DataFrame displayed in the center of the donut.
    """
    # Combine as colunas 'DATA_EXECUCAO' e 'HORA_EXECUCAO' em uma única coluna 'DATA_HORA_EXECUCAO'
    df_filt['DH_EXECUCAO']=pd.to_datetime(df_filt['DATA_EXECUCAO']+' '+df_filt['HORA_EXECUCAO'])

    # Ordene o DataFrame pelo campo 'DATA_HORA_EXECUCAO' do mais recente para o mais antigo
    df_filt.sort_values(by='DH_EXECUCAO', ascending=False, inplace=True)

    # Calcular o número total de linhas
    total_linhas = len(df_filt)

    color_mapping = alt.Scale(domain=['Sucesso', 'Falha'], range=['#6BF58D', '#F55D59'])

    # Criar um gráfico de anel
    chart = alt.Chart(df_filt).mark_arc().transform_aggregate(
        count='count()',
        groupby=['STATUS']
    ).encode(
        theta='count:Q',
        color=alt.Color('STATUS:N', scale=color_mapping),  # Configurar cores com base no mapeamento
    ).properties(
        width=300,
        height=300
    )

    # Adicionar o número total de linhas no centro do anel
    text = alt.Chart(pd.DataFrame({'total_linhas': [total_linhas]})).mark_text(
        size=24,
        color='white',
        fontSize=50,
        align='center',  # Centralizar horizontalmente
        baseline='middle'  # Centralizar verticalmente
    ).encode(
        text='total_linhas:Q'
    )

    # Combinar o gráfico de anel e o texto
    donut_chart = (chart + text).configure_arc(
        innerRadius=70  # Tamanho do buraco no meio do anel
    )

    return donut_chart

def line_chart_execution(df_filt):
    """
    The `line_chart_execution` creates a line chart with points to represent the success and
    failure status of executions over time.
    
    :param df_filt: The parameter `df_filt` is a DataFrame that contains the data to be plotted
    in the line chart. It should have the following columns:
    :return: a combined line chart and scatter plot.
    """
    df_bar = df_filt
    df_bar['STATUS'] = df_bar['STATUS'].replace({'Sucesso':1, 'Falha':0})
    df_bar['ID'] = [x for x in range(df_bar.shape[0])]

    # Criar a especificação do gráfico de barras
    chart = alt.Chart(df_bar).mark_line().encode(
        x=alt.X('ID:N', axis=alt.Axis(title='Data de Execução'), sort=None),
        y=alt.Y('STATUS:Q', axis=alt.Axis(title='STATUS'))
    ).properties(
        title='Contagem de Sucesso e Falha por Data de Execução'
    )

    # Adicionar pontos quando y=0
    points = alt.Chart(df_bar).mark_point(color='red', size=100).encode(
        x=alt.X('ID:N'),
        y=alt.Y('STATUS:Q'),
        tooltip=['DETALHES:N']
    )

    # Combinar o gráfico de linha com os pontos
    combined_chart = chart + points

    return combined_chart

def main_page():
    """
    The `main_page` function creates a webpage with two tabs, one for data execution and another for
    execution logs, and displays charts and data related to the execution logs.
    """
    #Header da pagina
    header.main()

    #Criando tabs para separar os itens da pagina
    tab1, tab2 = st.tabs(["Execução", "Log de Execução"])

    with tab1:
        amostragem_dados()

    with tab2:
        #Abindo o arquivo de log
        df_log = pd.read_excel(LOG_PATH)
        df_filt = df_log.loc[df_log['NOME_ROBO']=='extracao_dados']

         # Combine as colunas 'DATA_EXECUCAO' e 'HORA_EXECUCAO' em uma única coluna 'DH_EXECUCAO'
        df_filt['DH_EXECUCAO']=pd.to_datetime(df_filt['DATA_EXECUCAO']+' '+df_filt['HORA_EXECUCAO'])

        # Ordene o DataFrame pelo campo 'DATA_HORA_EXECUCAO' do mais recente para o mais antigo
        df_filt.sort_values(by='DH_EXECUCAO', ascending=False, inplace=True)

        st.header("Log de Execução")
        st.dataframe(df_filt.head(), hide_index=True)

        col1,col2 = st.columns(2)

        with col1:
            #Criando um grafico do tipo donuts, mostrando quantidade de execucao
            donut_chart = dount_chart_execution(df_filt)
            st.altair_chart(donut_chart, theme='streamlit')
        with col2:
            #Criando um grafico para indicar os status e detalhes da execucao
            line_chart = line_chart_execution(df_filt)
            st.altair_chart(line_chart, use_container_width=True, theme='streamlit')

if __name__ == '__main__':
    main_page()
