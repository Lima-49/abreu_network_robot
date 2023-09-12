"""
Extração dos dados de tratamento dos emails 
"""
import os
import datetime
import time
import requests
from selenium.webdriver.support.select import Select
import pandas as pd
import tools as tl

#Variaveis fixas, que serão utilizadas em todo o processo
URL = 'https://filter.mailinspector.com.br/login/index.php'
API_URL = 'https://filter.mailinspector.com.br/login/mailLogViewer.php'
OUTPUT_PATH = os.getcwd() + "/" + 'files'
CONFIG_PATH = os.getcwd() + "/" + 'config/config.txt'
DATABASE = os.getcwd() + "/" + 'database'
LOG_PATH = DATABASE + '/log_execucao.xlsx'

def replace_emails_with_names(email, customer_dict):
    """
    Esta função recebe um email e um dicionário de nomes de clientes e emails, 
    e retorna o nome correspondente do cliente se o email for encontrado no dicionário, 
    caso contrário, retorna o email original.

    :param email: O endereço de email que precisa ser substituído por um nome de cliente
    :param customer_dict: Um dicionário onde as chaves são nomes de clientes 
    e os valores são listas de seus endereços de email associados
    :return: ou o nome do cliente associado ao endereço de email fornecido
    """

    #alterando a string para caixa baixa
    normalized_email = email.lower()

    #Loop ao redor do dicionario com os nomes dos clientes e seus respectivos emails
    for name, emails in customer_dict.items():

        #Verifica se o email a ser procurado esta dentro do dicionario
        if normalized_email in (em.lower() for em in emails):

            #Se encontrar retorna o nome do cliente referente ao email
            return name

    #Caso contrario retorna o email normal
    return normalized_email

def create_customer_dict(customers_list, data_frame):
    """
    Esta função cria um dicionário onde as chaves são nomes de clientes
    e os valores são listas de endereços de email que pertencem a esse cliente.

    :param customers_list: Uma lista de strings representando os nomes dos clientes
    :param data_frame: É um DataFrame do pandas que contém dados de email,
    contendo os endereços de email dos destinatários dos emails
    :return: retorna um dicionário onde as chaves são os nomes dos clientes e
    os valores são listas de endereços de email do data_frame que terminam com o domínio do cliente.
    """
    #inicializa o dicionario que ira armazenar os usuarios e emails
    customer_dict = {}

    #Loop atraves da lista de clientes extraido do portal
    for customer in customers_list:

        #Adicionando no dicionario os emails relacionados com o nome do cliente
        customer_dict[customer] = [email for email in data_frame['To'] if
                                   (email.endswith('@'+customer.lower()+'.com.br')) or
                                   (email.endswith('@'+customer.lower()+'.com'))]

    #retorna o dicionario com os emails dos clientes
    return customer_dict

def get_portal_cookies():
    """
    Esta função faz login em um portal da web, 
    recupera uma lista de clientes e retorna os cookies da sessão.
    :retorno: uma tupla contendo uma lista de clientes e um dicionário de cookies.
    """
    #Acessando os dados para logar no portal
    user = tl.get_config_data('LOGIN', 'user', CONFIG_PATH)
    psw = tl.get_config_data('LOGIN', 'password', CONFIG_PATH)

    #Cria o objeto driver, responsavel por acessar os dados dentro da web
    driver = tl.create_driver_chrome()
    driver.get(URL)

    #Logando dentro do portal
    tl.clicking(element='clicando em login',path='email',btype='name',driver=driver).click()
    tl.clicking(element='passando o user',path='email',btype='name',driver=driver).send_keys(user)
    tl.clicking(element='clicando em senha',path='password',btype='name',driver=driver).click()
    tl.clicking(element='passandosenha',path='password',btype='name',driver=driver).send_keys(psw)
    tl.clicking(element='clicando no login',path="//input[@type='submit']",driver=driver).click()

    #Peagando a lista de clientes do portal
    tl.clicking(element='Linked Account',path="//*[text()='Linked Accounts']",driver=driver).click()
    drop_down = tl.clicking(element='lista clientes',path='hijackName',btype='name',driver=driver)
    drop_down_obj = Select(drop_down)

    #Transformando a lista dos clientes em uma array
    customers_list = [opt.text for opt in drop_down_obj.options]

    #Removendo o primeiro index que fica em branco
    customers_list.pop(0)

    #Armazendo os cookies do portal
    cookies = tl.get_cookies(driver)

    #Finalizando o driver
    driver.quit()

    return customers_list, cookies

