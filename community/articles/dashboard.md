# How Databricks Dashboards Handle Permissions and Refresh

Co-authored with [Abdul Sajid Mohammed](https://medium.com/@sajidhawk).

Databricks dashboards run every query with someone's permissions and answer it from one of several caches, and the choices you make when you publish decide which. This guide follows an AI/BI dashboard after it is built: you publish it, share it, schedule it and add subscribers. It explains whose credentials run each query, where the results come from, and how to keep the data fresh.

## What happens when a dashboard runs

A published dashboard is a fixed version of a draft that viewers open, filter and refresh. Two things decide what each viewer sees.

- Credentials: with Share data permission, the default, viewers run queries using the publisher's data permissions. With Individual data permission, viewers use their own credentials, and compute access is always granted by the publisher's credentials.
- Results: a dashboard first checks the dashboard cache, then the query result cache. The SQL warehouse starts only when a query cannot be served from the caches.
- Cache audience: with shared permissions all viewers share one cache. With individual permissions each viewer has a per user cache.
- Drafts: viewers always see the last published version. For a draft, the viewer's own data permissions always apply.

## Step 1: Publish the dashboard

Click Publish in the draft. Edits you make to the draft afterward stay invisible to viewers until you publish again. The dialog also shows a Materialize datasets option, marked Beta, which adds a daily schedule. You can also publish with the API. Set `embed_credentials` to `true` for shared data permission and to `false` for individual data permission.

```bash
databricks api post /api/2.0/lakeview/dashboards/<dashboard-id>/published \
  --json '{"embed_credentials": true, "warehouse_id": "<warehouse-id>"}'
```

## Step 2: Choose a data permission option

This choice decides whose credentials run the queries and who can view. The Publish dialog offers Share data permission (default) and Individual data permission. Use the first when many people view the same dashboard and should share one cache. Use the second when each viewer must see only the data they are allowed to see, because row filters and column masks then apply to them. With the default, the Publisher Credential field starts as your user account, and its menu lets you pick a service principal so the dashboard does not depend on one person.

If you republish a dashboard that was published with shared permissions and choose Individual data permission, the dialog warns that the action pauses all schedules and removes all subscribers. A test confirmed the warning is accurate.

## Step 3: Share the dashboard

Click Share and add users, groups or service principals with one of four levels. CAN VIEW and CAN RUN can view, interact with and refresh the dashboard. CAN EDIT adds editing and publishing. CAN MANAGE adds changing permissions and deleting the dashboard. To share with everyone in your account, set Sharing settings to "Anyone in my account can view". Users without workspace access are limited to CAN RUN, they cannot open the draft, and they use the publisher's credentials to reach compute.

## Step 4: Set a schedule

A schedule is the reliable way to refresh the dashboard cache. Open the published dashboard, click Schedule, choose Add schedule, and pick the frequency, start time and time zone. Under Advanced settings, choose the SQL warehouse for the run. Select "Use current filter selections" if you want the snapshot to keep the current filters. Click Create. Run now runs the schedule once without changing its regular cadence.

## Step 5: Add subscribers

In the schedule's advanced settings, choose subscribers and, if you want, attachments. Email subscribers receive a PDF snapshot, with optional CSV, TSV or Excel data attachments. A subscription list can hold up to 100 subscribers, and attachments over 9 MB are not included.

## Example: refresh a dashboard after new data arrives

A sales table feeds a dashboard. New rows arrive, but viewers keep the numbers from the cache.

```sql
INSERT INTO <catalog>.dash_demo.sales
SELECT 1000 + id, 'North', 'Laptop', 1000, DATE'2026-11-20' FROM range(0, 10);
```

After this insert, reopening the published dashboard still shows 50 orders and 14,600 in revenue for North. Clicking Refresh shows 60 orders and 24,600. With a second insert of 5 West rows, Run now on the schedule refreshed the dashboard, and reopening it showed West at 55 orders without clicking Refresh.

## Things to know

- The dashboard cache can be up to 24 hours old. A change to the table does not refresh it, and a pipeline step does not either. Add a schedule if viewers must see current data.
- Choose the permission option before you set up subscribers. Switching to Individual data permission removes them.
- Share data permission can expose data. Folders pass their permissions down, so keep dashboards that use shared permissions in a folder only the right people can reach.
- Account users have limits. They cannot see data from workspace-bound catalogs, so widgets that query them show no data. Do not publish such dashboards to account-wide audiences.
- Drafts always use the viewer's permissions, so check the draft as an ordinary viewer before you publish.
- The Refresh button runs the queries again. The documentation pages I read do not describe it, but in testing it showed new rows straight away.

## Best practices

- Schedule the dashboard right after the pipeline that feeds it.
- Publish production dashboards with a service principal as the Publisher Credential.
- Choose Individual data permission for data with row filters or column masks.
- Test the dashboard as a viewer with the lowest permission level you plan to grant, and open the published version, not only the draft.

Full article: [How Databricks Dashboards Handle Permissions and Refresh](https://medium.com/@nagarajubru/databricks-dashboards-permissions-refresh-553e82f3e4a1)

Code and test notes: [dashboard folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/dashboard)
