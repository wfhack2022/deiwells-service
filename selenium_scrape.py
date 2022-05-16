import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def start_crawl(company_name):
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        options.experimental_options["prefs"] = chrome_prefs
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=fake-useragent')         
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")

        driver.implicitly_wait(0.5)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(f'{company_name} dnb')
        search_box.send_keys(Keys.RETURN)
        driver.implicitly_wait(5)

        result = driver.find_element(By.TAG_NAME, 'h3')
        result.click()
        driver.implicitly_wait(5)

        contacts = driver.find_elements(By.CLASS_NAME, 'employee')
        company_info = {}
        company_info['name'] = company_name
        company_info['people'] = []
        company_info['position'] = []
        for contact in contacts:
            temp = contact.text.split('\n')
            name = temp[0]
            position = temp[1]
            peopleList = company_info['people']
            positionList = company_info['position']
            peopleList.append(name)
            positionList.append(position)

        links = driver.find_elements(By.ID, 'hero-company-link')
        if len(links) > 0:
            company_info['companyUrl'] = links[0].text
        else:
            company_info['companyUrl'] = None

        description = driver.find_element(By.NAME, 'company_description')
        company_info['about'] = description.text[21:]
        address = driver.find_element(By.NAME, 'company_address').text[9:]
        company_info['address'] = address.split(',')
        industry = driver.find_element(By.NAME, 'industry_links')
        company_info['industry'] = industry.text.split(':')[1].split(',')
        return company_info
    except Exception as e:
        print('Exception occurred', e)

company_info = start_crawl('EXECUTEAM CORPORATION')
print(json.dumps(company_info, indent=3))
