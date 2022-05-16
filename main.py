import json
from xml import dom
from elastic_enterprise_search import AppSearch
import os
from flask import Flask, jsonify
import time
from flask_cors import CORS
import requests
from fuzzywuzzy import fuzz
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from gender_api import get_gender_by_name

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

app_search = None 
DEIWELLS_ENGINE='deiwells'
SEARCH_ENGINE='idiversify'
SEARCH_ENGINE_ENDPOINT="https://my-deployment-24a00a.ent.us-central1.gcp.cloud.es.io:443"

@app.route('/diversity/categories')
def get_diversity_categories():
    diversity_categories = [
        'South Asian Founded',
        'Native Hawaiian / Pacific Islander Led',
        'Middle Eastern / North African Founded',
        'American Indian / Alaska Native Founded',
        'Black / African American Led',
        'East Asian Led',
        'South Asian Led',
        'Hispanic / Latinx Founded',
        'American Indian / Alaska Native Led',
        'Native Hawaiian / Pacific Islander Founded',
        'Middle Eastern / North African Led',
        'Southeast Asian Led',
        'Women Led',
        'Hispanic / Latinx Led',
        'Southeast Asian Founded',
        'Black / African American Founded',
        'Women Founded',
        'East Asian Founded',
    ]
    return jsonify(diversity_categories)

# @app.route('/companies', methods=['GET', 'OPTIONS'])
# def getfile():
#     with open('data.json', 'r') as f:
#         companies = []
#         Lines = f.readlines()
#         dedup = set()
#         for line in Lines:
#             print(line)
#             company = json.loads(line)

#             if(company['name'] not in dedup):
#                 companies.append(json.loads(line))
#                 dedup.add(company['name'])
#     return jsonify(companies)

@app.route('/companies', methods=['GET', 'OPTIONS'])
def get_companies():
    return (jsonify(get_all_companides_from_db())) 

def get_all_companides_from_db():
    output_data=[]
    retry=1
    while retry < 3:
        try:
            res=app_search.list_documents(engine_name=DEIWELLS_ENGINE, current_page=1)
            output_data.extend(res['results'])
            total_pages = res['meta']['page']['total_pages']
            print(total_pages)
            count=2
            while(count < total_pages):
                res=app_search.list_documents(engine_name=DEIWELLS_ENGINE, current_page=count)
                output_data.extend(res['results'])
                count+=1
            print(len(output_data))
            break
        except Exception as es:
            print('Exception occured retring...')
            retry+=1
            time.sleep(2)
            continue

    return output_data
    
#TODO Not a good coode, find the filter API in app search
def get_diversity_filtered_data(diversity):
    filtered_result=[]
    data=get_all_companides_from_db()
    keyValList=[]
    keyValList.append(diversity.lower())
    filtered_result = [d for d in data if 'diversity' in d and d['diversity'].lower() in keyValList]
    return filtered_result

@app.route('/keywordsearch/<diversity>')
def keywordsearch(diversity):
    print(diversity)
    return jsonify(get_diversity_filtered_data(diversity)) 

@app.route('/aggregates')
def aggregates():
    diversities = ['Women Led', 
            'Unknown',
             'Women Owned', 
             'Black or African American Led', 
             'LGBTQIA+', 
             'Veterans' ]
    data=[]
    for diversity in diversities:
        filter_data = get_diversity_filtered_data(diversity)
        data.append({diversity: len(filter_data)})
    # for diversity in diversities:
    #     print(diversity)
    #     resp = app_search.search(
    #     engine_name=DEIWELLS_ENGINE,
    #     body={
    #         "query": diversity,
    #         "filters" : {
    #         "diversity": diversity
    #         }        
    #     })
    #     data.append({diversity: resp['meta']['page']['total_results']})
    # print(data)
    # data.append({'Women Led': 134})
    # data.append({'Unknown': 424})
    return jsonify(data)

