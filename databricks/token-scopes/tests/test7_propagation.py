#!/usr/bin/env python3
"""Test 7: change a token's scopes with PATCH and measure how long the change takes to apply.

The token starts with sql:read, so the Jobs API is refused and the warehouse list works. After the PATCH it has
jobs:read only. The script polls both calls every 5 seconds and prints the time at which each one flips.
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import call, create_token, load_tokens  # noqa: E402

st, r = create_token("t7", ["sql:read"])
print("created t7 scopes sql:read:", st)
t = load_tokens()["t7"]
token, token_id = t["value"], t["token_id"]
print("before: jobs/list", call("/api/2.1/jobs/list?limit=1", token=token)[0], " sql/warehouses", call("/api/2.0/sql/warehouses", token=token)[0])

start = time.time()
st, r = call(f"/api/2.0/token/{token_id}", {"token": {"scopes": ["jobs:read"]}, "update_mask": "scopes"}, method="PATCH")
print(f"PATCH to jobs:read: HTTP {st}", "scopes now:", r.get("token", r).get("scopes") if isinstance(r, dict) else r)
jobs_ok = sql_blocked = None
while time.time() - start < 15 * 60 and not (jobs_ok and sql_blocked):
    j = call("/api/2.1/jobs/list?limit=1", token=token)[0]
    w = call("/api/2.0/sql/warehouses", token=token)[0]
    el = round(time.time() - start)
    if jobs_ok is None and j == 200:
        jobs_ok = el
        print(f"  jobs/list works after {el} s")
    if sql_blocked is None and w == 403:
        sql_blocked = el
        print(f"  sql/warehouses refused after {el} s")
    time.sleep(5)
print("jobs allowed after (s):", jobs_ok, " warehouses refused after (s):", sql_blocked)
