# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import msgpack
# from scrapy.utils.serialize import ScrapyJSONEncoder

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

from scrapy.exceptions import DropItem


class KafkaPipeline(object):
    # Notes: You have configured with the max_request_size configuration as following:
    # server.properties, message.max.bytes=20971520
    # server.properties, replica.fetch.max.bytes=20971520
    # producer.properties, max.request.size=20971520 
    # consumer.properties, max.partition.fetch.bytes =20971520 

    def __init__(self, producer):
        self.producer = producer
        # self.encoder = ScrapyJSONEncoder()

    def process_item(self, item, spider):
        # msg = json.dumps(dict(item), ensure_ascii=False)
        # msg = self.encoder.encode(item)
        # print(msg)
        self.producer.send(item['topic'], item['data'])
        return item

    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings
        :rtype: A :class:`~KafkaPipeline` instance
        """

        hosts = settings.get('KAFKA_HOSTS', ['localhost:9092'])
        # topics = settings.get('KAFKA_TOPICS', ['theculturetrip'])
        producer = KafkaProducer(bootstrap_servers=hosts, max_request_size=20971520)
        # producer = KafkaProducer(
        #     bootstrap_servers=hosts, value_serializer=lambda m: json.dumps(m).encode('utf-8'))

        return cls(producer)


class DuplicatesUrlPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['fingerprint'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['fingerprint'])
            return item
