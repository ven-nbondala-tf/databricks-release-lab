# Fact sheet: serverless cost

Official Azure Databricks documentation only. Part 1 first, then part 2.

## Part 1: standard mode


Base: https://learn.microsoft.com/en-us/azure/databricks
PM = /compute/serverless/performance-modes (ms.date 2026-11-17; page footer "Last updated 2026-11-18")
RSJ = /jobs/run-serverless-jobs (2026-11-13); LDP = /ldp/serverless (2026-11-13); BP = /compute/serverless/best-practices (2026-11-12)
SB = /admin/system-tables/serverless-billing "Monitor the cost of serverless compute" (2026-11-19); BILL = /admin/system-tables/billing (2026-11-20); BR = /dev-tools/bundles/resources (2026-11-20)

| # | Claim | Status | URL | ms.date |
|---|-------|--------|-----|---------|
| 1 | Performance-optimized: "Azure Databricks keeps a pool of warm compute ready, so workloads typically start in less than a minute and get more compute quickly when they need it." Use for "fast feedback during development and testing, or when standard mode cannot meet completion or data freshness requirements." | CONFIRMED | PM | 2026-11-17 |
| 2 | Standard: "Workloads typically start within 4 to 6 minutes and consume fewer Databricks units (DBUs). Evaluate this mode for scheduled and batch work when representative runs meet completion and data freshness requirements." | CONFIRMED | PM | 2026-11-17 |
| 3 | Run time: performance-optimized "Shorter for workloads that scale up, because compute is added from warm capacity." Standard "Can be longer for workloads that scale up, because compute is added more slowly." | CONFIRMED | PM | 2026-11-17 |
| 4 | "Both modes run your workload on the same serverless runtime and produce the same results." | CONFIRMED | PM | 2026-11-17 |
| 5 | The "up to 70%" cost claim | NOT FOUND on re-check (Nov 24, 2026). The best practices page, "Choose a performance mode", says only: "Standard mode consumes fewer Databricks units (DBUs), so it costs less." No percentage on that page, performance-modes, run-serverless-jobs, ldp/serverless or serverless-billing. | https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/best-practices | 2026-11-24 |
| 6 | Same SKU, fewer DBUs: table "Cost" row, standard "Consumes fewer DBUs for the same workload, at the same price per DBU and on the same SKU." Performance-optimized: "Consumes more DBUs for the same workload, in exchange for fast and predictable starts." | CONFIRMED | PM | 2026-11-17 |
| 7 | FAQ "Does standard mode have a different price?" "No. Both modes bill under the same SKU at the same price per DBU. Standard mode costs less because it consumes fewer DBUs." | CONFIRMED | PM | 2026-11-17 |
| 8 | Release status of standard mode for jobs/triggered pipelines: no GA/Preview label on the page | NOT FOUND (no status stated; RSJ labels other features Public Preview, not this one) | PM, RSJ | 2026-11-17 |
| 9 | Standard mode directly configurable for: "Serverless notebook, Python script, Python wheel, JAR, and dbt tasks, including notebooks that a task runs with dbutils.notebook.run()"; "Serverless pipelines run from a pipeline task"; "Refreshes of materialized views and streaming tables that a SQL task starts, or that a notebook or dbt task on a SQL warehouse starts. The mode doesn't change the SQL warehouse." | CONFIRMED | PM | 2026-11-17 |
| 10 | "The performance mode doesn't apply to interactive serverless notebooks, tasks that run on classic compute, SQL warehouses, or tasks that run on AI Runtime." (also BP: "The performance mode doesn't apply to interactive notebooks.") | CONFIRMED | PM; BP | 2026-11-17; 2026-11-12 |
| 11 | Scheduled notebook jobs: "When you schedule a notebook from the notebook, choose the mode in the schedule dialog." | CONFIRMED | PM | 2026-11-17 |
| 12 | Always performance-optimized: "Triggered pipeline updates that you start manually. The exception is a selective full refresh, which can run in standard mode." And "Continuous pipelines that use the pipeline's built-in continuous mode." | CONFIRMED | PM | 2026-11-17 |
| 13 | Continuous pipeline in standard mode: "run the pipeline with a continuous job and turn off Performance optimized for that job. A continuous job picks up a new mode when its run restarts... click Restart run." (LDP says "clear the Performance optimized checkbox in the schedule") | CONFIRMED | PM; LDP | 2026-11-17; 2026-11-13 |
| 14 | Triggered pipeline: "A serverless pipeline uses the performance mode of the job that runs it." LDP: "uses the performance mode of the job or schedule that runs it... To use standard mode for a triggered pipeline, clear Performance optimized in the pipeline schedule." | CONFIRMED | PM; LDP | 2026-11-17; 2026-11-13 |
| 15 | Pipeline schedule UI steps: Jobs & Pipelines > pipeline name > Schedule (or Add schedule) > configure trigger and job name > "Clear the Performance optimized checkbox" > Create. "The schedule creates a job that runs the pipeline in standard mode." | CONFIRMED | PM | 2026-11-17 |
| 16 | Selective full refresh in standard mode: select tables, click "Run now with different settings", turn on "Run pipeline with full table refresh", turn off "Performance optimized". | CONFIRMED | PM | 2026-11-17 |
| 17 | Account team requirement for standard mode | NOT FOUND (not mentioned in any page read) | PM | 2026-11-17 |
| 18 | Default: "Performance-optimized mode is the default for serverless jobs and pipelines, whether you create them in the UI, with the API, with Declarative Automation Bundles, with Terraform, or with the SDKs." | CONFIRMED | PM | 2026-11-17 |
| 19 | Default for jobs via bundles: "If you omit performance_target, the job uses performance-optimized mode." API create: "If you omit the field, the job uses PERFORMANCE_OPTIMIZED." runs/submit: "If you omit the field, the run uses PERFORMANCE_OPTIMIZED." | CONFIRMED | PM | 2026-11-17 |
| 20 | Default for notebooks: mode does not apply to interactive serverless notebooks; scheduled notebook jobs choose in schedule dialog (default for jobs is performance-optimized) | CONFIRMED | PM | 2026-11-17 |
| 21 | DIFFERS-ish (not a conflict): MVs/streaming tables refreshed on a schedule from the table definition "have their own setting, which defaults to standard mode". "Setting the mode for these refreshes is in Beta... a workspace admin must turn on the System-Managed Job for Materialized Views & Streaming Tables preview on the Previews page." | Beta (setting the mode for scheduled MV/ST refreshes) | PM | 2026-11-17 |
| 22 | History: "Until September 2025, standard mode was the default for new serverless jobs and pipeline schedules that you created in the UI. Jobs that the UI created in standard mode before the change keep that mode until you change it." | CONFIRMED | PM | 2026-11-17 |
| 23 | UI steps: "In your workspace, click Jobs & Pipelines in the sidebar. Click the name of the job. In the Job details pane, turn off Performance optimized." Switch back: turn on Performance optimized. "You can change the setting only when the job has at least one task that the mode applies to." | CONFIRMED | PM | 2026-11-17 |
| 24 | RSJ: "To use standard mode, turn off Performance optimized in the Job details pane. The setting applies only to the job's serverless tasks. You can change it only when the job has at least one serverless task." | CONFIRMED | RSJ | 2026-11-13 |
| 25 | Permission: "To change the performance mode of a job, you need the CAN MANAGE permission on the job." | CONFIRMED | PM | 2026-11-17 |
| 26 | Per-run choice: "Run now with different settings" (one time, without changing the job); "Repair run: By default, a repair uses the same mode as the run that it repairs. You can choose a different mode for the repair." | CONFIRMED | PM | 2026-11-17 |
| 27 | API field `performance_target`; values PERFORMANCE_OPTIMIZED and STANDARD. BR: "Valid values are STANDARD, which enables cost-efficient execution of serverless workloads, and PERFORMANCE_OPTIMIZED, which prioritizes fast startup and execution times through rapid scaling and optimized cluster performance." (BR run-level entry overrides job-level) | CONFIRMED | PM; BR | 2026-11-17; 2026-11-20 |
| 28 | Job-level bundle field description: "Defines how performant or cost efficient the execution of the run on serverless should be. Added in Databricks CLI version 0.241.0". PM: "you need Databricks CLI version 0.241.0 or above." | CONFIRMED | BR; PM | 2026-11-20; 2026-11-17 |
| 29 | API behaviours: update with `new_settings`; Create sets mode; "Reset a job: Replaces all job settings. To keep standard mode, include performance_target in the new settings."; "Run now and Repair a run: Sets the mode for that run only." Update endpoint shown: POST /api/2.2/jobs/update | CONFIRMED | PM | 2026-11-17 |
| 30 | CLI: `databricks jobs run-now 123456789 --performance-target STANDARD --no-wait` runs once in standard mode without changing the job. | CONFIRMED | PM | 2026-11-17 |
| 31 | Check mode of a run: UI "Performance optimized as Enabled ... or Disabled for standard mode"; API `effective_performance_target` in Get a single job run; system tables `product_features.performance_target` in billable usage, and `trigger_details.job_task.performance_target` in the pipeline update timeline table. | CONFIRMED | PM | 2026-11-17 |
| 32 | Startup: "Typically 4 to 6 minutes, depending on compute availability." FAQ: "Startup time in standard mode depends on compute availability and varies from run to run. Four to six minutes is typical, not a maximum. If a job needs a predictable start time, use performance-optimized mode." | CONFIRMED | PM | 2026-11-17 |
| 33 | Performance-optimized startup: "Typically less than a minute." | CONFIRMED | PM | 2026-11-17 |
| 34 | Queue delay: "Jobs that run every few minutes, where slower starts could delay or queue the next run." (guidance to use performance-optimized). Also file arrival / table update triggers should use performance-optimized. | CONFIRMED | PM | 2026-11-17 |
| 35 | How startup affects billing: no statement that startup/queue time is billed or not billed. Docs only say standard "consume[s] fewer DBUs" and tell you to compare "DBUs per run and the completion time, including startup". | NOT FOUND | PM | 2026-11-17 |
| 36 | What is billed in each mode (compute time vs. startup, etc.) | NOT FOUND (only "more DBUs" vs "fewer DBUs for the same workload"; usage is under the same SKU) | PM | 2026-11-17 |
| 37 | Billing data details: "Usage records can take several hours to appear in the table. The queries in this section use list prices, so the costs don't reflect discounts." Job-level query counts "only usage that's billed to the job (JOBS). Pipeline tasks are billed as pipeline usage (DLT)". | CONFIRMED | PM | 2026-11-17 |
| 38 | Billing columns: `billing_origin_product` ('JOBS', 'DLT'), `usage_metadata.job_id` / `job_run_id` (populated for "Serverless jobs and jobs run on job compute"), `usage_metadata.dlt_pipeline_id`, `usage_metadata.dlt_update_id`, `product_features.is_serverless`, `product_features.performance_target`: "Indicates the performance mode of the serverless job or pipeline. Values include PERFORMANCE_OPTIMIZED, STANDARD, or null. Non-serverless workloads have a null value." | CONFIRMED | BILL; PM | 2026-11-20; 2026-11-17 |
| 39 | Mode is job-level: "The mode applies to all serverless tasks in the job." "Can tasks in the same job use different modes? No." Split into separate jobs, orchestrate with a Run Job task (the child job uses its own mode). | CONFIRMED | PM | 2026-11-17 |
| 40 | No workspace-wide default: "Can I set a default mode for all jobs in a workspace? No. You set the mode for each job and each pipeline schedule." Bulk: Jobs API, SDK for Python, bundles, or Terraform. | CONFIRMED | PM | 2026-11-17 |
| 41 | Timing of change: "A change applies to runs that start after you save it. A run that's in progress keeps the mode that it started with." | CONFIRMED | PM | 2026-11-17 |
| 42 | Bundle/Terraform deploys overwrite UI/API edits: "If a bundle or Terraform deploys a job, change the mode in the configuration. The next deployment overwrites changes that you make in the UI or with the API. Jobs that a bundle deploys are read-only in the Jobs UI." | CONFIRMED | PM | 2026-11-17 |
| 43 | Try-it procedure: switch, let run "several representative runs", compare DBUs per run and completion time; "Use the job's scheduled runs for the comparison. Extra manual runs of a production job can write duplicate data." Switch back applies to next run. | CONFIRMED | PM | 2026-11-17 |
| 44 | RSJ requirements: "Your Azure Databricks workspace must have Unity Catalog enabled." "Because serverless compute for workflows uses standard access mode, your workloads must support this access mode." "Your Databricks workspace must be in a supported region for serverless compute." (Note: "standard mode" here is unrelated to access mode: PM note "Standard mode is a performance setting for serverless compute. It's unrelated to standard access mode for classic compute.") | CONFIRMED | RSJ; PM | 2026-11-13; 2026-11-17 |
| 45 | No standard-mode-specific region or runtime restrictions | NOT FOUND (only general serverless region requirement above) | PM, RSJ | 2026-11-17 |
| 46 | BP: standard mode "Best for scheduled and batch jobs and pipelines that can tolerate a typical startup time of 4 to 6 minutes. Standard mode consumes fewer Databricks units (DBUs), so it costs less." "For scheduled jobs where startup latency isn't critical, standard mode typically offers the best value." | CONFIRMED | BP | 2026-11-12 |
| 47 | RSJ note: "you might experience increased startup times when running a job that requires large amounts of memory or includes many tasks." | CONFIRMED | RSJ | 2026-11-13 |
| 48 | Best-fit workloads for standard: nightly/hourly scheduled batch; scheduled pipeline refreshes; backfills and one-time loads; "Jobs that an external orchestrator triggers on a schedule". External tool: run-now uses the job's mode; runs/submit uses performance-optimized unless the request sets performance_target. | CONFIRMED | PM | 2026-11-17 |
| 49 | Cost-monitoring page also has "Report on DBUs consumed by performance mode" sample query (SQL below). | CONFIRMED | SB | 2026-11-19 |

