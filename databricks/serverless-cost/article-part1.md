# Databricks Serverless Jobs: What Happens When You Press Run

Subtitle: Follow a Databricks serverless job from the Run click to its billing record in six steps, and learn what runs where and which settings change.

Databricks serverless jobs run on compute that Databricks creates, sizes and upgrades for you, so there is no cluster to configure. This guide follows one job from the moment you press Run to its record in the billing table, in six steps. Along the way you see where each part runs, which settings you give up and what to check before you move a job to serverless. Part 2 covers how to make serverless jobs cost less. The complete code for this guide is on GitHub: [serverless-cost](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/serverless-cost).

[VIDEO: add the Part 1 video link here]
Caption: What happens when you run a serverless job, in a short video, part 1 of 2.

Part 2 is [Cut Databricks Serverless Job Costs with Standard Mode](add the Part 2 link after publishing).

## Databricks serverless compute at a glance

Serverless compute is a managed service that connects notebooks, jobs and Lakeflow pipelines to on-demand compute. You run workloads without provisioning compute in your cloud account, and Databricks allocates and manages the resources instead.

| | Classic compute | Serverless compute |
| --- | --- | --- |
| Machine size and type | You pick the instance types for the driver and the workers. | Databricks optimizes infrastructure such as instance types, memory and processing engines. |
| Runtime version | You select a Databricks Runtime version. | Databricks upgrades the runtime. You choose an environment version for the client side. |
| Starting and stopping | You set an inactivity period for automatic termination. | Databricks allocates and manages the compute. Start-up depends on the performance mode of the job. |
| Scaling | You set a minimum and maximum number of workers. | Databricks scales the compute for you. |
| Where the machines live | In your Azure subscription, in the classic compute plane. | In the serverless compute plane in your Azure Databricks account, in the same region as your workspace. |

Serverless compute is available by default in most workspaces and needs no enablement.

## When to use Databricks serverless jobs

Use serverless for jobs when you want to run work without sizing, starting and upgrading compute yourself. The compute guide describes serverless as generally recommended, with faster start-up, automatic scaling and lower cost.

Use classic compute when a job needs something serverless does not offer: custom cluster settings, RDD APIs, R or Scala notebooks, or a run longer than 7 days.

## Prerequisites

- A workspace with Unity Catalog enabled, in a supported region for serverless compute.
- Permission to create and run jobs.
- Code that works with standard access mode, because serverless jobs use it.

## Step-by-step: what happens when you press Run

The diagram shows the six steps in order.

[image: run-steps.png | Caption: The six steps a serverless job goes through, from the Run click to the billing record. | Alt: A flow diagram with six numbered boxes: run scheduled, compute found, code connects to Spark, code runs in its own space, job reads data, usage recorded.]

### Step 1: The run is scheduled

Pressing Run sends the request to the control plane, the backend services that Azure Databricks manages in your Azure Databricks account, including the web application. The control plane does not process your data, because data is processed in the compute plane. Job run results are stored as workspace system data.

### Step 2: Compute is found

The work runs in the serverless compute plane. It runs in your Azure Databricks account, in the same Azure region as your workspace, and it sits inside a network boundary for your workspace that isolates it from other customers' workspaces. The control plane and the serverless compute plane talk over the cloud network backbone, not the public internet.

How fast compute is found depends on the performance mode of the job. Performance optimized mode keeps warm compute ready, and standard mode waits for compute to become available. Part 2 measures the difference.

### Step 3: Your code connects to Spark

Your code is the client, and Spark Connect carries its requests to a Spark server that Databricks runs. You choose an environment version, which fixes the Python version and the package versions, and Databricks upgrades the server without changes to your code. This is why serverless has no runtime version to pick: workloads always run on the latest runtime.

To pin the client side for a job, set the environment version in the job's environment settings.

### Step 4: Your code runs in its own space

Lakeguard isolates user code from the Spark engine and from other users, with secure containers. This isolation is why serverless limits some settings.

- Most Spark compute configurations cannot be set. Setting one fails, as the example below shows.
- The Spark UI is not available. Use the query profile instead.
- Spark Connect defers analysis and name resolution to execution time, which can change how your code behaves compared with classic compute.

### Step 5: The job reads your data

Access to data goes through Unity Catalog. For data outside your workspace, you use Unity Catalog external locations for cloud storage.

Serverless compute does not support the network peering that classic compute uses. To reach a resource that sits behind a firewall, add the Azure Databricks outbound IP set to the allowlist and automate keeping it current, or use a network connectivity configuration (NCC). An NCC is an account-level regional setting that manages private endpoints from serverless compute to your Azure resources.

### Step 6: The usage is recorded

Databricks writes the usage of the run to `system.billing.usage`. Each record has the amount in `usage_quantity`, the job in `usage_metadata.job_id`, the run in `usage_metadata.job_run_id`, the performance mode in `product_features.performance_target` and your tags in `custom_tags`.

