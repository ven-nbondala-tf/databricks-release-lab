"""Run one SQL statement on the serverless warehouse and print rows as tab-separated text. Set WAREHOUSE_ID first. Usage: sql.py "<statement>" """
import json, subprocess, sys, time
import os
WH = os.environ["WAREHOUSE_ID"]
def api(method, path, body=None):
    cmd = ["databricks", "api", method, path]
    if body: cmd += ["--json", json.dumps(body)]
    return json.loads(subprocess.check_output(cmd, stderr=subprocess.DEVNULL))
r = api("post", "/api/2.0/sql/statements", {"warehouse_id": WH, "statement": sys.argv[1], "wait_timeout": "50s"})
while r["status"]["state"] in ("PENDING", "RUNNING"):
    time.sleep(3); r = api("get", "/api/2.0/sql/statements/" + r["statement_id"])
if r["status"]["state"] != "SUCCEEDED":
    print(r["status"]); sys.exit(1)
cols = r.get("manifest", {}).get("schema", {}).get("columns")
if not cols:
    print("OK"); sys.exit(0)
print("\t".join(c["name"] for c in cols))
for row in r.get("result", {}).get("data_array", []): print("\t".join("" if v is None else str(v) for v in row))
