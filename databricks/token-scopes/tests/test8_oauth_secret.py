#!/usr/bin/env python3
"""Test 8: a service principal OAuth secret limited to sql:restricted-query, then token requests with matching and wider scopes.

Needs the service principal created in tests/.sp.json. Secrets and access tokens are never printed.
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import HOST, call  # noqa: E402

sp = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sp.json")))
SCOPE = ["sql:restricted-query"]


def mask(t):
    return re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<id>", str(t).replace(HOST, "<workspace-url>"))


# Give the service principal what it needs to query: SQL access, CAN USE on the warehouse and SELECT on the test table
WH = os.environ["WAREHOUSE_ID"]
CATALOG = os.environ.get("CATALOG", "main")
call(f"/api/2.0/preview/scim/v2/ServicePrincipals/{sp['id']}", {"schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"], "Operations": [
    {"op": "add", "path": "entitlements", "value": [{"value": "databricks-sql-access"}, {"value": "workspace-access"}]}]}, method="PATCH")
call(f"/api/2.0/permissions/warehouses/{WH}", {"access_control_list": [{"service_principal_name": sp["app"], "permission_level": "CAN_USE"}]}, method="PATCH")
for g in (f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{sp['app']}`", f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.token_scopes_test TO `{sp['app']}`",
          f"GRANT SELECT ON TABLE {CATALOG}.token_scopes_test.t TO `{sp['app']}`"):
    call("/api/2.0/sql/statements", {"statement": g, "warehouse_id": WH, "wait_timeout": "30s"})

st, r = call(f"/api/2.0/accounts/servicePrincipals/{sp['id']}/credentials/secrets", {"lifetime": "3600s", "scopes": SCOPE})
print("create secret with scopes", SCOPE, "-> HTTP", st, {k: v for k, v in r.items() if k not in ("secret", "secret_hash", "id")})
if st != 200:
    sys.exit(0)
secret = r["secret"]
basic = base64.b64encode(f"{sp['app']}:{secret}".encode()).decode()


def token_request(scope):
    data = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": scope}).encode()
    req = urllib.request.Request(HOST + "/oidc/v1/token", data=data, headers={"Authorization": "Basic " + basic})
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


for scope in ("sql:restricted-query", "sql", "all-apis", "sql:restricted-query jobs:read"):
    st, body = token_request(scope)
    shown = {k: v for k, v in body.items() if k not in ("access_token", "refresh_token")}
    print(f"token request scope={scope!r}: HTTP {st}", mask(shown))
    if st == 200:
        tok = body["access_token"]
        w = call("/api/2.0/sql/warehouses", token=tok)[0]
        j = call("/api/2.1/jobs/list?limit=1", token=tok)[0]
        s = call("/api/2.0/sql/statements", {"statement": f"SELECT * FROM {CATALOG}.token_scopes_test.t", "warehouse_id": WH, "wait_timeout": "30s"}, tok)
        print(f"   token granted scope: {body.get('scope')!r}; list warehouses HTTP {w}; list jobs HTTP {j}; SELECT {s[1].get('status', {}).get('state', s[1].get('message'))}")
