# Databricks Token Scopes Explained: Least-Privilege Access

Subtitle: Choose Databricks token scopes and access levels for BI tools, AI agents, CI/CD and scripts, with the exact errors each limited token returns.

Databricks token scopes limit which APIs a token can call, and without them a personal access token can call every API you can, so a token pasted into a BI tool or an agent hands that tool your full access. Scope modifiers, generally available since November 4, 2026, narrow a scope further to read operations or to read-only SQL queries. This guide shows how to list the scopes, create and test scoped tokens, change them later, and pick the right scopes for six common uses. The complete code for this guide is on GitHub: [databricks/token-scopes](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/token-scopes).

[VIDEO: add the YouTube link here]
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

The response has a `scopes` array. Each entry has `name`, `display_name`, `description` and `allowed_modifiers`. The list can include scopes that the API scopes reference does not show yet, such as `bundle`. The `allowed_modifiers` field shows only `read`, but the Token API also accepts `sql:restricted-query` and `sql:read:restricted-query`.

### Step 2: Create a scoped token

Create the token with the scopes the job needs and a short lifetime. In the UI, go to Settings, Developer, Access tokens, Manage, Generate new token. Choose BI Tools for SQL tools, or Other APIs to select scopes yourself, then pick an access level for each scope.

[image: token-dialog-access-levels.png | Caption: The access levels for the sql scope in the Generate new token dialog. | Alt: The Generate new token dialog with the sql scope added. The access level list shows Read, Restricted query, Read plus Restricted query, and Read plus Restricted query plus Write.]

For every scope the levels are Read, which is `<scope>:read`, and Read + Write, which is the scope without a modifier. The `sql` scope adds Restricted query, Read + Restricted query and Read + Restricted query + Write.

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

You can change the scopes of an existing personal access token with a PATCH request. The caller needs the `authentication` scope, or a token with full access.

```bash
curl -s -X PATCH "<workspace-url>/api/2.0/token/<token-id>" \
  -H "Authorization: Bearer <admin-or-owner-token>" -H "Content-Type: application/json" \
  -d '{"token": {"scopes": ["jobs:read"]}, "update_mask": "scopes"}'
```

Scope changes can take up to ten minutes to propagate, so wait before you test the new scopes.

### Step 5: Scope an OAuth secret for a service principal

An OAuth secret fixes its scopes when you generate it, and you cannot change them afterwards. In the UI, go to Settings, Identity and access, Service principals, open the service principal, then Secrets, Generate secret, and choose the scopes. Choose specific scopes, not "all APIs".

Then request an access token with a `scope` parameter. The scopes are separated by spaces:

```bash
curl -s -X POST "<workspace-url>/oidc/v1/token" \
  -u "<client-id>:<client-secret>" \
  -d "grant_type=client_credentials&scope=sql:restricted-query"
```

The access token lasts one hour and carries the scopes you asked for. A token cannot exceed the scopes of the secret it came from. A request for a wider scope is refused with HTTP 403 and `access_denied`, for example `Scopes 'sql' are not assigned to the client <client-id>; the client has scope(s) [sql:restricted-query] that cannot send this request`.

## Choose Databricks token scopes for each use

Choose scopes by what the token is for. Start with the narrowest option, and if a call fails with a missing-scope error, add the scope that the error names.

[image: decision-table.png | Caption: Scopes to select for six common uses of a token. | Alt: A table with six rows: BI tools and dashboards, AI agents and MCP clients, monitoring and alerting, CI/CD deployment, data pipelines and scripts, and admin automation. Each row lists the scopes to select, what the token can do and what it cannot do.]

### BI tools and dashboards

- Scopes: `sql:restricted-query`. Use `sql:read:restricted-query` if the tool lists SQL warehouses before it connects.
- It can run `SELECT` and `DESCRIBE`. It cannot run `INSERT`, `CREATE TABLE` or `DROP TABLE`, and it cannot call other SQL APIs.
- Do not use this token for a tool that writes results back to a table.

### AI agents and MCP clients

- Scopes: `sql:restricted-query` and `unity-catalog:read` for data access. Add `genie` for Genie conversations or `model-serving-inference` for model queries, only when the agent needs them.
- It can query data and read catalog metadata. A token with `unity-catalog:read` lists catalogs but cannot create a schema.
- Do not add `genie` casually: the scope also covers creating Genie spaces. The `:read` modifier is not enough for starting a conversation or querying an index, because those calls are not GET or HEAD requests.

### Monitoring and alerting

- Scopes: `jobs:read`, `pipelines:read`, `clusters:read` and `query-history:read`, as needed.
- It can list and get jobs, pipelines, clusters and query history. A token with `jobs:read` can list jobs but cannot create or delete one.
- Do not use it to trigger a run or a restart. Those calls are POST requests and need the full scope.

### CI/CD deployment

