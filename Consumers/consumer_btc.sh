#!/bin/bash

/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bitcoin >> ./btctweets
