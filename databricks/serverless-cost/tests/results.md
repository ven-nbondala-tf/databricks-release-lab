# Test results

Run on November 24, 2026 on a Databricks Free Edition workspace, serverless jobs compute. These notes are not part of the article.

## Workload

One serverless notebook task (`src/workload.py`): `spark.range` of 18,000,000,000 rows, a `customer_id` and an `amount` column, a group by `customer_id` (50,000 groups) and a table write. Deployed with the bundle: `dev` target `PERFORMANCE_OPTIMIZED`, `prod` target `STANDARD`. Runs alternated, one at a time, nothing else running.

## Calibration

- 400M rows: 34 s execution. 1.5B rows: about 21 s execution (pilot batch of 12 runs, kept in `tests/pilot/`, not used for the comparison). 12B rows: 102 s. 18B rows: about 151 s, used for the measured set.
- Three of the measured runs were separated by a gap of 46 minutes (between runs 3 and 4 the machine running the script was asleep). Runs were still one at a time.

## Measured runs (setup = startup time before the task runs)

| # | Mode | Run ID | Started (UTC) | Setup s | Execution s | Total s |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PERFORMANCE_OPTIMIZED | 266778897822027 | 04:10:46 | 3 | 151 | 154.6 |
| 2 | STANDARD | 579410995447042 | 04:13:35 | 165 | 151 | 316.6 |
| 3 | PERFORMANCE_OPTIMIZED | 695446087302015 | 04:18:59 | 2 | 152 | 154.8 |
| 4 | STANDARD | 1026151515198002 | 05:07:13 | 186 | 175 | 362.3 |
| 5 | PERFORMANCE_OPTIMIZED | 955186349917435 | 05:13:38 | 3 | 153 | 157.5 |
| 6 | STANDARD | 737445474560156 | 05:16:28 | 155 | 151 | 307.2 |
| 7 | PERFORMANCE_OPTIMIZED | 774143021644123 | 05:21:37 | 3 | 150 | 153.8 |
| 8 | STANDARD | 691683180728349 | 05:24:11 | 175 | 150 | 326.5 |
| 9 | PERFORMANCE_OPTIMIZED | 765355245077611 | 05:29:50 | 2 | 151 | 153.9 |
| 10 | STANDARD | 622447488725818 | 05:32:26 | 175 | 150 | 325.6 |
| 11 | PERFORMANCE_OPTIMIZED | 575684182843738 | 05:38:06 | 3 | 150 | 153.8 |
| 12 | STANDARD | 119051331571210 | 05:40:40 | 165 | 151 | 317.1 |

Averages over 6 runs each: PERFORMANCE_OPTIMIZED setup 2.7 s, execution 151.2 s, total 154.7 s. STANDARD setup 170.2 s, execution 154.7 s, total 325.9 s.

The Jobs API reports no `queue_duration` for these runs. The prod job page shows the Performance optimized toggle Off.

## What differed from the brief and the docs

- Startup in standard mode measured 155 to 186 s (about 2.5 to 3 minutes). The docs say a typical 4 to 6 minutes, depending on compute availability, so the measurement is shorter than typical.
- Execution time was nearly the same in both modes (151 s versus 155 s). The difference in total time came entirely from startup.
- The "up to 70%" wording was not found on the best practices page or any other docs page read on Nov 24, 2026. The page says only that standard mode consumes fewer DBUs, so it costs less.

## Billing records

- At 05:47 UTC the newest record in `system.billing.usage` ended at 01:00 UTC, and none existed yet for the demo jobs (first measured run started 04:10 UTC). Arrival delay and DBUs per run to be recorded once they arrive.
- The `ingestion_date` column exists in `system.billing.usage`.

## Billing records, partial (checked 08:04 UTC on Nov 24, 2026)

Records are hourly buckets split into 10 minute pieces, so one run has 2 or 3 records. Join key: `usage_metadata.job_run_id`; mode column: `product_features.performance_target`; SKU `PREMIUM_JOBS_SERVERLESS_COMPUTE_US_EAST_OHIO` for both modes.

Arrived so far: all 12 pilot runs (1.5B rows) and the first 3 measured runs. Runs 4 to 12 started at 05:07 UTC or later and had no records yet, so the newest hourly bucket ingested was the 04:00 to 05:00 UTC one, about 3 hours behind.

| Run | Mode | Rows | DBUs |
| --- | --- | --- | --- |
| Measured 1 | PERFORMANCE_OPTIMIZED | 18B | 1.3701 |
| Measured 2 | STANDARD | 18B | 0.4344 |
| Measured 3 | PERFORMANCE_OPTIMIZED | 18B | 1.3700 |
| Calibration | PERFORMANCE_OPTIMIZED | 12B | 1.0418 |
| Pilot, 6 runs | PERFORMANCE_OPTIMIZED | 1.5B | 0.5105, 0.5330, 0.5534, 0.5149, 0.5149, 0.4875 |
| Pilot, 6 runs | STANDARD | 1.5B | 0.1612, 0.1599, 0.1610, 0.1758, 0.1610, 0.1600 |

Not part of the comparison: run 415838955932833 (prod job, started 04:51 UTC, one time trigger, 333 s, 0.4574 DBUs). It was not started by the run script, and it ran between measured runs 3 and 4 without overlapping them.

First 3 measured runs only: STANDARD 0.4344 against about 1.3700 for PERFORMANCE_OPTIMIZED, 68% lower. This is a single standard run, so it is not the result. Final averages wait for all 12 runs.

