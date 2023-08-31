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
from pathlib import Path
import base64
import calendar
import streamlit as st
import schedule

LOGO_PATH = 'logo.png'

#Dia atual
actual_date = datetime.datetime.today()

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

def schedule_onetime():
    """
    The `schedule_onetime` allows the user to schedule the execution of a robot at a specific
    date and time.
    """
    #Cria dois conteiners para ordernar na pagina
    col1, col2 = st.columns(2)

    #Primeiro conteiner
    with col1:
        #Input da data inicial de execução do robo
        start_date = st.date_input("Escolha a data de inicio",actual_date,format="DD/MM/YYYY")

    #Segundo conteiner
    with col2:
        #Input do horario que o robo deve ser executo
        execution_time = st.time_input('Que horas o robô deve ser executado', datetime.time(8, 45))

    # Calcula a data e hora de execução
    scheduled_time = datetime.datetime.combine(start_date, execution_time)

    # Agendando a execução
    schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(img_to_bytes)
    st.write(f"Robô agendado para execução em: {scheduled_time}")

def schedule_daily():
    """
    The `schedule_daily` allows the user to schedule a robot to execute daily at a specified
    start date and time, with a specified number of executions per day.
    """

    #Cria dois conteiners para ordernar na pagina
    col1, col2 = st.columns(2)

    #Primeiro conteiner
    with col1:
        #Input da data inicial de execução do robo
        start_date = st.date_input("Escolha a data de inicio", actual_date, format="DD/MM/YYYY")

    #Segundo conteiner
    with col2:
        #Input do horario que o robo deve ser executo
        execution_time = st.time_input('Que horas o robô deve ser executado', datetime.time(8, 45))

    #Quantas vezes por dia deve ser executado
    execution_times = st.number_input('Quantas vezes deve executar no dia', step=1)

    # Calcula a data e hora de execução
    scheduled_time = datetime.datetime.combine(start_date, execution_time)

    # Agendando a execução múltiplas vezes no mesmo dia
    for _ in range(execution_times):
        schedule.every().day.at(scheduled_time.strftime('%H:%M:%S')).do(img_to_bytes)
        scheduled_time += datetime.timedelta(days=1)

    st.write(f"""Robô agendado para execução diária a cada {execution_times}
            vezes em: {start_date.strftime('%d/%m/%Y')}
            às {execution_time.strftime('%H:%M')}""")

def schedule_weekly():
    """
    The `schedule_weekly` function allows users to schedule a robot to execute at specific times and
    days of the week on a weekly basis.
    """

    #Cria dois conteiners para ordernar na pagina
    col1, col2 = st.columns(2)

    #Primeiro conteiner
    with col1:
        #Input da data inicial de execução do robo
        start_date = st.date_input("Escolha a data de inicio", actual_date, format="DD/MM/YYYY")

    #Segundo conteiner
    with col2:
        #Input do horario que o robo deve ser executo
        execution_time = st.time_input('Que horas o robô deve ser executado', datetime.time(8, 45))

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
            schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(img_to_bytes)
            scheduled_day += datetime.timedelta(weeks=1)

    st.write(f"""Robô agendado para execução semanal a cada {execution_times}
            vezes nos dias: {', '.join(one_time_op)}""")

def schedule_monthly():
    """
    The `schedule_monthly` allows the user to schedule a robot to execute on specific months
    and days of the month.
    """
    #Cria dois conteiners para ordernar na pagina
    col1, col2 = st.columns(2)

    #Primeiro conteiner
    with col1:
        #Input da data inicial de execução do robo
        start_date = st.date_input("Escolha a data de inicio", actual_date, format="DD/MM/YYYY")

    #Segundo conteiner
    with col2:
        #Input do horario que o robo deve ser executo
        execution_time = st.time_input('Que horas o robô deve ser executado', datetime.time(8, 45))

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
                schedule.every().day.at(scheduled_day.time().strftime('%H:%M:%S')).do(img_to_bytes)

    st.write(f"""Robô agendado para execução mensal nos meses: {', '.join(one_time_op)}
             nos dias: {', '.join(execution_day)}""")

def config_run():
    """
    The `config_run()` creates a markdown header for a mail security report and allows the user
    to select the execution period for a robot.
    """

    #Cria um markdown para centralizar os itens na pagina
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: center;">
            <h1 style="text-align: center;">MAIL SECURITY REPORT</h1>
            {img_to_html(LOGO_PATH, width='100px')}
        </div>
        """,
        unsafe_allow_html=True
    )

    #Input tipo RADIO para selecionar o modo do robo ser executado
    execution_op = st.radio(
        "Selecione o periodo de execução",
        ["Uma vez", "Diariamente", "Semanalmente", "Mensal"], horizontal=True)

    #Se for apenas uma vez
    if execution_op == 'Uma vez':
        schedule_onetime()

    #Se for executado diariamente
    elif execution_op == 'Diariamente':
        schedule_daily()

    #Se for semanalente
    elif execution_op == 'Semanalmente':
        schedule_weekly()

    #Se for mensalmente
    elif execution_op == 'Mensal':
        schedule_monthly()

if __name__ == "__main__":
    config_run()
