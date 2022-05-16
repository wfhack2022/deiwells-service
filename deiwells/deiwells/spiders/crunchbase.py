from turtle import Screen
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Company(scrapy.Item):
    name = scrapy.Field()

class CompaniesspiderSpider(scrapy.Spider):
    name = 'crunchbasespider'
    allowed_domains = ["/permid.org"]
    start_urls = ["https://permid.org/1-5037635088"]

    def parse(self, response):
            about = response.xpath('//*[@id="body"]/section/div/div[2]/div[2]/h3f/text()').getall()
            print(about)
