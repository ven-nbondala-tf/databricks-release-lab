# Test results

Run on 2026-11-13 in a Databricks Free Edition workspace with serverless compute only. Databricks CLI 1.24.0, bundle deployed with the direct engine. Version A defines the objects with SQL through `spark.sql()`. Version B defines the same two objects with the Python pipelines decorators. Both read JSON order files from the same landing volume, 200 orders per batch, and both build a streaming table and a materialized view with daily revenue by region.

Timings are the update durations from each object's event log, from the INITIALIZING event to the COMPLETED event. The job time is the whole job run, which also includes starting serverless compute and running the notebook cells.

## Environment

| How the notebook ran | Runtime reported | PySpark | `pyspark.pipelines` |
| --- | --- | --- | --- |
| Saved job created by the bundle, no environment set | `client.6.5` | 4.3.0.dev0 | available |
| One-time run from `jobs submit`, no environment set | `client.2.5` | 3.5.0 | missing |
| One-time run, environment version 2 | `client.2.5` | 3.5.0 | missing |
| One-time run, environment version 5 | `client.5.12` | 4.1.0 | available |
| One-time run, environment version 6 | `client.6.5` | 4.3.0.dev0 | available |
| One-time run, environment version 4 | failed, see errors below | | |

The server reports Spark 4.2.0 in every case. The SQL version works in the older environment too, because `spark.sql()` runs the statement on the server. Only the Python decorators need the newer client library.

## Results

| Test | Version A (SQL) | Version B (Python) |
| --- | --- | --- |
| Initial create, batch 1, 200 orders | Job 50.9 s. Streaming table 18.2 s, 200 rows. Materialized view 7.6 s, 8 rows, planned as `COMPLETE_RECOMPUTE` with reason `FIRST_COMPUTATION`. | Job 42.8 s. Streaming table 10.4 s, 200 rows. Materialized view 7.4 s, 8 rows, `COMPLETE_RECOMPUTE`. |
| Add batch 2 and refresh | `REFRESH` statements, job 46.8 s. Streaming table 8.2 s, read only the new file (200 new rows, 400 total). Materialized view 20.2 s, `GROUP_AGGREGATE` (incremental), 12 rows. | Notebook rerun, job 37.8 s. Streaming table 6.7 s, only the new file (400 total). Materialized view 12.6 s, `GROUP_AGGREGATE`, 12 rows. |
| Rerun the whole notebook, nothing changed | Job 31.7 s. Streaming table 5.9 s. Materialized view 6.3 s, `NO_OP`. Same object ids as before, so nothing was recreated. | Job 28.6 s. Streaming table 4.6 s. Materialized view 4.4 s, `NO_OP`. Same object ids. |
| Add `MAX(amount)` to the materialized view and rerun | Job 39.3 s. Streaming table 5.1 s, untouched. Materialized view 7.3 s, `COMPLETE_RECOMPUTE`, `last_refresh_type` `RECOMPUTED`. Same object id, new column `max_amount`. | Job 32.1 s (environment 6). Streaming table 5.1 s. Materialized view 6.5 s, `COMPLETE_RECOMPUTE` with reason `QUERY_FINGERPRINT_CHANGED`. Same object id, new column. |
| Drop both objects from a warehouse and recreate | Job 39.0 s. Both objects have new ids. Streaming table 10.3 s and re-read both files in one update (400 rows). Materialized view 6.9 s, `FIRST_COMPUTATION`. | Job 38.0 s. New ids. Streaming table 10.1 s, 400 rows in one update. Materialized view 7.2 s, `FIRST_COMPUTATION`. |
| Add batch 3 and run the refresh job, first run | Job 37.6 s. Streaming table 6.4 s, 200 new rows (600 total). Materialized view 13.4 s, `GROUP_AGGREGATE`, 16 rows. | Job 37.0 s. Streaming table 6.6 s, 200 new rows. Materialized view 11.3 s, `GROUP_AGGREGATE`, 16 rows. |
| Same job, second run, nothing new | Job 27.7 s. Streaming table 5.2 s. Materialized view 3.9 s, `NO_OP`. | Job 27.8 s. Streaming table 4.7 s. Materialized view 3.7 s, `NO_OP`. |
| `REFRESH` statement on the objects | Works. | Fails, see errors below. |
| Refresh from a SQL task on a warehouse | Fails, see errors below. | Fails, same error. |

Both versions end with identical data after every step. Row counts: streaming table 200, 400, 600. Materialized view 8, 12, 16. Total revenue after batch 1 is 50,309.27 and after batch 2 is 100,471.87.

Version A has 16 lines of code in the notebook and Version B has 21, not counting comments and blank lines.

## Observations

