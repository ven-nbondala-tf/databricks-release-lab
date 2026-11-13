# Test results

This file only covers creating the materialized view. Streaming tables, refresh timings and the event log analysis are in `../../mv-refresh-deep-dive/tests/results.md`.

Everything ran in a Databricks Free Edition workspace with serverless compute only, Databricks CLI 1.24.0, bundle deployed with the direct engine.

## Part A: first round, view over a streaming table (2026-11-13)

These were measured before the scope change, on views built on a streaming table that read order files from a volume. The create statements and the decorator are the same as the ones in `notebooks/`, only the source differs. They are kept because they are the results about creating the view itself.

### Environment

| How the notebook ran | Runtime reported | PySpark | `pyspark.pipelines` |
| --- | --- | --- | --- |
| Saved job created by the bundle, no environment set | `client.6.5` | 4.3.0.dev0 | available |
| One-time run from `jobs submit`, no environment set | `client.2.5` | 3.5.0 | missing |
| One-time run, environment version 2 | `client.2.5` | 3.5.0 | missing |
| One-time run, environment version 5 | `client.5.12` | 4.1.0 | available |
| One-time run, environment version 6 | `client.6.5` | 4.3.0.dev0 | available |
| One-time run, environment version 4 | failed, see the errors below | | |

The server reports Spark 4.2.0 in every case. The SQL version works in the older environment too, because `spark.sql()` runs the statement on the server. Only the Python decorator needs the newer client library.

### Creation and rerun

| Test | SQL (`spark.sql()`) | Python (`@dp.materialized_view`) |
| --- | --- | --- |
| First creation | Materialized view update 7.6 s, 8 rows, planned as a complete recompute because it was the first computation. Job 50.9 s. | Update 7.4 s, 8 rows, complete recompute. Job 42.8 s. |
| Rerun the whole notebook, nothing changed | Update 6.3 s, planned as `NO_OP`. The object id stayed the same, so nothing was recreated. Job 31.7 s. | Update 4.4 s, `NO_OP`, same object id. Job 28.6 s. |
| Add a column to the definition and rerun | Same object id, new column, recomputed in full (`last_refresh_type` was `RECOMPUTED`). Job 39.3 s. | Same object id, new column, complete recompute. Job 32.1 s on environment 6. |

### Errors

Exact messages.

The Python decorator in the default one-time environment:

```
ImportError: cannot import name 'pipelines' from 'pyspark' (/databricks/python/lib/python3.11/site-packages/pyspark/__init__.py)
```

The Python version on environment 5 with an Auto Loader read, which the first version of the notebook had and the new one does not:

```
[CLOUDFILES_SCHEMA_LOCATION_REQUIRED] Could not find required option: schemaLocation. Provide a schema location using `cloudFiles.schemaLocation` for storing the inferred schema and supporting schema evolution. SQLSTATE: 42601
```

The same notebook worked on environment 6. The fix for the import error was environment version 6 (version 5 also imports the module).

Refreshing a view created in a serverless notebook from a SQL task on a warehouse, in a job that failed after 13 seconds:

```
INVALID_PARAMETER_VALUE: This table was created in serverless generic compute and cannot be refreshed from a DBSQL warehouse. Refresh it through a serverless generic compute like serverless notebooks or jobs.
```

Screenshot: `../../mv-refresh-deep-dive/tests/screenshots/warehouse-refresh-error.png`.

### Where the behavior differed from the docs

- **SQL task.** The docs say to use a SQL task to orchestrate materialized views with a job. That does not work for views created in a serverless notebook. They need a notebook task.
- **Python environment.** The docs say the decorators need serverless environment version 5 or above. They do not say that a one-time run defaults to an older environment that cannot import them, while a saved job from the bundle defaults to a newer one.
- **Status label.** The docs pages I read show no GA, Public Preview or Beta label for creating standalone objects from a notebook. I could not confirm a release status.

## Part B: workflow tests (2026-11-13)

Workflow `materialized-view`, environment `prod`, CLI 1.24.0, bundle target `prod`. The views are now built on `release_lab.jct_demo.bronze_orders` (500 orders, 30 days). There is no region column in that table, so the views give daily revenue and the order count only. Times are from the job run, which includes starting serverless compute. The workflow job time adds installing the CLI, validate and deploy.

