# Answer bank

Common questions that each folder in this repo answers, with a short answer and the folder link. Every answer comes from the folder's article, fact sheet, README or tests. Where a point was not tested, the answer says so. Before posting, check that the answer still matches the current docs, because several of these features are in Beta.

Folder base: https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks

## ai-forecast

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/ai-forecast)

**Why does holiday_region give an UNSUPPORTED_ARGS error?**
`ai_forecast` uses version 1 unless you pass `version => '2'`, and `holiday_region`, `covariate_col` and `positive_only` only work with version 2. Add `version => '2'` and the query runs. The error is `PYTHON_TVF_UNSUPPORTED_ARGS_FOR_VERSION`, and it was reproduced in tests.

**Why did adding a covariate not improve my ai_forecast results?**
A covariate only helps if it also has values for the forecast window. In the test, a promo flag filled for the forecast days roughly halved the error, and the same flag on past days only gave no real gain. To use a future covariate, add rows for the horizon with the covariate filled in and the value column NULL.

**Why does ai_forecast return only future rows, and how many?**
The output holds forecast rows only, from the end of the history up to `horizon`, and `horizon` is right-exclusive. A horizon of `'2027-01-15'` returns rows up to 2027-01-14. UNION the history if you want to plot both.

**Why is my forecast's lower bound below zero?**
The prediction interval can go below zero even when the forecast does not. Set `positive_only => TRUE` with version 2 and the lower bounds stop at zero. In the test, the point forecasts were not negative either way.

**Which warehouse can run ai_forecast?**
The function page says a Pro or Serverless SQL warehouse, and the AI Functions page says they are not available on Classic SQL warehouses. Version 2 ran on a serverless SQL warehouse without any preview setting in the test workspace, but the function page mentions an admin "AI Forecast V2" setting on the Previews page for some workspaces.

## dashboard

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/dashboard)

**Why does my dashboard show old data after the pipeline ran?**
The dashboard cache can return results up to 24 hours old, and a table change or a pipeline step does not refresh it. Add a schedule to the published dashboard, because a schedule run refreshes the cache. In the test, reopening the dashboard still showed the old numbers until the Refresh button was clicked or a schedule ran.

**Whose permissions run a published dashboard's queries?**
With Share data permission, the default, viewers run queries with the publisher's data permissions. With Individual data permission, each viewer uses their own credentials. Drafts always use the viewer's own permissions.

**Why did my dashboard subscribers disappear?**
Republishing a dashboard from Share data permission to Individual data permission pauses all its schedules and removes all subscribers. The Publish dialog warns about it, and a test confirmed it. Pick the permission option first, then add the schedule and subscribers.

**Can viewers see data they have no access to?**
Yes, with Share data permission, because the queries run with the publisher's credentials. Check who the dashboard and its folder are shared with, because folder access passes down to the dashboard.

## materialized-view-serverless-notebook

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/materialized-view-serverless-notebook)

**Why can't my SQL warehouse refresh a materialized view created in a notebook?**
A view created on serverless general compute can only be refreshed with serverless general compute, such as a serverless notebook or job. In the test, a SQL task on a warehouse failed with `INVALID_PARAMETER_VALUE: This table was created in serverless generic compute and cannot be refreshed from a DBSQL warehouse.` Also, only the owner of the view can refresh it.

**Why do I get "cannot import name 'pipelines' from 'pyspark'" in a notebook?**
The Python decorators need a serverless environment version that includes `pyspark.pipelines`. In the test, a one-time run on environment version 4 failed with this error, and version 6 worked. The docs list version 5 as the minimum, and one test on version 5 worked.

**Which runtime does spark.sql() need to create a materialized view?**
The folder lists Databricks Runtime 18.1 or above. Interactive notebooks meet this automatically, but a job pinned to an older version does not.

**What happens if I run the create statement again with no changes?**
In the test, both views kept the same table and pipeline ids and the refresh type changed to `NO OPERATION`. Adding a column to the definition and rerunning recomputed the view in full.

## serverless-compute-objects

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/serverless-compute-objects)

**How do I point a job at a serverless compute object?**
Put the object's ID in a job cluster with `serverless_compute.policy_id` and give the task that job cluster key. You copy the ID from the object's page on the Serverless tab of the Compute page.

**Why can't other users use the serverless compute object I created?**
A new object is private: only the creator and admins can manage it, and the `users` group has no access. Grant Can Use to a group with `databricks permissions update serverless-compute <object id>`, which adds an entry and keeps the others. `permissions set` replaces the whole list.

**Does the size of a serverless compute object change my job's run time?**
In the test, the same job ran in 84 to 86 seconds on all five sizes, so size made no difference. The size belongs to the rate limit feature, which the docs mark as Beta and which an admin turns on from the Previews page. That workspace had no Previews page, so the size was most likely not enforced.

## job-completion-triggers

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/job-completion-triggers)

