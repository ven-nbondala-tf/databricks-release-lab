# Fact sheet: Databricks dashboards, permissions and refresh

Checked on November 20, 2026 against Azure Databricks documentation on learn.microsoft.com only. One line per claim. Status: CONFIRMED, or NOT FOUND (no official wording found, so it stays out of the article unless marked as a test observation). Page dates are the `ms.date` values.

Base URL: A = https://learn.microsoft.com/en-us/azure/databricks/

Pages checked (all open, no redirects):

| Page | Title | ms.date |
| --- | --- | --- |
| A dashboards/share/share | Share a dashboard | 2026-11-05 |
| A dashboards/concepts | Dashboard concepts | 2026-11-05 |
| A dashboards/caching | Dataset optimization and caching | 2026-10-09 |
| A dashboards/share/schedule-subscribe | Manage scheduled dashboard updates and subscriptions | 2026-09-11 |
| A dashboards/limits | Dashboard limits | 2026-11-18 |
| A security/auth/access-control/ | Access control lists | 2026-11-18 |
| A ai-bi/admin/ | AI/BI administration guide | 2026-10-30 |
| A ai-bi/consumers/ | What is consumer access? | 2026-11-18 |
| A ai-bi/admin/embed | Manage dashboard and Genie Agent embedding | 2026-11-05 |

## Publishing and data permissions

| Claim | Status | Source |
| --- | --- | --- |
| There are two publish options: "Share data permissions (default)" and "Individual data permissions". The earlier bullets on the page write "Share data permission" and "Individual data permission" (singular), and the concepts page writes "Shared data permissions". | CONFIRMED. The Publish dialog in the product uses the singular labels. | A dashboards/share/share; A dashboards/concepts |
| Shared: "Viewers run queries using the publisher's data permissions." | CONFIRMED | A dashboards/share/share |
| Individual: "Viewers run queries using their own credentials." | CONFIRMED | A dashboards/share/share |
| Compute under Individual: "Compute access is always granted by the publisher's credentials." | CONFIRMED | A dashboards/share/share |
| Who can view with shared permissions: "Users and groups explicitly granted access. Users must be registered with the account, but do not require workspace access." | CONFIRMED | A dashboards/share/share |
| Who can view with individual permissions: "Users explicitly granted dashboard access who have data permissions to the underlying data. Workspace membership is not required." | CONFIRMED | A dashboards/share/share |
| The Publisher Credential field "shows the selected credential, which defaults to your user account." | CONFIRMED | A dashboards/share/share |
| A service principal can be the publisher credential: "click the kebab menu next to this option and select a service principal." Through the API, set `embed_credentials` to `true` on the publish endpoint. | CONFIRMED | A dashboards/share/share |
| Sharing with data permissions "might expose data to users who have not been granted direct access to it." | CONFIRMED. The exact phrase "viewers can see data they would not otherwise have access to" is not on the pages. | A dashboards/share/share |
| Without shared permissions, "you must verify that viewers have the necessary permissions to access the data displayed on the dashboard." | CONFIRMED | A dashboards/share/share |
| Shared data permissions "requires careful permission management." | CONFIRMED | A dashboards/concepts |

## Drafts and published versions

| Claim | Status | Source |
| --- | --- | --- |
| "For draft dashboards, the viewer's data permissions are always applied, even if the dashboard is published with shared data permissions." | CONFIRMED | A dashboards/share/share |
| "The published version remains unchanged until you publish again, even if you continue editing the draft." | CONFIRMED | A dashboards/share/share |
| "Viewers always see the last published version, not the current draft." | CONFIRMED | A dashboards/concepts |
| "Changes to a draft dashboard are saved automatically but are not visible to viewers until you publish." | CONFIRMED | A dashboards/concepts |
| To modify and republish a draft, a user needs "at least CAN EDIT permission". | CONFIRMED | A dashboards/share/share |
| Account members without workspace access cannot open the draft: "Members without access to the workspace cannot access the draft version of the dashboard." | CONFIRMED | A dashboards/share/share |

## Sharing and permission levels

| Claim | Status | Source |
| --- | --- | --- |
| CAN VIEW (the API calls it CAN READ) can view the dashboard, results and datasets, interact with widgets, refresh and clone. | CONFIRMED | A security/auth/access-control/ (Dashboard ACLs) |
| CAN RUN has the same rows ticked as CAN VIEW in the dashboard table. | CONFIRMED | A security/auth/access-control/ |
| CAN EDIT adds "Edit dashboard" and "Publish dashboard snapshot". | CONFIRMED | A security/auth/access-control/ |
| CAN MANAGE adds "Modify permissions" and "Delete dashboard". | CONFIRMED | A security/auth/access-control/ |
| "Dashboard ownership does not grant special privileges. The owner has the same access as any user with CAN MANAGE permission on the dashboard." | CONFIRMED | A security/auth/access-control/ |
| The level needed to share, to create a schedule or to manage subscriptions is not stated in the permission table. | NOT FOUND | A security/auth/access-control/ |
| "Users who do not have access to the workspace are limited to CAN RUN permissions." Higher grants show in the dialog but do not apply until the user is added to the workspace. | CONFIRMED | A dashboards/share/share |
| The account-wide setting is "Anyone in my account can view", under "Sharing settings" at the bottom of the Sharing dialog. An administrator must first register users with the account. It is set by the dashboard author, not by an admin toggle. | CONFIRMED | A dashboards/share/share; A ai-bi/admin/ |
| Account users get a view-only copy and "use the publisher's credentials to access compute resources". Account-level sharing supports email and one-time passcode sign-in, and single sign-on. | CONFIRMED | A dashboards/share/share |
| Users with the Consumer access entitlement and account users are limited to view-only access. Consumer access users "cannot create or edit a dashboard or change its sharing settings", and cannot view SQL warehouses or Query History. | CONFIRMED | A dashboards/share/share; A ai-bi/consumers/ |
| "Dashboards inherit the workspace permissions set on the enclosing folder." Anyone with access to the enclosing folder can also access the dashboard. | CONFIRMED | A dashboards/share/share |
| Only workspace admins can change ownership of a dashboard. | CONFIRMED | A dashboards/share/share |
| "Account users who are not members of a workspace cannot access dashboard data from workspace-bound securables, such as workspace-bound catalogs". Such widgets "do not display data for account users." | CONFIRMED | A dashboards/share/share; A ai-bi/admin/ |
| A workspace admin can turn embedding on or off: Settings, Security, External access, Embed dashboards, with Allow, Allow approved domains and Deny. | CONFIRMED | A ai-bi/admin/embed |

