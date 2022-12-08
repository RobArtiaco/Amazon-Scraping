from cgitb import text
from cmath import asin
from dataclasses import replace

import scrapy, urllib.parse, json

prodotto = input('Cosa vuoi cercare?')
queries = [prodotto]

class AmazonSpider(scrapy.Spider):
    name = 'amazon_scraping'
    allowed_domains = ['amazon.com', 'amazon.it', 'amazon.ch']
    start_urls = ['http://www.amazon.it/']

    def parse(self, response):
        pass
    
    def start_requests(self):
        for query in queries:
            url = 'https://www.amazon.it/s?' + urllib.parse.urlencode({'k': query})
            yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_product_page(self, response):
        asin = response.meta['asin']
        title = response.xpath('//*[@id="productTitle"]/text()').extract_first()
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        price =response.xpath('//*[@class="a-offscreen"]/text()').extract_first()
        if price != 'null':
            yield{'Title':title, 'Rating': rating, 'NumberOfReviews':number_of_reviews, 'Price':price }
         
        temp = response.xpath('//*[@id="twister"]')
        sizes = []
        colors = []
        if temp:
            s = re.search('"variationValues" : ({.*})', response.text).groups()[0]
            json_acceptable = s.replace("'", "\"")
            di = json.loads(json_acceptable)
            sizes = di.get('size_name', [])
            colors = di.get('color_name', [])

        bullet_points = response.xpath('//*[@id="feature-bullets"]//li/span/text()').extract()
        seller_rank = response.xpath('//*[text()="Amazon Best Sellers Rank:"]/parent::*//text()[not(parent::style)]').extract()
        yield {'Title': title, 'Rating': rating, 'NumberOfReviews': number_of_reviews,
               'Price': price}


    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.it/dp/{asin}"
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'asin': asin})

        next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        if next_page:
            url = urllib.parse.urljoin("https://www.amazon.it",next_page)
            yield scrapy.Request(url=product_url, callback=self.parse_keyword_response)
