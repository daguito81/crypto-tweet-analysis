
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json

spark = SparkSession.builder.appName("Test1").getOrCreate()

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
    .option("checkpointLocation", "/home/daguito81/Desktop/crypto-tweet-analysis/SparkStream-test/pyspark-tests/checkpoints") \
    .start()

df_stream_btc = spark\
    .readStream\
    .format("kafka")\
    .option("kafka.bootstrap.servers", "localhost:9092, localhost:9093, localhost:9094")\
    .option("subscribe", "bitcoin")\
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
    .option("topic", "btc-processed") \
    .option("checkpointLocation", "/home/daguito81/Desktop/crypto-tweet-analysis/SparkStream-test/pyspark-tests/checkpoints2") \
    .start()