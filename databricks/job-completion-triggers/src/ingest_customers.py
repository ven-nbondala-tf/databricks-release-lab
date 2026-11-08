# Databricks notebook source
# MAGIC %md
# MAGIC # Ingest customers
# MAGIC Loads the customer list into `bronze_customers`.

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

# COMMAND ----------

from pyspark.sql import functions as F

regions = F.array(F.lit("north"), F.lit("south"), F.lit("east"), F.lit("west"))

batch = (
    spark.range(1, 51)
    .withColumnRenamed("id", "customer_id")
    .withColumn("name", F.concat(F.lit("customer_"), F.col("customer_id").cast("string")))
    .withColumn("region", regions[(F.col("customer_id") % 4).cast("int")])
    .withColumn("_ingested_at", F.current_timestamp())
)

# COMMAND ----------

if should_fail:
    raise Exception("failing on purpose")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to bronze

# COMMAND ----------

batch.write.mode("overwrite").saveAsTable("bronze_customers")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check what landed

# COMMAND ----------

rows = spark.table("bronze_customers").count()
print(f"bronze_customers now has {rows} rows")
display(spark.table("bronze_customers").orderBy("customer_id").limit(10))