## Bundle YAML (verbatim from PM, "Declarative Automation Bundles" section)

Intro: "To use standard mode for a job in a bundle, set performance_target on the job resource. The following example uses standard mode, and uses performance-optimized mode in the dev target for faster feedback during development:"

```yaml
resources:
  jobs:
    nightly_etl:
      name: nightly_etl
      performance_target: STANDARD
      tasks:
        - task_key: transform
          notebook_task:
            notebook_path: ../src/transform.ipynb

targets:
  dev:
    resources:
      jobs:
        nightly_etl:
          performance_target: PERFORMANCE_OPTIMIZED
```

(Indentation reconstructed from the flattened page text; the docs show no explicit prod target, prod inherits STANDARD from the top-level resource.)

## API / CLI / SDK / Terraform (verbatim from PM)

```bash
curl -X POST "$DATABRICKS_HOST/api/2.2/jobs/update" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 123456789,
    "new_settings": {
      "performance_target": "STANDARD"
    }
  }'

databricks jobs update --json '{"job_id": 123456789, "new_settings": {"performance_target": "STANDARD"}}'

databricks jobs run-now 123456789 --performance-target STANDARD --no-wait
```

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

w = WorkspaceClient()

# Replace with the IDs of the jobs to switch to standard mode.
job_ids = [123456789, 234567890]