**Why didn't my downstream job start after the upstream job finished?**
The default result filter is Succeeded (`SUCCESS`), so a failed upstream run does not start it. Use `FAILED` for something like an alert or cleanup job, or `DONE` to react to any outcome. The test with `fail=true` showed the downstream job staying idle.

**How does a job completion trigger work with several upstream jobs?**
The downstream job starts only after every monitored job has a new matching completion, and one trigger watches 1 to 10 jobs with one result filter. Completions that happened before you created the trigger do not count.

**What do I need before I can use job completion triggers?**
It is a Beta, and a workspace admin enables it on the Previews page in the downstream and every upstream workspace. The workspaces share one Unity Catalog metastore, you need CAN MANAGE on the downstream job, and its Run as identity needs CAN VIEW on every monitored job.

**Why does my development-mode bundle reject the UNPAUSED trigger preset?**
A target in development mode does not accept the `trigger_pause_status` preset set to `UNPAUSED`. Set `pause_status` on the job trigger itself, or resume the trigger after you deploy.

## genie-code-instructions

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/genie-code-instructions)

**Where do Genie Code workspace instructions live, and who can edit them?**
They live in `/Workspace/.assistant_workspace_instructions.md`, and only workspace admins can add or edit the file. Genie Code ignores everything past 20,000 characters.

**Can I use Genie Code instructions to make production read-only?**
Instructions guide how Genie Code answers, but the docs describe them as guidance and not as a way to enforce a policy. Use Unity Catalog permissions for enforcement, and use the instructions to steer behavior. The folder's PROD file asks for read-only SQL and no execution, and `tests/test_prompts.md` has the prompts to check it.

**Does Genie Code read AGENTS.md and CLAUDE.md files?**
Yes, it looks for them by walking up the folder tree from the open notebook or file. The docs say workspace instructions are generally prioritized over user instructions, but they do not say how workspace instructions rank against `AGENTS.md` and `CLAUDE.md`.

**How can I deploy different instructions to DEV, TEST and PROD?**
Keep one file per environment in git and deploy it with a workflow you start by hand, with an approval for PROD. The folder has the workflow, a length check and a deploy script that uploads the file with `databricks workspace import`.

## genie-code-failure-investigator

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/genie-code-failure-investigator)

**Can I define a Genie Code task in a Databricks Asset Bundle?**
The docs list Genie Code tasks as Jobs UI only, so they cannot be defined in a bundle, the Jobs API or the SDKs. The folder deploys everything around the job with a bundle and builds the Genie Code task by hand in the UI.

**Can I turn auto-approval off for a Genie Code task?**
The docs say auto-approval cannot be turned off for Genie Code tasks and call it a productivity feature, not a security boundary. Put the limits in permissions, for example a service principal that can read the sources and only insert into the report table. That setup was not tested.

**Why does my SQL alert only email on the first failure?**
By default an alert only emails on its first trigger. Set `retrigger_seconds` to 1 so that every failed run sends an email. The folder's alert query also returns only the newest report from the last 15 minutes.

**Which identity does a Genie Code task run as?**
The docs do not say. In the lab it ran as the job owner.

## efficient-column-updates

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/efficient-column-updates)

**Why is my UPDATE still rewriting data files with efficient column updates on?**
Enabling the feature does not guarantee that every `UPDATE` uses it, and Databricks can fall back to a standard update that rewrites the affected files. In the test, the update rewrote the files and returned the same results. The reason for the fallback could not be determined in that workspace.

**What do I need to turn on efficient column updates?**
It is a Beta. A workspace admin turns it on from the Previews page, and the table must be a Unity Catalog managed Delta table with catalog commits, row tracking, deletion vectors and column mapping in `id` mode. Reading and writing need Databricks Runtime 19 or above.

**Does MERGE use efficient column updates?**
No. The folder lists these as not supported: `MERGE`, write-time change data feed, UniForm, Iceberg managed tables and Lakeflow pipelines.

**Can I remove the feature after a rollback?**
A rollback stops new column files and consolidates the existing ones, but the feature stays in the table protocol. `DROP FEATURE` cannot remove it, so reads and writes still need Runtime 19 or above.

## ai-overview

[folder](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/ai-overview)

**What are the new names for Databricks One, Assistant, Genie Spaces and AI Gateway?**
Databricks One is now Genie One, Databricks Assistant is now Genie Code, Genie Spaces is now Genie Agents, and AI Gateway is now Unity Gateway. The fact sheet in the folder lists the source page for each.

**How do Unity Catalog, Unity Gateway, Genie, Agent Bricks and AI Functions fit together?**
The folder's article and diagrams explain it, and every claim is in `notes/facts.md` with the official page it came from. Statuses are as of November 2026, so check the release notes before relying on them.

## Gaps

Folders without an answer here: `mv-refresh-deep-dive` (work in progress), `serverless-compute` (older tests, replaced by serverless-compute-objects) and `genie-zeroops-vs-diy` (no README). The OAuth on-behalf-of article has no folder in this repo, so it has no entries.
