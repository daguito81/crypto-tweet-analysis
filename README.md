# crypto-tweet-analysis  
Project to ingest crypto price and tweet data and analyze it
***

## The Plan
The original plan is to have python scripts get the data and publish them to a kafka topic, then load this data into pyspark and then do the required transformations and then load them into durable storage.

**Notes:**  
1) We will set up Zookeeper and 3 Kafka brokers locally for prototyping
2) We will set Kafka topics to retain logs for 24 hours
3) we will try doing hourly aggregates before dumping on durable media (to keep it simple)
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
This next part depends on how many brokers do you want to run. In the case of this example, we will run 3 brokers on the same machine. In a real example, each broker can be run on it's own instance. This we need to set up on the config files for kafka. As we are running the 3 locally, we need to change the broker ID number which needs to be unique, but also the port as they are all localhost.

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

## Consumers and Producers

### Creating and Running the Consumers.

### Creating and Running Producers

### Testing that we are generating data
