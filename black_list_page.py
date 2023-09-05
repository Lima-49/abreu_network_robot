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
import calendar
import time
import streamlit as st
import schedule
import altair as alt
import pandas as pd
import header
import black_list as bl

#Dia atual
actual_date = datetime.datetime.today()
LOG_PATH = r'database\log_execucao.xlsx'
CONFIG_RUN_PATH = r'database\config_execucao.xlsx'

def schedule_onetime(robot, config_values):
    """
    The `schedule_onetime` allows the user to schedule the execution of a robot at a specific
    date and time.
    """

    if config_values is not None:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = datetime.datetime.strptime(config_values['HORARIO'], "%H:%M:%S")
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Agendando a execução
        schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(robot)

    else:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            start_date = st.date_input("Escolha a data de inicio",actual_date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        datetime.time(8,45),
                                        step=datetime.timedelta(minutes=1))

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Agendando a execução
        schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(robot)

    #Salvando o dicionario e retornando a config
    config_values = {'NOME_ROBO':'Black List',
                    'PERIODO':'Uma vez',
                    'DATA_INICIO':start_date,
                    'HORARIO':execution_time}

    return f"Robô agendado para execução em: {scheduled_time}", schedule, config_values

def schedule_daily(robot, config_values):
    """
    The `schedule_daily` allows the user to schedule a robot to execute daily at a specified
    start date and time, with a specified number of executions per day.
    """

    if config_values is None:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = datetime.datetime.strptime(config_values['HORARIO'], "%H:%M:%S")
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Quantas vezes por dia deve ser executado
        execution_times = st.number_input('Quantas vezes deve executar no dia', step=1)

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Agendando a execução múltiplas vezes no mesmo dia
        for _ in range(execution_times):
            schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(robot)
            scheduled_time += datetime.timedelta(days=1)
    else:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio", date, format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = config_values['HORARIO']
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Quantas vezes por dia deve ser executado
        execution_times = st.number_input('Quantas vezes deve executar no dia', step=1)

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Agendando a execução múltiplas vezes no mesmo dia
        for _ in range(execution_times):
            schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(robot)
            scheduled_time += datetime.timedelta(days=1)

    #Salvando o dicionario e retornando a config
    config_values = {'NOME_ROBO':'Black List',
                    'PERIODO':'Diariamente',
                    'DATA_INICIO':start_date,
                    'HORARIO':execution_time, 
                    'QTD_AO_DIA':execution_times}

    return f"""Robô agendado para execução diária a cada {execution_times}
            vezes em: {start_date.strftime('%d/%m/%Y')}
            às {execution_time.strftime('%H:%M')}""", schedule, config_values

