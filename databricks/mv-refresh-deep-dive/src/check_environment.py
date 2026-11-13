# Databricks notebook source
# Reports the runtime and whether the Python pipelines decorators are available

import json
import os

import pyspark

result = {
    "databricks_runtime_version": os.environ.get("DATABRICKS_RUNTIME_VERSION"),
    "pyspark_version": pyspark.__version__,
}
try:
    from pyspark import pipelines  # noqa: F401
    result["pyspark_pipelines"] = "available"
except ImportError as e:
    result["pyspark_pipelines"] = f"missing: {e}"

print(json.dumps(result))
dbutils.notebook.exit(json.dumps(result))
