# Databricks Token Scopes Explained: Least-Privilege Access

Subtitle: Choose Databricks token scopes and access levels for BI tools, AI agents, CI/CD and scripts, with the exact errors each limited token returns.

Databricks token scopes limit which APIs a token can call, and without them a personal access token can call every API you can, so a token pasted into a BI tool or an agent hands that tool your full access. Scope modifiers, generally available since November 4, 2026, narrow a scope further to read operations or to read-only SQL queries. This guide shows how to list the scopes, create and test scoped tokens, change them later, and pick the right scopes for six common uses. The complete code for this guide is on GitHub: [databricks/token-scopes](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/token-scopes).

[VIDEO: https://youtu.be/ohhDVVHqtdQ]
Caption: Databricks token scopes in a short video.

## What are Databricks token scopes

A scope limits which Databricks REST API endpoints a token can call. A modifier narrows a scope to a subset of its operations, and you write it after a colon, for example `clusters:read`.

- A scope names an API area, such as `sql`, `jobs`, `clusters` or `unity-catalog`. Without a modifier, the token can call every operation in that area.
- `:read` limits a scope to its read operations, which are GET and HEAD requests.
- `:restricted-query` applies to the `sql` scope only. It allows read-only SQL queries and nothing else in that scope. You can combine it as `sql:read:restricted-query`.
- Scopes and modifiers work on personal access tokens, on OAuth secrets for service principals, and in the `scope` parameter of an OAuth token request.
- Scope modifiers are generally available.
- A personal access token with an empty scopes array has full access, which is the same as the `all-apis` scope.

The diagram shows how a token, its scopes and the modifiers fit together.

[image: scope-modifiers.png | Caption: A token carries scopes, and each scope can carry a modifier. | Alt: A flow diagram. A token has a scope. The scope leads to four options: no modifier for every operation, read for GET and HEAD requests, restricted-query for SELECT and DESCRIBE on the sql scope, and read plus restricted-query for read operations and read-only queries. An empty scopes array gives full access.]

## When to use scoped tokens

Use a scoped token for anything that runs outside your own session: a BI tool, an agent, a scheduled script, a deployment pipeline. The token should be able to do the one job it exists for, so a leaked token does limited harm.

Use OAuth for automation where you can. Databricks recommends OAuth over personal access tokens, and scoped OAuth secrets for service principals give the same limits with a one-hour access token. A personal access token is the simpler choice when a tool only accepts a token or when you need a quick, short-lived credential.

## Prerequisites

- An Azure Databricks workspace and permission to create personal access tokens.
- For automation with OAuth: a service principal added to the workspace, and permission to generate secrets for it.
- Token scopes limit the API areas a token can call. They do not replace permissions on tables, jobs and other objects, which still apply to the user or service principal behind the token.

## Step-by-step guide

### Step 1: List the scopes in your workspace

The scope list tells you which names you can use. Call the token scopes endpoint with any valid token.

```bash
curl -s -H "Authorization: Bearer <token>" "<workspace-url>/api/2.0/token-scopes"
```

The response has a `scopes` array. Each entry has `name`, `display_name`, `description` and `allowed_modifiers`. The list can include scopes that the API scopes reference does not show. A later section lists the ones found on one workspace. The `allowed_modifiers` field shows only `read`, but the Token API also accepts `sql:restricted-query` and `sql:read:restricted-query`.

### Step 2: Create a scoped token

Create the token with the scopes the job needs and a short lifetime. In the UI, go to Settings, Developer, and select Manage next to Access tokens.

[image: ui-01-access-tokens.png | Caption: The Developer page, with the Manage button for access tokens. | Alt: The Developer settings page. Under Access tokens, a Manage button sits on the right.]

On the Access tokens page, select Generate new token. Enter a Name that says what the token is for, set the Lifetime (days), and choose a scope type. BI Tools starts from the `sql` scope. Other APIs lets you choose any scope yourself.

[image: ui-02-generate-token.png | Caption: The Generate new token dialog with a name and a one-day lifetime. | Alt: The Generate new token dialog. The Name is "reporting tool, read only" and the Lifetime is 1 day. Below are the Auto-scope tokens switch, the BI Tools and Other APIs choices, and an Add scope button. No scopes are selected yet.]

Select Add scope and tick the scopes you need. The list has a search box and shows what each scope covers.

[image: ui-03-add-scope.png | Caption: The scope list, with jobs and its neighbours. | Alt: The Add scope list open under the dialog, with a Search scopes box. It lists instance-pools, instance-profiles, jobs, knowledge, knowledge-assistants and lakewatch, each with a tick box and a one-line description.]

Then pick an access level for each scope. For every scope the levels are Read, which is `<scope>:read`, and Read + Write, which is the scope without a modifier. The `sql` scope adds Restricted query, Read + Restricted query and Read + Restricted query + Write.

[image: ui-04-sql-access-levels.png | Caption: The access levels for the sql scope. | Alt: The Generate new token dialog with the sql scope added. The access level list shows Read, Restricted query, Read plus Restricted query, and Read plus Restricted query plus Write.]

Select Generate. The dialog shows the token value once, so copy it into a secret manager before you select Done.

[image: ui-05-token-created.png | Caption: The confirmation after a token is created. The token value is hidden here. | Alt: A dialog that says the token has been created successfully. A field shows the token value as dots, with a warning to copy it now because it cannot be shown again, and a Done button.]

The new token appears in the list with its name, scopes and expiry.

[image: ui-06-token-list.png | Caption: The token in the list, with its scopes and expiry. | Alt: A table row for the token "reporting tool, read only". The Scopes column shows sql:restricted-query, and the Expiration column shows a date one day after the creation date. The token ID is hidden.]

To create the token with the API, send the scopes in the request:

```bash
curl -s -X POST "<workspace-url>/api/2.0/token/create" \
  -H "Authorization: Bearer <admin-or-owner-token>" \
  -H "Content-Type: application/json" \
  -d '{"lifetime_seconds": 3600, "comment": "bi-tool read only", "scopes": ["sql:restricted-query"]}'
```

The response contains `token_value`, which you see once, and `token_info` with the token ID and the scopes. Store the value in a secret manager.

### Step 3: Check what the token can do

Run one call the token should allow and one it should refuse before you hand it over. This query runs through the Statement Execution API with a `sql:restricted-query` token:

```bash
curl -s -X POST "<workspace-url>/api/2.0/sql/statements" \
  -H "Authorization: Bearer <scoped-token>" -H "Content-Type: application/json" \
  -d '{"warehouse_id": "<warehouse-id>", "wait_timeout": "30s", "statement": "SELECT * FROM <catalog>.<schema>.<table>"}'
```

The `SELECT` and `DESCRIBE` statements succeed. An `INSERT`, `CREATE TABLE` or `DROP TABLE` statement fails with `[OP_NOT_SUPPORTED_READ_ONLY] ... is not supported in read-only session mode. SQLSTATE: 42KD1`. Listing the SQL warehouses returns HTTP 403 with `Provided access token has scope(s) [sql:restricted-query] that cannot send a GET request to this endpoint`.

### Step 4: Change the scopes of a token

You can change the scopes of an existing personal access token. In the UI, open the menu at the end of the token's row, choose Update token, change the scopes and select Update.

[image: ui-07-update-token.png | Caption: The Update token dialog for an existing token. | Alt: The Update token dialog. It shows the token name, the BI Tools and Other APIs choices, an Add scope button, and the sql scope set to Restricted query. Cancel and Update buttons are at the bottom.]

With the API, send a PATCH request. The caller needs the `authentication` scope.

```bash
curl -s -X PATCH "<workspace-url>/api/2.0/token/<token-id>" \
  -H "Authorization: Bearer <admin-or-owner-token>" -H "Content-Type: application/json" \
  -d '{"token": {"scopes": ["jobs:read"]}, "update_mask": "scopes"}'
```

The change took about five minutes in our test, and the documentation says it can take up to ten minutes, so wait before you test the new scopes.

### Step 5: Scope an OAuth secret for a service principal

An OAuth secret fixes its scopes when you generate it, and you cannot change them afterwards. In the UI, go to Settings, Identity and access, and select Manage next to Service principals. Open the service principal and select the Secrets tab. The table lists each secret with its scopes.

[image: ui-08-sp-secrets.png | Caption: The Secrets tab of a service principal. | Alt: The Secrets tab of a service principal. A table with the columns ID, Created at, Expires at, Last accessed and Scopes shows "No OAuth secrets". A Generate secret button sits below it.]

Select Generate secret. Enter a Lifetime (days), then add specific scopes and set an access level for each. Avoid full access, which the documentation marks as not recommended.

[image: ui-09-sp-secret-scopes.png | Caption: The Generate OAuth secret dialog with the sql scope limited to Restricted query. | Alt: The Generate OAuth secret dialog. The Lifetime is 1 day. The sql scope is added with the access level Restricted query. Cancel and Generate buttons are at the bottom.]


Then request an access token with a `scope` parameter. The scopes are separated by spaces:

```bash
curl -s -X POST "<workspace-url>/oidc/v1/token" \
  -u "<client-id>:<client-secret>" \
  -d "grant_type=client_credentials&scope=sql:restricted-query"
```

The access token lasts one hour and carries the scopes you asked for. A token cannot exceed the scopes of the secret it came from. A request for a wider scope is refused with HTTP 403 and `access_denied`, for example `Scopes 'sql' are not assigned to the client <client-id>; the client has scope(s) [sql:restricted-query] that cannot send this request`.

## Choose Databricks token scopes for each use

Choose scopes by what the token is for. Start with the narrowest option, and if a call fails with a missing-scope error, add the scope that the error names. The sets for BI tools, MCP clients and bundle deployments come from the API scopes reference, not from a run with the real tool, so check them with one allowed call and one refused call before you rely on them.

### Start with the :read trap

The `:read` modifier means GET and HEAD requests only. Running a SQL statement through the Statement Execution API is a POST request, so a token with `sql:read` can list SQL warehouses but cannot run a `SELECT`. The call returns HTTP 403: `Provided access token has scope(s) [sql:read] that cannot send a POST request to this endpoint`.

For read-only data access, use `sql:restricted-query`. If the tool also lists SQL warehouses before it connects, use `sql:read:restricted-query`. The same rule applies to other scopes: anything that starts a run, sends a query or creates a conversation is a POST and needs the scope without `:read`.

### Treat the authentication scope as an admin credential

A token with the `authentication` scope can create new tokens with any scope. That makes it an admin credential. Never give it to a tool, an agent or a pipeline.

The scope does not look dangerous by itself. A token with only `authentication` is refused on the Jobs API:

```bash
curl -s -H "Authorization: Bearer <authentication-only-token>" "<workspace-url>/api/2.1/jobs/list?limit=1"
# HTTP 403: Provided access token does not have required scopes: jobs
```

The same token can create a new token with an empty scopes array, which means full access, and the new token is not refused:

```bash
curl -s -X POST "<workspace-url>/api/2.0/token/create" \
  -H "Authorization: Bearer <authentication-only-token>" -H "Content-Type: application/json" \
  -d '{"lifetime_seconds": 600, "comment": "created by the authentication-only token", "scopes": []}'
# HTTP 200, and the new token can call the Jobs API
```

Give `authentication` only to a token whose job is to manage other tokens, and guard it like a password.

[image: decision-table.png | Caption: Scopes to select for six common uses of a token. | Alt: A table with six rows: BI tools and dashboards, AI agents and MCP clients, monitoring and alerting, CI/CD deployment, data pipelines and scripts, and admin automation. Each row lists the scopes to select, what the token can do and what it cannot do.]

### BI tools and dashboards

- Scopes: `sql:restricted-query`. Use `sql:read:restricted-query` if the tool lists SQL warehouses before it connects.
- It can run `SELECT` and `DESCRIBE`. It cannot run `INSERT`, `CREATE TABLE` or `DROP TABLE`, and it cannot call other SQL APIs.
- Do not use this token for a tool that writes results back to a table.
- This set comes from the API scopes reference and the SQL test above, not from a run with Tableau or Power BI.

### AI agents and MCP clients

- Scopes: `sql:restricted-query` and `unity-catalog:read` for data access. Add `genie` for Genie conversations or `model-serving-inference` for model queries, only when the agent needs them.
- It can query data and read catalog metadata. A token with `unity-catalog:read` lists catalogs but cannot create a schema.
- Do not add `genie` casually: the scope also covers creating Genie spaces. The `:read` modifier is not enough for starting a conversation or querying an index, because those calls are not GET or HEAD requests.
- The scopes for MCP clients come from the API scopes reference and were not tested with a real client.

### Monitoring and alerting

- Scopes: `jobs:read`, `pipelines:read`, `clusters:read` and `query-history:read`, as needed.
- It can list and get jobs, pipelines, clusters and query history. A token with `jobs:read` can list jobs but cannot create or delete one.
- Query history is its own scope. `sql` does not cover it: a token without `query-history` gets `Provided access token does not have required scopes: query-history`.
- Do not use it to trigger a run or a restart. Those calls are POST requests and need the full scope.

### CI/CD deployment

- Scopes: start with `jobs`, `pipelines`, `workspace` and `files` on a scoped OAuth secret for a service principal, and add scopes as the deployment reports missing ones.
- It can create and update jobs and pipelines and import files. It cannot manage users, groups or tokens.
- Do not use a personal access token of a person for a pipeline. The documentation does not list which scopes a bundle deployment needs. This set comes from the API scopes reference and was not tested with a bundle deployment, so read the missing-scope errors and add only the scopes they name.

### Data pipelines and scripts

- Scopes: `sql` for scripts that write data, `files` for uploads and downloads, `unity-catalog:read` for metadata.
- It can run any SQL statement that its user may run and read and write files. It cannot start jobs or change compute.
- Do not use plain `sql` for a script that only reads. Use `sql:restricted-query`.

### Admin automation

- Scopes: `identity`, `access-management` or `settings`, only the ones the script needs.
- It can manage the identities, permissions or settings that its scope covers.
- Do not add `authentication` unless the token manages other tokens, and see the warning above: it is an admin credential.

## SQL access levels, from narrowest to widest

SQL is where most people start, so the levels are worth knowing in order.

- `sql:restricted-query`: `SELECT` and `DESCRIBE` through the Statement Execution API and SQL drivers. No writes, no DDL, no other SQL API calls.
- `sql:read:restricted-query`: the same queries, plus the read operations of the `sql` scope, such as listing SQL warehouses.
- `sql`: everything in the scope, including `INSERT`, `CREATE TABLE`, `DROP TABLE` and warehouse changes. In the UI this is Read + Restricted query + Write.

`sql:read` alone sits beside this list, not in it. It lists warehouses but cannot run a query, which is the `:read` trap described above. That is why the `restricted-query` modifier exists.

## Scopes in the API but not in the reference

Check the scope list on your own workspace, because it can differ from the documentation. On November 28, 2026, `GET /api/2.0/token-scopes` on the workspace used for this guide returned 61 scopes, and 15 of them do not appear in the API scopes reference, which lists 46:

- `ai-gateway`
- `billing`
- `bundle`
- `bundle-deployments`
- `compute-migrations`
- `custom-llms`
- `databricks-connect`
- `disaster-recovery`
- `forecasting`
- `genie-agents`
- `genie-migrate`
- `provisioning`
- `qualitymonitor`
- `search`
- `zerobus`

The documentation does not say what these cover, so this guide does not recommend any of them. Every scope in the reference was also in the live list. Run `GET /api/2.0/token-scopes` on your workspace and compare it with the reference before you rely on a scope. The response also lists only the `read` modifier for each scope, although the Token API accepts `sql:restricted-query` and `sql:read:restricted-query`.

## Personal access tokens or OAuth secrets

Both carry scopes, but they behave differently.

- A personal access token belongs to one user in one workspace. You set its scopes at creation and can change them later with a PATCH request. It can be valid for up to 730 days by default, an admin can set a lower maximum, and Databricks revokes it after 90 days without use. A workspace allows up to 600 tokens per user.
- An OAuth secret belongs to a service principal. Its scopes are fixed when you generate it, and you create a new secret to change them. The access token it produces lasts one hour, and a token can never exceed the scopes of its secret.
- A personal access token cannot automate account-level functionality, and PATs do not support `all-apis:read`. OAuth accepts `all-apis:read`, which gives read operations on every API the principal can use.

For automation, use a scoped OAuth secret on a service principal. The access token expires after an hour, the scopes are fixed, and the credential does not depend on a person staying in the workspace.

## Example: a read-only token for a reporting tool

A reporting tool needs to read one table and nothing else. You create a token with `sql:restricted-query`, a one-hour lifetime and a clear comment, then check it with three statements.

```bash
# 1. Create the token (the value appears once)
curl -s -X POST "<workspace-url>/api/2.0/token/create" -H "Authorization: Bearer <owner-token>" \
  -H "Content-Type: application/json" \
  -d '{"lifetime_seconds": 3600, "comment": "reporting tool, read only", "scopes": ["sql:restricted-query"]}'

# 2. Allowed: SELECT
curl -s -X POST "<workspace-url>/api/2.0/sql/statements" -H "Authorization: Bearer <scoped-token>" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": "<warehouse-id>", "wait_timeout": "30s", "statement": "SELECT * FROM <catalog>.<schema>.orders"}'

# 3. Refused: INSERT. The request body goes in a file, so the SQL can keep its single quotes
cat > insert.json <<'JSON'
{"warehouse_id": "<warehouse-id>", "wait_timeout": "30s", "statement": "INSERT INTO <catalog>.<schema>.orders VALUES (2, 'x')"}
JSON
curl -s -X POST "<workspace-url>/api/2.0/sql/statements" -H "Authorization: Bearer <scoped-token>" \
  -H "Content-Type: application/json" -d @insert.json
```

The `SELECT` returns the rows with the state `SUCCEEDED`. The `INSERT` returns the state `FAILED` with `[OP_NOT_SUPPORTED_READ_ONLY]`, and the table keeps its original rows. The full example, including setup, every test call and cleanup, is in the [token-scopes](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/token-scopes) folder of the repository.

## The errors you will see

These are the responses from a workspace on November 28, 2026. The ID and workspace values are masked.

Three forms tell you a scope is missing:

- The token has no scope for the API area: HTTP 403 `Provided access token does not have required scopes: jobs`.
- The token has the scope but not for this kind of request: HTTP 403 `Provided access token has scope(s) [jobs:read] that cannot send a POST request to this endpoint`. The same form appears with `GET` for `[sql:restricted-query]` on the warehouse list.
- An OAuth token request asks for a scope that the secret does not have: HTTP 403 `access_denied` with `Scopes 'sql' are not assigned to the client <client-id>; the client has scope(s) [sql:restricted-query] that cannot send this request`.

Two more cover writing the scopes and writing data:

- A scope name the API does not accept returns HTTP 400 `Invalid scopes: all-apis`. The same message appears for `all-apis:read` and for names that do not exist.
- An `INSERT`, `CREATE TABLE` or `DROP TABLE` under `sql:restricted-query` returns HTTP 200 with the statement state `FAILED` and `[OP_NOT_SUPPORTED_READ_ONLY] ... is not supported in read-only session mode. SQLSTATE: 42KD1`. The documentation shows `[INSUFFICIENT_PERMISSIONS]` for data changes, but the Statement Execution API returned `OP_NOT_SUPPORTED_READ_ONLY` for `INSERT` as well as for DDL.

An OAuth token request that asks for more than its secret allows is refused with the 403 `access_denied` above. It is not narrowed to the secret's scopes.

## Things to know

- Treat `authentication` as an admin credential. A token with that scope can mint a full-access token, as shown above.
- A scope change takes time. A PATCH on a personal access token took about five minutes in our test, and the documentation says up to ten, so test after the wait. To change the scopes of an OAuth secret, generate a new secret.
- Send an empty `scopes` array for full access. The literal `all-apis` is not accepted for personal access tokens, and neither is `all-apis:read`.
- Query history needs the `query-history` scope, not `sql`.
- When the documentation does not say what a scope covers, create a short-lived test token and read the error. Do this for any scope that is in your workspace list but not in the reference.

## Best practices

- Create one token per tool, with a comment that names the tool and the owner.
- Set the shortest lifetime that works, and rotate the token before it expires.
- Start from the narrowest scope and add scopes only when a call fails with a missing-scope error.
- Prefer scoped OAuth secrets for service principals over personal access tokens for anything automated.
- Review your tokens regularly and remove the ones that have not been used.

## Summary

Token scopes limit which APIs a Databricks token can call, and the `:read` and `:restricted-query` modifiers narrow a scope to read operations or read-only SQL. Start from the narrowest scope for the job, check it with one allowed call and one refused call, and read the missing-scope error to add what's missing. Use scoped tokens for every BI tool, agent, script and pipeline, and scoped OAuth secrets for anything that runs on its own.

Which of your tokens still has full access?

## References

- [Scope modifiers for Databricks tokens](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/scope-modifiers)
- [Authenticate with Databricks personal access tokens](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat)
- [Authorize service principal access with OAuth (M2M)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-m2m)
- [Authorize user access with OAuth (U2M)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-u2m)
- [Monitor and manage personal access tokens](https://learn.microsoft.com/en-us/azure/databricks/admin/access-control/tokens)
- [API scopes reference](https://docs.databricks.com/api/workspace/scopes)
- [November 2026 release notes](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november)
