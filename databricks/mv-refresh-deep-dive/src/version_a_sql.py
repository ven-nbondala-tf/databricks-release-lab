# Databricks notebook source
# Version A: a streaming table and a materialized view defined with SQL

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

# Streaming table: reads new files from the landing volume
spark.sql(f"""
    CREATE OR REFRESH STREAMING TABLE {catalog}.{schema}.orders_st_sql AS
    SELECT order_id, region, amount, CAST(order_ts AS TIMESTAMP) AS order_ts
    FROM STREAM read_files('/Volumes/{catalog}/{schema}/landing/', format => 'json')
""")

# COMMAND ----------

# Materialized view: daily revenue by region on top of the streaming table
spark.sql(f"""
    CREATE OR REPLACE MATERIALIZED VIEW {catalog}.{schema}.daily_revenue_sql AS
    SELECT CAST(order_ts AS DATE) AS order_date, region,
           SUM(amount) AS revenue, COUNT(*) AS orders
    FROM {catalog}.{schema}.orders_st_sql
    GROUP BY CAST(order_ts AS DATE), region
""")