def format_date_api():
    """
    Esta função formata a data atual e a data do próximo dia em um formato específico.
    :retorno: uma tupla com duas strings: a data atual formatada como "mm/dd/yyyy" 
    e a data do próximo dia formatada como "mm/dd/yyyy",
    ambas com a barra inclinada substituída por "-".
    """

    # Obtém a data atual
    data_atual = datetime.date.today()
    data_atual_formatada = data_atual.strftime("%m-%d-%Y")
    data_atual_formatada = data_atual_formatada.replace('-', '%2F')

    # Adiciona um dia - proximo dia
    data_nova = data_atual + datetime.timedelta(days=1)
    data_nova_formatada = data_nova.strftime("%m-%d-%Y")
    data_nova_formatada = data_nova_formatada.replace('-', '%2F')

    #Retorna o dia atual e o proximo dia foramatado
    return data_atual_formatada, data_nova_formatada

def insert_log(**kwargs):
    """
    `insert_log` reads an Excel file, adds execution data to it, and saves the updated
    file.
    """
    #Abrindo o arquivo de execucao
    df_log = pd.read_excel(LOG_PATH)

    line_index = df_log.shape[0]

    #Adicionando os dados de execucao no df
    for field in kwargs.items():
        df_log.at[line_index,field[0]]=field[1]

    #salvando o arquivo
    df_log.to_excel(LOG_PATH, index=False)

def run():
    """
    Esta função faz o download de dados de uma API, 
    formata-os, substitui os endereços de email
    por nomes de clientes e os salva como um arquivo CSV.
    """

    try:

        #tempo inicial da execucao
        tempo_inicio = time.time()

        #Limpa o diretório que os arquivos ficarao salvos
        tl.create_dir(OUTPUT_PATH, clean=True)

        #Lista de clientes cadastrados e os cookies do portal
        customer_list, cookie = get_portal_cookies()

        #Criando o dicionario para passar como paramentro
        header_list = {
        "Cookie": f"PHPSESSID={cookie['PHPSESSID']}; lang=pt_BR",
        "Referer": API_URL, 
        }

        #formatando as datas para passar na API
        dia_atual, proximo_dia = format_date_api()

        #Requisição na api para baixar os dados dos clientes
        response = requests.get(API_URL+f'?from={dia_atual}&to={proximo_dia}&page=-1',
                                headers=header_list,
                                timeout=100)
        result = response.text

        #Salvando o resultado da API no arquivo txt, ja no padrao csv
        with open(f'{OUTPUT_PATH}/log_view.txt', 'w', encoding='utf-8') as file:
            file.write(result)

        #Lendo o arquivo txt como csv
        df_api = pd.read_csv(f'{OUTPUT_PATH}/log_view.txt')

        #Removendo os valroes duplicados, para diminuir o scopo
        df_duplicates = df_api.drop_duplicates(subset='To')

        #Formatando o arquivo da APi, alterando o email 'To' para o nome dos clientes
        customers_dict = create_customer_dict(customer_list, df_api)
        df_api_all = pd.DataFrame({
            'Date': df_duplicates['Date'],
            'From':df_duplicates['From'], 
            'To': df_duplicates['To'].apply(replace_emails_with_names,customer_dict=customers_dict), 
            'Action': df_duplicates['Action']
        })

        #Filtra o df removendo valores '@' da coluna 'To'
        df_api_all = df_api_all.loc[~df_api_all['To'].str.contains('@')]

        #Salva o arquivo de log
        df_api_all.to_csv(f'{OUTPUT_PATH}/log_view.csv', sep=',', index=False)

        #tempo final da execucao
        tempo_final = time.time()

        #Adicionando os dados de execucao no log
        print("Salvando No Log")
        actual_date = datetime.datetime.today().strftime('%d/%m/%Y')
        actual_time = datetime.datetime.today().strftime('%H:%M')
        execution_time = tl.convert(tempo_final-tempo_inicio)
        insert_log(NOME_ROBO='extracao_dados',
                   DATA_EXECUCAO=actual_date,
                   HORA_EXECUCAO=actual_time,
                   TEMPO_EXECUCAO=execution_time,
                   STATUS='Sucesso',
                   DETALHES='Robo excutado com sucesso'
                   )

    except Exception as error:
        #tempo final da execucao
        tempo_final = time.time()

        #Adiciona os dados de execucao no log
        actual_date = datetime.datetime.today().strftime('%d/%m/%Y')
        actual_time = datetime.datetime.today().strftime('%H:%M')
        execution_time = tl.convert(tempo_final-tempo_inicio)
        insert_log(NOME_ROBO='extracao_dados',
            DATA_EXECUCAO=actual_date,
            HORA_EXECUCAO=actual_time,
            TEMPO_EXECUCAO=execution_time,
            STATUS='Falha',
            DETALHES=error
            )
if __name__ == '__main__':
    run()