for job_id in job_ids:
    w.jobs.update(
        job_id=job_id,
        new_settings=jobs.JobSettings(performance_target=jobs.PerformanceTarget.STANDARD),
    )
```

```hcl
resource "databricks_job" "nightly_etl" {
  name = "nightly_etl"
  performance_target = "STANDARD"

  task {
    task_key = "transform"
    notebook_task {
      notebook_path = "/Workspace/Users/someone@example.com/transform"
    }
  }
}
```

## SQL queries (verbatim, whitespace re-indented)

Source for first two: https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/performance-modes (Measure the cost of each mode, ms.date 2026-11-17)

Find jobs and pipelines to switch (last 30 days, performance-optimized, by list cost):

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
LIMIT 50
```

Compare a job's usage before and after the switch (replace <job-id>):

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
GROUP BY ALL
```

Doc text: for pipelines "filter on u.billing_origin_product = 'DLT' and u.usage_metadata.dlt_pipeline_id = '<pipeline-id>' instead, and count u.usage_metadata.dlt_update_id instead of u.usage_metadata.job_run_id." Also: "DBU consumption per run also depends on how much data each run processes, so compare runs that process similar amounts of data."

Source: https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/serverless-billing (Report on DBUs consumed by performance mode, ms.date 2026-11-19)

```sql
SELECT
  product_features.performance_target,
  billing_origin_product,
  SUM(usage_quantity) as total_dbu
