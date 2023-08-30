
"""
Automação da BlackList
"""
import os
import datetime
import requests
import pandas as pd
import tools as tl

#Variaveis fixas, que serão utilizadas em todo o processo
URL = 'https://filter.mailinspector.com.br/login/index.php'
API_URL = 'https://filter.mailinspector.com.br/login/mailLogViewer.php'
OUTPUT_PATH = os.getcwd() + "\\" + 'files'
CONFIG_PATH = 'config.txt'

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
    driver = tl.create_driver_chrome(headless=False)
    driver.get(URL)

    #Logando dentro do portal
    tl.clicking(element='clicando em login',path='email',btype='name',driver=driver).click()
    tl.clicking(element='passando o user',path='email',btype='name',driver=driver).send_keys(user)
    tl.clicking(element='clicando em senha',path='password',btype='name',driver=driver).click()
    tl.clicking(element='passandosenha',path='password',btype='name',driver=driver).send_keys(psw)
    tl.clicking(element='clicando no login',path="//input[@type='submit']",driver=driver).click()

    #Armazendo os cookies do portal
    cookies = tl.get_cookies(driver)

    return cookies, driver

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

def extract_emails_log(authorization):
    """
    The function extrai o log de emails enviados filtrando pela data
    """

    #formatando as datas para passar na API
    dia_atual, proximo_dia = format_date_api()

    #Criando o dicionario para passar como paramentro
    header_list = {
    "Cookie": f"PHPSESSID={authorization['PHPSESSID']}; lang=pt_BR",
    "Referer": API_URL, 
    }

    #Requisição na api para baixar os dados dos clientes
    response = requests.get(API_URL+f'?from={dia_atual}&to={proximo_dia}&page=-1',
                            headers=header_list,
                            timeout=100)
    result = response.text

    #Salvando o resultado da API no arquivo txt, ja no padrao csv
    with open(f'{OUTPUT_PATH}/emails_log.txt', 'w', encoding='utf-8') as file:
        file.write(result)

def run():

    """
    Função criada para automatizar a alimentação
    da base de dados com os IPs infectados
    """
    #Pegando os cookies do portal
    authorization, driver =  get_portal_cookies()
    extract_emails_log(authorization)

    #Lendo o arquivo txt como csv
    df_api = pd.read_csv(f'{OUTPUT_PATH}/log_view.txt')
    df_api.to_excel(f'{OUTPUT_PATH}/teste.xlsx', index=False)

    #Filtra o arquivo extraido mantendo apenas valores "Blacklisted"
    df_filt = df_api.loc[df_api['Action']=='Blacklisted']

    #Acessando a pagina da Blacklist do portal
    tl.clicking(element="Selecionando Blacklist",
                path='//*[@id="seg-menuce"]/ul/li[12]',
                driver=driver).click()

    #passando os ips na area de texto do portal
    ip_blacklist = "\n".join(df_filt['Source IP'].drop_duplicates())
    tl.clicking(element='Passado a lista de IPs, dentro do portal',
                path='entries',
                btype='name',
                driver=driver).send_keys(ip_blacklist)

    #ADicionando na blacklist
    try:
        tl.clicking(element='Clicando no botãoo de adcicionar',
                    path='add_blacklist', btype='name', driver=driver).click()
    except TimeoutError:
        tl.clicking(element='Clicando no botãoo de adcicionar',
                    path='add_blacklist', btype='name', driver=driver).click()
        
    #Fechando o navegador
    driver.quit()

if __name__ == '__main__':
    run()
