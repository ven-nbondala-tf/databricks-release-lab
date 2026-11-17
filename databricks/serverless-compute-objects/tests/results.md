# Test results

Run on November 17, 2026 with Databricks CLI 1.24.0 and the direct deployment engine. The job is `serverless_objects_demo` from this folder. Before every run the job's `serverless_compute.policy_id` was read back from the Jobs API and compared with the object being tested.

## Objects

| Name | Size | ID |
| --- | --- | --- |
| Default Automated Compute | Default | `66c36de7-c991-3857-8248-d289a92730c1` |
| `serverless_small` | Small | `b58b3a27-6146-4c62-b122-1802a6ff78fa` |
| `serverless_medium` | Medium | `975bd5be-4a4f-4e56-ab51-5a682a90d1be` |
| `serverless_large` | Large | `66b9608c-043f-4740-b8a3-a29d904d5041` |
| `serverless_xlarge` | X-Large | `bcfbcc3c-fb8b-48ef-8f4d-9fac5f1561b1` |
| `serverless_2xlarge` | 2X-Large | `70e7ee45-df34-40f9-85ce-1afe5e4f8a46` |

## Run times

3 billion rows, 12,000 partitions. The six computes were run in turn, then once more in the same order, with nothing else running.

| Compute | Run 1 | Run 2 | Execution (run 1, run 2) |
| --- | --- | --- | --- |
| Default Automated Compute | 100 s | 85 s | 96 s, 82 s |
| `serverless_small` | 85 s | 84 s | 82 s, 81 s |
| `serverless_medium` | 86 s | 85 s | 83 s, 81 s |
| `serverless_large` | 85 s | 85 s | 82 s, 82 s |
| `serverless_xlarge` | 86 s | 84 s | 82 s, 81 s |
| `serverless_2xlarge` | 85 s | 84 s | 82 s, 81 s |

Run IDs: 117537509803166, 1122114748202329, 55775752580577, 103990228681410, 430078633615789, 946764141949496 (run 1) and 591171405696319, 557353743118759, 484684747004306, 227569007417951, 224215265422759, 1124744628457940 (run 2), in the order of the table.

Earlier runs on `serverless_small` and `serverless_2xlarge` at 300M rows (18 to 20 s each, three runs per size) and at 3B rows (88 s and 87 s) agree with these.

## Permissions

| Object | Permissions read back |
| --- | --- |
| Default Automated Compute | `users` Can Use (direct), `admins` Can Manage (inherited) |
| A new custom object | the creator Can Manage (direct), `admins` Can Manage (inherited) |

## Not covered

- Tags on an object. The tag keys in the create dialog are governed tags, and none was set.
- Interactive objects, Databricks Connect and Lakeflow pipelines.
- Whether the size cap is enforced. The run times were the same on every size.
