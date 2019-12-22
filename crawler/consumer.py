from kafka import KafkaConsumer
import json

from fingerprint import hostname_local_fingerprint
from binascii import unhexlify
import happybase

from datetime import datetime
from calendar import timegm

KAFKA_TOPICS = ["theculturetrip", "tripadvisor_attraction"]

families = {
    'm': dict(max_versions=1),  # metadata
    'c': dict(max_versions=1)   # content
}


class HBaseBackend():
    def __init__(self, connection):
        self.connection = connection

    def get_table(self, table):
        return self.connection.table(table)

    def create_table(self, table, schema):
        self.connection.create_table(table, schema)

    def table_exist(self, kafka_topic):
        if bytes(kafka_topic, encoding="utf-8") in self.connection.tables():
            return True
        else:
            return False

    def insert_data(self, table, rowkey, data):
        table.put(unhexlify(hostname_local_fingerprint(rowkey)), data)

    def get_row(self, table, rowkey):
        return table.row(rowkey)


def utcnow_timestamp():
    return timegm(datetime.utcnow().timetuple())


def kafka_to_hbase(kafka_topic):
    consumer = KafkaConsumer(kafka_topic,
                             bootstrap_servers=['localhost:9092'], consumer_timeout_ms=5000, auto_offset_reset='earliest', enable_auto_commit=False, value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    hbase = HBaseBackend(happybase.Connection(
        'localhost', protocol='compact', transport='framed'))

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        # print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
        #                                      message.offset, message.key,
        #                                      message.value))

        url = json.loads(json.loads(message.value))[
            'props']['pageProps']['articleStoreState']['articleData']['data']['link']

        if not hbase.table_exist(kafka_topic):
            hbase.create_table(kafka_topic, families)

        table = hbase.get_table(kafka_topic)

        hbase.insert_data(table, url, {b'm:url': url})
        hbase.insert_data(table, url, {b'm:created_at': str(utcnow_timestamp())})
        hbase.insert_data(table, url, {b'c:content': message.value})
        
    print("done.")



kafka_to_hbase(KAFKA_TOPICS[0])