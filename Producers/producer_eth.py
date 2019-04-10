from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import json

with open("keys.json") as f:
    keys = json.loads(f.read())

access_token = keys['access_token']
access_token_secret = keys['access_token_secret']
consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']

kafka = KafkaClient(["localhost:9092", "localhost:9093", "localhost:9094"])
producer = SimpleProducer(kafka)


class StdOutListener(StreamListener):
    def on_data(self, data):
        producer.send_messages("ethereum", data.encode('utf-8'))
        print(data)
        return True

    def on_error(self, status):
        print(status)


listener = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, listener)
stream.filter(track=["ETH", "eth", "ethereum", "Ethereum", "$ETH"],
              is_async=True)