FROM
  system.billing.usage
WHERE
  product_features.is_serverless
  and billing_origin_product in ('JOBS','DLT')
  and usage_unit = 'DBU'
  and usage_date >= DATEADD(day, -30, current_date)
GROUP BY
  1,2
ORDER BY
  total_dbu DESC
```

Full URLs: PM https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/performance-modes ; RSJ .../jobs/run-serverless-jobs ; LDP .../ldp/serverless ; BP .../compute/serverless/best-practices ; BR .../dev-tools/bundles/resources ; BILL .../admin/system-tables/billing ; SB .../admin/system-tables/serverless-billing

## Part 2: cost controls


Base: https://learn.microsoft.com/en-us/azure/databricks

| Claim | Status | URL | ms.date |
|---|---|---|---|
| Serverless cost page: identity_metadata.run_as "shows the user or service principal whose credentials were used to run the workload" | CONFIRMED | /admin/system-tables/serverless-billing | 2026-11-19 |
| usage_metadata fields that describe serverless workload: "job_run_id, job_name, notebook_id, and notebook_path" | CONFIRMED | /admin/system-tables/serverless-billing | 2026-11-19 |
| usage_metadata.job_id: "Serverless jobs and jobs run on job compute (does not populate for jobs run on all-purpose compute)"; job_run_id same wording | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| usage_metadata.notebook_id: "ID of the notebook associated with the usage" populated for "Serverless notebooks"; notebook_path: "Notebooks run on serverless compute"; job_name: "Jobs run on serverless compute" | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| Pipeline: usage_metadata.dlt_pipeline_id ("ID of the pipeline associated with the usage record"), also dlt_update_id, for "Lakeflow pipelines and features that use Lakeflow pipelines, such as materialized views..." | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| Warehouse: usage_metadata.warehouse_id, "Workloads run on a SQL warehouse" | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| Usage policy: usage_metadata.usage_policy_id, "ID of the serverless usage policy associated with the usage record" | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| usage_metadata.budget_policy_id: "Deprecated. Use usage_policy_id instead." | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| Performance mode: product_features.performance_target, "Indicates the performance mode of the serverless job or pipeline. Values include PERFORMANCE_OPTIMIZED, STANDARD, or null. Non-serverless workloads have a null value." | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| product_features.is_serverless: "Values include true or false, or null (value is true or false when you can choose between serverless and classic compute, otherwise it's null)" | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| usage_metadata.serverless_compute_id: "Serverless billing records include a serverless_compute_id field in usage_metadata. Use it to track which compute object a workload ran on" (field is not in the billing page's metadata table) | CONFIRMED | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| billing_origin_product values relevant to serverless: JOBS ("Costs associated with Lakeflow Jobs workloads"), DLT ("Lakeflow pipelines workloads"), INTERACTIVE ("serverless interactive workloads"), SQL ("Databricks SQL, including workloads run on SQL warehouses and materialized views"), ALL_PURPOSE ("classic all-purpose compute"), BASE_ENVIRONMENTS, NETWORKING, LAKEHOUSE_MONITORING, PREDICTIVE_OPTIMIZATION | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| Data quality monitoring, predictive optimization and serverless workflows "are all billed under the same serverless jobs SKU" | CONFIRMED | /admin/system-tables/billing | 2026-11-20 |
| sku_name patterns: docs only show `sku_name LIKE '%SERVERLESS%'` and `sku_name like '%JOBS_SERVERLESS_COMPUTE%'` in queries; no list of serverless SKU names found on these pages | NOT FOUND (full SKU list) | /admin/system-tables/serverless-billing | 2026-11-19 |
| Multiple records per run: "you might see multiple records with the same job_id, job_run_id, or job_name but with different DBU consumption values... The sum of these DBUs represents the hourly DBU consumption for a given job run in that timeframe." | CONFIRMED | /admin/system-tables/serverless-billing | 2026-11-19 |
| Billing table record availability: "Records are typically available within 12 hours." (FAQ says "up to a 24-hour delay") | DIFFERS (12 h vs 24 h between pages) | /admin/system-tables/billing ; /compute/serverless/ | 2026-11-20 ; 2026-11-17 |
| Serverless usage policies status: "This feature is in Public Preview." | Public Preview | /admin/usage/budget-policies | 2026-09-28 |
| Usage policies: "consist of tags that are applied to any serverless compute activity incurred by a user assigned to the policy. The tags are logged in your billing records, allowing you to attribute serverless usage to specific budgets." | Public Preview | /admin/usage/budget-policies | 2026-09-28 |
| Usage policies creator: "You must be a workspace admin to create serverless usage policies. Non-admins can manage policies if they are assigned Serverless usage policy: Manager permissions." | Public Preview | /admin/usage/budget-policies | 2026-09-28 |
| Usage policy tags propagate "to your system.billing.usage system table in the custom_tags column" and to Azure cost analysis | Public Preview | /admin/usage/budget-policies | 2026-09-28 |
| Usage policies do not enforce spend: no limit or blocking behavior is described; "Serverless usage policies do not apply tags to classic compute resources." | CONFIRMED (attribution only; no enforcement stated) | /admin/usage/budget-policies | 2026-09-28 |
| Budget tracks: "You can set up budgets to either track account-wide spending, or apply filters to track the spending of specific teams, projects, or workspaces." Measured in "USD and use the list price of the SKU, including platform add-ons." | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budget requirements: "You must be an account admin to create and manage budgets." Created in account console > Usage > Budgets tab > Create budget | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budget filters: "limit the budget's tracked spending based on product, workspace, and custom tags"; with tags, "the budget only tracks usage that includes the specified custom tags" | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budget alerts: "Create up to four shared thresholds, which monitor monthly spend"; optional Send email; "Shared thresholds are monthly only." | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budget "Trigger webhook": "This feature is in Beta... turn on the Account-level Webhook Destinations preview" | Beta | /admin/account-settings/budgets | 2026-11-20 |
| Budget Block usage only applies to Unity Gateway ("prevent users from making further requests through Unity Gateway"); not described for serverless compute | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budgets do not stop spending for serverless: "Do not use this feature as a way to ensure an absolute spend cap on final billed amounts." (stated for Unity Gateway budgets); serverless budgets alert by email only per the page | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Email delay: "There could be up to a 24-hour delay between usage occurring and an email notification being sent." | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| "Budgets do not factor in any billing credits or negotiated discounts your account might have. The spent amount is calculated by multiplying usage by the SKU list price." | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budget limits: "Your account can have a maximum of 1,000 budgets." | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Budgets page for serverless: "you can use serverless usage policies to attribute your account's serverless usage" | CONFIRMED | /admin/account-settings/budgets | 2026-11-20 |
| Rate limits status: "Serverless rate limits are in Beta. Workspace admins can enable rate limits from the Previews page using the Serverless Compute Rate Limit setting." | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limit definition: "A rate limit controls how far an automated workload's Spark executors can autoscale." Admins create custom automated compute objects and assign a size | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limits scope: "Rate limits only apply to automated workloads (jobs and Lakeflow pipelines). Interactive workloads (notebooks and Databricks Connect) aren't rate-limited." | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limits are not a spend cap: "Rate limits do not set a hard limit on total workload cost or final billed amounts. They don't cap driver, REPL virtual machine, GPU, or materialized view and streaming table refresh costs." | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limit sizes: Small "~60 DBUs per hour", Medium "~120", Large "~240", X-Large "~480", 2X-Large "~960 DBUs per hour"; "These values are estimates." | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limit set via: Compute > Serverless tab > Create serverless compute > Size (Small to 2X-Large, or Default); requires "workspace admin or have the unrestricted cluster creation entitlement"; Jobs API: `serverless_compute.policy_id` in a job cluster, `job_cluster_key` on every serverless task | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Rate limit per workload: "The rate limit applies independently to each workload that uses the compute object... A compute object does not impose an aggregate limit across all workloads"; "You can't set a rate limit on a default compute object." | Beta | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Access control to serverless: default objects "Default Interactive Compute" and "Default Automated Compute"; "By default, all workspace users have Can Use on both objects"; admins can remove users. Not a spend cap: "Do not use this feature to ensure an absolute spend cap on final billed amounts." | CONFIRMED (status not stated) | /compute/serverless/manage-serverless-compute | 2026-11-17 |
| Standard performance mode: "Standard mode consumes fewer Databricks units (DBUs), so it costs less." Startup "typically 4 to 6 minutes"; "at the same price per DBU and on the same SKU" | CONFIRMED | /compute/serverless/best-practices ; /compute/serverless/performance-modes | 2026-11-12 ; 2026-11-17 |
| Performance-optimized is the default: "Performance-optimized mode is the default for serverless jobs and pipelines"; for batch "Databricks recommends evaluating standard mode for lower cost" | CONFIRMED | /compute/serverless/performance-modes | 2026-11-17 |
| "The performance mode setting doesn't apply to interactive serverless notebooks." Scheduled MV/streaming table refreshes default to standard mode; setting that mode "is in Beta" | CONFIRMED / Beta (MV refresh setting) | /compute/serverless/performance-modes | 2026-11-17 |
| Standard mode is job-level: "The mode applies to all serverless tasks in the job"; needs CAN MANAGE; one-time runs via runs/submit use `performance_target` | CONFIRMED | /compute/serverless/performance-modes | 2026-11-17 |
| Serverless notebook timeout (overspend protection): "serverless notebooks have a default execution timeout of 2.5 hours (9,000 seconds). Queries that exceed the timeout are canceled." | CONFIRMED | /compute/serverless/notebooks | 2026-10-22 |
| Notebook timeout configuration: admins change "Serverless interactive execution timeout" in Settings > Compute; per-notebook override with `spark.databricks.execution.timeout` | CONFIRMED | /compute/serverless/notebooks | 2026-10-22 |
| Serverless jobs query timeout: "By default, serverless jobs have no query execution timeout. You can set an execution timeout for job queries using the spark.databricks.execution.timeout property." | CONFIRMED | /compute/serverless/limitations | 2026-11-23 |
| Maximum runtime: "Serverless compute has a maximum runtime of 7 days. Runs that exceed 7 days are terminated by the platform and are not retried." | CONFIRMED | /compute/serverless/limitations | 2026-11-23 |
| Job concurrency: "By default, the maximum concurrent runs for all new jobs is 1." Queueing: "the run is queued for up to 48 hours if resources are unavailable" | CONFIRMED | /jobs/settings | 2026-11-17 |
| Job duration thresholds: "Enter a duration in the Warning field to configure the job's expected completion time. If the job exceeds this threshold, an event is triggered" (warning/notification; page excerpt does not say it stops the run) | CONFIRMED | /jobs/settings | 2026-11-17 |
| Job-level "timeout" setting that cancels a run on serverless: not confirmed on pages read | NOT FOUND | /jobs/settings | 2026-11-17 |
| Serverless environment versions: "Azure Databricks supports each environment version for three years from its release date"; environments "cache installed packages, which reduces startup latency for subsequent runs" | CONFIRMED | /compute/serverless/best-practices | 2026-11-12 |
| Pin package versions: "If you don't specify a version, the package may resolve to a different version... which can increase latency as new packages need to be installed." | CONFIRMED | /compute/serverless/best-practices | 2026-11-12 |
| Notebook virtual environment cached "so dependencies don't reinstall every time you reopen a notebook or resume after inactivity" | CONFIRMED | /compute/serverless/dependencies | 2026-11-23 |
| Best practices intro: "Follow these recommendations to maximize productivity, reduce costs, and improve reliability" | CONFIRMED | /compute/serverless/best-practices | 2026-11-12 |
| Streaming: with Trigger.AvailableNow, "limit the amount of data processed per micro-batch by setting maxFilesPerTrigger or maxBytesPerTrigger" (reliability, not cost) | CONFIRMED | /compute/serverless/best-practices | 2026-11-12 |
| Best-practices page cost monitoring list: usage policies, system tables, "Set up budget alerts in your account", "Import a pre-configured usage dashboard" | CONFIRMED | /compute/serverless/best-practices | 2026-11-12 |
| Estimating cost: "Databricks recommends running and benchmarking a representative or specific workload and then analyzing the billing system table." | CONFIRMED | /compute/serverless/ (FAQ) | 2026-11-17 |
| Serverless SQL warehouse Auto Stop: "Idle SQL warehouses continue to accumulate DBU and cloud instance charges until they are stopped." Serverless default "10 minutes, which is recommended for typical use. The minimum is 5 minutes when you use the UI"; API as low as "1 minute" | CONFIRMED | /compute/sql-warehouse/create | 2026-11-20 |
| Warehouse sizing: "Cluster Size... The default is X-Large. To reduce query latency, increase the size." Scaling: "Azure Databricks recommends a cluster for every 10 concurrent queries." | CONFIRMED | /compute/sql-warehouse/create | 2026-11-20 |
| Per-warehouse statement timeout: "you can set with the SQL warehouses API. This option is not available in the UI." | CONFIRMED | /compute/sql-warehouse/create | 2026-11-20 |
| "Assign Can manage to users responsible for SQL warehouse sizing and spend limits decisions." | CONFIRMED | /compute/sql-warehouse/create | 2026-11-20 |
| Idle serverless notebook auto-termination / idle-notebook guidance as a cost lever: not found on pages read | NOT FOUND | /compute/serverless/notebooks | 2026-10-22 |
| Classic vs serverless, notebooks: Serverless "Generally recommended. Offers faster start-up, automatic scaling, and lower cost." Classic all-purpose "When you need RDD APIs or R language support." | CONFIRMED | /compute/choose-compute | 2026-11-17 |
| Classic vs serverless, jobs: Classic jobs compute "For non-SQL jobs that require custom cluster settings not available in serverless."; classic all-purpose "Generally avoid. Not optimized for automated workloads." | CONFIRMED | /compute/choose-compute | 2026-11-17 |
| Classic vs serverless, pipelines: Classic pipeline compute "When you need a feature not supported in serverless or when you are working with the legacy Hive metastore." | CONFIRMED | /compute/choose-compute | 2026-11-17 |
| SQL warehouse types: Serverless "Recommended for BI, ETL, and exploratory analysis. Startup typically 2-6 seconds"; Pro "Use when serverless is not available or you require custom networking" | CONFIRMED | /compute/choose-compute | 2026-11-17 |
| Classic for long runs: "To run workloads longer than 7 days, break them into smaller runs or use classic compute." | CONFIRMED | /compute/serverless/limitations | 2026-11-23 |
| Classic required: "Certain workloads that depend on R or Scala notebooks require classic compute and can't migrate to serverless." | CONFIRMED | /compute/serverless/migration | 2026-11-16 |
| Doc statement that classic is cheaper for steady/predictable workloads: not found | NOT FOUND | /compute/choose-compute | 2026-11-17 |

## Docs sample queries (verbatim)

### Sort serverless notebooks based on total spend
Source: https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/serverless-billing (ms.date 2026-11-19)

```sql
SELECT
 usage_metadata.notebook_id,
 usage_metadata. notebook_path,
 SUM(usage_quantity) as total_dbu
