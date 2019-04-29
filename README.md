# crypto-tweet-analysis  
Project to injest crypto price and tweet data and analyze it.  
The purpose of this project (and looooong README.md) is to educate on how to set up this project and how every piece works, instead of simply providing some code.
***

## The Plan
The original plan is to have python scripts get the data and publish them to a kafka topic, then load this data into pyspark and then do the required transformations and then load them into durable storage. 

**Notes:**  
1) We will set up Zookeeper and 3 Kafka brokers locally for prototyping
2) We will set Kafka topics to retain logs for 24 hours
3) we will try doing hourly aggregates before dumping on durable media (to keep it simmple)
4) We will run this on a Ubuntu 16:04 machine (Ubuntu needs some love as well)
***
## Setting Up

First we need to download a copy of zookeeper as Apache kafka requires it to store its metadata
We can do the following:  
```
wget http://apache.rediris.es/zookeeper/stable/zookeeper-3.4.14.tar.gz
tar -xvf zookeeper-3.4.14.tar.gz -C /opt/
ln -s /opt/zookeeper-3.4.14 /opt/zookeeper
```

This will create the zookeeper folder in /opt/ which we can use to run and configure our zookeeper server.

For our purposes, we will use the sample config file that comes with zookeeper, although we will copy it in case we need to change things. And then we start our zookeeper instance.  
In this case we will use a single node instead of an ensemble
```
cd /opt/zookeeper/
cp conf/zoo_sample.cfg conf/zookeeper.properties
bin/zkServer.sh start conf/zookeeper.properties
```

With our zookeeper server running (default at port 2181) we can now start setting up our kafka brokers. We do this in a manner very similar to the zookeeper (download, untar, link and config).
```
wget http://apache.rediris.es/kafka/2.2.0/kafka_2.11-2.2.0.tgz
tar -xvf kafka_2.11-2.2.0.tgz -C /opt/
ln -s /opt/kafka_2.11-2.2.0 /opt/kafka
cd /opt/kafka
```
This next part depends on how many brokers do you want ot run. In the case of this example, we will run 3 brokers on the same machine. In a real example, each broker can be run on it's own instance. This we need to set up on the config files for kafka. As we are running the 3 locally, we need to change the broker ID number which needs to be unique, but also the port as they are all localhost. 

```
cd /opt/kafka/config
cp server.properties server1.properties
cp server.properties server2.properties
cp server.properties server3.properties
```
Then using a text editor like nano or vim you can change the following:  
broker.id=1  
listeners=PLAINTEXT://localhost:9092  
advertised.listeners=PLAINTEXT://localhost:9092  
log.dirs=/tmp/kafka-logs-1  
log.retention.hours=24  
offsets.topic.replication.factor=3  
transaction.state.log.replication=3

And repeat the process for the other 2 brokers changing the broker.id, the port number and the log dir so that there are no conflicts  

After that we are ready to get the brokers running. For that we can do:
```
cd /opt/kafka
bin/kafka-server-start.sh config/server1.properties &
bin/kafka-server-start.sh config/server2.properties &
bin/kafka-server-start.sh config/server3.properties &
```
This works by detaching the processes from the console. If you prefer to have it attached you need to do each server on a different terminal or use a tool like `screen` if using screen we can do:
```
screen -S kafka1
bin/kafka-server-start.sh config/server1.properties
```
Then hit CTRL+A CTRL+D to detach and repeat the process for the other 2 servers.

With this we have our 3 kafka brokers running and ready to create topics, producers and consumers.
***
## Creating and testing our Topics
So we already have our brokers running, having 3 brokers will allow us to replicate our data for fault-tolerance. Normally these brokers would be hosted in 3 different servers.

Kafka works by having producers send data into a topic and then consumers taking that data from the same topic.
By using partitions and different producers / consumers, we can design how our data will flow through our architecture.  

#TODO Add a diagram here

In this case we will have 2 topics and 2 producers, 1 for Ethereum tweets and 1 for Bitcoin tweets.

The first step is to create the topics and configure them. We already know we set the global message retention to 24 hours, so data in a topic will be deleted after 24 hours.  

