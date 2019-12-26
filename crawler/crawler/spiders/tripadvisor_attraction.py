import scrapy
from crawler.items import AttractionItem
import json
from collections import defaultdict
from backend.fingerprint import hostname_local_fingerprint
# from requests.models import PreparedRequest


class AttractionSpider(scrapy.Spider):
    name = "attraction"

    # start_urls = ['']
    # base_url = "https://tripadvisor.com.my"
    allowed_domains = ["tripadvisor.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        # 'ITEM_PIPELINES': {
        #     'crawler.pipelines.DuplicatesUrlPipeline': 300,
        # },
    }

    def start_requests(self):
        urls = [
            'https://www.tripadvisor.com.my/Attraction_Products-g293951-Malaysia.html', ]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_category)

    def parse_category(self, response):
        category = response.xpath(
            '//div[contains(@class, "filter_list_0")]')[0]
        category_title = category.xpath('./div/label/a/text()')
        category_link = category.xpath('./div/label/a/@href')
        if category.xpath('./div[contains(@class, "collapse hidden")]'):
            category_link += category.xpath(
                './div[contains(@class, "collapse hidden")]/div/label/a/@href')
            category_title += category.xpath(
                './div[contains(@class, "collapse hidden")]/div/label/a/text()')

        # category_link = [self.base_url + i for i in category_link.extract()]
        category_title = ['_'.join(i.split(' ')[:-1]).lower()
                          for i in category_title.extract()]
        for i in range(len(category_link)):
            url = response.urljoin(category_link[i].extract())
            yield scrapy.Request(url=url, meta={'category': category_title[i]}, dont_filter=True, callback=self.parse_attraction)

    def parse_attraction(self, response):

        for attraction_path in response.xpath('//div[contains(@class,"listing_title")]/a/@href'):
            # url = response.urljoin(attraction_path.extract())
            item = AttractionItem()
            item['fingerprint'] = hostname_local_fingerprint(attraction_path.extract()).decode('UTF-8')
            item['attraction_path'] = attraction_path.extract()
            item['category'] = response.meta['category']
            yield item

            # yield {
            #     'attraction_path': attraction_path,
            #     'category': response.meta['category'],
            # }

        next_page = response.xpath(
            '//div[contains(@class,"unified pagination")]')
        if next_page != []:
            if next_page.xpath("./span/@class").extract_first() != "nav next disabled":
                url = response.urljoin(next_page.xpath(
                    './a[contains(@class,"nav next")]/@href').extract_first())
                # next_page.xpath("./a/@data-page-number").extract_first()
                yield scrapy.Request(url=url, meta={'category': response.meta['category']}, dont_filter=True, callback=self.parse_attraction)

    # post processing of duplicate values
    def merge_json_data(self, src_fpath, dsn_fpath, uni_key, dup_key):
        with open(src_fpath, 'r') as f:
            data = json.load(f)

        # Using defaultdic
        temp = defaultdict(list)

        # Using extend
        for el in data:
            temp[el[uni_key]].extend([el[dup_key]])

        data = [{uni_key: x, dup_key: y} for x, y in temp.items()]

        # printing
        with open(dsn_fpath, 'w') as f:
            f.write('[\n' + ',\n'.join(json.dumps(i) for i in data) + '\n]')
