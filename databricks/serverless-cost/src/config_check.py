# Databricks notebook source
# Tries to set a Spark configuration that serverless compute does not allow.
try:
    spark.conf.set("spark.executor.memory", "8g")
    result = "spark.executor.memory was set"
except Exception as e:
    result = type(e).__name__ + ": " + str(e)[:700]
dbutils.notebook.exit(result)
