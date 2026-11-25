# Cut Databricks Serverless Job Costs with Standard Mode

Subtitle: Switch Databricks serverless jobs to standard mode, see what one workload measured over 6 runs per mode, and find the jobs worth switching.

Databricks serverless jobs run in one of two performance modes, and the mode decides how fast compute starts and how many DBUs a run consumes. In part 1 of this series, step 2 was finding compute, and that step can happen in two ways: from a pool of warm compute, or when compute becomes available. This guide explains both modes, shows what one test workload measured in each, and walks through how to switch a job and how to find the jobs worth switching. The complete code for this guide is on GitHub: [serverless-cost](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/serverless-cost).

[VIDEO: add the Part 2 video link here]
Caption: Standard mode for serverless jobs in a short video, part 2 of 2.

Part 1 follows one job from the Run click to its billing record: [Databricks Serverless Jobs Explained: From Run to Billing](add the Part 1 link after publishing).

## What are Databricks serverless performance modes

A performance mode is a job-level setting for serverless jobs and pipelines. It trades startup speed for DBUs: performance optimized mode starts fast and consumes more, and standard mode starts slower and consumes fewer.

- Performance optimized mode is the default. Databricks keeps a pool of warm compute ready, so workloads typically start in less than a minute.
- Standard mode is for scheduled and batch work. Workloads typically start within 4 to 6 minutes and consume fewer DBUs.
- Both modes run on the same serverless runtime and produce the same results.
- You choose the mode for each job and each pipeline schedule. The setting does not apply to interactive serverless notebooks.

## How each mode gets compute

In performance optimized mode, compute comes from warm capacity, so a run starts quickly and gets more compute fast when it needs it. In standard mode, startup depends on compute availability, and compute is added more slowly. This can lengthen workloads that scale up.

The price per DBU does not change. The documentation says standard mode consumes fewer DBUs for the same workload, at the same price per DBU and on the same SKU.

## Example: one workload in both modes

On our test workload, standard mode used 65% fewer DBUs per run than performance-optimized mode, over 6 runs in each mode. Every workload is different, so your savings will be different. Measure your own jobs with the before-and-after query from the docs.

The workload is one serverless notebook task. It generates 18 billion rows, aggregates them by customer and writes a table. One bundle deploys it twice: the dev target uses performance optimized mode and the prod target uses standard mode. The runs alternated between the two jobs, one at a time, with nothing else running.

| | Performance optimized | Standard |
| --- | --- | --- |
| DBUs per run, average | 1.27 | 0.44 |
| DBUs per run, lowest to highest | 1.10 to 1.37 | 0.434 to 0.465 |
| Startup, average | 3 seconds | 170 seconds |
| Execution, average | 151 seconds | 155 seconds |
| Total time, average | 155 seconds | 326 seconds |

These are the DBUs of each pair of runs, in the order they ran:

| Pair | Performance optimized | Standard |
| --- | --- | --- |
| 1 | 1.3701 | 0.4344 |
| 2 | 1.3700 | 0.4646 |
| 3 | 1.2459 | 0.4532 |
| 4 | 1.1006 | 0.4351 |
| 5 | 1.1426 | 0.4349 |
| 6 | 1.3700 | 0.4348 |

Three things stand out on this workload:

- Execution time was nearly the same in both modes, 151 seconds against 155 seconds. The difference in total time, about double, came entirely from startup.
- Startup in standard mode took between 155 and 186 seconds, about 2.5 to 3 minutes. The documentation gives a typical 4 to 6 minutes and says startup depends on compute availability.
- Standard mode was also more consistent here. Its DBUs per run stayed within 0.434 to 0.465, while performance optimized mode ranged from 1.10 to 1.37.

The usage records for these runs took between about 3 and 12 hours to appear in `system.billing.usage`.

The full example, including setup and cleanup, is in the [serverless-cost](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/serverless-cost) folder of the repository.

## When to use each mode

Use standard mode for work that meets its completion and data freshness requirements with a slower start. The documentation lists nightly and hourly batch jobs, pipelines that refresh tables on a schedule, backfills and one-time loads, and jobs that an external orchestrator triggers on a schedule.

Use performance optimized mode when someone waits for the result or when a slow start would cause damage:

