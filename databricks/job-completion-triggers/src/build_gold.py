# Databricks notebook source
# MAGIC %md
# MAGIC # Build gold revenue
# MAGIC Runs on its own once both ingest jobs have finished. Joins the two bronze tables into `gold_revenue_by_region`.

# COMMAND ----------

import json

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "jct_demo")
dbutils.widgets.text("upstream_completions", "[]")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
completed = json.loads(dbutils.widgets.get("upstream_completions"))

spark.sql(f"USE {catalog}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## What triggered this run
# MAGIC The trigger hands over the upstream runs that finished. Empty means someone started it by hand.

# COMMAND ----------

if not completed:
    print("no upstream info, this looks like a manual run")

for job in completed:
    print(job["job_id"], job["run_id"], job["termination_code"], job["completion_time"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Join and aggregate

# COMMAND ----------

from pyspark.sql import functions as F

orders = spark.table("bronze_orders")
customers = spark.table("bronze_customers")

gold = (
    orders.join(customers, "customer_id")
    .groupBy("region")
    .agg(
        F.count("order_id").alias("orders"),
        F.round(F.sum("amount"), 2).alias("revenue"),
        F.round(F.avg("amount"), 2).alias("avg_order"),
    )
    .withColumn("_built_at", F.current_timestamp())
)

gold.write.mode("overwrite").saveAsTable("gold_revenue_by_region")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Result

# COMMAND ----------

display(spark.table("gold_revenue_by_region").orderBy(F.desc("revenue")))
