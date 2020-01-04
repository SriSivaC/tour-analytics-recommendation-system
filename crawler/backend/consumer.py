from kafka import KafkaConsumer
import json

from fingerprint import hostname_local_fingerprint
from binascii import unhexlify
import happybase

from datetime import datetime
from calendar import timegm


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


def kafka_to_hbase(broker, hbase_host, kafka_topic, key, column):
    hbase = HBaseBackend(happybase.Connection(hbase_host, protocol='compact', transport='framed'))

    consumer = KafkaConsumer(kafka_topic, bootstrap_servers=broker, consumer_timeout_ms=5000,
                             auto_offset_reset='earliest', enable_auto_commit=False, value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print("processing...")
    for message in consumer:
        url_id = json.loads(json.dumps(message.value))

        for k in key:
            url_id = url_id[k]

        if not hbase.table_exist(kafka_topic):
            hbase.create_table(kafka_topic, families)

        table = hbase.get_table(kafka_topic)

        hbase.insert_data(table, str(url_id), {bytes(column[0], encoding='utf-8'): str(url_id)})
        hbase.insert_data(table, str(url_id), {b'm:created_at': str(utcnow_timestamp())})
        hbase.insert_data(table, str(url_id), {b'c:content': json.dumps(message.value)})

    print("done.")

def kafka_to_json(broker, kafka_topic, filepath, key):
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=broker,
        max_partition_fetch_bytes=20971520,
        consumer_timeout_ms=5000,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print("processing...")
    with open(filepath, 'w') as f:
        f.write('[')

        for message in consumer:
            value = message.value
            
            for k in key:
                value = value[k]
            
            if type(value) == list:
                for v in value:
                    f.write(json.dumps(v))
                    f.write(',')
            else:
                f.write(json.dumps(value))
                f.write(',')
                
        f.write(
            '{"__COMMENT":"THIS IS PLACED HERE JUST TO IGNORE TRAILING COMMA AT THE END OF LAST OBJECT AND THIS OBJECT MUST IGNORE WHILE PARSING"}'
        )
        f.write(']')

    print("done.")


def kafka_consumer(broker, kafka_topic, filepath, key):
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=broker,
        max_partition_fetch_bytes=20971520,
        consumer_timeout_ms=5000,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    print("processing...")
    for message in consumer:
        value = message.value
            
        for k in key:
            value = value[k]
            
        if type(value) == list:
            for v in value:
                print(v)
        else:
            print(value)
                
    print("done.")

