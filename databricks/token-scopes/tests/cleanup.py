#!/usr/bin/env python3
"""Revoke every test token, delete the test service principal and drop the test schema.

Tokens are found two ways: the ids saved in tests/.tokens.json and every token whose comment starts with
"token-scopes" or "reporting tool, read only" (the token made in the UI). Needs DATABRICKS_HOST, DATABRICKS_TOKEN, WAREHOUSE_ID and CATALOG in the environment.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import TOKENS_FILE, call, load_tokens  # noqa: E402

PREFIXES = ("token-scopes", "reporting tool, read only")  # the second is the token made in the UI for the screenshots


def is_test_token(t):
    return (t.get("comment") or "").startswith(PREFIXES)


ids = {v["token_id"] for v in load_tokens().values()}
st, r = call("/api/2.0/token/list")
for t in r.get("token_infos", []):
    if is_test_token(t):
        ids.add(t["token_id"])
revoked = failed = 0
for i in sorted(ids):
    st, b = call("/api/2.0/token/delete", {"token_id": i})
    if st == 200:
        revoked += 1
    else:
        failed += 1
        print("could not revoke one token (usually already expired):", st)
print(f"revoked {revoked} test tokens, {failed} failed")
st, r = call("/api/2.0/token/list")
left = [t for t in r.get("token_infos", []) if is_test_token(t)]
print("test tokens still listed:", len(left))

sp_file = os.path.join(os.path.dirname(TOKENS_FILE), ".sp.json")
if os.path.exists(sp_file):
    sp = json.load(open(sp_file))
    st, b = call(f"/api/2.0/preview/scim/v2/ServicePrincipals/{sp['id']}", method="DELETE")
    print("delete test service principal (its secrets go with it): HTTP", st)
    os.remove(sp_file)
call("/api/2.0/sql/statements", {"statement": f"DROP SCHEMA IF EXISTS {os.environ.get('CATALOG', 'main')}.token_scopes_test CASCADE",
                                 "warehouse_id": os.environ["WAREHOUSE_ID"], "wait_timeout": "30s"})
print("dropped the test schema")
if os.path.exists(TOKENS_FILE):
    os.remove(TOKENS_FILE)
    print("removed the local token file")
