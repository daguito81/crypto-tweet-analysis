#!/bin/bash

sudo /opt/zookeeper/bin/zkServer.sh start /opt/zookeeper/conf/zookeeper.properties
echo Zookeper started...

sudo /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server1.properties &
sudo /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server2.properties &
#sudo /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server3.properties &

echo Kafka brokers online...

