# Databricks notebook source
# Writes one batch of order files into the landing volume

import json
import random
from datetime import date, timedelta

dbutils.widgets.text("batch", "1")
dbutils.widgets.text("rows", "200")
dbutils.widgets.text("catalog", "release_lab")
dbutils.widgets.text("schema", "mvst_demo")

batch = int(dbutils.widgets.get("batch"))
rows = int(dbutils.widgets.get("rows"))
landing = f"/Volumes/{dbutils.widgets.get('catalog')}/{dbutils.widgets.get('schema')}/landing"

# COMMAND ----------

random.seed(batch)
regions = ["north", "south", "east", "west"]
first_day = date(2026, 11, 1) + timedelta(days=batch - 1)

lines = []
for i in range(rows):
    # Most orders are for the batch's own day, the rest are late orders for the day before
    day = first_day if i % 4 else first_day - timedelta(days=1)
    lines.append(json.dumps({
        "order_id": batch * 100000 + i,
        "region": random.choice(regions),
        "amount": round(random.uniform(5, 500), 2),
        "order_ts": f"{day.isoformat()}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
    }))

path = f"{landing}/orders_batch_{batch:03d}.json"
with open(path, "w") as f:
    f.write("\n".join(lines))

print(f"Wrote {rows} orders to {path}")
dbutils.notebook.exit(json.dumps({"batch": batch, "rows": rows, "path": path}))