FROM
 system.billing.usage
WHERE
 usage_metadata.notebook_id is not null
 and billing_origin_product = 'INTERACTIVE'
 and product_features.is_serverless
 and usage_unit = 'DBU'
 and usage_date >= DATEADD(day, -30, current_date)
GROUP BY
 1,2
ORDER BY
 total_dbu DESC
```

### Sort serverless jobs based on total spend
Source: same page.

```sql
SELECT
 usage_metadata.job_id,
 usage_metadata.job_name,
 SUM(usage_quantity) as total_dbu
FROM
 system.billing.usage
WHERE
 usage_metadata.job_id is not null
 and usage_unit = 'DBU'
 and usage_date >= DATEADD(day, -30, current_date)
 and sku_name like '%JOBS_SERVERLESS_COMPUTE%'
GROUP BY
 1,2
ORDER BY
 total_dbu DESC
```

### Report on DBUs consumed by performance mode
Source: same page.

```sql
SELECT
 product_features.performance_target,
 billing_origin_product,
 SUM(usage_quantity) as total_dbu
FROM
 system.billing.usage
WHERE
 product_features.is_serverless
 and billing_origin_product in ('JOBS','DLT')
 and usage_unit = 'DBU'
 and usage_date >= DATEADD(day, -30, current_date)
