# Databricks notebook source
# A parallel Spark workload that is easy to scale. It runs the same work whatever the
# serverless compute size is, so the run time shows what the rate limit changes.

import time
from pyspark.sql import functions as F

dbutils.widgets.text("rows", "300000000")
dbutils.widgets.text("partitions", "1200")

rows = int(dbutils.widgets.get("rows"))
partitions = int(dbutils.widgets.get("partitions"))

# COMMAND ----------

start = time.time()

df = (
    spark.range(0, rows, 1, partitions)
    .withColumn("h", F.sha2(F.col("id").cast("string"), 256))
    .withColumn("bucket", F.col("id") % 1000)
)

result = df.groupBy("bucket").agg(F.count("*").alias("n"), F.max("h").alias("max_hash")).collect()

elapsed = round(time.time() - start, 1)
print(f"rows={rows} partitions={partitions} buckets={len(result)} elapsed_seconds={elapsed}")
