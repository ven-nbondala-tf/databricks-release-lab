# Databricks notebook source
# Reports who the task runs as and whether it can read the demo table.

user = spark.sql("SELECT current_user()").first()[0]
rows = spark.sql("SELECT count(*) FROM release_lab.jct_demo.bronze_orders").first()[0]

result = f"current_user={user} rows={rows}"
print(result)
dbutils.notebook.exit(result)