| Test | What I did | Result |
| --- | --- | --- |
| 0. Merge of the branch | The merge to `main` changed this folder, so the push trigger ran by itself, before I dropped anything. | Succeeded. The views from the earlier round were replaced in place: creation time unchanged, `RECOMPUTED`, the old region column gone. Workflow 1m 55s. |
| 1. Create from scratch | Dropped both views, then started the workflow by hand (run 43506855362). | Succeeded. Job 40.5 s: `create_mv_python` 29.9 s, `create_mv_sql` 30.9 s, `verify_mv` 8.7 s. Both views were new objects (new table id and pipeline id), 30 rows each, columns `order_date`, `revenue`, `orders`. `last_refresh_type` `RECOMPUTED`. Workflow job 55 s. |
| 2. Run again, no changes | Started the workflow by hand again (run 43508282364). | Succeeded. Job 33.0 s: 23.1 s, 23.1 s, 8.9 s. Both views kept the same table id, pipeline id and creation time. `last_refresh_type` changed to `NO OPERATION`. So the views are refreshed and not recreated. Workflow job 49 s. |
| 3. Add a column to the SQL view | Added `MAX(amount) AS largest_order` to `create_mv_sql.py` and pushed to `main` (commit 87f7ce1). The push trigger ran (run 43508796534). | Succeeded. Job 33.3 s: 20.4 s, 22.3 s, 10.1 s. The SQL view kept its id, gained `largest_order` and was recomputed (`RECOMPUTED`, 30 rows). The Python view was untouched (`NO OPERATION`). Latest day in the SQL view: 20 orders, revenue 1887.47, largest order 200.06. Workflow job 58 s, 1m 47s in total. |

`verify_mv` printed the same fields every time: rows, columns, owner, type `MANAGED`, pipeline id, refresh schedule `MANUAL`, last refresh type and latest refresh status `Succeeded`. The owner was the identity behind the token in the `prod` environment.

The job pinned serverless environment version 6 on the job, and the notebook tasks accepted `environment_key`. The Python task imported `pyspark.pipelines` and succeeded in all four runs.

Screenshots in `screenshots/`: `workflow-run.png` (run 3), `job-run-graph.png` (the job run of test 3), `view-details.png` (Catalog Explorer details of the SQL view) and `views-owner.png` (both views with their owner).

### Where the behavior differed from what I expected

- **The merge ran the workflow.** I had planned to start test 1 by hand, but the push trigger fired on the merge itself, because the merge touched this folder. It deployed to `prod` before I dropped the views.
- **The `prod` environment waited for approval.** It had no required reviewer when the genie-code workflow was tested, and it had one by this round. Every run, including the push-triggered one in test 3, waited for the reviewer to approve before the deploy step started.
- **Compute type.** `DESCRIBE TABLE EXTENDED ... AS JSON` has no field for it. Catalog Explorer shows it on the Details tab as "Creation compute type: Serverless Generic Compute".
- **Created by, not owner, on the Details tab.** The Details tab shows "Created by". The owner column is on the schema page, and `DESCRIBE` has an `owner` field. All three showed the same identity.
- **The no-change rerun is cheap.** Running the notebooks again did not recreate anything, and the Python view stayed a no-operation even when the SQL view changed.

## Part C: environment version 5 check (2026-11-13)

Question: does `create_mv_python` work on serverless environment version 5, the documented minimum?

I submitted a one-time run with the same three tasks, the same notebooks from the deployed bundle and the same parameters, with the environment set to version 5 instead of 6. It was a one-time run, not a workflow run, and the saved job in the bundle was not changed, so there was nothing to restore. It still pins version 6.

| Task | Result | Time |
| --- | --- | --- |
| `create_mv_sql` | Succeeded | 53.2 s |
| `create_mv_python` | Succeeded | 53.2 s |
| `verify_mv` | Succeeded | 9.6 s |

The whole run took 63.5 s. Both views kept their ids and were refreshed as a no-operation, and the SQL view kept its `largest_order` column. So version 5 works for the view as defined here. The earlier failure on version 5 in the first round was the Auto Loader read in a streaming table, which this notebook no longer has.

## Part D: expectations in the docs (2026-11-13)

The "Use Python with standalone pipelines" page, dated 2026-11-11 and updated on 2026-11-12, lists expectations as unsupported for tables defined with the decorators. Under Unsupported APIs: "Expectations, such as `@dp.expect` and `@dp.expect_or_fail`". Under Limitations: "Expectations, additional flows, change data capture (CDC) flows, sinks, and temporary views are not supported." The page says nothing about expectations for the `spark.sql()` path. The November 2026 release notes page has the entry "Standalone pipelines on serverless general compute are now generally available" dated November 11, 2026, and I did not find the line "Standalone pipeline materialized views support expectations" on it.