GROUP BY
 1,2
ORDER BY
 total_dbu DESC
```

### Report on workloads sharing a custom tag
Source: same page.

```sql
SELECT
 usage_metadata.job_id,
 usage_metadata.job_name,
 usage_metadata.notebook_id,
 usage_metadata. notebook_path,
 SUM(usage_quantity) as total_dbu
FROM
 system.billing.usage
WHERE
 custom_tags.<key> = '<value>'
 and billing_origin_product in ('JOBS','INTERACTIVE')
 and product_features.is_serverless
 and usage_unit = 'DBU'
 and usage_date >= DATEADD(day, -30, current_date)
GROUP BY
 1,2,3,4
ORDER BY
 total_dbu DESC
```

### Alert when a job exceeds the threshold in the last 30 days
Source: same page.

```sql
SELECT
 t1.workspace_id,
 t1.usage_metadata.job_id,
 SUM(t1.usage_quantity * list_prices.pricing.default) as list_cost
FROM system.billing.usage t1
INNER JOIN system.billing.list_prices on
 t1.cloud = list_prices.cloud and
 t1.sku_name = list_prices.sku_name and
 t1.usage_start_time >= list_prices.price_start_time and
 (t1.usage_end_time <= list_prices.price_end_time or list_prices.price_end_time is null)
