#!/usr/bin/env python3
"""Test 10: edge cases from the documentation. Empty scopes array, all-apis:read for PATs, and the authentication scope."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import HOST, call, create_token, load_tokens  # noqa: E402


def mask(t):
    return re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<id>", str(t).replace(HOST, "<workspace-url>"))


for name, scopes in (("x_all_apis_read", ["all-apis:read"]), ("x_empty", []), ("x_auth", ["authentication"]), ("x_unknown", ["not-a-scope"])):
    st, r = create_token(name, scopes)
    info = r.get("token_info", {})
    print(f"create PAT scopes={scopes}: HTTP {st}", mask(r.get("message", "")) or f"returned scopes={info.get('scopes')} autoscope={info.get('autoscope_state')}")

t = load_tokens().get("x_empty")
if t:
    st, b = call("/api/2.1/jobs/list?limit=1", token=t["value"])
    print(f"token with empty scopes: GET jobs/list HTTP {st}")
a = load_tokens().get("x_auth")
if a:
    st, b = call("/api/2.1/jobs/list?limit=1", token=a["value"])
    print(f"token with only authentication: GET jobs/list HTTP {st} {mask(b.get('message',''))}")
    st, r = call("/api/2.0/token/create", {"lifetime_seconds": 600, "comment": "token-scopes test: made by x_auth", "scopes": []}, a["value"])
    print(f"token with only authentication creates a token with empty scopes (full access): HTTP {st}")
    if st == 200:
        tk = load_tokens()
        tk["x_auth_child"] = {"value": r["token_value"], "token_id": r["token_info"]["token_id"], "scopes": []}
        from _api import save_tokens
        save_tokens(tk)
        st2, _ = call("/api/2.1/jobs/list?limit=1", token=r["token_value"])
        print(f"   the new token: GET jobs/list HTTP {st2}")
