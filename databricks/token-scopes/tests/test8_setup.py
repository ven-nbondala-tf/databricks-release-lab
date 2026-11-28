#!/usr/bin/env python3
"""Create the test service principal for test 8 and save its IDs in tests/.sp.json (ignored by git).

cleanup.py deletes the service principal again.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _api import call, write_private  # noqa: E402

st, r = call("/api/2.0/preview/scim/v2/ServicePrincipals", {
    "displayName": "token-scopes-test-sp", "active": True,
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServicePrincipal"]})
if st not in (200, 201):
    sys.exit(f"could not create the service principal: HTTP {st} {r.get('message', '')}")
write_private(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sp.json"), {"id": r["id"], "app": r["applicationId"]})
print("created the test service principal, IDs saved in tests/.sp.json")