@app.route("/company/<name>")
def company(name):
    output_data = get_company(name, None)
    data = None
    if len(output_data) > 0:
        data = output_data[0]
    else:
      #check in reuters
      output_data = get_company_detail(name)  
    if len(output_data) > 0:
        data = output_data[0]
        validate_domain_data(output_data,name)
        data['diversity'] = 'Unknown'
        if 'people' in data and  data['people'] is not None and len(data['people']) > 0:           
            if is_women_led_company(data) is True:
                data['diversity'] = 'Women Led'
            else:
                data['diversity'] = 'Unknown'
        index_document(data)
        with open("companyinfo.json", "a") as outfile:
            outfile.write('\n')
            json.dump(data, outfile)

    return jsonify(output_data)

def is_women_led_company(data):
    is_women_owned = False
    if data['people'] is not None and len(data['people']) > 0:
        female_count=0
        for person in data['people']:
            gender = get_gender_by_name(person)
            print(person, gender)
            if gender == 'female':
                female_count += 1
        if female_count >= len(data['people']) // 2:
            is_women_owned = True
    return is_women_owned

def get_company_detail(name):
    token = os.environ['TOKEN']
    if not token:
        print('ERROR:No Token set....')
        return jsonify([])

    reuters_endpoint = "https://api-eit.refinitiv.com/permid/search?q=name:{COMPANY_NAME}&num=1&access-token={TOKEN}&entitytype=organization&format=JSON"
    URL = reuters_endpoint.format(TOKEN=token, COMPANY_NAME=name)
    try:
        r = requests.get(url=URL)
        data = r.json()
        print(data)

        if not data:
            print('No data found...')
            return []

        output_data = []
        if len(data['result']['organizations']['entities']) and 'organizationName' in data['result']['organizations']['entities'][0]:
            orgName = data['result']['organizations']['entities'][0]['organizationName']
            score = fuzz.token_sort_ratio(name, orgName)
            print('fuzzy score: ' + str(score))
            if(score < 80):
                print('Skip record due to less score - match between: ' +
                name + ' and ' + orgName + ' is: ' + str(score))
                return []

            detail = {}
            if len(data['result']['organizations']['entities']) and 'hasURL' in data['result']['organizations']['entities'][0]:
                detail['companyUrl'] = data['result']['organizations']['entities'][0]['hasURL']

            if len(data['result']['quotes']['entities']) and 'hasExchangeTicker' in data['result']['quotes']['entities'][0]:
                detail['ticker'] = data['result']['quotes']['entities'][0]['hasExchangeTicker']

            scrape_service_url = os.environ.get('SCRAPE_SERVICE_HOST', 'localhost')
            scraped_item = {}
            if len(data['result']['quotes']['entities']) > 0 and 'hasRIC' in data['result']['quotes']['entities'][0]:
                ric = data['result']['quotes']['entities'][0]['hasRIC']
                url = 'https://www.reuters.com/markets/companies/'+ric
                #detail['companyDetailUrl'] = url+'/financials/income-annual'
                scrapeUrl = 'http://'+scrape_service_url + ':8080/crawl.json?spider_name=reutersspider&url=' + url
                try:
                    r = requests.get(url=scrapeUrl)
                    data = r.json()
                    print(data)
                    scraped_item = data['items'][0]
                    print(scraped_item)
                except Exception as e:
                    print('Exeception occured, continuing')
                    return []
            else:
                print('No RIC data found...')
                detail['name'] = name
                return []

            companyInfo = scraped_item | detail
            print(companyInfo)
            output_data.append(companyInfo)
        else:
            print('company does not exist:' + name)
            return []
    except Exception as e:
        print('Exeception occured in calling the API, continuing')
        return []
    return output_data
    
def get_company(company_name, seldriver):
    try:
        driver = seldriver
        if not driver:
            driver = get_seleinium_driver()
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
        output_data = []
        output_data.append(company_info)
        print('*************************')
        print(output_data)
        print('*************************')        
        return output_data
    except Exception as e:
        print('Exception occurred', e)
        return []


@app.route("/search")
def search():
    startCrawl()
    return jsonify({})

