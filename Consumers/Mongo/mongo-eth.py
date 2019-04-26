import json
from kafka import KafkaConsumer
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.tweets
ethereum = db.ethereum

consumer_eth = KafkaConsumer(
    'eth-processed',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my_group_eth',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer_eth:
    message = message.value
    ethereum.insert_one(message)