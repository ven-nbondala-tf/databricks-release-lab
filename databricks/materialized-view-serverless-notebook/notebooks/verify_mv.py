# Databricks notebook source
# Checks both materialized views. Fails the task if either one has no rows.

import json

dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
base = f"{dbutils.widgets.get('catalog')}.{dbutils.widgets.get('schema')}"
views = [f"{base}.daily_revenue_sql", f"{base}.daily_revenue_py"]

# COMMAND ----------

report = {}
for view in views:
    info = json.loads(spark.sql(f"DESCRIBE TABLE EXTENDED {view} AS JSON").collect()[0][0])
    refresh = info.get("refresh_information", {})
    report[view] = {
        "rows": spark.table(view).count(),
        "columns": spark.table(view).columns,
        "owner": info.get("owner"),
        "type": info.get("type"),
        "pipeline_id": info.get("table_properties", {}).get("pipelines.pipelineId"),
        "refresh_schedule": refresh.get("refresh_schedule"),
        "last_refresh_type": refresh.get("last_refresh_type"),
        "latest_refresh_status": refresh.get("latest_refresh_status"),
    }
    print(view)
    print(json.dumps(report[view], indent=2))

empty = [v for v, r in report.items() if r["rows"] == 0]
if empty:
    raise Exception(f"No rows in: {', '.join(empty)}")

dbutils.notebook.exit(json.dumps(report))
