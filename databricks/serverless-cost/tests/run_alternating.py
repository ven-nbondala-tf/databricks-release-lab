"""Run both bundle jobs alternately and record timings. Usage: run_alternating.py <dev_job_id> <prod_job_id> <pairs>"""
import json, subprocess, sys, time

def api(method, path, body=None):
    cmd = ["databricks", "api", method, path]
    if body: cmd += ["--json", json.dumps(body)]
    return json.loads(subprocess.check_output(cmd))

dev, prod, pairs = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = []
for i in range(pairs):
    for mode, job in (("PERFORMANCE_OPTIMIZED", dev), ("STANDARD", prod)):
        rid = api("post", "/api/2.2/jobs/run-now", {"job_id": int(job)})["run_id"]
        while True:
            time.sleep(15)
            r = api("get", f"/api/2.2/jobs/runs/get?run_id={rid}")
            if r["state"]["life_cycle_state"] in ("TERMINATED", "INTERNAL_ERROR", "SKIPPED"):
                break
        row = {"mode": mode, "job_id": job, "run_id": rid,
               "start_time": r["start_time"], "end_time": r["end_time"],
               "result": r["state"].get("result_state"),
               "queue_ms": r.get("queue_duration"), "setup_ms": r.get("setup_duration"),
               "execution_ms": r.get("execution_duration"), "cleanup_ms": r.get("cleanup_duration"),
               "run_ms": r.get("run_duration")}
        out.append(row)
        json.dump(out, open("tests/runs.json", "w"), indent=1)
        print(row, flush=True)
