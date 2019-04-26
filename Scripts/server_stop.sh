#!/bin/bash

sudo /opt/kafka/bin/kafka-server-stop.sh

echo Killing Kafka brokers...
echo Waiting 30 seconds

sleep 30s

sudo /opt/zookeeper/bin/zkServer.sh stop /opt/zookeeper/conf/zookeeper.properties

echo Killed Zookeeper server...
