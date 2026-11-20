# Test results

Run on November 19 and 20, 2026 on a Databricks Free Edition workspace, on a serverless SQL warehouse. These notes are not part of the article. The article explains behavior from the Azure Databricks documentation and uses these tests only to confirm it.

## Setup

- Schema `dash_demo` with a `sales` table of 200 rows: `order_id`, `region` (North, South, East, West, 50 rows each), `product`, `amount`, `order_date`. Total amount 54,200.
- Dashboard `dash_demo_sales`, one page, created through the dashboards API and saved in `dashboard/dash_demo_sales.lvdash.json`.
  - Dataset `sales_by_region`: orders and revenue per region, with the parameter `min_amount` (default 0).
  - Dataset `recent_orders`: the 20 latest orders.
  - A Region filter that applies to both datasets, a Minimum amount parameter control and two tables.
- Only one user exists in this workspace.

## Test 1: Publish with shared data permission (the default)

The Publish dialog shows two cards.

| Item | What the dialog shows |
| --- | --- |
| First card | "Share data permission (default)", "Publisher Credential: <your user> (you)", and "Viewers run queries using the publisher's credentials, enabling a shared cache for performance" |
| Second card | "Individual data permission": "Each viewer of a published dashboard uses their own data permission to run queries. This can lead to more frequent refresh operations." |
| Checkboxes | "Notify viewers (emails individuals and small groups)" and "Materialize datasets 1 (Beta)": "Pre-compute and store results for faster performance, only applies to enabled datasets." with "Adds daily schedule" |
| Buttons | Copy link, Publish |

- The Publisher Credential field has a menu. It lists the signed-in user (ticked) and a "Service Principals" search. The search returned "No results found", so a service principal could not be selected on this workspace.
- Publishing opened the Sharing dialog straight away.
- The publish API shows `embed_credentials: true` for this option.
- Screenshots: `01-publish-dialog-shared.png`, `01b-publisher-credential-menu.png`.

## Test 2: Republish with individual data permission

- Choosing the second card on a dashboard that was published with shared permission adds a red warning to the dialog: "Since this dashboard was previously published as embedded credentials, this action will pause all schedules for the dashboard and remove all subscribers".
- The "Materialize datasets" option disappears, and an "Unpublish" button appears next to Publish.
- After publishing: `embed_credentials: false`, the schedule `pause_status` is `PAUSED`, and the schedule has 0 subscriptions. The warning was accurate.
- Screenshot: `02-publish-dialog-individual.png`.

## Test 3: Draft versus published

- With the dashboard published, the draft table title was changed to "Revenue by region (draft edit)".
- The draft view shows the new title. The published view still shows "Revenue by region".
- Screenshots: `03a-draft-after-edit.png`, `03b-published-unchanged.png`.

## Test 4: Sharing dialog

- Permission levels offered when adding someone: Can Manage, Can Edit, Can Run, Can View. There is also an "Email new users (includes individuals and small groups)" checkbox.
- "People with access" lists the signed-in user and the Admins group, both "Can Manage (inherited)".
- "Sharing settings" is a dropdown with "Only people with access can view" (the default) and "Anyone in my account can view". It was not changed.
- The add box offered only Admins, All workspace users, the signed-in user and All account users. No second user exists, so the CAN RUN test was skipped.
- Screenshots: `04-share-dialog-permission-levels.png`, `04b-share-dialog-sharing-settings.png`.

## Test 5: Refresh with shared permission

Dashboard published with shared permission. Times are UTC.

| Step | Result |
| --- | --- |
| 05:47 insert 10 North rows of 1,000 (North becomes 60 orders, 24,600) | Table updated |
| Reopen the published dashboard | North still 50 orders, 14,600. The new rows did not appear. |
| Click the Refresh button on the published dashboard | North 60 orders, 24,600. The button label changed to "Refresh (Updated: 10 seconds ago)". |
| 05:50 insert 5 West rows of 2,000 (West becomes 55 orders, 22,950), then Run now on the schedule | Dashboard queries ran about 7 seconds later, according to query history |
| Reload the published dashboard without clicking Refresh | West 55 orders, 22,950. The scheduled run had refreshed it. |

The published toolbar has "Refresh (Updated: N minutes ago)", Schedule and Share. The documentation pages read do not describe the Refresh button.

## Test 6: Schedules

- The Add schedule dialog: a message "Refreshed data becomes available to all users, and they can optionally receive an email.", then Schedule (Every Day at 21:48), "Show cron syntax", a time zone (America/Los_Angeles), and Advanced settings: Name, SQL warehouse (required choice, "Select a SQL warehouse"), "Use current filter selections", Custom email subject, Subscribers, and Attachments (Include pages, Include data with a file format, "Attachments over 9 MB won't be included.").
- After Create, the Schedules panel lists the schedule with its subscriber count (1), five run indicators and "Subscribed". The row menu offers Edit, Pause, Run now and Delete.
- After Run now the last indicator spins. It kept spinning in the open panel for several minutes while query history showed the dashboard queries finished. After reloading the page it showed a green check.
- Screenshots: `06-schedule-dialog.png`, `06b-schedule-run-history.png`.

## Test 7: Subscriptions

- The only option in the Subscribers list was the signed-in user's own email address. It was selected.
- Run now sent one email from Databricks with the subject "Dashboard snapshot: dash_demo_sales" at 9:50 PM local time, the same minute as the run.
- It had one attachment, `dash_demo_sales-20261120_05-50.pdf`. The body had a "Go to Dashboard" link, a line saying the address was subscribed to the dashboard, an Unsubscribe link and a timestamp. No data attachment was selected, so there was none.
- Email subscriptions are allowed on this workspace.

## What differed from the documentation

- The dialog labels are "Share data permission (default)" and "Individual data permission" (singular). The share page uses "Share data permissions (default)" in the publish steps, and the concepts page says "Shared data permissions".
- Republishing with individual permission paused the schedule and removed the subscriber. The documentation says paused schedules keep their subscribers, and does not mention this effect of switching the publish option.
- The Refresh button on a published dashboard fetched new rows immediately. The pages read do not describe it.
- The publish dialog has a "Materialize datasets (Beta)" option that adds a daily schedule. The pages read do not mention it.
- The dashboard cache behavior matched the documentation: reopening did not show new rows, and a schedule run refreshed the cache.

## Not tested

- A second user with CAN RUN, and account users without workspace access (no second user exists).
- Publishing with a service principal (none available).
- A pipeline update as the source of the data change.
- The "Anyone in my account can view" setting (not changed).
- Whose credentials run a scheduled refresh.
- The contents of the PDF snapshot.
- Slack and Teams subscriptions.
