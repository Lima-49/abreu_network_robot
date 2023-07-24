"""
Extração dos dados de tratamento dos emails 
"""
import datetime
import os
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import requests
import pandas as pd
import tools as tl

#Variaveis fixas, que serão utilizadas em todo o processo
URL = 'https://filter.mailinspector.com.br/login/index.php'
API_URL = 'https://filter.mailinspector.com.br/login/mailLogViewer.php'
OUTPUT_PATH = os.getcwd() + "\\" + 'files'
CONFIG_PATH = 'config.txt'

def replace_emails_with_names(email, customer_dict):
    """
    This function takes an email and a dictionary of customer names and emails, and returns the
    corresponding customer name if the email is found in the dictionary, otherwise it returns the
    original email.
    
    :param email: The email address that needs to be replaced with a customer name
    :param customer_dict: A dictionary where the keys are customer names and the values are lists of
    their associated email addresses
    :return: either the name of the customer associated with the given email address if it exists 
    in the
    customer dictionary, or the original email address if it does not exist in the dictionary.
    """

    for name, emails in customer_dict.items():
        if (email.lower() in [em.lower() for em in emails]):
            return name
    return email

def create_customer_dict(customers_list, data_frame):
    """
    This function creates a dictionary where the keys are customer names and the values are lists of
    email addresses that belong to that customer.
    
    :param customers_list: A list of strings representing the names of customers
    :param data_frame: It is a pandas DataFrame that contains email data
    which contains the email addresses of the recipients of the emails
    :return: The function `create_customer_dict` is returning a dictionary where the keys 
    are the names
    of the customers in `customers_list` and the values are lists of email addresses from the
    `data_frame` that end with the customer's domain name (either '.com.br' or '.com').
    """
    customer_dict = {}

    for customer in customers_list:
        customer_dict[customer] = [email for email in data_frame['To'] if
                                   (email.endswith('@'+customer.lower()+'.com.br')) or
                                   (email.endswith('@'+customer.lower()+'.com'))]

    return customer_dict

def replace_custom_names(customer_names):
    """
    This function replaces specific customer names with their corresponding corrected names from a
    dictionary.
    
    :param customer_names: a list of customer names
    replaced with their correct names
    :return: the updated list of customer names after replacing any custom names with their
    corresponding standardized names from the `diff_custom` dictionary.
    """
    diff_custom = {
        'aguia':'aguiasecuritizadora',
        'bombinhassummer':'bombinhassummerbeach', 
        'dutoclean': 'dutocleanbauru',
        'fabricenter': 'fabricenter470',
        'fazcomunicacao': 'fazcomunicacaovisual',
        'galli': 'galliatacadista',
        'impacto': 'impactoesports',
        'jcleletronica': 'jcleletronicaindustrial',
        'mailinspector': 'filter.mailinspector',
        'plantfort': 'plantfortfertil',
        'primedigital': 'primemidiadigital',
        'quinta': 'quintadonino',
        'raysolar': 'raysolarbrasil',
        'reset': 'resetmairinque',
        'revar': 'revarcondicionado',
        'rodoflex': 'rodoflexpneus',
        'sany': 'sanydobrasil',
        'supernagai': 'supermercadosnagai',
        'agrotecagro': 'agrotecagroquimica',
        'barulhinhobomchips': 'barulhinhobom',
        'marcospaulo': 'marcospauloimoveis',
        'cortedobra': 'cortedobraseguranca',
        'ortobaby': 'ortobabycalcados',
        'arinteli': 'arinteligenciatributaria',
    }

    for diff_name in diff_custom.items():
        list_index = customer_names.index(diff_name[0])
        customer_names[list_index] = diff_name[1]

    return customer_names

def replace_numeric_chars(string):
    """
    The function replaces certain numeric characters in a string with corresponding alphabetic
    characters.
    
    :param string: a string that contains alphanumeric characters
    :return: the input string with any numeric characters replaced with their corresponding 
    alphabetic
    characters according to the replacements dictionary. However, if the input string is 
    '5stintas' or 'c3', no replacements will be made.
    """
    replacements = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b'}
    for char, replacement in replacements.items():
        if string not in ['5stintas','c3']:
            string = string.replace(char, replacement)
    return string

def get_portal_cookies():
    """
    This function logs into a web portal, retrieves a list of customers, 
    and returns the cookies for the
    session.
    :return: a tuple containing a list of customers and a dictionary of cookies.
    """

    #Acessando os dados para logar no portal
    user = tl.get_config_data('LOGIN', 'user', CONFIG_PATH)
    senha = tl.get_config_data('LOGIN', 'password', CONFIG_PATH)

    #Cria o objeto driver, responsavel por acessar os dados dentro da web
    driver = tl.create_driver_firefox()
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(URL)

    #Loga dentro do portal
    tl.clicking(element='clicando em login',path='email',by='name',driver=driver).click()
    tl.clicking(element='passando o user',path='email',by='name',driver=driver).send_keys(user)

    tl.clicking(element='clicando em senha',path='password',by='name',driver=driver).click()
    tl.clicking(element='passando a senha',path='password',by='name',driver=driver).send_keys(senha)

    tl.clicking(element='clicando no login',path="//input[@type='submit']",driver=driver).click()

    #Peagando a lista de clientes do portal
    tl.clicking(element='Linked Account',path="//*[text()='Linked Accounts']",driver=driver).click()
    drop_down = tl.clicking(element='lista de clientes',path='hijackName',by='name',driver=driver)
    drop_down_obj = Select(drop_down)

    customers_list = [opt.text for opt in drop_down_obj.options]
    customers_list.pop(0)

    #Armazendo os cookies do portal
    cookies = tl.get_cookies(driver)

    #Finalizando o driver
    driver.quit()

    return customers_list, cookies

def format_date_api():
    """
    This Python function formats the current date and the next day's date in a specific
    format for use
    in an API.
    :return: a tuple with two strings: the current date formatted as "mm/dd/yyyy" and the next day's
    date formatted as "mm/dd/yyyy", both with the forward slash replaced by "-".
    """

    # Obtém a data atual
    data_atual = datetime.date.today()
    data_atual_formatada = data_atual.strftime("%m-%d-%Y")
    data_atual_formatada = data_atual_formatada.replace('-', '%2F')

    # Adiciona um dia
    data_nova = data_atual + datetime.timedelta(days=1)
    data_nova_formatada = data_nova.strftime("%m-%d-%Y")
    data_nova_formatada = data_nova_formatada.replace('-', '%2F')
    return data_atual_formatada, data_nova_formatada

def run():
    """
    This function downloads data from an API, formats it,
    replaces email addresses with customer names,
    and saves it as a CSV file.
    """
    #Limpa o diretório que os arquivos ficarao salvos
    tl.create_dir(OUTPUT_PATH, clean=True)

    #Lista de clientes cadastrados e os cookies do portal
    customer_list, cookie = get_portal_cookies()

    #Cruiando o dicionario para passar como paramentro
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

    #Formatando o arquivo da APi, alterando o email 'To' para o nome dos clientes
    customers_dict = create_customer_dict(customer_list, df_api)
    df_api_all = pd.DataFrame({
        'Date': df_api['Date'],
        'From':df_api['From'], 
        'To': df_api['To'].apply(replace_emails_with_names,customer_dict=customers_dict), 
        'Action': df_api['Action']
    })

    df_api_all = df_api_all.loc[~df_api_all['To'].str.contains('@')]
    df_api_all.to_csv(f'{OUTPUT_PATH}/log_view.csv', sep=',', index=False)

if __name__ == '__main__':
    run()
