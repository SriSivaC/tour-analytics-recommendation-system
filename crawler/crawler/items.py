# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TheculturetripItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()
    data = scrapy.Field()
    pass


class AttractionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fingerprint = scrapy.Field()
    attraction_path = scrapy.Field()
    category = scrapy.Field()
    pass


class AttrDetailItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()
    data = scrapy.Field()
    pass

class HotelUrlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    fingerprint = scrapy.Field()
    href = scrapy.Field()
    pass

class HotelInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()
    data = scrapy.Field()
    pass

class HotelReviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()
    data = scrapy.Field()
    pass
