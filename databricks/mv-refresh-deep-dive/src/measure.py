# Databricks notebook source
# Reports row counts and the refresh history of one version's two objects

import json

dbutils.widgets.text("version", "sql")
dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")
version = dbutils.widgets.get("version")
base = f"{dbutils.widgets.get('catalog')}.{dbutils.widgets.get('schema')}"
st = f"{base}.orders_st_{'sql' if version == 'sql' else 'py'}"
mv = f"{base}.daily_revenue_{'sql' if version == 'sql' else 'py'}"

# COMMAND ----------

def history(name, limit=40):
    rows = spark.sql(f"""
        SELECT date_format(timestamp, 'HH:mm:ss.SSS') AS ts, event_type, message,
               CASE WHEN event_type = 'planning_information' THEN details ELSE substr(details, 1, 240) END AS details
        FROM event_log(TABLE({name}))
        WHERE event_type IN ('planning_information', 'update_progress', 'flow_progress')
        ORDER BY timestamp DESC LIMIT {limit}
    """).collect()
    return [r.asDict() for r in rows]

def detail(name):
    j = json.loads(spark.sql(f"DESCRIBE TABLE EXTENDED {name} AS JSON").collect()[0][0])
    props = j.get("table_properties", {})
    return {
        "id": props.get("io.unitycatalog.tableId"),
        "created_time": j.get("created_time"),
        "refresh_fields": {k: j[k] for k in j if "refresh" in k.lower() or "schedule" in k.lower()},
    }

report = {
    "streaming_table_detail": detail(st),
    "materialized_view_detail": detail(mv),
    "streaming_table_rows": spark.table(st).count(),
    "materialized_view_rows": spark.table(mv).count(),
    "materialized_view_revenue": spark.table(mv).agg({"revenue": "sum"}).collect()[0][0],
    "streaming_table_history": history(st),
    "materialized_view_history": history(mv),
}
print(json.dumps(report, indent=1, default=str))
dbutils.notebook.exit(json.dumps(report, default=str))
