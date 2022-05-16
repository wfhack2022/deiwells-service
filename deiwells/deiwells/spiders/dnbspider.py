from turtle import Screen
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Company(scrapy.Item):
    name = scrapy.Field()

class CompaniesspiderSpider(scrapy.Spider):
    name = 'dnbspider'
    allowed_domains = ["owler.com"]
    start_urls = ["https://www.owler.com/company/cpyi"]

    def parse(self, response):
            about = response.xpath('//*[@id="__next"]/div/div[2]/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[1]/div[2]/div[5]/div[2]/div/p/a/@href').getall()
            print(about)
