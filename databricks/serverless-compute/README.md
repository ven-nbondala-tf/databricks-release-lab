# Serverless compute

Two tests of the built-in serverless compute objects, run on a Databricks Free Edition workspace.

| Folder | What it tests | Result |
| --- | --- | --- |
| `access-control/` | Removing the `users` group from Default Automated Compute so a service principal cannot start jobs, and giving that service principal its own compute object. | The restriction works after a few minutes. Databricks SQL is not covered. |
| `rate-limits/` | Serverless rate limits, which cap how far executors can autoscale. The same workload on a Small, a 2X-Large and the default compute. | No difference in run time. The setting that enables the feature was not found in this workspace. |

Each folder has its own README with the steps to reproduce it and the results.
