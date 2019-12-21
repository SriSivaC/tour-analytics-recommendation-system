from kafka import KafkaConsumer

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('scrapy_kafka_item',
                         bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest', enable_auto_commit=False)

for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                         message.offset, message.key,
                                         message.value))

# import happybase

# connection = happybase.Connection(
#     'localhost', protocol='compact', transport='framed')
# # connection.create_table(
# #     'mytable',{'family:qual1': dict(),}
# # )
# table = connection.table('mytable')

# table.put(b'row-key', {b'family:qual1': b'value1',
#                        b'family:qual2': b'value2'})

# row = table.row(b'row-key')
# print(row[b'family:qual1'])  # prints 'value1'

# # for key, data in table.rows([b'row-key-1', b'row-key-2']):
#     # print(key, data)  # prints row key and data for each row

# for key, data in table.scan(row_prefix=b'row'):
#     print(key, data)  # prints 'value1' and 'value2'
