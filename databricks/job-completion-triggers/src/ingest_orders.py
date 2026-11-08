# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest orders
# MAGIC Loads a fresh batch of orders into `bronze_orders`.

# COMMAND ----------

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "jct_demo")
dbutils.widgets.text("fail", "false")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
should_fail = dbutils.widgets.get("fail").lower() == "true"

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"USE {catalog}.{schema}")
print(f"writing to {catalog}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate a batch
# MAGIC There is no real source system here, so the batch is made up. Swap this cell for your own read.

# COMMAND ----------

from pyspark.sql import functions as F

batch = (
    spark.range(1, 501)
    .withColumnRenamed("id", "order_id")
    .withColumn("customer_id", (F.rand(seed=1) * 50).cast("int") + 1)
    .withColumn("amount", F.round(F.rand(seed=2) * 200 + 5, 2))
    .withColumn("order_ts", F.current_timestamp() - F.expr("make_interval(0, 0, 0, cast(rand() * 30 as int))"))
    .withColumn("_ingested_at", F.current_timestamp())
)

# COMMAND ----------

if should_fail:
    raise Exception("failing on purpose")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to bronze

# COMMAND ----------

batch.write.mode("overwrite").saveAsTable("bronze_orders")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check what landed

# COMMAND ----------

rows = spark.table("bronze_orders").count()
print(f"bronze_orders now has {rows} rows")
display(spark.table("bronze_orders").orderBy("order_id").limit(10))
