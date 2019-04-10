#!/bin/bash

/opt/kafka/bin/kafka-topics.sh --create --replication-factor 3 --partitions 3 --bootstrap-server localhost:9092 --topic ethereum
/opt/kafka/bin/kafka-topics.sh --create --replication-factor 3 --partitions 3 --bootstrap-server localhost:9092 --topic bitcoin

echo Checking topic creation...

/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
