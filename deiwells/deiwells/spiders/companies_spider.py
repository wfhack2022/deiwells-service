import scrapy

URLS = {
    'BLACK_OWNED': 'https://theimpactinvestor.com/black-owned-stocks/',
    'WOMEN_OWNED': 'https://financebuzz.com/women-owned-businesses',
    'HISPANIC_LED': 'https://www.kiplinger.com/slideshow/investing/t052-s001-7-latin-american-stocks-to-buy-for-the-long-term/index.html'
}

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    start_urls = URLS.values()
    companies = {}

    def add_to_companies(self, companies, category):
        for company in companies:
          self.companies[company] = category
        print(self.companies)

    def parse(self, response):
        if response.url == URLS['BLACK_OWNED']:
            black_owned_companies = response.selector.xpath('//*[@id="genesis-content"]/article/div[2]/ul[1]/li/text()').getall()
            self.add_to_companies(black_owned_companies, 'BLACK_OWNED')
        elif response.url == URLS['WOMEN_OWNED']:
            women_owned_companies = response.selector.css('div.article__content h3::text').getall()[:-3]
            self.add_to_companies(women_owned_companies, 'WOMEN_OWNED')
        elif response.url == URLS['HISPANIC_LED']:
            hispanic_led_companies = response.selector.css('div.polaris__single-slide--wrapper h3 span::text').getall()
            self.add_to_companies(hispanic_led_companies, 'HISPANIC_LED')
        

