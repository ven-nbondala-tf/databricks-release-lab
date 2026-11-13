# Databricks notebook source
# Version A: refresh both objects with REFRESH statements

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
base = f"{dbutils.widgets.get('catalog')}.{dbutils.widgets.get('schema')}"

# COMMAND ----------

spark.sql(f"REFRESH STREAMING TABLE {base}.orders_st_sql")

# COMMAND ----------

spark.sql(f"REFRESH MATERIALIZED VIEW {base}.daily_revenue_sql")
