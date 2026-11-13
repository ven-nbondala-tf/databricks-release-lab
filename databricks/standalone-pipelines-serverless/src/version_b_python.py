# Databricks notebook source
# Version B: the same two objects with the Python pipelines decorators

from pyspark import pipelines as dp
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

@dp.table(name=f"{catalog}.{schema}.orders_st_py")
def orders_st_py():
    # Streaming table: reads new files from the landing volume
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load(f"/Volumes/{catalog}/{schema}/landing/")
        .select("order_id", "region", "amount", F.col("order_ts").cast("timestamp").alias("order_ts"))
    )

# COMMAND ----------

@dp.materialized_view(name=f"{catalog}.{schema}.daily_revenue_py")
def daily_revenue_py():
    # Materialized view: daily revenue by region on top of the streaming table
    return (
        spark.read.table(f"{catalog}.{schema}.orders_st_py")
        .groupBy(F.col("order_ts").cast("date").alias("order_date"), "region")
        .agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))
    )