@app.route("/load/companies")
def load_company():
    with open('companydata.json') as json_file:
        companydata = json.load(json_file)

    organizations = companydata['MOA Data']
    count = 1
    driver = get_seleinium_driver()
    output_data=[]
    for org in organizations:
        name = org['dunsName']
        print('Input company name: ' + name + ' count: ' + str(count))
        count += 1
        time.sleep(3)
        if count == 500:
            break

        output_data = get_company(name,driver)
        if len(output_data) > 0:
            data = output_data[0]
        else:
            # if no data try from reuters
            output_data = get_company_detail(name)

        if len(output_data) > 0:
            data = output_data[0]
            validate_domain_data(output_data,name)
            data['diversity'] = 'Unknown'
            if 'people' in data and  data['people'] is not None and len(data['people']) > 0:           
                if is_women_led_company(data) is True:
                    data['diversity'] = 'Women Led'
                else:
                    data['diversity'] = 'Unknown'
            index_document(data)            
            with open("companyinfo.json", "a") as outfile:
                outfile.write('\n')
                json.dump(data, outfile)
        else:
            continue
    return jsonify(output_data)

def validate_domain_data(output_data,name):
    #TODO potential refactor as reuters will be called twice
    data = output_data[0]  
    if 'companyUrl' in data and data['companyUrl'] is not None:
      add_domain(data['companyUrl'])
    else:
        reuters = get_company_detail(name)
        if(len(reuters) > 0 and 'companyUrl' in reuters[0]):
            data['companyUrl'] = reuters[0]['companyUrl']
            add_domain(data['companyUrl'])

def add_domain(domain):
    print(domain)
    url=domain
    if domain.rfind('http:') >= 0:
        url = domain.replace('http://', 'https://')
    pathIdx = url.rindex(urlparse(url).path)
    if pathIdx > 0:
        url = url[0:pathIdx]
    if url.startswith('www'):
        url = 'https://' + url
    print(url)
    try:
        domain_id = create_domain(url)
        res=validate_domain(url)
        print(res)
        return res
    except Exception as e:
        print('Unexpected error, continuing' + str(e))
        return None

def getDomainId(domainId):
    resp = app_search.get_crawler_domain(engine_name=SEARCH_ENGINE, domain_id=domainId)
    print(resp)
    return resp

def create_domain(domain):
    resp = app_search.create_crawler_domain(
    engine_name=SEARCH_ENGINE,
    body={
        "name": domain
    })
    domain_id = resp["id"]
    print(domain_id)
    return domain_id

def validate_domain(domain):

    res = app_search.get_crawler_domain_validation_result(
    body={
        "url": domain,
        "checks": [
        "dns",
        "robots_txt",
        "tcp",
        "url",
        "url_content",
        "url_request"
        ]
    })
    print(res)
    return res

def startCrawl(domain):
  app_search.create_crawler_crawl_request(engine_name=SEARCH_ENGINE)

def start_partial_crawl(domain):
    try:
        domain_list=[]
        domain_list.append(domain)
        res=app_search.create_crawler_crawl_request(engine_name=SEARCH_ENGINE, domain_allowlist=domain_list)

        # url = SEARCH_ENGINE_ENDPOINT + '/api/as/v1/engines/{ENGINE_NAME}/crawler/crawl_requests'
        # url = url.format(ENGINE_NAME=SEARCH_ENGINE)
        # res = requests.post(url, data = {'overrides': {'domain_allowlist':domain_list}})
        print('********************')
        print(res)
    except Exception as e:
        print('Unable to start the crawl ' + str(e))

def get_seleinium_driver():
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

    return driver

def initElastic():
    print('initialize elastic')
    key = os.environ['SEARCH_API_KEY']
    if not key:
        print('ERROR:No API KEY set....')
        exit
    ent_search = AppSearch(
         SEARCH_ENGINE_ENDPOINT,
         http_auth=key
    )
    return  ent_search

def index_document(document):
    doc = document.copy()
    print(doc)
    url = doc['companyUrl']
    del doc['companyUrl']
    doc['companyurl'] = url 
    documents=[]
    documents.append(doc)
    res=app_search.index_documents(
        engine_name=DEIWELLS_ENGINE,
        documents=documents)
    print('*************')
    print(res)
    print('*************')

# def initDeiWellsElastic():
#     print('initialize elastic')
#     key = os.environ['SEARCH_API_KEY']
#     if not key:
#         print('ERROR:No API KEY set....')
#         exit
#     ent_search = AppSearch(
#          SEARCH_ENGINE_ENDPOINT,
#          http_auth=key
#     )
#     return  ent_search


if __name__ == "__main__":
    app_search = initElastic()
    app.run(host="0.0.0.0", port=5000, debug=True)
