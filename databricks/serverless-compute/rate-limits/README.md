# Serverless rate limits

A rate limit on serverless compute caps how far the Spark executors of a job or a Lakeflow pipeline can autoscale. This folder runs the same parallel workload on automated serverless compute objects of different sizes, so the effect of the limit can be compared run by run.

A rate limit is not a spend cap. The docs say it does not set a hard limit on total workload cost, and it only covers executor autoscaling of jobs and pipelines. Notebooks, the driver, GPUs and materialized view or streaming table refreshes are not limited.

## What is in this folder

| Path | What it is |
| --- | --- |
| `databricks.yml` | The bundle. It defines one job that runs on a serverless compute object you pass in as `compute_id`. |
| `src/workload.py` | The notebook. It hashes a few hundred million generated rows and aggregates them, which splits into many parallel tasks. It prints the elapsed seconds. |
| `tests/results.md` | Run times for each compute size and what is not covered. |

## Requirements

- A workspace with the Serverless tab under Compute and the Create serverless compute button. The docs say a workspace admin turns the feature on with the Serverless Compute Rate Limit setting on the Previews page, and that creating a compute object needs workspace admin or the unrestricted cluster creation entitlement.
- Databricks CLI 1.24.0 with the direct deployment engine:

```bash
export DATABRICKS_BUNDLE_ENGINE=direct
```

## Reproduce it

1. In Compute, open the Serverless tab and choose Create serverless compute. Give it a name, pick a Size (Small, Medium, Large, X-Large or 2X-Large) and create it. The Default objects cannot be given a rate limit.
2. Open the new object, use the kebab menu and choose Copy compute ID.
3. Deploy the bundle with that id:

```bash
cd databricks/serverless-compute/rate-limits
databricks bundle deploy --var compute_id=<compute id>
```

4. Run the job and read the elapsed seconds from the task output, and the run duration from the job run:

```bash
databricks bundle run rate_limit_workload
```

5. To compare another size, deploy again with the id of the other object and run again. A job can use only one object, so each deploy points the same job at a different one.

The job uses the Jobs API setting `serverless_compute.policy_id` on a job cluster, which the docs describe. The `rows` and `partitions` parameters scale the workload. Start with small values on Free Edition, which limits how much compute you can use.

## Cleanup

Delete the job with `databricks bundle destroy`, then delete the compute objects you created from the Serverless tab.

## Reference

- [Set rate limits on serverless compute](https://learn.microsoft.com/en-us/azure/databricks/compute/serverless/manage-serverless-compute#set-rate-limits-on-serverless-compute), Microsoft Learn
