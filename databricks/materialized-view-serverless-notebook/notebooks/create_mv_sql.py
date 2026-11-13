# Databricks notebook source
# Creates the materialized view with SQL through spark.sql()

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
dbutils.widgets.text("source_table", "release_lab.jct_demo.bronze_orders")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
source = dbutils.widgets.get("source_table")

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE MATERIALIZED VIEW {catalog}.{schema}.daily_revenue_sql AS
    SELECT CAST(order_ts AS DATE) AS order_date,
           SUM(amount) AS revenue,
           COUNT(*) AS orders
    FROM {source}
    GROUP BY CAST(order_ts AS DATE)
""")
