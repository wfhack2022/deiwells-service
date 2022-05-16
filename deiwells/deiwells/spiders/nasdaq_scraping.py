import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Financials(scrapy.Item):
    name = scrapy.Field()

class NasdaqspiderSpider(scrapy.Spider):
    name = 'nashdaqspider'
    allowed_domains = ["reuters.com"]
    start_urls = ["https://www.reuters.com/markets/companies/BLK.N/financials/income-annual"]

    def parse(self, response):
        name = response.xpath('//*[@id="main-content"]/div[3]/div/div[1]/div/div[2]/div/div/div[2]').getall()
        print(name)