- Interactive work, such as runs started with Run now or from an app.
- Development, testing and validation.
- Jobs that a file arrival trigger or a table update trigger starts.
- Jobs that run every few minutes, where a slow start could delay or queue the next run.
- Short jobs, where startup is a large share of the total time.

The mode is a job setting. If a job mixes tasks that are time-sensitive with tasks that can wait, split them into separate jobs and connect them with a Run Job task. Each job then keeps its own mode.

## Prerequisites

- A serverless job or pipeline.
- The CAN MANAGE permission on the job, to change its mode.
- Databricks CLI 0.241.0 or above, to set the mode in a bundle.
- Read access to `system.billing.usage` and `system.billing.list_prices`, to measure the cost.

## How to switch a job to standard mode

You can switch a job in the UI or in a bundle. The change applies to runs that start after you save it.

In the UI, open Jobs & Pipelines, click the job name and, in the Job details pane, turn off Performance optimized.

[image: 03-performance-toggle.png | Caption: The Job details pane of a job in standard mode, with Performance optimized off. | Alt: The Job details pane of a job with the Performance optimized toggle switched off.]

[image: 04-performance-toggle-dev.png | Caption: The same pane for a job in performance optimized mode, with the toggle on. | Alt: The Job details pane of a job with the Performance optimized toggle switched on.]

In a bundle, set `performance_target` on the job and override it in the targets that need a different mode. This bundle runs the job in performance optimized mode in `dev` and in standard mode in `prod`:

```yaml
bundle:
  name: serverless-cost

variables:
  catalog:
    default: <catalog>

resources:
  jobs:
    orders_by_customer:
      name: orders_by_customer_${bundle.target}
      performance_target: STANDARD
      tasks:
        - task_key: aggregate_orders
          notebook_task:
            notebook_path: src/workload.py
            base_parameters:
              catalog: ${var.catalog}

targets:
  dev:
    default: true
    resources:
      jobs:
        orders_by_customer:
          performance_target: PERFORMANCE_OPTIMIZED
  prod:
    resources:
      jobs:
        orders_by_customer:
          performance_target: STANDARD
```

If you omit `performance_target`, the job uses performance optimized mode. To change one run without changing the job, use Run now with different settings.

## Find the jobs to switch

The documentation provides a query that lists the jobs and pipelines still in performance optimized mode, ranked by list cost over the last 30 days. Start from the top of the list.

```sql
SELECT
  u.workspace_id,
  u.billing_origin_product AS product,
  u.usage_metadata.job_id AS job_id,
  u.usage_metadata.dlt_pipeline_id AS pipeline_id,
  MAX(u.usage_metadata.job_name) AS job_name,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS job_runs,
  SUM(u.usage_quantity) AS dbus,
  SUM(u.usage_quantity * lp.pricing.default) AS list_cost
FROM system.billing.usage AS u
INNER JOIN system.billing.list_prices AS lp
  ON u.cloud = lp.cloud
  AND u.sku_name = lp.sku_name
  AND u.usage_start_time >= lp.price_start_time
  AND (u.usage_end_time <= lp.price_end_time OR lp.price_end_time IS NULL)
WHERE
  u.billing_origin_product IN ('JOBS', 'DLT')
  AND u.product_features.is_serverless
  AND u.product_features.performance_target = 'PERFORMANCE_OPTIMIZED'
  AND u.usage_unit = 'DBU'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY
  u.workspace_id,
  u.billing_origin_product,
  u.usage_metadata.job_id,
  u.usage_metadata.dlt_pipeline_id
ORDER BY list_cost DESC
LIMIT 50;
```

After you switch a job, let it run on its normal schedule for several runs and compare the modes with this query. Replace `<job-id>` with the job ID.

```sql
SELECT
  u.product_features.performance_target AS performance_mode,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS runs,
  SUM(u.usage_quantity) AS dbus,
  SUM(u.usage_quantity) / COUNT(DISTINCT u.usage_metadata.job_run_id) AS dbus_per_run
FROM system.billing.usage AS u
WHERE
  u.billing_origin_product = 'JOBS'
  AND u.product_features.is_serverless
  AND u.usage_unit = 'DBU'
  AND u.usage_metadata.job_id = '<job-id>'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY ALL;
```

DBUs per run also depend on how much data each run processes, so compare runs that process similar amounts of data. The query covers the last 30 days, so change the date filter to the period you want to compare.

