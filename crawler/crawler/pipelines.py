# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from kafka import KafkaProducer
from kafka.errors import KafkaError
import msgpack
import json

# from kafka import SimpleClient
# from kafka.producer import SimpleProducer

# from scrapy.utils.serialize import ScrapyJSONEncoder
# import json


class CrawlerPipeline(object):
    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic
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
        topics = settings.get('KAFKA_TOPICS', ['theculturetrip'])
        # producer = KafkaProducer(
        #     bootstrap_servers=hosts, value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        producer = KafkaProducer(
            bootstrap_servers=hosts)

        return cls(producer, topics)