- Scopes: start with `jobs`, `pipelines`, `workspace` and `files` on a scoped OAuth secret for a service principal, and add scopes as the deployment reports missing ones.
- It can create and update jobs and pipelines and import files. It cannot manage users, groups or tokens.
- Do not use a personal access token of a person for a pipeline. The documentation does not list which scopes a bundle deployment needs, so read the missing-scope errors and add only those.

### Data pipelines and scripts

- Scopes: `sql` for scripts that write data, `files` for uploads and downloads, `unity-catalog:read` for metadata.
- It can run any SQL statement that its user may run and read and write files. It cannot start jobs or change compute.
- Do not use plain `sql` for a script that only reads. Use `sql:restricted-query`.

### Admin automation

- Scopes: `identity`, `access-management` or `settings`, only the ones the script needs.
- It can manage the identities, permissions or settings that its scope covers.
- Do not add `authentication` unless the token manages other tokens. A token with only that scope can create a token with full access.

## SQL access levels, from narrowest to widest

SQL is where most people start, so the levels are worth knowing in order.

- `sql:restricted-query`: `SELECT` and `DESCRIBE` through the Statement Execution API and SQL drivers. No writes, no DDL, no other SQL API calls.
- `sql:read:restricted-query`: the same queries, plus the read operations of the `sql` scope, such as listing SQL warehouses.
- `sql`: everything in the scope, including `INSERT`, `CREATE TABLE`, `DROP TABLE` and warehouse changes. In the UI this is Read + Restricted query + Write.

`sql:read` alone sits beside this list, not in it. It can list warehouses, but it cannot run a query, because running a statement is a POST request: `Provided access token has scope(s) [sql:read] that cannot send a POST request to this endpoint`. That is why the `restricted-query` modifier exists.

## Personal access tokens or OAuth secrets

Both carry scopes, but they behave differently.

- A personal access token belongs to one user in one workspace. You set its scopes at creation and can change them later with a PATCH request. It can be valid for up to two years by default, and Databricks revokes it after 90 days without use. A workspace allows up to 600 tokens per user.
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

# 3. Refused: INSERT
curl -s -X POST "<workspace-url>/api/2.0/sql/statements" -H "Authorization: Bearer <scoped-token>" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": "<warehouse-id>", "wait_timeout": "30s", "statement": "INSERT INTO <catalog>.<schema>.orders VALUES (2, \"x\")"}'
```

The `SELECT` returns the rows with the state `SUCCEEDED`. The `INSERT` returns the state `FAILED` with `[OP_NOT_SUPPORTED_READ_ONLY]`, and the table keeps its original rows. The full example, including setup, every test call and cleanup, is in the [token-scopes](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/token-scopes) folder of the repository.

## Things to know

- Use the missing-scope error to find the scope. A call to the Jobs API with a `sql` token returns HTTP 403 with `Provided access token does not have required scopes: jobs`. A call with the right scope but the wrong method returns `Provided access token has scope(s) [jobs:read] that cannot send a POST request to this endpoint`.
- Write the scopes exactly. An unknown name returns HTTP 400 with `Invalid scopes: <name>`. The literal `all-apis` and `all-apis:read` are not accepted for personal access tokens. For full access, send an empty `scopes` array.
- The `authentication` scope removes the limit. A token with only `authentication` is refused on the Jobs API, but it can create a new token with an empty scopes array that is not refused. Give the scope only to tokens that manage tokens.
- Wait after you change scopes. A PATCH on a personal access token can take up to ten minutes to apply, so test after the wait, not right after the call. To change the scopes of an OAuth secret, generate a new secret.
- Check the scope for the data you need. Query history needs the `query-history` scope, not `sql`, and a few scopes in the live list, such as `bundle`, have no entry in the API scopes reference. When the documentation does not say what a scope covers, create a test token and read the error.

## Best practices

- Create one token per tool, with a comment that names the tool and the owner.
- Set the shortest lifetime that works, and rotate the token before it expires.
- Start from the narrowest scope and add scopes only when a call fails with a missing-scope error.
- Prefer scoped OAuth secrets for service principals over personal access tokens for anything automated.
- Review your tokens regularly and remove the ones that have not been used.

## Summary

Token scopes limit which APIs a Databricks token can call, and the `:read` and `:restricted-query` modifiers narrow a scope to read operations or read-only SQL. The main takeaway is to start from the narrowest scope for the job, check it with one allowed call and one refused call, and read the missing-scope error to add what is missing. Use scoped tokens for every BI tool, agent, script and pipeline, and scoped OAuth secrets for anything that runs on its own.

Which of your tokens still has full access?

## References

- [Scope modifiers for Databricks tokens](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/scope-modifiers)
- [Authenticate with Databricks personal access tokens](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat)
- [Authorize service principal access with OAuth (M2M)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-m2m)
- [Authorize user access with OAuth (U2M)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-u2m)
- [Monitor and manage personal access tokens](https://learn.microsoft.com/en-us/azure/databricks/admin/access-control/tokens)
- [API scopes reference](https://docs.databricks.com/api/workspace/scopes)
- [November 2026 release notes](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november)