def schedule_weekly(robot, config_values):
    """
    The `schedule_weekly` function allows users to schedule a robot to execute at specific times and
    days of the week on a weekly basis.
    """

    if config_values is None:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = datetime.datetime.strptime(config_values['HORARIO'], "%H:%M:%S")
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Cria dois conteiners para ordernar na pagina
        col3, col4 = st.columns(2)

        #Terceiro conteiner
        with col3:
            #Quantas vezes por dia deve ser executado
            execution_times = st.number_input('Quantas vezes deve executar no dia', step=1)

        #Quarto conteiner
        with col4:

            #Input para selecionar quais os dias da semana deve ser executado
            one_time_op = st.multiselect(
            'Quais dias da semana gostaria de executar o robô',
            ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Todos os dias'],
            ['Segunda', 'Terça'])

            #Faz uma validação
            if 'Todos os dias' in one_time_op:
                #Se selecionado "Todos os dias" deve alterar a lista para todos os dias
                one_time_op = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)
        all_days_list = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

        # Agendar para os dias selecionados
        for day in one_time_op:
            day_index = all_days_list.index(day)
            day_at_datetime = datetime.timedelta(days=(day_index-scheduled_time.weekday()) % 7)
            scheduled_day = scheduled_time + day_at_datetime

            for _ in range(execution_times):
                schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(robot)
                scheduled_day += datetime.timedelta(weeks=1)
    else:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = config_values['HORARIO']
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Cria dois conteiners para ordernar na pagina
        col3, col4 = st.columns(2)

        #Terceiro conteiner
        with col3:
            #Quantas vezes por dia deve ser executado
            execution_times = st.number_input('Quantas vezes deve executar no dia', step=1)

        #Quarto conteiner
        with col4:

            #Input para selecionar quais os dias da semana deve ser executado
            one_time_op = st.multiselect(
            'Quais dias da semana gostaria de executar o robô',
            ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Todos os dias'],
            config_values['DIAS_SEMANA'].split(" "))

            #Faz uma validação
            if 'Todos os dias' in one_time_op:
                #Se selecionado "Todos os dias" deve alterar a lista para todos os dias
                one_time_op = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

        # Calcula a data e hora de execução
        scheduled_time = datetime.datetime.combine(start_date, execution_time)
        all_days_list = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']

        # Agendar para os dias selecionados
        for day in one_time_op:
            day_index = all_days_list.index(day)
            day_at_datetime = datetime.timedelta(days=(day_index-scheduled_time.weekday()) % 7)
            scheduled_day = scheduled_time + day_at_datetime

            for _ in range(execution_times):
                schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(robot)
                scheduled_day += datetime.timedelta(weeks=1)

    #Salvando o dicionario e retornando a config
    config_values = {'NOME_ROBO':'Black List',
                    'PERIODO':'Semanalmente',
                    'DATA_INICIO':start_date,
                    'HORARIO':execution_time, 
                    'QTD_AO_DIA':execution_times, 
                    'DIAS_SEMANA': " ".join(one_time_op)}

    return f"""Robô agendado para execução semanal a cada {execution_times}
            vezes nos dias: {', '.join(one_time_op)}""", schedule, config_values

def schedule_monthly(robot, config_values):
    """
    The `schedule_monthly` allows the user to schedule a robot to execute on specific months
    and days of the month.
    """

    if config_values is None:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

        #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = datetime.datetime.strptime(config_values['HORARIO'], "%H:%M:%S")
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Cria dois conteiners para ordernar na pagina
        col3, col4 = st.columns(2)

        #Terceiro conteiner
        with col3:

            #Input para selecionar quais os meses para executar o robo
            one_time_op = st.multiselect(
            'Quais os meses gostaria de executar o robô',
            ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
            'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
            ['Janeiro'])

        #Quart conteiner
        with col4:

            #Input para selecionar quais os dias deve executar
            execution_day = st.multiselect(
            'Quais dias do mês gostaria de executar o robô',
            [str(x) for x in range(1,32,1)],
            ['1', '2'])

        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Dicionário para mapear nomes dos meses para números
        months_mapping = {
            'Janeiro': 1,
            'Fevereiro': 2,
            'Março': 3,
            'Abril': 4,
            'Maio': 5,
            'Junho': 6,
            'Julho': 7,
            'Agosto': 8,
            'Setembro': 9,
            'Outubro': 10,
            'Novembro': 11,
            'Dezembro': 12
        }

        for month in one_time_op:
            month_number = months_mapping[month]
            days_in_month = calendar.monthrange(scheduled_time.year, month_number)[1]

            for day in execution_day:
                if day.isdigit() and 1 <= int(day) <= days_in_month:
                    scheduled_day = scheduled_time.replace(month=month_number, day=int(day))
                    schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(robot)
    else:
        #Cria dois conteiners para ordernar na pagina
        col1, col2 = st.columns(2)

       #Primeiro conteiner
        with col1:
            #Input da data inicial de execução do robo
            date = config_values['DATA_INICIO']
            start_date = st.date_input("Escolha a data de inicio",date,format="DD/MM/YYYY")

        #Segundo conteiner
        with col2:
            #Input do horario que o robo deve ser executo
            horario = config_values['HORARIO']
            execution_time = st.time_input('Que horas o robô deve ser executado',
                                        horario,
                                        step=datetime.timedelta(minutes=1))

        #Cria dois conteiners para ordernar na pagina
        col3, col4 = st.columns(2)

        #Terceiro conteiner
        with col3:

            #Input para selecionar quais os meses para executar o robo
            one_time_op = st.multiselect(
            'Quais os meses gostaria de executar o robô',
            ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
            'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
            config_values['MESES'].split(" "))

        #Quart conteiner
        with col4:

            #Input para selecionar quais os dias deve executar
            execution_day = st.multiselect(
            'Quais dias do mês gostaria de executar o robô',
            [str(x) for x in range(1,32,1)],
            config_values['DIAS_DO_MES'].split(" "))

        scheduled_time = datetime.datetime.combine(start_date, execution_time)

        # Dicionário para mapear nomes dos meses para números
        months_mapping = {
            'Janeiro': 1,
            'Fevereiro': 2,
            'Março': 3,
            'Abril': 4,
            'Maio': 5,
            'Junho': 6,
            'Julho': 7,
            'Agosto': 8,
            'Setembro': 9,
            'Outubro': 10,
            'Novembro': 11,
            'Dezembro': 12
        }

        for month in one_time_op:
            month_number = months_mapping[month]
            days_in_month = calendar.monthrange(scheduled_time.year, month_number)[1]

            for day in execution_day:
                if day.isdigit() and 1 <= int(day) <= days_in_month:
                    scheduled_day = scheduled_time.replace(month=month_number, day=int(day))
                    schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(robot)

    #Salvando o dicionario e retornando a config
    config_values = {'NOME_ROBO':'Black List',
                    'PERIODO':'Mensal',
                    'DATA_INICIO':start_date,
                    'HORARIO':execution_time, 
                    'MESES':" ".join(one_time_op), 
                    'DIAS_DO_MES': " ".join(execution_day)}

    return f"""Robô agendado para execução mensal nos meses: {', '.join(one_time_op)}
             nos dias: {', '.join(execution_day)}""", schedule, config_values

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