## Billing records, complete (checked 17:55 UTC on Nov 24 and again 02:07 UTC on Nov 25, 2026)

All 12 measured runs have records. Records for runs 4 to 12 (started 05:07 UTC or later) were missing at 08:04 UTC and present at 17:55 UTC. The first 3 runs (started 04:10 to 04:18 UTC) were present at 08:04 UTC, so records arrived between about 3.8 and 13 hours after the run. The newest record in the whole table was 7 hours behind at 02:07 UTC on Nov 25.

| # | Mode | Run ID | Total s | DBUs |
| --- | --- | --- | --- | --- |
| 1 | PERFORMANCE_OPTIMIZED | 266778897822027 | 154.6 | 1.3701 |
| 2 | STANDARD | 579410995447042 | 316.6 | 0.4344 |
| 3 | PERFORMANCE_OPTIMIZED | 695446087302015 | 154.8 | 1.3700 |
| 4 | STANDARD | 1026151515198002 | 362.3 | 0.4646 |
| 5 | PERFORMANCE_OPTIMIZED | 955186349917435 | 157.5 | 1.2459 |
| 6 | STANDARD | 737445474560156 | 307.2 | 0.4532 |
| 7 | PERFORMANCE_OPTIMIZED | 774143021644123 | 153.8 | 1.1006 |
| 8 | STANDARD | 691683180728349 | 326.5 | 0.4351 |
| 9 | PERFORMANCE_OPTIMIZED | 765355245077611 | 153.9 | 1.1426 |
| 10 | STANDARD | 622447488725818 | 325.6 | 0.4349 |
| 11 | PERFORMANCE_OPTIMIZED | 575684182843738 | 153.8 | 1.3700 |
| 12 | STANDARD | 119051331571210 | 317.1 | 0.4348 |

## Comparison (6 runs per mode, 18B rows)

List price: $0.35 per DBU for both modes, SKU `PREMIUM_JOBS_SERVERLESS_COMPUTE_US_EAST_OHIO` (same SKU, same price). Cost is DBUs times the list price from `system.billing.list_prices`. It is a list cost in USD, not an invoice, and ignores discounts and credits.

| | PERFORMANCE_OPTIMIZED | STANDARD | Difference | Difference % |
| --- | --- | --- | --- | --- |
| DBUs, 6 runs | 7.5993 | 2.6571 | 4.9422 | 65.0 |
| DBUs per run | 1.2665 | 0.4429 | 0.8236 | 65.0 |
| List cost, 6 runs | $2.6598 | $0.9300 | $1.7298 | 65.0 |
| List cost per run | $0.4433 | $0.1550 | $0.2883 | 65.0 |
| Total time per run | 154.7 s | 325.9 s | 171.2 s longer | 110.7 longer |
| Execution time per run | 151.2 s | 154.7 s | 3.5 s | 2.3 |

Per run DBUs range from 1.1006 to 1.3701 in performance optimized mode and from 0.4344 to 0.4646 in standard mode. The same per-run figures from the SQL (`sql/07_cost_per_mode.sql`) give 1.2665 and 0.4429, and the table totals for the demo jobs match the sum of the per-run figures.

Not part of the comparison: the one-time prod job run 415838955932833 (0.4574 DBUs) and the 12B calibration run 983100640924320 (1.0418 DBUs).

## Docs queries (run Nov 25, 2026, 02:10 UTC)

- `sql/01_find_jobs_to_switch.sql` ran as written and returned 50 rows. Top rows by list cost: `serverless_objects_demo` (27 runs, 14.61 DBUs), `orders_by_customer_dev` (13 runs, 11.76 DBUs), `rate_limit_workload` (13 runs, 6.94 DBUs).
- `sql/03_dbus_by_mode.sql` (30 days, whole workspace): PERFORMANCE_OPTIMIZED JOBS 53.15 DBUs, PERFORMANCE_OPTIMIZED DLT 9.27, STANDARD JOBS 4.25.
- `sql/02_compare_modes_for_a_job.sql` per job (each job has 13 runs including pilot and calibration runs of different sizes, so these figures are not the headline): dev job 0.9043 DBUs per run, prod job 0.3149. The docs say to compare runs that process similar amounts of data, which is why the comparison above uses only the 6 measured runs per mode.
- `sql/05_most_expensive_jobs.sql` (Part 2) ran and returned 10 rows joined to job names from `system.lakeflow.jobs`.
- Per run, the first query row for the prod job is not in the PERFORMANCE_OPTIMIZED list, as expected, since the query filters on that mode.

## Part 2 tests that could not be done here

- Serverless usage policy with a team tag, and showing the tag in `custom_tags`: the Settings, Compute page does not exist in this workspace, and the policy API paths tried (`/api/2.1/budget-policies`, `/api/2.0/serverless-usage-policies`, `/api/2.0/accounts/budget-policies`) return Not Found. Skipped. The tag mechanism is covered by the tags guide, part 2.
- Budgets: an account-level feature, not available here. Skipped.
- Serverless rate limits: there is no Previews page here, so the admin setting cannot be turned on. Not repeated for this guide. The earlier test in `databricks/serverless-compute/rate-limits` (November 17, 2026) ran the same workload on compute objects of different sizes and found no difference in run time, and it could not tell whether the limit was enforced. The `rate_limit_workload` job in the 30 day queries above comes from that test.
