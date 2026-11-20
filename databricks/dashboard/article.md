# How Databricks Dashboards Handle Permissions and Refresh

Subtitle: What happens when you publish, share and schedule a Databricks dashboard: whose permissions run the queries, which cache answers, and how to keep it fresh.

Co-authored with [Abdul Sajid Mohammed](https://medium.com/@sajidhawk).

Databricks dashboards run every query with someone's permissions and answer it from one of several caches, and the choices you make when you publish decide which. This guide follows an AI/BI dashboard after it is built: you publish it, share it, schedule it and add subscribers. It explains whose credentials run each query, where the results come from, and how to keep the data fresh. The complete code for this guide is on GitHub: [dashboard](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/dashboard).

[VIDEO: https://www.youtube.com/watch?v=yQTWy0OZFVc]
Caption: A short visual tour of how publishing, permissions and refresh fit together.

## What happens behind the scenes when a dashboard runs

A published AI/BI dashboard is a fixed version of a draft that viewers open, filter and refresh. Two things decide what each viewer sees: whose credentials run each query, and where the results come from.

- Credentials: with Share data permission, the default, viewers run queries using the publisher's data permissions. With Individual data permission, viewers run queries using their own credentials, and compute access is always granted by the publisher's credentials.
- Results: a dashboard first checks the dashboard cache, then the query result cache. The SQL warehouse starts only when a dashboard runs a query that the caches cannot serve. For small datasets, filtering and aggregation also run in your browser after the first load.
- Cache audience: with shared permissions all viewers share one cache and see the same results. With individual permissions each viewer has a per user cache.
- Drafts and published versions: viewers always see the last published version. For a draft, the viewer's own data permissions always apply.

The diagram shows the life of a dashboard from draft to snapshot.

[image: dashboard-lifecycle.png | Caption: The life of a dashboard: draft, publish, share, and the three ways its data is refreshed. | Alt: A flow diagram. A draft is published with either shared or individual data permissions. Both lead to sharing. From sharing, one path is a viewer opening the dashboard, which uses the dashboard cache, then the query result cache, then the SQL warehouse. The other path is a schedule run, which refreshes the dashboard cache and sends a PDF snapshot to subscribers.]

## When to use each publish option

Use Share data permission when many people view the same dashboard and you want one shared cache. Viewers see the same results, and they do not need access to the underlying tables. Use Individual data permission when each viewer must see only the data they are allowed to see, because queries then run with their own credentials and row filters and column masks apply to them.

The shared option can expose data to people who have no direct access to it, so check who the dashboard is shared with before you publish. The table compares the two options.

[image: publish-options.png | Caption: Share data permission and Individual data permission compared. | Alt: A table with two columns, Share data permission and Individual data permission, and rows for who runs queries, whose data permissions apply, compute, who can view, cache and best for.]

## Prerequisites

- A dashboard with at least one dataset, and a SQL warehouse to run its queries.
- CAN EDIT or CAN MANAGE on the dashboard to publish it.
- For account-wide sharing: users who a workspace administrator has registered with your Azure Databricks account.
- For email subscriptions: a workspace admin has left "Enable dashboard email subscriptions" on. Subscribers are workspace users or email notification destinations that a workspace admin has defined.

## Step 1: Publish the dashboard

Publishing creates the version your viewers see. Click Publish in the draft. Edits you make to the draft afterward stay invisible to viewers until you publish again. The dialog also shows a Materialize datasets option, marked Beta, which adds a daily schedule.

You can also publish with the API. Set `embed_credentials` to `true` for shared data permission and to `false` for individual data permission.

```bash
databricks api post /api/2.0/lakeview/dashboards/<dashboard-id>/published \
  --json '{"embed_credentials": true, "warehouse_id": "<warehouse-id>"}'
```

## Step 2: Choose a data permission option

This choice decides whose credentials run the queries and who can view. The Publish dialog offers Share data permission (default) and Individual data permission. With the default, the Publisher Credential field shows the credential used for every viewer's queries. It starts as your user account, and its menu lets you pick a service principal instead, so the dashboard does not depend on one person's account.

[image: 01-publish-dialog-shared.png | Caption: The Publish dialog with Share data permission selected. | Alt: The Publish dialog with two cards. The first card, Share data permission (default), shows a Publisher Credential field. The second card is Individual data permission.]

If you republish a dashboard that was published with shared permissions and choose Individual data permission, the dialog warns that the action pauses all schedules for the dashboard and removes all subscribers.

[image: 02-publish-dialog-individual.png | Caption: Switching to Individual data permission warns that schedules are paused and subscribers are removed. | Alt: The Publish dialog with Individual data permission selected and a red warning that the action will pause all schedules for the dashboard and remove all subscribers.]

## Step 3: Share the dashboard

Sharing decides who can open the dashboard and what they can do. Click Share and add users, groups or service principals with one of four levels. CAN VIEW and CAN RUN can view, interact with and refresh the dashboard. CAN EDIT adds editing and publishing. CAN MANAGE adds changing permissions and deleting the dashboard.

[image: 04-share-dialog-permission-levels.png | Caption: The four permission levels in the Sharing dialog. | Alt: The Sharing dialog with a permission menu open. The levels are Can Manage, Can Edit, Can Run and Can View.]

To share with everyone in your Azure Databricks account, set Sharing settings to "Anyone in my account can view". Users who do not have access to the workspace are limited to CAN RUN, and they cannot open the draft. They use the publisher's credentials to reach compute.

## Step 4: Set a schedule

A schedule is the reliable way to refresh the dashboard cache. Open the published dashboard, click Schedule and choose Add schedule. Pick the frequency, start time and time zone. Under Advanced settings, choose the SQL warehouse for the run and, if you want, select "Use current filter selections". Click Create. Run now runs the schedule once without changing its regular cadence.

[image: 06-schedule-dialog.png | Caption: The Add schedule dialog with its advanced settings. | Alt: The Add schedule dialog. It shows the frequency, time and time zone, and under advanced settings a name, a SQL warehouse, a filter selection checkbox, a custom email subject, subscribers and attachments.]

## Step 5: Add subscribers

Subscribers receive a snapshot each time the schedule runs. In the schedule's advanced settings, choose subscribers and, if you want, attachments. Email subscribers receive a PDF snapshot, with optional CSV, TSV or Excel data attachments. A subscription list can hold up to 100 subscribers, and attachments over 9 MB are not included.

Each run shows an indicator that reports whether it succeeded, failed or was skipped.

[image: 06b-schedule-run-history.png | Caption: The Schedules panel after a run, with its subscriber count and run indicators. | Alt: The Schedules panel with one schedule, one subscriber, four empty indicators and a green check for the last run.]

## Example: refresh a sales dashboard after new data arrives

A sales table feeds a dashboard with two datasets, a Region filter and a Minimum amount parameter. New rows arrive, but viewers keep the numbers from the cache until it is refreshed. The setup SQL creates the table, and a second statement stands in for a pipeline run.

```sql
INSERT INTO <catalog>.dash_demo.sales
SELECT 1000 + id, 'North', 'Laptop', 1000, DATE'2026-11-20' FROM range(0, 10);
```

After this insert, reopening the published dashboard still shows 50 orders and 14,600 in revenue for North. Clicking Refresh on the dashboard shows 60 orders and 24,600.

For the scheduled path, a second insert adds 5 West rows.

```sql
INSERT INTO <catalog>.dash_demo.sales
SELECT 2000 + id, 'West', 'Phone', 2000, DATE'2026-11-20' FROM range(0, 5);
```

After Run now on the schedule, reopening the dashboard shows West at 55 orders and 22,950 without clicking Refresh.

The full example, including setup and cleanup, is in the [dashboard](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/dashboard) folder of the repository.

## Things to know

- Drafts always use the viewer's permissions. Even when a dashboard is published with shared permissions, anyone opening the draft runs queries with their own data permissions, so check the draft as an ordinary viewer before you publish.
- Share data permission can expose data. Folders pass their permissions down, so anyone with access to the folder that holds the dashboard can also open it. Keep dashboards that use shared permissions in a folder only the right people can reach, and grant access to the dashboard itself.
- Account users have limits. Users without workspace access are limited to CAN RUN, and account users cannot see data from workspace-bound catalogs. Widgets that query them show no data, so do not publish such dashboards to account-wide audiences.
- The dashboard cache can be up to 24 hours old. A change to the table does not refresh it, and a pipeline step that refreshes the data does not refresh it either. Add a schedule if viewers must see current data.
- Choose the permission option before you set up subscribers. Switching a published dashboard from Share data permission to Individual data permission pauses all its schedules and removes all its subscribers. The Publish dialog warns about this, and testing confirmed it. Settle on the option first, then add the schedule and the subscribers.
- The Refresh button on a published dashboard runs the queries again. The documentation pages read do not describe it, but in testing it showed new rows straight away. Use it to check the latest data yourself, and use a schedule for everyone else.

## Best practices

- Schedule the dashboard right after the pipeline that feeds it, for example 15 minutes after the pipeline normally finishes, so the cache is refreshed with the new data.
- Publish production dashboards with a service principal as the Publisher Credential, so the dashboard does not stop working when one person's account changes.
- Choose Individual data permission for any dashboard that shows data with row filters or column masks.
- Test the dashboard as a viewer with the lowest permission level you plan to grant, and open the published version, not only the draft.

## Summary

A Databricks dashboard runs its queries with the publisher's credentials or the viewer's own, depending on the publish option, and it answers from the dashboard cache, the query result cache or the SQL warehouse. The main takeaway is that the dashboard cache can be up to 24 hours old and only a schedule refreshes it reliably. Publish with the option that matches who may see the data, then schedule the dashboard right after the pipeline that feeds it.

What is the first dashboard in your workspace that should have a schedule?

## References

- [Share a dashboard](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/share), Microsoft Learn
- [Dashboard concepts](https://learn.microsoft.com/en-us/azure/databricks/dashboards/concepts), Microsoft Learn
- [Dataset optimization and caching](https://learn.microsoft.com/en-us/azure/databricks/dashboards/caching), Microsoft Learn
- [Manage scheduled dashboard updates and subscriptions](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/schedule-subscribe), Microsoft Learn
- [Dashboard limits](https://learn.microsoft.com/en-us/azure/databricks/dashboards/limits), Microsoft Learn
- [Access control lists](https://learn.microsoft.com/en-us/azure/databricks/security/auth/access-control/), Microsoft Learn
- [AI/BI administration guide](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/admin/), Microsoft Learn
- [What is consumer access?](https://learn.microsoft.com/en-us/azure/databricks/ai-bi/consumers/), Microsoft Learn

## Medium settings

- SEO title: How Databricks Dashboards Handle Permissions and Refresh
- SEO description: same as the subtitle
- Slug: databricks-dashboards-permissions-refresh
- Tags: Databricks, Data Engineering, Dashboards, Business Intelligence, SQL
