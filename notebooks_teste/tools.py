"""
Caixa de ferramentas com as
principais funcoes utilizadas
"""
import os
import sys
import time
from datetime import date
import glob
from pathlib import Path
import configparser
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def error(error_msg):
    """
    This function logs errors that occur during execution of a Python program.
    
    :param e: The parameter "e" is an exception object that contains
    information about the error that
    occurred in the code. It is passed to the "error" function when an error is caught
    """
    print("Apresentou erro, gravando o erro")
    exc_type = sys.exc_info()[0]
    exc_tb = sys.exc_info()[2]
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    path_erro = r'path_error'
    today = date.today()
    name = str(fname) + '_' + str(today) + '.txt'
    arquivo = open(path_erro + '\\' + name, 'w', encoding='utf-8')
    arquivo.write(str(fname) + "\n")
    arquivo.write(str(error_msg) + "\n")
    arquivo.write(str(exc_type) + "\n")
    arquivo.write(str(exc_tb.tb_lineno) + "\n")
    arquivo.close()

def get_cookies(driver):
    """
    This function retrieves cookies from a web driver and returns them as a dictionary.
    
    :param driver: The "driver" parameter is an instance of a web driver, which is used to automate
    interactions with a web browser. It can be used to navigate to web pages,
    interact with elements on
    the page, and retrieve information from the page. In this specific function,
    the driver is used to
    retrieve cookies
    :return: The function `get_cookies` returns a dictionary of cookies obtained from a Selenium
    webdriver instance.
    """
    starling_cookies = driver.get_cookies()

    cookies = {}
    for cookie in starling_cookies:
        cookies[cookie['name']] = cookie['value']

    return cookies

def create_driver_chrome(download_dir=None, headless=True):
    """
    It creates a Chrome webdriver with the specified options.

    :param download_dir: The directory where you want to download the files to
    :return: A webdriver object
    """
    chrome_options = Options()

    if download_dir is not None:
        download_dir = str(download_dir)
        preferences = {
            "download.default_directory": download_dir,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", preferences)

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def create_driver_firefox(download_dir=None, headless=True):

    """
    It creates a Firefox webdriver with the specified options.

    :param download_dir: The directory where you want to download the files to
    :return: A webdriver object
    """
    firefox_options = FirefoxOptions()

    if headless:
        # Enable headless mode for the Firefox webdriver
        firefox_options.add_argument("--headless")

    if download_dir is not None:
        download_dir = str(download_dir)
        preferences = {
            "browser.download.dir": download_dir,
            "browser.download.folderList": 2,
            "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream"
        }
        firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("browser.download.manager.useWindow", False)
        firefox_options.set_preference("browser.download.manager.focusWhenStarting", False)
        firefox_options.set_preference("browser.download.manager.showAlertOnComplete", False)
        firefox_options.set_preference("browser.download.manager.closeWhenDone", True)
        for key, value in preferences.items():
            firefox_options.set_preference(key, value)

    driver = webdriver.Firefox(options=firefox_options)
    driver.implicitly_wait(20)

    return driver

def clicking(path, driver, element='elemento', refresh=False, btype='xpath', limit=3, wait=True):
    """
    The function "clicking" clicks on a specified element on a webpage using Selenium WebDriver 
    and can handle errors and refresh the page if needed.
    
    :param path: The xpath or css selector of the element to be clicked
    :param driver: The Selenium WebDriver instance used to interact with the web page
    :param element: A string that represents the name of the element being clicked. It is used for
    printing messages to the console. If not provided, it defaults to 'elemento'
    defaults to elemento (optional)

    :param refresh: a boolean indicating whether to refresh the page before attempting to click the
    element, defaults to False (optional)
    :param type: the method used to locate the element (e.g. 'xpath', 'id', 'class_name')
    defaults to xpath (optional)
    param limit: The maximum number of attempts to click the element before giving up, defaults to 3
    (optional)
    :param wait: A boolean parameter that determines whether to wait for the element to be visible
    before clicking on it If set to True, the function will wait for the element to be visible using
    WebDriverWait before clicking on it If set to False, the function will not wait and will attempt 
    to click on the element immediately, defaults to True (optional)
    :return: the found element after attempting to click on it. If there is an
    ElementClickInterceptedException, the function will retry clicking on the element up to the
    specified limit.
    """

    if limit == 0:
        return None

    elif refresh:
        driver.refresh()


    try:
        if wait:
            wait = WebDriverWait(driver, 60)
            wait.until(ec.visibility_of_element_located((btype, path)))

        obj_to_find = driver.find_element(btype, path)
        actions = ActionChains(driver)
        actions.move_to_element(obj_to_find).perform()

        found_element = driver.find_element(btype, path)
        print(f">>>Sucesso {element}>>>")

    except ElementClickInterceptedException:
        print(f"<<<Erro ao {element}, tentando novamente>>>")
        found_element = clicking(element, path, refresh, btype, limit - 1, driver)


    return found_element

def download_checker(folder):
    """
    This function checks if a download is still in progress type looking for temporary files
    and waits until they are finished before printing a message
    indicating that the download is complete.
    
    :param folder: The folder parameter is a string that represents the path to the folder where the
    downloaded files are stored
    """
    total = 1
    while total != 0:
        filenames = glob.glob(folder + "/*tmp*")
        total = len(filenames)
        print('Ainda não terminou o download - tmp')
        time.sleep(10)

    total = 1
    while total != 0:
        filenames = glob.glob(folder + "/*crdownload*")
        total = len(filenames)
        print('Ainda não terminou o download - crdownload')
        time.sleep(10)

    print("  *Download concluído*")

def convert(seconds):
    """
    Funcao responsavel para calcular o tempo de excecucao do processo
    - seconds: segundos enviados que sera retornado como h:min:seg
    """
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def create_dir(path, clean=False):

    """
    Função que cria o diretorio, se ele não existir 
    path: caminho do diretorio que sera criado 
    """
    if os.path.isdir(path):
        #Se não, apenas limpa o diretorio
        print("Diretorio ja existe")

        #Se quiser que o diretorio seja zerado, chama a função para limpar os arquivos da pasta
        if clean:
            clean_dir(path, False)

    else:
        #Se o dirertorio não existir, cria
        os.mkdir(path)

    return path

def clean_dir(path, delete_folder=True):

    """
    Função que limpa todos os arquivos do diretorio selecionado 
    - path: caminho do diretorio que sera limpado por completo
    """
    print("Limpando arquivos gerais")
    if os.path.exists(Path(path)):

        #Loop dentro do diretorio passado
        for file in os.listdir(path):

            #Se for apenas arquivo, apaga
            if os.path.isfile(path + '\\' + file):
                os.remove(path + '\\' + file)
                print(file + " removido com sucesso.")

            elif os.path.isdir(path + '\\' + file):
                clean_dir(path=path + '\\' + file)

                if delete_folder:
                    os.rmdir(path + "\\" + file)

def get_config_data(iten_title, iten, config_path):
    """
    It reads a config file and returns the value of a given item
    :param iten_title: The title of the section in the config file
    :param iten: the name of the parameter you want to get from the config file
    :param config_path: The path to the config file
    :return: A string
    """

    arq_config = configparser.RawConfigParser()
    arq_config.read(config_path)

    data = arq_config.get(iten_title, iten)
    data_encoded = base64.b64decode(data).decode('utf-8')

    return str(data_encoded)
