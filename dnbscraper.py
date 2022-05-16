import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class DNBScraper:
    def __init__(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        options.experimental_options["prefs"] = chrome_prefs
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=fake-useragent')         
        self.driver = webdriver.Chrome(options=options)    

    def scrape(self, company_name):    
        try:
            self.driver.get("https://www.google.com")

            self.driver.implicitly_wait(0.5)
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.send_keys(f'{company_name} dnb')
            search_box.send_keys(Keys.RETURN)
            self.driver.implicitly_wait(5)

            result = self.driver.find_element(By.TAG_NAME, 'h3')
            result.click()
            self.driver.implicitly_wait(5)

            contacts = self.driver.find_elements(By.CLASS_NAME, 'employee')
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

            links = self.driver.find_elements(By.ID, 'hero-company-link')
            if len(links) > 0:
                company_info['companyUrl'] = links[0].text
            else:
                company_info['companyUrl'] = None

            description = self.driver.find_element(By.NAME, 'company_description')
            company_info['about'] = description.text[21:]
            address = self.driver.find_element(By.NAME, 'company_address').text[9:]
            company_info['address'] = address.split(',')
            industry = self.driver.find_element(By.NAME, 'industry_links')
            company_info['industry'] = industry.text.split(':')[1].split(',')
            output_data = []
            output_data.append(company_info)
            print('*************************')
            print(output_data)
            print('*************************')        
            return output_data
        except Exception as e:
            print('Exception occurred', e)
            return []