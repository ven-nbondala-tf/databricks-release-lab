# Databricks notebook source
# A realistic serverless workload: generate rows, aggregate them and write a table.
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "<catalog>")
catalog = dbutils.widgets.get("catalog")

rows = 18_000_000_000
df = (spark.range(0, rows)
      .withColumn("customer_id", (F.col("id") % 50000).cast("int"))
      .withColumn("amount", F.round((F.hash("id") % 10000) / 100.0, 2)))

agg = (df.groupBy("customer_id")
         .agg(F.count("*").alias("orders"), F.sum("amount").alias("revenue")))
agg.write.mode("overwrite").saveAsTable(f"{catalog}.cost_demo.orders_by_customer")
print(agg.count())
