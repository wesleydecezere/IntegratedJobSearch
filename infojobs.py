from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
from unidecode import unidecode


def infojobs(op):
    option = Options()
    option.headless = False
    driver = webdriver.Chrome(options=option)

    # Get the URL
    driver.get("https://www.infojobs.com.br/")
    driver.implicitly_wait(1)  # in seconds

    # Accept the cookies
    driver.find_element(By.ID, "AllowCookiesButton").click()

    # Set the position
    elem = driver.find_element(By.NAME, "Palabra")
    elem.clear()
    elem.send_keys(op['position'])

    # Set the locale
    elem = driver.find_element(By.CLASS_NAME,
                               "ui-state-default"+
                               ".ui-combobox-input"+
                               ".ui-widget"+
                               ".ui-widget-content"+
                               ".ui-corner-left"+
                               ".ui-autocomplete-input"+
                               ".span4")
    elem.clear()
    elem.send_keys(op['state'])
    elem.send_keys(Keys.DOWN)
    elem.send_keys(Keys.RETURN)
    try:
        elem.send_keys(Keys.RETURN)
    except StaleElementReferenceException:
        pass

    # seleciona a cidade de busca
    driver.find_element(By.LINK_TEXT, 'Outras Localizações').click()
    elem = driver.find_elements(By.XPATH, "//section[@class='container']/div/ol/li/a")

    for i in range(len(elem)):
        href = elem[i].get_attribute('href')

        op['city'] = unidecode(op['city'])  # remove os acentos da cidade
        op['city'] = op['city'].lower()
        op['city'] = op['city'].replace(' ', '-')

        if op['city'] in href and op['city'] != '':
            elem[i].click()
            break
        elif i == len(elem)-1:
            # voltar pagina
            try:
                driver.find_element(By.ID, 'ctl00_phMasterPage_cGridEmpregosMaisBuscadosLoc_lnkSearch').click()
            except NoSuchElementException:
                driver.find_element(By.ID, 'ctl00_phMasterPage_cGridEmpregosMaisBuscados_lnkSearch').click()

    # dados exportados pro dataframe
    d = {
        'vacancy': [],
        'company': [],
        'location': [],
        'date': [],
        'link': [],
        }

    # Catch the information
    while op['nbr'] > len(d['vacancy']):
        jobs = driver.find_elements(By.CLASS_NAME, "vagaTitle.js_vacancyTitle")
        companies = driver.find_elements(By.CLASS_NAME, "vaga-company.js_linkCompany")
        locations = driver.find_elements(By.CLASS_NAME, "location2")

        for i in range(0, len(jobs)):
            d['vacancy'] += [jobs[i].get_attribute("innerText")]
            d['link'] += [jobs[i].get_attribute("href")]

            d['company'] += [companies[i].text]

            location = (locations[i*2+1].text).split(' - ')
            d['location'] += [location[1]]
            d['date'] += [location[0]]

        try:
            driver.find_element(By.LINK_TEXT, "Próxima >").click()
        except NoSuchElementException:
            op['nbr'] = len(d['vacancy'])
            break

    driver.quit()

    # Put all this info in a dataframe, to show it formatted and to be easy to export
    df = pd.DataFrame(data=d)
    #print(df)
    return df