- The streaming table only read new files. After batch 2 the update wrote 200 rows and reported 0 backlog files.
- The materialized view over the streaming table refreshed incrementally. The planning event for batch 2 shows 200 changed rows out of 400, and the technique `GROUP_AGGREGATE`.
- `CREATE OR REPLACE MATERIALIZED VIEW` with an unchanged definition did not recreate the view. It was planned as `NO_OP`.
- Changing the definition of the materialized view kept the same object and recomputed it in full. The streaming table was not touched, and did not re-read any files.
- Dropping and recreating a streaming table loses its checkpoint, so it re-reads every file in the volume. The landing volume was not affected.
- The refresh type is visible in three places: `DESCRIBE TABLE EXTENDED ... AS JSON` has `refresh_information.last_refresh_type` with the values `INCREMENTAL`, `RECOMPUTED` and `NO OPERATION`. The event log has a `planning_information` event with the technique. The pipeline page behind "See refresh details" has an Incrementalization column.
- Each streaming table and materialized view creates two extra managed tables in the same schema: `__materialization_mat_<pipeline id>_<name>_1` and `event_log_<pipeline id>`. Dropping the object removes the first and leaves the second behind, with its history. One of the orphaned event logs still held 61 events after the drop.
- A cell that runs `CREATE OR REFRESH STREAMING TABLE` waits for the update to finish. In the job run page the streaming table cell took 11.0 s and the materialized view cell 17.5 s.
- Dropping from a SQL warehouse works, even though refreshing from one does not.
- A rejected `REFRESH` on an object created with the decorators still starts an update that fails. The event log shows the update as FAILED and `DESCRIBE TABLE EXTENDED ... AS JSON` reports `latest_refresh_status` as `Failed`. The data was not changed (600 and 16 rows), and the status went back to `Succeeded` after the next successful run of the notebook.

## Errors

Exact messages.

Python decorators in the default one-time environment:

```
ImportError: cannot import name 'pipelines' from 'pyspark' (/databricks/python/lib/python3.11/site-packages/pyspark/__init__.py)
```

Python version on environment 5, with the Auto Loader options in `version_b_python.py`:

```
[CLOUDFILES_SCHEMA_LOCATION_REQUIRED] Could not find required option: schemaLocation. Provide a schema location using `cloudFiles.schemaLocation` for storing the inferred schema and supporting schema evolution. SQLSTATE: 42601
```

The same notebook worked on environment 6 without a schema location.

Refreshing an object created in a serverless notebook from a SQL task on a warehouse, and the same statement run directly on the warehouse:

```
INVALID_PARAMETER_VALUE: This table was created in serverless generic compute and cannot be refreshed from a DBSQL warehouse. Refresh it through a serverless generic compute like serverless notebooks or jobs.
```

`REFRESH` on objects created with the Python decorators:

```
IllegalArgumentException: Exactly one CREATE [ LIVE TABLE | MATERIALIZED VIEW | STREAMING TABLE ] statement expected, but 0 found. If the streaming table or materialized view is not created in SQL, REFRESH is currently not supported.
```

`DESCRIBE DETAIL` on a materialized view:

```
[EXPECT_TABLE_NOT_VIEW.NO_ALTERNATIVE] 'DESCRIBE DETAIL' expects a table but `release_lab`.`mvst_demo`.`daily_revenue_sql` is a view. SQLSTATE: 42809
```

Environment version 4, running `check_environment.py`:

```
Py4JJavaError: An error occurred while calling o38.get.
: java.util.NoSuchElementException: None.get
```

## Where the behavior differed from the docs

- **Status label.** The docs pages I read (last updated Nov 11 and earlier) show no GA, Public Preview or Beta label for creating standalone objects from a notebook. Only some sub-features are labeled. Search summaries of the same pages described the notebook path as Beta. I could not confirm GA from the pages.
- **Technique name.** The docs list `FULL_RECOMPUTE` as the technique for a full refresh. The event log reports `COMPLETE_RECOMPUTE`, and the maintenance type `MAINTENANCE_TYPE_COMPLETE_RECOMPUTE`.
- **Refresh type field.** The docs say `DESCRIBE TABLE EXTENDED` shows the refresh type but do not name the field. It is `refresh_information.last_refresh_type`. The same output also has `refresh_schedule` (`MANUAL` here) and, for materialized views, `refresh_policy` (`Not Set, defaulting to AUTO`).
- **Auto Loader in a decorator.** The Python docs page has no file ingestion example. `cloudFiles` works inside `@dp.table` on environment 6, and fails on environment 5 without a schema location.
- **Python environment requirement.** The docs say the decorators need serverless environment version 5 or above, and they imported fine on 5 and 6. What the docs do not say is that a one-time `jobs submit` run defaults to an older environment that cannot import them, while a saved job from the bundle defaults to a newer one.
- **SQL task.** The docs say to use the SQL task type to orchestrate materialized views with a job. That does not work for objects created in a serverless notebook, which need a notebook task.
- **`REFRESH` on Python-created objects.** The docs say a decorated table cannot contain a REFRESH or SCHEDULE. They do not say that a separate `REFRESH` statement against it fails too.

## Not tested

- `REFRESH ... ASYNC` and `REFRESH ... FULL`, and `full_refresh=True` on a decorator.
- The `SCHEDULE` and `TRIGGER ON UPDATE` clauses. Scheduling here means running a job task.
- Refreshing as a user who is not the owner, and the permissions needed to query.
- Cost and cost attribution, which the docs say are not available for this compute.
- Larger data than 200 rows per batch. All timings are for a very small dataset and mostly measure start-up, so they say little about performance at scale.
- Regions other than the workspace's own.
