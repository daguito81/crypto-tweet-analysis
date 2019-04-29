#!/bin/bash

/opt/kafka/bin/kafka-topics.sh --create --replication-factor 2 --partitions 1 --bootstrap-server localhost:9092 --topic ethereum
/opt/kafka/bin/kafka-topics.sh --create --replication-factor 2 --partitions 1 --bootstrap-server localhost:9092 --topic bitcoin
/opt/kafka/bin/kafka-topics.sh --create --replication-factor 2 --partitions 1 --bootstrap-server localhost:9092 --topic eth-processed
/opt/kafka/bin/kafka-topics.sh --create --replication-factor 2 --partitions 1 --bootstrap-server localhost:9092 --topic btc-processed

echo Checking topic creation...

/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
