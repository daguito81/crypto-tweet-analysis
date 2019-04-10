#!/bin/bash
/opt/kafka/bin/kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic ethereum
/opt/kafka/bin/kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic bitcoin

echo Checking topic deletion...

/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

echo If nothing showed up, everything is ok!
