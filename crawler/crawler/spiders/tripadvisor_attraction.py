import scrapy
from crawler.items import CrawlerItem
# from requests.models import PreparedRequest


class AttractionSpider(scrapy.Spider):
    name = "attraction"

    # start_urls = ['']
    base_url = "https://tripadvisor.com.my"
    allowed_domains = ["tripadvisor.com"]

    def start_requests(self):
        urls = [
            'https://www.tripadvisor.com.my/Attraction_Products-g293951-Malaysia.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_category)

    def parse_category(self, response):
        cat = response.xpath('//div[@class="filter_list_0"]')[0]
        tour_categories = cat.xpath('./div/label/a/text()')
        category_links = cat.xpath('./div/label/a/@href')
        if cat.xpath('./div[@class="collapse hidden"]'):
            category_links += cat.xpath(
                './div[@class="collapse hidden"]/div/label/a/@href')
            tour_categories += cat.xpath(
                './div[@class="collapse hidden"]/div/label/a/text()')

        category_links = [self.base_url + i for i in category_links.extract()]
        tour_categories = ['_'.join(i.split(' ')[:-1]).lower()
                           for i in tour_categories.extract()]
        for i in range(len(tour_categories)):
            yield scrapy.Request(url=category_links[i], meta={'category': tour_categories[i]}, dont_filter=True, callback=self.parse_attraction)

    def parse_attraction(self, response):
        for attr in response.xpath('//div[@data-slot]//div[@class="listing_title"]/a/@href'):
            yield {
                'attraction_url': self.base_url + attr.extract(),
                'category': response.meta['category'],
            }

        next_page = response.xpath("//div[@class='unified pagination ']")
        if next_page != [] and next_page.xpath("./span/@class").extract_first() != "nav next disabled":
                url = next_page.xpath("./a/@href").extract_first()
                # next_page.xpath("./a/@data-page-number").extract_first()
                yield scrapy.Request(url=self.base_url + url, meta={'category': response.meta['category']}, dont_filter=True, callback=self.parse_attraction)