## Caching and refresh

| Claim | Status | Source |
| --- | --- | --- |
| "Dashboards maintain a 24-hour result cache to optimize initial loading times". | CONFIRMED | A dashboards/caching |
| "The dashboard cache can return results that are up to 24 hours old even when the underlying data has changed". | CONFIRMED | A dashboards/caching |
| Dashboards "first check the dashboard cache", then the query result cache. | CONFIRMED | A dashboards/caching |
| "The query result cache never returns stale data, because a change to the underlying data invalidates all of its entries." | CONFIRMED | A dashboards/caching |
| "The warehouse starts only when a dashboard runs a query that the cache cannot serve." | CONFIRMED | A dashboards/caching |
| Shared data permissions: "Shared cache. All viewers see the same results." | CONFIRMED | A dashboards/caching |
| Drafts and individual data permissions: "Per user cache. Viewers see results based on their data permissions." | CONFIRMED | A dashboards/caching |
| "To reliably refresh the dashboard cache, configure a dashboard schedule." Otherwise the cache updates only when a query it cannot serve runs. | CONFIRMED | A dashboards/caching |
| "A change to the underlying data does not refresh the dashboard cache on its own, and refreshing the data as part of a pipeline step does not refresh the dashboard cache." | CONFIRMED | A dashboards/caching |
| With parameters or filters applied and stale results present, queries rerun unless the same parameters were used in the past 24 hours. | CONFIRMED | A dashboards/caching |
| current_timestamp() and similar functions do not invalidate the dashboard-level cache, but they do invalidate the query result cache. | CONFIRMED | A dashboards/caching |
| A separate "browser cache" is described. | NOT FOUND. The page describes client-side filtering and aggregation for small datasets, not a browser cache. | A dashboards/caching |
| What the Refresh button does. | NOT FOUND in the docs. See the test notes for what was observed. | |
| A recommendation to schedule a dashboard right after the pipeline that feeds it. | NOT FOUND as a stated recommendation. It follows from two documented facts: a pipeline step does not refresh the dashboard cache, and a schedule does. The article labels it as a recipe, not as a quote. | A dashboards/caching |

## Schedules and subscriptions

| Claim | Status | Source |
| --- | --- | --- |
| Schedule settings: "Use the drop-down selectors to specify the frequency, start time, and time zone", or edit as Quartz cron. | CONFIRMED | A dashboards/share/schedule-subscribe |
| Advanced settings: a SQL warehouse for scheduled runs, "Use current filter selections", a custom email subject, subscribers and attachments (pages, data). | CONFIRMED | A dashboards/share/schedule-subscribe |
| "Running a schedule now updates the dashboard and sends notifications without changing its regular cadence." | CONFIRMED | A dashboards/share/schedule-subscribe |
| Run indicators report whether a run "succeeded, failed, or was skipped because the schedule had already reached its limit for concurrent runs". | CONFIRMED | A dashboards/share/schedule-subscribe |
| Paused schedules keep their configuration, but the dashboard does not update or send notifications. | CONFIRMED | A dashboards/share/schedule-subscribe |
| You can subscribe yourself with at least CAN VIEW. You can add and remove other subscribers with at least CAN EDIT. | CONFIRMED. The AI/BI administration guide says "Dashboard editors cannot add subscribers, and dashboard viewers do not have the option to subscribe to a scheduled dashboard." The two pages conflict, so the article does not state who can add subscribers beyond the schedule page. | A dashboards/share/schedule-subscribe; A ai-bi/admin/ |
| Email subscribers get a PDF snapshot, with optional CSV, TSV or Excel data attachments. Slack and Teams get a PNG snapshot. | CONFIRMED | A dashboards/share/schedule-subscribe |
| Account users, distribution lists and external users can be email notification destinations. "Workspace admins must define notification destinations before they can be selected as subscribers." | CONFIRMED | A dashboards/share/schedule-subscribe |
| "Subscription lists can contain up to 100 subscribers." | CONFIRMED | A dashboards/share/schedule-subscribe |
| Email attachments have a 9 MB combined limit, and Excel attachments omit rows beyond 100,000. | CONFIRMED | A dashboards/limits |
| If a workspace admin turns off "Enable dashboard email subscriptions" (Settings, Notifications), existing subscriptions are paused. | CONFIRMED | A ai-bi/admin/ |
| Whose credentials run a scheduled refresh; how many schedules a dashboard can have; which level can create a schedule. | NOT FOUND | |

## Concepts

| Claim | Status | Source |
| --- | --- | --- |
| "Each dataset is based on a table, view, metric view, or custom SQL query." Datasets "inherit Unity Catalog permissions". | CONFIRMED | A dashboards/concepts |
| Filters can be global, page-level or widget-level. Parameters "can be referenced in SQL queries and calculations". | CONFIRMED | A dashboards/concepts |
| "All data access is governed by Unity Catalog permissions, including row filters and column masks". | CONFIRMED | A dashboards/concepts |
