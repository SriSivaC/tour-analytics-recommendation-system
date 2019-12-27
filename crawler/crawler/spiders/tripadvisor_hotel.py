import scrapy
from crawler.items import HotelItem
import json
from collections import defaultdict
from backend.fingerprint import hostname_local_fingerprint
# from requests.models import PreparedRequest


class AttractionSpider(scrapy.Spider):
    name = "hotel"

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
        urls = ['https://www.tripadvisor.com.my/Hotels-g293951-Malaysia-Hotels.html', ]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parseHotelCity)

    def parseHotelCity(self, response):

        hotelCityList = response.xpath('//*[@data-geoid]/@href').extract()

        for cityHref in hotelCityList:
            cityHref = response.urljoin(cityHref)
            yield scrapy.Request(url=cityHref, dont_filter=True, callback=self.parseHotelItem)

        hotelCityPaginationXpath = response.xpath('//*[contains(@class,"leaf_geo_pagination")]') 
        nextHotelCityPageHref = hotelCityPaginationXpath.xpath('.//a[contains(@class,"next")]/@href').extract_first()

        if nextHotelCityPageHref is not None:
            nextHotelCityPageHref = response.urljoin(nextHotelCityPageHref)
            yield scrapy.Request(url=nextHotelCityPageHref, dont_filter=True, callback=self.parseHotelCity)

    def parseHotelItem(self, response):
        hotelItemContainerXpath = response.xpath('//*[contains(@id,"taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0")]')
        hotelUrlList = hotelItemContainerXpath.xpath('.//@data-url')

        for url in hotelUrlList:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parseHotelDetail)

        hotelItemPaginationXpath = response.xpath('//*[contains(@class,"standard_pagination")]') 
        nextHotelItemPageHref = hotelItemPaginationXpath.xpath('.//a[contains(@class,"next")]/@href').extract_first()

        if nextHotelItemPageHref is not None:
            nextHotelItemPageHref = response.urljoin(nextHotelItemPageHref)
            yield scrapy.Request(url=nextHotelItemPageHref, dont_filter=True, callback=self.parseHotelItem)

    def parseHotelDetail(self, response):
        pass

# https://www.tripadvisor.com.my/data/1.0/location/293951
# https://www.tripadvisor.com.my/data/1.0/hotelDetail/614528/heatMap