To rank jobs by DBUs in any mode, with their names, join the usage table to `system.lakeflow.jobs`:

```sql
WITH job_names AS (
  SELECT workspace_id, job_id, name,
         ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id ORDER BY change_time DESC) AS rn
  FROM system.lakeflow.jobs
)
SELECT
  n.name AS job_name,
  u.usage_metadata.job_id AS job_id,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS runs,
  ROUND(SUM(u.usage_quantity), 2) AS dbus
FROM system.billing.usage AS u
LEFT JOIN job_names AS n
  ON u.workspace_id = n.workspace_id
  AND u.usage_metadata.job_id = n.job_id
  AND n.rn = 1
WHERE u.billing_origin_product = 'JOBS'
  AND u.product_features.is_serverless
  AND u.usage_unit = 'DBU'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY n.name, u.usage_metadata.job_id
ORDER BY dbus DESC
LIMIT 10;
```

## Other ways to control serverless cost

Three more tools help with cost, and none of them changes how a single job runs.

- Serverless usage policies add tags to serverless work, so the cost shows up by team or project in `custom_tags`. They are in Public Preview and attribute spend without limiting it. The tags series, part 2, covers them: [Databricks Cost Tags Explained: Default, Custom, Serverless](https://medium.com/@nagarajubru/databricks-cost-tags-default-custom-serverless-5058cebd0b8a).
- Budgets track spending, for the whole account or filtered by product, workspace and custom tags, and send an email when a threshold is reached. An account admin creates them, and they use the list price of the SKU.
- Rate limits cap how far the Spark executors of jobs and pipelines can autoscale. They are in Beta, a workspace admin turns them on from the Previews page, and they are not a spend cap.

## Things to know

- Set `STANDARD` explicitly. Performance optimized mode is the default in the UI, the API, bundles, Terraform and the SDKs, so a job stays in that mode until you change it.
- Do not expect the setting to apply to interactive notebooks. Triggered pipeline updates that you start manually also run in performance optimized mode.
- Expect a slower start. The documentation gives a typical 4 to 6 minutes for standard mode and says it varies by run. Keep performance optimized mode for jobs that a trigger starts or that run every few minutes.
- Read the result as one workload. The price per DBU and the SKU are the same in both modes, only the DBUs differ, and the difference depends on the workload.
- Wait for the usage records before you compare. They can take several hours to appear in `system.billing.usage`.

## Best practices

- Switch scheduled batch jobs first, starting with the most expensive ones from the query above.
- Compare several representative runs, including startup time, before you decide. If a job no longer meets its deadline, switch it back, and the change applies to the next run.
- Use the scheduled runs for the comparison. Extra manual runs of a production job can write duplicate data.
- Use performance optimized mode in `dev` and standard mode in `prod` in the same bundle.

## Summary

A performance mode decides how fast serverless compute starts and how many DBUs a run consumes: performance optimized starts fast, and standard consumes fewer DBUs at the same price per DBU. On our test workload, standard mode used 65% fewer DBUs per run over 6 runs in each mode, with the same execution time and about twice the total time because of startup. Use standard mode for scheduled batch jobs that can wait a few minutes to start, and measure your own jobs before you rely on a number.

Which of your jobs could wait a few minutes to start?

## References

- [Performance modes for serverless jobs and pipelines](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/performance-modes), Microsoft Learn
- [Serverless compute best practices](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/best-practices), Microsoft Learn
- [Run your Lakeflow Jobs with serverless compute](https://learn.microsoft.com/en-us/azure/databricks/jobs/run-serverless-jobs), Microsoft Learn
- [Monitor the cost of serverless compute](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/serverless-billing), Microsoft Learn
- [Billable usage system table reference](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing), Microsoft Learn
- [Attribute usage with serverless usage policies](https://learn.microsoft.com/en-us/azure/databricks/admin/usage/budget-policies), Microsoft Learn
- [Create and monitor budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets), Microsoft Learn
- [Manage serverless compute](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/manage-serverless-compute), Microsoft Learn

## Medium settings

- SEO title: Cut Databricks Serverless Job Costs with Standard Mode
- SEO description: same as the subtitle
- Slug: cut-databricks-serverless-job-costs-standard-mode
- Tags: Databricks, Data Engineering, Serverless, FinOps, Cost Management
