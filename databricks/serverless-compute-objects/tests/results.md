# Test results

Everything ran on a Databricks Free Edition workspace on November 17, 2026, with Databricks CLI 1.24.0 and the direct deployment engine. The job is `serverless_objects_demo` from this folder. Before every run the job's `serverless_compute.policy_id` was read back from the Jobs API and compared with the object being tested.

## Objects created

| Name | Size | How |
| --- | --- | --- |
| `serverless_small` | Small | Create serverless compute in the UI |
| `serverless_2xlarge` | 2X-Large | Create serverless compute in the UI |

`serverless_small` was first created under another name and renamed from its Edit page. The ID did not change.

## Run times

| Workload | Compute | Run time | Execution |
| --- | --- | --- | --- |
| 300M rows, 1,200 partitions | `serverless_small`, three runs | 18, 20, 19 s | 15, 16, 15 s |
| 300M rows, 1,200 partitions | `serverless_2xlarge`, three runs | 18, 18, 18 s | 15, 15, 15 s |
| 3B rows, 12,000 partitions | `serverless_small` | 88 s | 85 s |
| 3B rows, 12,000 partitions | `serverless_2xlarge` | 87 s | 84 s |
| 3B rows, 12,000 partitions | Default Automated Compute | 87 s | 84 s |

The three runs on each size at 300M rows were alternated and run with nothing else running.

## Runs left out

- The first run on `serverless_small` took 35 s, against 18 to 20 s for every later run. It was the first run on a new object, so it is treated as a cold start.
- An earlier batch of 300M row runs included one run of 23 s on `serverless_2xlarge` that overlapped with another job running at the same time. The runs above were repeated without any overlap.

## Pointing a job at an object

| Method | Result |
| --- | --- |
| Bundle, `serverless_compute.policy_id` on a job cluster | Worked. The job read back the object's ID, and ran on it. |
| Jobs UI, Configure compute policy, then Update Configuration and Save task | Worked on a job created by hand. The job read back the object's ID, and the run succeeded in 24 s. |
| Jobs UI on a job deployed by a bundle | The task form is read only, with the banner "This task was deployed as part of a bundle, avoid editing this copy, instead edit the source and redeploy the bundle." |

The UI dropdown listed Default Automated Compute, `serverless_2xlarge` and `serverless_small`, and no interactive object.

## Permissions

| Object | Permissions read back |
| --- | --- |
| Default Automated Compute | `users` Can Use (direct), `admins` Can Manage (inherited) |
| `serverless_small` | the creator Can Manage (direct), `admins` Can Manage (inherited) |
| `serverless_2xlarge` | the creator Can Manage (direct), `admins` Can Manage (inherited) |

## Not covered

- Tags on an object. The tag key list in the create dialog is made of governed tags such as `class.*` and `ai.*`, and none was set.
- Sizes other than Small and 2X-Large.
- Interactive access and Databricks Connect, and Lakeflow pipelines.
- Whether the size is enforced. The workspace has no Previews page and no rate limit setting, and the run times were the same on every size.