```sql
SELECT usage_start_time,
       usage_end_time,
       billing_origin_product,
       usage_metadata.job_id,
       product_features.performance_target AS performance_mode,
       ROUND(usage_quantity, 4) AS usage_quantity
FROM system.billing.usage
WHERE usage_metadata.job_run_id = '<run-id>'
ORDER BY usage_start_time;
```

Records are typically available within 12 hours. The billing table can also contain correction records, so sum `usage_quantity` instead of reading single rows.

## Example: follow one job through the six steps

The example job is a serverless notebook task in the bundle in the repository. It generates 18 billion rows, aggregates them by customer and writes a table, and it runs for about two and a half minutes.

[image: 01-run-page.png | Caption: The run list of the example job, with the duration of each run. | Alt: The Runs chart and run list of a job in the Jobs UI, with one green bar for each successful run and the duration of each run in the table.]

Steps 1 and 2 happen when you start the run: the control plane takes the request and the serverless compute plane runs the task. In step 4, a Spark setting that classic compute accepts is refused. This task tries to set the executor memory:

```python
spark.conf.set("spark.executor.memory", "8g")
```

The run returns this error:

```
AnalysisException: [CONFIG_NOT_AVAILABLE.WITHOUT_SUGGESTION] Configuration spark.executor.memory is not available.  SQLSTATE: 42K0I
```

In step 6, the query from above returns the usage of the run.

[image: 02-billing-record.png | Caption: The usage records of one run in system.billing.usage. | Alt: A query result with three rows for one job run, each with a start time, an end time, the product JOBS, the performance mode and a usage quantity of a few tenths of a DBU.]

The records add up to 1.3701 DBUs for this run. In our tests, records appeared between about 3 and 12 hours after the runs.

The full example, including setup and cleanup, is in the [serverless-cost](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/serverless-cost) folder of the repository.

## Things to know

- Remove Spark settings from your code before you move a job to serverless. Most Spark compute configurations are not available, and setting one raises an error. The documentation lists the supported ones in the page on Spark properties for serverless notebooks and jobs.
- Use the query profile in place of the Spark UI. The Spark UI and Spark logs are not available on serverless, and you only get client-side application logs.
- Plan network access before the first run. Serverless compute does not support network peering, so allowlist the outbound IP set or attach a network connectivity configuration.
- Wait before you check the cost of a run. Records in `system.billing.usage` can take several hours to arrive, and corrections arrive as extra records, so aggregate `usage_quantity` per run.
- Split work that needs more than 7 days. Serverless compute has a maximum runtime of 7 days, and the platform ends longer runs.

## Best practices

- Run a representative job on serverless and read its usage records before you migrate the rest.
- Pin an environment version for jobs that must behave the same over time.
- Keep data access in Unity Catalog, with external locations for cloud storage, so serverless jobs follow the same permissions as everything else.
- Tag serverless work with a serverless usage policy so its cost can be attributed.

## Summary

A serverless job goes through six steps: the control plane takes the run, the serverless compute plane runs it, your code connects through Spark Connect, Lakeguard isolates it, Unity Catalog governs the data and the usage lands in `system.billing.usage`. The main takeaway is that serverless removes compute choices, so you move Spark settings, network access and cost checks to the places the steps above describe. Use serverless jobs when you want Databricks to manage the compute, and read Part 2 to see how the performance mode changes what a run costs.

Which of the six steps surprised you most?

## References

- [High-level architecture](https://learn.microsoft.com/en-us/azure/databricks/getting-started/high-level-architecture), Microsoft Learn
- [Connect to serverless compute](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/), Microsoft Learn
- [Serverless compute limitations](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/limitations), Microsoft Learn
- [Serverless compute best practices](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/best-practices), Microsoft Learn
- [Serverless environment versions](https://learn.microsoft.com/en-us/azure/databricks/release-notes/serverless/environment-version/), Microsoft Learn
- [How does Databricks enforce user isolation?](https://learn.microsoft.com/en-us/azure/databricks/compute/lakeguard), Microsoft Learn
- [Serverless network security](https://learn.microsoft.com/en-us/azure/databricks/security/network/serverless-network-security/), Microsoft Learn
- [Billable usage system table reference](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing), Microsoft Learn
- [Compute configuration reference](https://learn.microsoft.com/en-us/azure/databricks/compute/configure), Microsoft Learn
- [Choose the right compute](https://learn.microsoft.com/en-us/azure/databricks/compute/choose-compute), Microsoft Learn

## Medium settings

- SEO title: Databricks Serverless Jobs: What Happens When You Press Run
- SEO description: same as the subtitle
- Slug: databricks-serverless-jobs-what-happens-when-you-press-run
- Tags: Databricks, Data Engineering, Serverless, Cloud Computing, Azure