def config_run():
    """
    The `config_run()` creates a markdown header for a mail security report and allows the user
    to select the execution period for a robot.
    """

    #Header da pagina
    header.main()

    #Criando tabs para separar os itens da pagina
    tab1, tab2 = st.tabs(["Configuração", "Log de Execução"])

    with tab1:
        #Selector para o usuario selecionar qual robo ele quer configurar
        robot_list = ['Black List']
        robot = None
        bot_option = st.selectbox('Selecione o robô',(robot_list))
        config_values = read_config_path(bot_option)

        #Atualiza a variavel robor dependendo da opcao selecionada
        if bot_option == 'Black List':
            robot = bl.run

        #Verifica se ja teve alguma configuracao anterior
        if config_values is not None:
            op_list = ["Uma vez", "Diariamente", "Semanalmente", "Mensal"]
            op_value = config_values['PERIODO']
            position = op_list.index(op_value)
        else:
            position = 0

        #Input tipo RADIO para selecionar o modo do robo ser executado
        execution_op = st.radio(
            "Selecione o periodo de execução",
            ["Uma vez", "Diariamente", "Semanalmente", "Mensal"], horizontal=True, index=position)

        if execution_op == 'Uma vez':
            msg, task, config_values = schedule_onetime(robot, config_values)

        #Se for executado diariamente
        elif execution_op == 'Diariamente':
            msg, task, config_values = schedule_daily(robot, config_values)

        #Se for semanalente
        elif execution_op == 'Semanalmente':
            msg, task, config_values = schedule_weekly(robot, config_values)

        #Se for mensalmente
        elif execution_op == 'Mensal':
            msg, task, config_values = schedule_monthly(robot, config_values)

        #Botao para confirmar as configuracoes
        confi_btn = st.button("Confirmar")

        #Botao para confirmar a configuracao
        if confi_btn:
            st.success(msg)
            insert_config_path(config_values)
            while True:
                time.sleep(1)
                task.run_pending()

    with tab2:
        #Abindo o arquivo de log
        df_log = pd.read_excel(LOG_PATH)
        df_filt = df_log.loc[df_log['NOME_ROBO']==bot_option]

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
