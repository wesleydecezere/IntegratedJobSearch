from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

def indeed(op):
    option = Options()
    option.headless = False 
    driver = webdriver.Chrome(options=option)

    # Get the URL
    driver.get("https://br.indeed.com/")
    driver.implicitly_wait(1)  # in seconds

    # Accept the cookies
    time.sleep(1)
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()

    # Set the position
    elem = driver.find_element(By.NAME, "q")
    elem.clear()
    elem.send_keys(op['position'])

    # Set the locale
    elem = driver.find_element(By.NAME,"l")
    elem.clear()
    elem.send_keys(op['city']+" "+op['state'])
    elem.send_keys(Keys.RETURN)

    # dicionario de dados
    d = {
        'vacancy': [],
        'company': [],
        'location': [],
        'date': [],
        'link': [],
        }

    # Catch the information
    while op['nbr'] > len(d['vacancy']):
        jobs = driver.find_elements(By.CLASS_NAME, "jobtitle.turnstileLink ")
        comp_loc = driver.find_elements(By.CLASS_NAME, "sjcl") # diferente
        dates = driver.find_elements(By.CLASS_NAME, "date ")

        for i in range(0, len(jobs)):
            d['vacancy'] += [jobs[i].get_attribute("innerText")]
            d['link'] += [jobs[i].get_attribute("href")]

            try:
                company = comp_loc[i].find_element(By.CLASS_NAME, "company").text
            except NoSuchElementException:
                company = '[none]'
            d['company'] += [company]

            d['location'] += [comp_loc[i].find_element(By.CLASS_NAME, "location.accessible-contrast-color-location").text]

            date = (dates[i].text).split()
            if date[0] == 'Hoje':
                date = '00 dias atrás'
            else:
                if date[0].islower():
                    date.pop(0)
                    date.append("atrás")
                    if len(date[0]) == 1:
                        date[0] = '0' + date[0]
                date = " ".join(date)
            d['date'] += [date]

        try:
            if len(d['vacancy']) > 15:
                driver.find_element(By.XPATH, "//td/nav/div/ul/li/a[@aria-label='Próxima']").click()
            else:
                driver.find_element(By.XPATH, "//td/nav/div/ul/li/a[@aria-label='Próxima']").click()
        except NoSuchElementException:
            op['nbr'] = len(d['vacancy'])
            break

    driver.quit()

    # Put all this info in a dataframe, to show it formatted and to be easy to export
    df = pd.DataFrame(data=d)
    #print(df)
    return(df)