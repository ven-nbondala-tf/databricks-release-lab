#!/usr/bin/env python3
"""Test 11: plain sql:read. Can it list warehouses (a GET) and run a query (a POST to the Statement Execution API)?"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import HOST, call, create_token, load_tokens  # noqa: E402

WH = os.environ["WAREHOUSE_ID"]


def mask(t):
    return re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<id>", str(t).replace(HOST, "<workspace-url>").replace(WH, "<warehouse-id>"))


st, r = create_token("t11", ["sql:read"])
tok = load_tokens()["t11"]["value"]
print("created t11 scopes sql:read: HTTP", st)
print("list SQL warehouses: HTTP", call("/api/2.0/sql/warehouses", token=tok)[0])
st, b = call("/api/2.0/sql/statements", {"statement": "SELECT 1", "warehouse_id": WH, "wait_timeout": "30s"}, tok)
print("SELECT 1 through the Statement Execution API: HTTP", st, mask(b.get("message") or b.get("status", {}).get("state")))
st, b = call("/api/2.0/sql/history/queries?max_results=1", token=tok)
print("GET query history: HTTP", st, mask(b.get("message", "")))
# Revoke the token right away
tid = load_tokens()["t11"]["token_id"]
print("revoke t11: HTTP", call("/api/2.0/token/delete", {"token_id": tid})[0])
os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tokens.json"))
