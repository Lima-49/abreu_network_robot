"""
The above code is a Python script that allows users to schedule the execution of a robot at specific
dates and times, with options for one-time, daily, weekly, and monthly scheduling.

:param img_path: The `img_path` parameter is a string that represents the path to an image file. It
should include the file name and extension
:return: The code does not have a specific return statement. It defines several functions and
executes the `config_run()` function at the end. The `config_run()` function allows the user to
select the execution period for a robot and does not return any value.
"""
import datetime
import os
import requests
import streamlit as st
import altair as alt
import pandas as pd
import header
import black_list as bl

#Dia atual
actual_date = datetime.datetime.today()
LOG_PATH = r'database\log_execucao.xlsx'
CONFIG_RUN_PATH = r'database\config_execucao.xlsx'
OUTPUT_PATH = os.getcwd() + "\\" + 'files'

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

def chart_execution(df_show):
    """
    The function `chart_execution` takes a dataframe as input
    counts the occurrences of each country in
    a specific column, and creates a bar chart using Altair to visualize the counts.

    :param df_show: The parameter `df_show` is a pandas DataFrame
    that contains the data to be used for
    creating the chart. It should have a column named 'Pais'
    which represents the countries, and the
    function will count the occurrences of each country in this column
    :return: The function `chart_execution` returns an Altair bar chart object.
    """
    # Conte o número de ocorrências de cada país
    country_counts = df_show['Pais'].value_counts().reset_index()
    country_counts.columns = ['Pais', 'Contagem']

    # Crie um gráfico de barras com Altair
    chart = alt.Chart(country_counts).mark_bar().encode(
        x=alt.X('Contagem:Q', title='Contagem'),
        y=alt.Y('Pais:N', title='País', sort='-x')
    )

    # Personalize o gráfico
    chart = chart.properties(width=600)
    return chart

def read_config_path(bot_option):
    """
    This function reads a configuration file and returns a dictionary of values for a specific robot
    option.
    
    :param bot_option: `bot_option` parameter is the name of the robot for which you want to read
    the configuration path
    :return: a dictionary containing the values from the specified row in the "df_config" DataFrame.
    If there is no configuration for the specified robot, it returns None.
    """
    #abrindo arquivo de config
    df_config = pd.read_excel(CONFIG_RUN_PATH)

    #Filtra o nome do robo
    df_robot = df_config.loc[df_config['NOME_ROBO']==bot_option]

    #Se existir configuracao para esse robo
    if df_robot.shape[0] > 0:

        #pega a linha que esta salvo
        robot_line = df_robot.index[0]

        #cria um dicionario com esses valores
        values_dict = {col: df_robot.at[robot_line, col] for col in df_robot.columns}

        #Retorna esse dicionario
        return values_dict

    return None

def insert_config_path(config_values):
    """
    The function `insert_config_path` reads an Excel file,
    appends new data to it, and saves the updated
    file.
    
    :param config_values: The `config_values` parameter is a list or array-like object
    that contains the new configuration values
    that you want to insert into the existing configuration file
    """

    df_log = pd.read_excel(CONFIG_RUN_PATH)

    df_new = pd.DataFrame(config_values, index=[df_log.shape[0]])

    df_concat = pd.concat([df_log, df_new])

    df_concat.to_excel(CONFIG_RUN_PATH, index=False)

def call_api(ip_address):
    """
    The function `call_api` takes an IP address as input and returns the country name associated wit
    that IP address using the ip2location.io API.
    
    :param ip_address: The `ip_address` parameter is a string representing the IP address for which
    want to retrieve the country name
    :return: the country name associated with the given IP address.
    """

    key = '6C9230AA6FCFBB5F51A9B096E2259EFE'
    url = f'https://api.ip2location.io/?key={key}&ip={ip_address}'
    response = requests.get(url, timeout=10)

    return response.json()['country_name'] if response.status_code == 200 else None

def config_run():
    """
    The `config_run()` creates a markdown header for a mail security report and allows the user
    to select the execution period for a robot.
    """

    #Header da pagina
    header.main()

    #Criando tabs para separar os itens da pagina
    tab1, tab2 = st.tabs(["Execução", "Log de Execução"])

    with tab1:
        #Clica no botão atualizar os dados
        st.subheader("Clique em Rodar para executar o robô")
        if st.button('Rodar'):

            #Enquanto rodar o robo para extrair os arquivos, fica carregando
            with st.spinner('Executando robo'):

                #Rodando o robo black list
                bl.run()

                #Abrindo o arquivo extraido
                df_bl = pd.read_csv(f'{OUTPUT_PATH}/black_list.csv')

                #Removendo os valores duplicados
                ip_list = df_bl['Source IP'].drop_duplicates()

                #Criando um dicionario com os ips e com os paises respectivos
                coutry_list = list(map(call_api, ip_list))

                #Salvando em um df
                df_show = pd.DataFrame()
                df_show['Ip'] = ip_list
                df_show['Pais'] = coutry_list
                df_show.to_excel(f'{OUTPUT_PATH}/black_list.xlsx', index=False)

                #soltando os baloes
                st.balloons()

        #mostrando o novo  df criado
        df_show.read_excel(f'{OUTPUT_PATH}/black_list.xlsx')
        st.dataframe(df_show, width=800)

        # Exiba o gráfico no Streamlit
        chart = chart_execution(df_show)
        st.title("Países mais frequentes")
        st.altair_chart(chart, use_container_width=True)

    with tab2:
        #Abindo o arquivo de log
        df_log = pd.read_excel(LOG_PATH)
        df_filt = df_log.loc[df_log['NOME_ROBO']=='Black List']

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

if __name__ == "__main__":
    config_run()
