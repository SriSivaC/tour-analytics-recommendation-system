import scrapy
from crawler.items import CrawlerItem
# from requests.models import PreparedRequest


class AttractionSpider(scrapy.Spider):
    name = "attraction"

    # start_urls = ['']
    # base_url = "https://tripadvisor.com.my"
    allowed_domains = ["tripadvisor.com"]

    def start_requests(self):
        urls = [
            'https://www.tripadvisor.com.my/Attraction_Products-g293951-Malaysia.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_category)

    def parse_category(self, response):
        cat = response.xpath('//div[contains(@class, "filter_list_0")]')[0]
        tour_categories = cat.xpath('./div/label/a/text()')
        category_links = cat.xpath('./div/label/a/@href')
        if cat.xpath('./div[contains(@class, "collapse hidden")]'):
            category_links += cat.xpath(
                './div[contains(@class, "collapse hidden")]/div/label/a/@href')
            tour_categories += cat.xpath(
                './div[contains(@class, "collapse hidden")]/div/label/a/text()')

        # category_links = [self.base_url + i for i in category_links.extract()]
        tour_categories = ['_'.join(i.split(' ')[:-1]).lower()
                           for i in tour_categories.extract()]
        for i in range(len(category_links)):
            url = response.urljoin(category_links[i].extract())
            yield scrapy.Request(url=url, meta={'category': tour_categories[i]}, dont_filter=True, callback=self.parse_attraction)

    def parse_attraction(self, response):
        for attr in response.xpath('//div[contains(@class,"listing_title")]/a/@href'):
            url = response.urljoin(attr.extract())
            yield {
                'attraction_url': url,
                'category': response.meta['category'],
            }

        next_page = response.xpath(
            '//div[contains(@class,"unified pagination")]')
        if next_page != []:
            if next_page.xpath("./span/@class").extract_first() != "nav next disabled":
                url = response.urljoin(next_page.xpath(
                    './a[contains(@class,"nav next")]/@href').extract_first())
                # next_page.xpath("./a/@data-page-number").extract_first()
                yield scrapy.Request(url=url, meta={'category': response.meta['category']}, dont_filter=True, callback=self.parse_attraction)
