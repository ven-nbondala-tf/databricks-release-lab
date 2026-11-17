# Test results

All runs used the `rate_limit_workload` job from this folder on a Databricks Free Edition workspace, deployed with Databricks CLI 1.24.0 and the direct deployment engine. Each run was started by hand on November 17, 2026. Before every run the job's `serverless_compute.policy_id` was read back from the Jobs API and compared with the compute object being tested.

## Run times

| Workload | Compute | Run time | Execution time |
| --- | --- | --- | --- |
| 300M rows, 1,200 partitions | Small, three runs | 19, 18, 18 s | 16, 15, 14 s |
| 300M rows, 1,200 partitions | 2X-Large, three runs | 18, 19, 19 s | 14, 15, 16 s |
| 3B rows, 12,000 partitions | Small | 87 s | 84 s |
| 3B rows, 12,000 partitions | 2X-Large | 87 s | 83 s |
| 3B rows, 12,000 partitions | Default Automated Compute | 87 s | 84 s |

The three runs on each size at 300M rows were alternated (Small, 2X-Large, Small, and so on).

## Runs left out

- The first Small run took 33 seconds. It was the first run on a new compute object and every later run was faster, so it is treated as a cold start.
- One further Small run took 20 seconds, but a deploy hung afterwards and the compute it ran on was not verified.

## What the results show

Small, 2X-Large and the Default Automated Compute took the same time at both data sizes. Ten times the data took about 5.6 times as long to execute on all three, so the workload does use its parallelism, but no size changed it.

## What is not covered

- The docs say a workspace admin enables the Serverless Compute Rate Limit setting from the Previews page. This workspace has no Previews page and no rate-limit setting under Settings, then Compute, although the sizes are offered. It is not known whether the limit was enforced.
- Executor counts and DBUs are not visible on serverless here, and the billing records for these runs had not landed when checked, so no cost was measured.
- Medium, Large and X-Large were not run, and neither were Lakeflow pipelines.
- Each 3B row result is a single run.
