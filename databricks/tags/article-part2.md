# Databricks Cost Tags Explained: Default, Custom, Serverless

Subtitle: Databricks cost tags attribute spend to teams and projects. Learn default, custom and usage policy tags, and where they show up in billing and budgets.

Databricks cost tags attribute compute spend to teams, projects and workloads, and they come as default tags, custom tags and serverless usage policy tags. A tag on compute never controls who sees data, and a tag on a table never shows up in the bill, because cost tags and data tags are two separate systems. This guide, part 2 of 2, covers cost tags: where they are set, what they do and how to read them in `system.billing.usage`, budgets and Azure cost analysis. The complete code for this guide is on GitHub: [tags](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/tags).

[VIDEO: https://www.youtube.com/watch?v=SKvkbf36WQQ]
Caption: Cost tags explained in a short video, part 2 of 2.

Part 1 covers data tags: [Databricks Data Tags Explained: Regular, Governed, System](PART1_LINK).

[image: data-vs-cost-tags.png | Caption: Cost tags and data tags are two separate systems. | Alt: A table comparing data tags and cost tags. It has four rows: what they label, who sets them, where you see them and what they are for.]

## What are cost tags in Databricks

Cost tags are key-value pairs on compute resources and serverless workloads, and Databricks carries them into your usage records so you can see which team or project spent what. There are two kinds on classic compute and SQL warehouses, and a third for serverless.

- Default tags are added automatically by Databricks. They propagate to the detailed cost analysis reports in the Azure portal.
- Custom tags are tags you define on workspaces, pools, clusters, SQL warehouses and jobs. They reach your account's usage logs and the cloud resources, and you use them to build and monitor budgets.
- Usage policy tags are custom tags that a serverless usage policy adds to serverless workloads. Serverless usage policies are in Public Preview, and some pages and URLs still call them budget policies.
- Budgets can be scoped by custom tags. Budget threshold webhooks are in Beta.

The diagram shows where each kind of tag ends up.

[image: cost-tags-overview.png | Caption: Default, custom and usage policy tags, and where they end up. | Alt: A flow diagram. Default tags go to Azure cost analysis. Custom tags and usage policy tags go to the custom_tags column of system.billing.usage and to Azure cost analysis. The usage table feeds budgets scoped by custom tags.]

## When to use cost tags

Use cost tags when you need to answer "who spent this" for compute: split the bill by team, project or environment, scope a budget to one team, or find the job that cost the most. Tag every shared resource with the owner, and use a serverless usage policy for serverless notebooks, jobs and pipelines, because those workloads are not tagged any other way.

Cost tags do not control access and they do not label data. To mark a table as sensitive, to find tables by owner, or to drive an access policy, use the data tags from part 1.

## Prerequisites

- To add custom tags, you need permission to edit the compute, SQL warehouse, pool or job. Workspace tags are set in the Azure portal.
- To create serverless usage policies, you must be a workspace admin. A user can manage a policy if they have the Manager permission on it.
- To create a budget, you must be an account admin.
- Read access to `system.billing.usage` to query the tags.

## Step 1: Know the default tags

Databricks adds default tags for you, and the keys depend on the compute type.

| Compute | Default tags |
| --- | --- |
| All-purpose and jobs compute | Vendor, ClusterId, ClusterName, Creator. Jobs compute also has RunName and JobId. |
| SQL warehouses | Vendor, ClusterId, SqlEndpointId, Creator |
| Pools, and compute created from them | Vendor, DatabricksInstancePoolId, DatabricksInstancePoolCreatorId |

Default tags propagate to the detailed cost analysis reports in the Azure portal, so a report grouped by the `ClusterId` tag works without any setup.

## Step 2: Add custom tags

Custom tags are yours, so you choose the keys. Each compute type has its own place for them.

- Clusters: the Tags section when you create or edit the compute.
- SQL warehouses: Advanced options when you create or edit the warehouse, or the Warehouses API.
- Pools: the Tags tab at the bottom of the Create Pool page. A pool supports up to 41 custom tags.
- Jobs: the Tags field in the Job details side panel, or the `tags` field in the Jobs API.

This example creates a job with two tags through the Jobs API. The notebook path is a placeholder.

```bash
databricks api post /api/2.2/jobs/create --json '{
  "name": "tags-demo-job",
  "tags": {"team": "data_platform", "project": "tags_demo"},
  "tasks": [{"task_key": "run", "notebook_task": {"notebook_path": "<notebook path>"}}]
}'
```

The job page shows both tags in the Tags section.

[image: 14-job-custom-tags.png | Caption: The job details show the two custom tags. | Alt: The Tags section of a job page with two tags, project tags_demo and team data_platform.]

An Azure resource can carry no more than 50 tags. Tag keys and values can contain letters, spaces, numbers and the characters + - = . _ : / @. Tag data is stored as plain text, so keep personal and sensitive values out of tags.

## Step 3: Avoid the default tag names

A custom tag must not reuse a default tag's key. What happens depends on where you set it.

- Workspace, cluster and pool tags with a default key are renamed during propagation: the custom tag gets an `x_` prefix, and the default tag keeps its own name.
- Tags added through a compute policy are not renamed. The cluster or pool fails with an invalid settings error.
- A job tag with a default key is rejected when you create the job:

```
Error: Invalid tags - the following custom keys conflict with the keys of Databricks default tags: Vendor.
```

Pick keys that do not match a default tag, such as `team`, `project` or `cost_center`.

## Step 4: Tag serverless workloads with a usage policy

Serverless compute has no cluster to tag, so you attach tags to the workload with a serverless usage policy. A policy is a named set of custom tags, and it covers serverless notebooks, jobs, pipelines, model serving endpoints, apps and Lakebase Autoscaling projects. Serverless usage policies are in Public Preview. They are also called budget policies, and the documentation URLs still use that name.

1. A workspace admin opens Settings, then Compute, and next to Serverless usage policies chooses Manage, then Create.
2. Give the policy a name, choose the workspaces it applies to (none selected means all workspaces in the account) and add the custom tags.
3. On the Permissions tab, grant the User role to the users, groups or service principals who may select it. The Manager role also lets them edit the policy.

A user with one policy gets it applied automatically to new resources. A user with several must pick one, and if none is picked the first policy alphabetically applies. Existing notebooks, jobs and pipelines are not assigned a policy automatically, so set the policy on each asset. If a notebook runs as part of a job, only the job's policy applies, and a pipeline that a job triggers does not inherit the job's policy.

## Step 5: Enforce tags

To require a tag on classic compute, write a compute policy with a `custom_tags.<tag-name>` rule. This policy limits the `COST_CENTER` tag to three values.

```json
{
  "custom_tags.COST_CENTER": {
    "type": "allowlist",
    "values": ["9999", "9921", "9531"]
  }
}
```

To enforce custom tags on serverless workloads, use serverless usage policies, as the documentation recommends.

## Step 6: Read the tags in billing

`system.billing.usage` has a `custom_tags` map column. It holds the tags applied to the compute resource and the tags that serverless usage policies add. Records can take several hours to arrive, so a workload you ran this morning may not be there yet.

```sql
SELECT custom_tags['project'] AS project,
       billing_origin_product,
       ROUND(SUM(usage_quantity), 4) AS dbus
FROM system.billing.usage
WHERE usage_date >= DATE'2026-11-01'
  AND custom_tags['project'] IS NOT NULL
GROUP BY ALL
ORDER BY dbus DESC;
```

[image: 18-billing-custom-tags.png | Caption: Usage grouped by the project tag. | Alt: The SQL editor with a query on system.billing.usage grouped by the project tag. One result row shows job-completion-triggers, JOBS and 1.1015 DBUs.]

The usage metadata columns tell you which object produced the usage. For a serverless usage policy, `usage_metadata.usage_policy_id` holds the policy ID.

## Step 7: Scope budgets and read Azure cost analysis

A budget can be limited by product, workspace and custom tags. In the budget's Resource tags section you pick the custom tags, and the budget then tracks only usage that has them. Default tags are not part of this, and only an account admin can create a budget. Budget threshold webhooks are in Beta.

Azure cost analysis shows more than the usage table does. Default tags and serverless usage policy tags go to the billing records in Azure cost analysis. Workspace, pool and cluster custom tags are assigned as resource tags on the Azure VMs that host the clusters.

## Example: split job cost by project

A team runs several jobs and wants the cost of each project. Each job carries a `project` tag, and the query in Step 6 groups the usage by that tag. In the test, the jobs of one bundle carried the project tag `job-completion-triggers`, and the query returned one row for it: JOBS usage of 1.1015 DBUs.

The two tag systems stay apart. The table tags from part 1, `cost_center`, `domain`, `pii` and the rest, are not among the keys in `custom_tags`, and a tag on a job never shows up on a table. Use this query to list the keys that do appear.

```sql
SELECT k AS tag_key, COUNT(*) AS records
FROM (SELECT EXPLODE(MAP_KEYS(custom_tags)) AS k
      FROM system.billing.usage WHERE custom_tags IS NOT NULL)
GROUP BY k
ORDER BY records DESC;
```

The full example, including setup and cleanup, is in the [tags](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/tags) folder of the repository.

## Things to know

- Tag changes are not retroactive. A change to compute tags applies after the compute restarts or the pool expands, and a usage policy change applies only to usage that starts after the update. A change to a workspace tag can take up to one hour to propagate.
- Clusters created from a pool pass only the workspace and pool tags to the VMs. Cluster tags on those clusters appear in DBU usage reports but not on the cloud resources.
- Tags from a serverless usage policy do not appear in the Jobs list, and the policies do not tag classic compute.
- Budgets use the list price in US dollars and ignore credits and negotiated discounts.
- Records in `system.billing.usage` can take several hours to arrive, and a budget email can lag usage by up to 24 hours.

## Best practices

- Agree on a small set of tag keys, such as `team` and `project`, and apply them to every compute resource and job.
- Use a serverless usage policy for each team, and grant it to the team's group.
- Require the tags with a compute policy for classic compute, and with a usage policy for serverless workloads.
- Avoid the default tag names, so you never depend on the `x_` prefix.

## Summary

Cost tags attribute compute spend: default tags come from Databricks, custom tags come from you, and serverless usage policies tag serverless workloads. The main point is that cost tags reach `system.billing.usage`, budgets and Azure cost analysis, and they never touch your data tags. Use them when you need to answer which team or project spent what.

Which tag would you add to your jobs first?

## References

- [Use tags to attribute and track usage](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/usage-detail-tags), Microsoft Learn
- [Attribute usage with serverless usage policies](https://learn.microsoft.com/en-us/azure/databricks/admin/usage/budget-policies), Microsoft Learn
- [Billable usage system table reference](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing), Microsoft Learn
- [Create and monitor budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets), Microsoft Learn
- [Compute policy reference](https://learn.microsoft.com/en-us/azure/databricks/admin/clusters/policy-definition), Microsoft Learn
- [Compute configuration reference](https://learn.microsoft.com/en-us/azure/databricks/compute/configure), Microsoft Learn

## Medium settings

- SEO title: Databricks Cost Tags Explained: Default, Custom, Serverless
- SEO description: same as the subtitle
- Slug: databricks-cost-tags-default-custom-serverless
- Tags: Databricks, Data Engineering, FinOps, Cost Management, Azure
