# Databricks notebook source
# Daily orders load

import urllib.request

dbutils.widgets.text("scenario", "ok")
dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "failure_demo")

scenario = dbutils.widgets.get("scenario")
src = f"{dbutils.widgets.get('catalog')}.{dbutils.widgets.get('schema')}"

# COMMAND ----------

if scenario == "ok":
    df = spark.sql(f"""
        SELECT o.order_id, c.region, o.order_amount
        FROM {src}.orders_raw o
        JOIN {src}.customers c USING (customer_id)
    """)
elif scenario == "case_1":
    df = spark.table(f"{src}.orders_staging")
elif scenario == "case_2":
    df = spark.sql(f"SELECT order_id, amount FROM {src}.orders_raw")
elif scenario == "case_3":
    df = spark.sql(f"SELECT order_id, CAST(customer_id AS INT) AS customer_id FROM {src}.orders_raw")
elif scenario == "case_4":
    urllib.request.urlopen("https://signoff.internal.example.com/ready", timeout=10)
    df = spark.table(f"{src}.orders_raw")
else:
    raise ValueError(f"Unknown scenario: {scenario}")

rows = df.collect()  # collect() forces Spark to evaluate every expression
print(f"Scenario {scenario}: {len(rows)} rows loaded")