We can create topics with:
```
cd /opt/kafka/
bin/kafka-topics.sh --create --replication-factor 3 --partitions 3 --bootstrap-server localhost:9092 --topic ethereum
bin/kafka-topics.sh --create --replication-factor 3 --partitions 3 --bootstrap-server localhost:9092 --topic bitcoin
```
### Testing the topic

To test that our server is working right, we can make a test topic and use a console producer and consumer to test it out. 

```
cd /opt/kafka
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic my-test-topic
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic my-test-topic
```
Then on another terminal window do:
```
cd /opt/kafka
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic my-test-topic
```
Now everything you write on the first terminal will appear on the second terminal. 

For ease of use we have provided some shell scripts that will run these servers and create both topics needed automatically in the Producer folder.
***

## Creating the brokers and topics for the project
Attached to this repo, we have a couple of script files that help us create our brokers and topics for this project.  
These are:  
`./Scripts/server_start.sh`  
`./Scripts/topic_creation.sh`

The first script runs the zookeeper instance and brokers (Set for 3 brokers but 1 commented out).  
The second script creates the topics with 1 partition and a replication factor of 2. It creates the topic where the raw tweets will be passed and the processed ones.

## Consumers and Producers
We've already made sure that our kafka brokers are working and that they transmit data the way we want to. For the sake of simplicity, we will create topics with 1 partition and 1 prducer / consumer combo. However Kafka allows us to create Consumer Groups and partition the data between different consumers in the same group.  
Because the velocity of our data is not that high, we can get away with using single producer / consumer combos with 1 partition.

### Producer creation and setup
The main goal is to scrape tweets and ingest them into a database. So the first step is to actually get the tweets. For this we create python scripts and use the library tweepy and kafka-python. 
#### Example Code:
```
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import json

keys = json.loads(open("keys.json").read())

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
stream.filter(track=["ETH", "eth", "Ethereum", "ethereum", "$ETH"],
              is_async=True)

```
In here we create our listener and auth objects using tweepy and our credentials from Twitter (passed as a json file for security purposes)

Then we create our KafkaClient instance with the same values as we have in `--bootstrap-server` which is `localhost:9092` by default. 

At the end we send the data stream to the specific topic filtering by certain keywords. All the tweets that match our criteria are sent to the specified topic and retained for a certain perdiod of time (24 hours in our case) until it's consumed by the consumer.  

Provided in this repo we have 2 files in ./Producers which each scrape tweets for a certain crypto.

To run these producers, we just need to run an instance of the python script in an environment that contains `tweepy` and `kafka-python`.  

To scale these producers horizontally, we can deploy this script on a docker image and then run several instances of the container. This can be deployed using docker swarm or kubernetes. This will be addressed later on in the project

### Creating and Running the first Consumers.
After we have our filtered tweets, we need to select the fields that we care about and drop the rest as a tweet object has dozens of fields and most of them are not any of use. This can alos be changed over time to include or drop fields. These can be done with Structured Streaming in Spark. For this project we decided to use Pyspark but we will transfer to Scala later on.  

The example script for pyspark is: 

```
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json

spark = SparkSession.builder.appName("eth-process").getOrCreate()

tweet_schema = spark.read.json("/home/daguito81/tweets/*").schema

df_stream_eth = spark\
    .readStream\
    .format("kafka")\
    .option("kafka.bootstrap.servers", "localhost:9092, localhost:9093, localhost:9094")\
    .option("subscribe", "ethereum")\
    .load()\
    .select(from_json(col("value").cast("string"), tweet_schema).alias("parsed_value"))\
    .selectExpr("parsed_value.entities.hashtags",
                  "parsed_value.favorite_count",
                  "parsed_value.lang",
                  "parsed_value.retweet_count",
                  "parsed_value.text",
                  "parsed_value.user.followers_count",
                  "parsed_value.user.name",
                  "parsed_value.id",
                  "parsed_value.created_at")\
    .selectExpr("CAST(id AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "eth-processed") \
    .option("checkpointLocation", "/home/daguito81/Desktop/checkpoints/checkpoints-eth") \
    .start()
df_stream_eth.awaitTermination()
```
The files that we run for spark are:  
`./Consumers/Spark/pyspark-eth.py`  
`./Consumers/Spark/pyspark-btc.py`

