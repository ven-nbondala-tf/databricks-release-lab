# Databricks notebook source
# Small serverless workload used to generate billing records for the cost tag tests.
df = spark.range(0, 5_000_000).selectExpr("id", "id % 10 AS bucket")
print(df.groupBy("bucket").count().orderBy("bucket").count())
