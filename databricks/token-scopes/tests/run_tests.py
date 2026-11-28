#!/usr/bin/env python3
"""Run the token scope tests 1 to 6 and print what each scoped token can and cannot do.

Needs DATABRICKS_HOST and DATABRICKS_TOKEN (a token that can create tokens), WAREHOUSE_ID and CATALOG in the environment.
Test tokens last one hour and are stored in tests/.tokens.json (gitignored). Token values are never printed.
Run cleanup.py when you are done to revoke them.

    python tests/run_tests.py > tests/output.txt
"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import ADMIN, HOST, call, create_token, load_tokens  # noqa: E402

WH = os.environ["WAREHOUSE_ID"]
CATALOG = os.environ.get("CATALOG", "main")
SCHEMA = f"{CATALOG}.token_scopes_test"


def mask(text):
    text = str(text)
    text = text.replace(HOST, "<workspace-url>").replace(WH, "<warehouse-id>").replace(CATALOG, "<catalog>")
    text = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<id>", text)
    return re.sub(r"\b(dapi|dose)[0-9a-f]{20,}", "<token>", text)


def show(label, st, body):
    msg = body.get("message") or body.get("error_code") or ""
    if isinstance(body, dict) and body.get("status", {}).get("state"):
        s = body["status"]
        msg = s["state"] + (": " + s.get("error", {}).get("message", "") if s.get("error") else "")
    print(f"  {label:48} HTTP {st}  {mask(msg)[:330]}")


def sql(token, statement):
    st, b = call("/api/2.0/sql/statements", {"statement": statement, "warehouse_id": WH, "wait_timeout": "30s"}, token)
    return st, b


def run_sql(label, token, statement):
    show(label, *sql(token, statement))


def tok(name):
    return load_tokens()[name]["value"]


# Setup with your own token: a schema and two tables to work on
for s in (f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}", f"CREATE OR REPLACE TABLE {SCHEMA}.t (id INT, note STRING)",
          f"INSERT INTO {SCHEMA}.t VALUES (1, 'seed')", f"CREATE OR REPLACE TABLE {SCHEMA}.t_to_drop (id INT)"):
    sql(ADMIN, s)

TESTS = {
    "t1": ["sql:restricted-query"], "t2": ["sql:read:restricted-query"], "t3": ["sql"],
    "t4": ["jobs:read"], "t4b": ["clusters:read"], "t5": ["unity-catalog:read"], "t6": ["sql"],
}
for name, scopes in TESTS.items():
    st, r = create_token(name, scopes)
    info = r.get("token_info", {})
    print(f"created {name}: HTTP {st} scopes={info.get('scopes', r.get('message'))} autoscope={info.get('autoscope_state')}")

print("\nTest 1: sql:restricted-query")
t = tok("t1")
run_sql("SELECT 1", t, "SELECT 1 AS one")
run_sql("SELECT from table", t, f"SELECT * FROM {SCHEMA}.t")
run_sql("DESCRIBE TABLE", t, f"DESCRIBE TABLE {SCHEMA}.t")
run_sql("INSERT", t, f"INSERT INTO {SCHEMA}.t VALUES (2, 'from t1')")
run_sql("CREATE TABLE", t, f"CREATE TABLE {SCHEMA}.t1_new (id INT)")
run_sql("DROP TABLE", t, f"DROP TABLE {SCHEMA}.t_to_drop")
show("list SQL warehouses", *call("/api/2.0/sql/warehouses", token=t))

print("\nTest 2: sql:read:restricted-query")
t = tok("t2")
show("list SQL warehouses", *call("/api/2.0/sql/warehouses", token=t))
run_sql("SELECT from table", t, f"SELECT * FROM {SCHEMA}.t")
run_sql("INSERT", t, f"INSERT INTO {SCHEMA}.t VALUES (3, 'from t2')")

print("\nTest 3: sql (plain, for comparison)")
t = tok("t3")
run_sql("SELECT from table", t, f"SELECT * FROM {SCHEMA}.t")
run_sql("INSERT", t, f"INSERT INTO {SCHEMA}.t VALUES (4, 'from t3')")
run_sql("CREATE TABLE", t, f"CREATE TABLE {SCHEMA}.t3_new (id INT)")
run_sql("DROP TABLE", t, f"DROP TABLE {SCHEMA}.t_to_drop")
show("list SQL warehouses", *call("/api/2.0/sql/warehouses", token=t))

print("\nTest 4: jobs:read")
t = tok("t4")
show("GET jobs/list", *call("/api/2.1/jobs/list?limit=1", token=t))
show("POST jobs/create", *call("/api/2.1/jobs/create", {"name": "token-scopes-test-should-not-exist", "tasks": []}, t))
show("POST jobs/delete (job 1)", *call("/api/2.1/jobs/delete", {"job_id": 1}, t))
print("Test 4b: clusters:read")
t = tok("t4b")
show("GET clusters/list", *call("/api/2.1/clusters/list", token=t))
show("POST clusters/delete (fake id)", *call("/api/2.1/clusters/delete", {"cluster_id": "0000-000000-fake0000"}, t))

print("\nTest 5: unity-catalog:read")
t = tok("t5")
show("GET catalogs", *call("/api/2.1/unity-catalog/catalogs", token=t))
show("POST schemas", *call("/api/2.1/unity-catalog/schemas", {"name": "token_scopes_should_fail", "catalog_name": CATALOG}, t))

print("\nTest 6: missing scope (sql-only token calls the Jobs API)")
t = tok("t6")
show("GET jobs/list", *call("/api/2.1/jobs/list?limit=1", token=t))
show("GET clusters/list", *call("/api/2.1/clusters/list", token=t))

print("\nTable rows after the tests:")
st, b = sql(ADMIN, f"SELECT id, note FROM {SCHEMA}.t ORDER BY id")
print("  ", b.get("result", {}).get("data_array"))
