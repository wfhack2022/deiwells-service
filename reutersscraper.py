import json
import os
from deiwells.deiwells.spiders.reuters_scraping import ReutersspiderSpider
from flask import Flask, render_template, jsonify, request, redirect, url_for
import time
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerRunner
from scrapy import signals
import crochet
from flask_cors import CORS
import requests
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from dao import DataAccessUtil
import dnbscraper as dnb

def scrape(name):
    token = os.environ['TOKEN']
    if not token:
        print('ERROR:No Token set....')
        return jsonify([])

    reuters_endpoint = "https://api-eit.refinitiv.com/permid/search?q=name:{COMPANY_NAME}&num=1&access-token={TOKEN}&entitytype=organization&format=JSON"
    URL = reuters_endpoint.format(TOKEN=token, COMPANY_NAME=name)
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
            detail['companyDetailUrl'] = url+'/financials/income-annual'
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

        companyInfo = scraped_item | detail
        print(companyInfo)
        output_data.append(companyInfo)
    else:
        print('company does not exist:' + name)
        return []

    return output_data