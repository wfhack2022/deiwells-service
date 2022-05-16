import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Company(scrapy.Item):
    name = scrapy.Field()
    about = scrapy.Field()
    address = scrapy.Field()
    industry = scrapy.Field()
    people = scrapy.Field()
    position = scrapy.Field()
    news = scrapy.Field()
    ticker = scrapy.Field()
    companyUrl = scrapy.Field()
    companyDetailUrl = scrapy.Field()

class ReutersspiderSpider(scrapy.Spider):
    name = 'reutersspider'
    allowed_domains = ["reuters.com", "globenewswire.com"]
    start_urls = []

    # myBaseUrl = ''
    # companyDetails = {}
    # def __init__(self, category='', companyDetails={}, **kwargs): 
    #     self.myBaseUrl = category
    #     self.start_urls.append(self.myBaseUrl)
    #     self.companyDetails = companyDetails
    #     super().__init__(**kwargs)

    # custom_settings = {'FEED_URI': 'deiwells/reuters.json', 'CLOSESPIDER_TIMEOUT' : 15}

    def parse(self, response):
        name = response.xpath('//*[@id="main-content"]/div/div/div[1]/div/h1/text()').extract_first()
        about = response.xpath('//*[@id="main-content"]/div/div/div/div/div/div[1]/p/text()').extract_first()
        address = response.xpath('//*[@id="main-content"]/div/div/div/div/div/div[2]/div[1]/address/text()').getall()
        industry = response.xpath('//*[@id="main-content"]/div/div/div/div/div/div[2]/div[3]/p/text()').extract_first()
   
        people = response.xpath('//*[@id="main-content"]/div[3]/div/div[2]/div/div/div[3]/dl/div/dt/text()').getall()
        position = response.xpath('//*[@id="main-content"]/div[3]/div/div[2]/div/div/div[3]/dl/div/dd/text()').getall()
        company = Company(name=name, about=about, address=address, industry=industry, people=people, position=position)
        company['news']=[]
        # if(self.companyDetails['ticker']):
        #     company['ticker'] = self.companyDetails['ticker']
        #     company['companyUrl'] = self.companyDetails['companyUrl']
        #     company['companyDetailUrl'] = self.companyDetails['companyDetailUrl']
        yield company
        # yield scrapy.Request('https://www.globenewswire.com/search/keyword/'+company['name'], 
        #         callback=self.parse_news,  meta={'item': company})
                

    def parse_news(self, response):
        company = response.meta['item']
        companyNews = response.xpath('//*[@id="app-body-container"]/div/div[2]/div/div[2]/div/div/div/a/@href').getall()
        news = []
        for event in companyNews:
            event = 'https://www.globenewswire.com'+event
            news.append(event)

        company['news']=news
        # print(company)
        yield company