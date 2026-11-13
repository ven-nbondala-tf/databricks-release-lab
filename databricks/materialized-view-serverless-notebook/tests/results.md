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

## Part B: pipeline tests

Not run yet.
