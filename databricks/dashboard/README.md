# How Databricks dashboards handle permissions and refresh

This folder holds the test data, the dashboard definition and the diagrams for the article on how AI/BI dashboards handle permissions and refresh: whose credentials run the queries, which cache answers, and how a schedule keeps a dashboard fresh.

The behavior described comes from the Azure Databricks documentation, listed in `notes/facts.md`, and was confirmed with a small test dashboard. The test notes are in `tests/results.md`.

## What is in this folder

| Path | What it holds |
| --- | --- |
| `sql/01_setup.sql` | Creates the `dash_demo` schema and a 200 row `sales` table |
| `sql/02_add_rows.sql` | Adds rows to the table, as a stand-in for a pipeline run |
| `sql/03_cleanup.sql` | Drops the table and the schema |
| `dashboard/dash_demo_sales.lvdash.json` | The dashboard: two datasets, one Region filter, one Minimum amount parameter and two tables |
| `diagrams/dashboard-lifecycle.mmd` | Mermaid source for the lifecycle diagram, with the exported PNG |
| `diagrams/publish-options.html` | Source of the comparison table image of the two publish options, with the exported PNG |
| `notes/facts.md` | The fact sheet, one line per claim with its documentation page |
| `tests/results.md` and `tests/screenshots/` | The exact test results and screenshots |

## Prerequisites

- A Unity Catalog catalog where you can create a schema and a table.
- A SQL warehouse.
- The Databricks CLI, configured for your workspace, and `jq`.

## Setup

1. Run `sql/01_setup.sql` in a SQL editor, with `<catalog>` replaced by your catalog.
2. Import the dashboard. Set the three variables first.

```bash
CATALOG=<catalog>
WAREHOUSE_ID=<warehouse-id>
USER_NAME=<user>

sed "s/<catalog>/$CATALOG/g" dashboard/dash_demo_sales.lvdash.json > /tmp/dash.json

jq -n --rawfile d /tmp/dash.json \
  --arg wh "$WAREHOUSE_ID" \
  --arg path "/Workspace/Users/$USER_NAME" \
  '{display_name: "dash_demo_sales", warehouse_id: $wh, parent_path: $path, serialized_dashboard: $d}' \
  > /tmp/dash_create.json

databricks api post /api/2.0/lakeview/dashboards --json @/tmp/dash_create.json
```

The `sed` command writes your catalog name into the dataset queries.

## How to run

1. Open the dashboard, click Publish, and keep Share data permission selected.
2. Run `sql/02_add_rows.sql`.
3. Reopen the published dashboard. It still shows the old numbers, because the dashboard cache can be up to 24 hours old.
4. Click Refresh on the dashboard, or add a schedule and choose Run now. The new rows appear.

To publish from the API, set `embed_credentials` to `true` for shared data permission and to `false` for individual data permission.

```bash
databricks api post /api/2.0/lakeview/dashboards/<dashboard-id>/published \
  --json '{"embed_credentials": true, "warehouse_id": "<warehouse-id>"}'
```

## Expected result

- Before a refresh, the North row shows 50 orders and 14,600 in revenue. After the 10 new North rows and a refresh, it shows 60 orders and 24,600.
- After the 5 new West rows and Run now on a schedule, the West row shows 55 orders and 22,950.
- A schedule with a subscriber sends an email with the subject "Dashboard snapshot: dash_demo_sales" and a PDF attachment.
- Publishing with Individual data permission after Share data permission pauses the schedules and removes the subscribers.

## Cleanup

Delete the dashboard from the Dashboards page, then run `sql/03_cleanup.sql`.

## References

- [Share a dashboard](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/share)
- [Dataset optimization and caching](https://learn.microsoft.com/en-us/azure/databricks/dashboards/caching)
- [Manage scheduled dashboard updates and subscriptions](https://learn.microsoft.com/en-us/azure/databricks/dashboards/share/schedule-subscribe)
- [Dashboard concepts](https://learn.microsoft.com/en-us/azure/databricks/dashboards/concepts)
