# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from kafka import SimpleClient
from kafka.producer import SimpleProducer

from scrapy.utils.serialize import ScrapyJSONEncoder
import json


class CrawlerPipeline(object):
    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic
        self.encoder = ScrapyJSONEncoder()

    def process_item(self, item, spider):
        # msg = json.dumps(dict(item), ensure_ascii=False)
        # msg = self.encoder.encode(item)
        self.producer.send_messages(
            self.topic, item['data'].encode(encoding="UTF-8"))
        return item

    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings
        :rtype: A :class:`~KafkaPipeline` instance
        """
        k_hosts = settings.get('SCRAPY_KAFKA_HOSTS', ['localhost:9092'])
        topic = settings.get('KAFKA_TOPIC', 'scrapy_kafka_item')
        kafka = SimpleClient(k_hosts)
        conn = SimpleProducer(kafka)
        return cls(conn, topic)
