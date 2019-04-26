import json

from kafka import KafkaConsumer
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.tweets
bitcoin = db.bitcoin

consumer_btc = KafkaConsumer(
    'btc-processed',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my_group_btc',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer_btc:
    message = message.value
    bitcoin.insert_one(message)