# Databricks notebook source
# Creates the same materialized view with the Python pipelines decorator.
# This needs a serverless environment version that can import pyspark.pipelines.

from pyspark import pipelines as dp
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
dbutils.widgets.text("source_table", "release_lab.jct_demo.bronze_orders")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
source = dbutils.widgets.get("source_table")

# COMMAND ----------

@dp.materialized_view(name=f"{catalog}.{schema}.daily_revenue_py")
def daily_revenue_py():
    return (
        spark.read.table(source)
        .groupBy(F.col("order_ts").cast("date").alias("order_date"))
        .agg(F.sum("amount").alias("revenue"), F.count("*").alias("orders"))
    )
