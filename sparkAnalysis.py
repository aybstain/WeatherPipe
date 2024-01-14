from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, max
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

print("Create a SparkSession")
# Create a SparkSession
spark = SparkSession.builder \
    .appName("KafkaStreamProcessing") \
    .getOrCreate()

print("SparkSession created!")
# Define the schema to match the JSON structure
schema = StructType([
    StructField("name", StringType(), True),
    StructField("lon", DoubleType(), True),
    StructField("lat", DoubleType(), True),
    StructField("weather_main", StringType(), True),
    StructField("weather_description", StringType(), True),
    StructField("temp_min", DoubleType(), True),
    StructField("temp_max ", DoubleType(), True),
    StructField("temp_kelvin", DoubleType(), True),
    StructField("temp_celsius", DoubleType(), True),
    StructField("feels_like_kelvin", DoubleType(), True),
    StructField("feels_like_celsius", DoubleType(), True),
    StructField("pressure", DoubleType(), True),
    StructField("wind_speed", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
])
print("Schema defined!")
# Read data from Kafka as a streaming DataFrame
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:19092") \
    .option("subscribe", "weather_data") \
    .option("startingOffsets", "earliest") \
    .load()
print("Data loaded!")
# Parse the JSON data and perform column renaming and dropping
result_df = kafka_df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", schema).alias("data")) \
    .select(
        "data.name",
        "data.lon",
        "data.lat",
        "data.weather_main",
        "data.weather_description",
        "data.temp_min",
        "data.temp_max ",
        "data.temp_celsius",
        "data.feels_like_celsius",
        "data.pressure",
        col("data.wind_speed").alias("wind"),
        "data.humidity"
    )

# Create a streaming query to show the original data
data_query = result_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime='60 seconds') \
    .start()

# Calculate streaming averages and maximum values for humidity and temp_celsius for each name
analysis_df = result_df.groupBy("name") \
    .agg(
        avg("humidity").alias("avg_humidity"),
        max("humidity").alias("max_humidity"),
        avg("temp_celsius").alias("avg_temp_celsius"),
        max("temp_celsius").alias("max_temp_celsius")
    )

# Create a streaming query to show the averages
analysis_query = analysis_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .trigger(processingTime='60 seconds') \
    .start()

print("Streaming started!")
# Wait for the streaming queries to terminate
data_query.awaitTermination()
analysis_query.awaitTermination()
print("Streaming terminated!")
