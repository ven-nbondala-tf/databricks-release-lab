# Serverless cost: standard mode and other cost controls

Working code for two guides:

- Part 1: Cut Databricks Serverless Job Costs with Standard Mode
- Part 2: More Ways to Control Databricks Serverless Costs

The bundle deploys one serverless job twice. The `dev` target runs it in performance optimized mode and the `prod` target runs it in standard mode. You run both, then compare the DBUs each mode billed in `system.billing.usage`.

## What is in this folder

| Path | Purpose |
| --- | --- |
| `databricks.yml` | The bundle: one job, a `dev` target (`PERFORMANCE_OPTIMIZED`) and a `prod` target (`STANDARD`) |
| `src/workload.py` | The serverless task: generates rows, aggregates them and writes a table |
| `src/config_check.py` | Part 1 example: a serverless task that tries to set a Spark configuration serverless does not allow |
| `diagrams/run-steps.mmd` | Part 1 diagram: the six steps of a serverless run |
| `tests/run_alternating.py` | Runs both jobs one after the other, alternating, and records the timings |
| `sql/01_find_jobs_to_switch.sql` | Finds jobs that still use performance optimized mode |
| `sql/02_compare_modes_for_a_job.sql` | DBUs per run in each mode for one job |
| `sql/03_dbus_by_mode.sql` | Total DBUs by performance mode |
| `sql/04_dbus_per_run.sql` | DBUs for each run of the demo jobs |
| `sql/05_most_expensive_jobs.sql` | Part 2: the most expensive jobs with their names |
| `sql/06_usage_policy_tags.sql` | Part 2: usage that carries a serverless usage policy and its tags |
| `sql/07_cost_per_mode.sql` | DBUs and list cost per mode for the measured runs |
| `sql/cleanup.sql` | Drops the demo schema |

## Prerequisites

- A workspace with serverless compute for jobs and Unity Catalog.
- A recent Databricks CLI, signed in with `databricks auth login`.
- A catalog you can create a schema in, and read access to `system.billing.usage`.
- For Part 2: permission to read `system.lakeflow.jobs`. Creating a usage policy needs a workspace admin, and creating a budget needs an account admin.

## Setup

1. Create the schema the job writes to:

   ```sql
   CREATE SCHEMA IF NOT EXISTS <catalog>.cost_demo;
   ```

2. In `databricks.yml`, set the default of the `catalog` variable to your catalog, or pass `--var catalog=<catalog>` when you deploy and run.
3. Deploy both targets:

   ```bash
   databricks bundle deploy -t dev
   databricks bundle deploy -t prod
   ```

4. Read the job IDs from the deploy output or with `databricks bundle summary -t dev` and `databricks bundle summary -t prod`.

## Run

Run the jobs alternately, with nothing else running, so the timings are comparable:

```bash
python3 tests/run_alternating.py <dev-job-id> <prod-job-id> 6
```

To run the SQL files from the terminal, set `WAREHOUSE_ID` to a SQL warehouse ID and use `python3 tests/sql.py "<statement>"`.

The script starts each run, waits for it to finish and writes the queue, setup, execution and total times of every run to `tests/runs.json`.

Usage records arrive in `system.billing.usage` after the runs finish, and can take several hours. When they are there, run `sql/04_dbus_per_run.sql` with your two job IDs, then `sql/02_compare_modes_for_a_job.sql` for each job.

## Expected result

- Both jobs succeed and write `<catalog>.cost_demo.orders_by_customer`.
- The standard mode job has a startup time of minutes. The performance optimized job starts in seconds.
- Execution time is about the same in both modes.
- `system.billing.usage` bills fewer DBUs per run for the standard mode job. The size of the difference depends on the workload, so measure your own.

## Cleanup

```bash
databricks bundle destroy -t dev
databricks bundle destroy -t prod
```

Then run `sql/cleanup.sql` with your catalog name.