WHERE
 t1.sku_name LIKE '%SERVERLESS%'
 AND billing_origin_product IN ("JOBS")
 AND t1.usage_date >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY
 t1.workspace_id, t1.usage_metadata.job_id
HAVING
 list_cost > {budget}
```

### Audit serverless usage by compute object
Source: https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/manage-serverless-compute (ms.date 2026-11-17)

```sql
SELECT
 usage_metadata.serverless_compute_id,
 identity_metadata.run_as,
 SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE billing_origin_product IN ('JOBS', 'DLT', 'INTERACTIVE')
 AND usage_metadata.serverless_compute_id IS NOT NULL
 AND usage_date >= date_add(now(), -30)
GROUP BY 1, 2
ORDER BY 3 DESC;
```

## Added Nov 24, 2026: startup time wording (verified on the pages)

| # | Claim | Status | URL |
| --- | --- | --- | --- |
| S1 | "Standard mode: Best for scheduled and batch jobs and pipelines that can tolerate a typical startup time of 4 to 6 minutes." | Confirmed | https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/best-practices |
| S2 | "For workloads that can tolerate a typical startup time of 4 to 6 minutes, standard mode consumes fewer Databricks units (DBUs) and costs less." | Confirmed | https://learn.microsoft.com/en-us/azure/databricks/jobs/run-serverless-jobs |
| S3 | "For pipelines that can tolerate a typical startup time of 4 to 6 minutes, standard mode consumes fewer Databricks units (DBUs) and costs less." | Confirmed | https://learn.microsoft.com/en-us/azure/databricks/ldp/serverless |
| S4 | "Workloads typically start within 4 to 6 minutes and consume fewer Databricks units (DBUs)." Also "Typically 4 to 6 minutes, depending on compute availability." | Confirmed | https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/performance-modes |
| S5 | Startup time in standard mode depends on compute availability and varies from run to run. | Confirmed (FAQ on the performance-modes page) | https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/performance-modes |
