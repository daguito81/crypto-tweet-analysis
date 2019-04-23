#!/bin/bash

sudo /opt/kafka/bin/kafka-server-stop.sh

echo Killed Kafka brokers...

sleep 10s

sudo /opt/zookeeper/bin/zkServer.sh stop /opt/zookeeper/conf/zookeeper.properties

echo Killed Zookeeper server...