Each script of Spark Structured Streaming is grabbing the messages from its respective kafka topic, transforming the data into a JSON file, selecting certain fields and then writing them back into a different kafka topic that can be consumed later on by another process. These files are both consumers and producers at the same time.  

#### Running the Spark Scripts
As we are using a kafka library for spark, we need to submit this script for our specific installation:

To submit this in standalone mode:  
`spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 pyspark-eth.py`  

To submit it in a cluster running YARN:  
`spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --master yarn --deploy-mode cluster pyspark-eth.py`  

The specific package might be different depending on the Scala and Spark versions installed. In this case is Scala 2.11 and Spark 2.4.0.

The good thing about using Spark is that it's easily scalable by simply running it in a cluster. In the case that the processing takes too long and it requires more computing power, it's as simple as adding more machines to the cluster and there is no need to change anything in the code (Except perhaps the replication and partitioning of kafka topics).  

***
## Durable Storage
For this project we decided to work on an instance of MongoDB in a docker container. MongDB is a document based NoSQL database and the JSON files that the tweets are being moved as are a perfect fit for a document oriented Database.

This assumes we have Docker working on the system.
As this is a simple project working on a container, we won't go through the trouble of setting up mongo in a secure way.  
To create the container with authentication enabled, you can follow the following article:  
https://hackernoon.com/securing-mongodb-on-your-server-1fc50bd1267b  

### Setting up MongoDB container
As we want to have persistent data, we can create a linked folder in our HOME directory with:  
`mkdir -p ~/DockerData/mongo`

And then run the container with:  
`docker run --name my_mongo -d --rm --volume=$HOME/DockerData/mongo:/data/db -p 27017:27017 mongo`  
To check and administer the database we can use:  
`docker run --name my_mongo-express -d --rm --link my_mongo:mongo -p 8085:8081 mongo-express`  


### Creating and Running MongoDB Consumers.
We know that we have our processed tweets in kafka topics and we need to insert them into MongoDB. Luckily we can do that with a simple python script that can eb run locally or deployed in containers as needed.

The sample code is:  
```
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
```
As we can see, we only need to create the MongoClient instance with the required information and then a KafkaConsumer instance that reads the same `--bootstrap-server` as before and the topic name. 
We set `auto_offset_reset='earliest'` and `enable_auto_commit=True` so the script passes the information of which messages it has processed. This allows us to run this in batches or in continuous mode as well as being able to restart the service without reinserting every tweet back into the mongo database.

To run these we just run an instance using python, or deploy them in a container.

***
Ingestion Summary:

For this phase of the project, we got certain tweets streamed from the twitter API, passed it to a kafka topic, then a spark script grabbed those tweets and selected certain fields and passed them to a different kafka topic and then a python script grabbed those processed tweets and inserted them one by one into a mongo database instance running on a docker container.  

The steps in code to get this run after cloning the repo are:

1) Run the `./Scripts/server_start.sh` script and wait for the kafka brokers to be online
2) Run to `./Scripts/topic_creation.sh` to create the topics required
3) Run the producer scripts (preferably 1 in each terminal for monitoring purposes) `python ./Producers/producer_eth.py` and the same with the btc
4) Run the spark script by doing `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 ./Consumers/Spark/pyspark-eth.py` and the same for the btc script
5) Create the docker containers for the mongodb instance and mongo-express admin tool. by doing:  
`docker run --name my_mongo -d --rm --volume=$HOME/DockerData/mongo:/data/db -p 27017:27017 mongo`  
`docker run --name my_mongo-express -d --rm --link my_mongo:mongo -p 8085:8081 mongo-express`  
6) Run the mongo consumers by doing `python ./Consumers/Mongo/mongo-eth.py` and the equivalent with btc
7) Monitor the inserted tweets either by using the mongo express web interface at `localhost:8085` or:  
`docker exec -it my_mongo mongo`  
and then querying the database with:  
`use tweets`  
`db.ethereum.count()`
***
## Next Steps
* For the next steps we will include another stream coming from a crypto price API and then join this data with our tweets on the spark Transformation step
* Analyze several metrics from both price and tweets using approximation algorithms.
* Create NLP functions and map them to the tweets in the spark transforming step.

