from turtle import Screen
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Company(scrapy.Item):
    name = scrapy.Field()

class CompaniesspiderSpider(scrapy.Spider):
    name = 'companiesspier'
    allowed_domains = ["theimpactinvestor.com"]
    start_urls = ["https://theimpactinvestor.com/black-owned-stocks/"]

    def parse(self, response):
            name = response.xpath('//*[@id="genesis-content"]/article/div[2]/ul[1]/li/text()').getall()
            print(name)