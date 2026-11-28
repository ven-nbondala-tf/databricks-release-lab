# Test results: token scopes

Workspace type: Databricks Free Edition, serverless SQL warehouse. Run on 2026-11-28. Token values and IDs are masked or omitted. All test tokens were revoked at the end (see Cleanup).

## Live scope list (GET /api/2.0/token-scopes)

- 61 scopes. Every scope reports `allowed_modifiers` of only `read`. No entry lists `restricted-query`.
- The Token API still accepts `sql:restricted-query` and `sql:read:restricted-query` (tests 1 and 2).
- 15 scopes are in the live list but not in the documentation's API scopes reference (46 entries): `ai-gateway`, `billing`, `bundle`, `bundle-deployments`, `compute-migrations`, `custom-llms`, `databricks-connect`, `disaster-recovery`, `forecasting`, `genie-agents`, `genie-migrate`, `provisioning`, `qualitymonitor`, `search`, `zerobus`.
- The documentation reference has no scope that the live list lacks.

## Test 1: sql:restricted-query (SQL, Statement Execution API)

| Call | Result |
| --- | --- |
| SELECT 1 | SUCCEEDED |
| SELECT from a table | SUCCEEDED |
| DESCRIBE TABLE | SUCCEEDED |
| INSERT | FAILED: `[OP_NOT_SUPPORTED_READ_ONLY] AppendData RelationV2[id#13788, note#13789] <catalog>.token_scopes_test.t, [__internal_isByName=false], false, false, true is not supported in read-only session mode. SQLSTATE: 42KD1` |
| CREATE TABLE | FAILED: `[OP_NOT_SUPPORTED_READ_ONLY] CreateTable [...] is not supported in read-only session mode. SQLSTATE: 42KD1` |
| DROP TABLE | FAILED: `[OP_NOT_SUPPORTED_READ_ONLY] DropTable false, false is not supported in read-only session mode. SQLSTATE: 42KD1` |
| GET /api/2.0/sql/warehouses | HTTP 403 `Provided access token has scope(s) [sql:restricted-query] that cannot send a GET request to this endpoint` |

The statement calls return HTTP 200 with the failure in `status.state`.

## Test 2: sql:read:restricted-query

- List SQL warehouses: HTTP 200.
- SELECT from a table: SUCCEEDED.
- INSERT: FAILED with `[OP_NOT_SUPPORTED_READ_ONLY] ... is not supported in read-only session mode. SQLSTATE: 42KD1`.

## Test 3: plain sql (comparison)

SELECT, INSERT, CREATE TABLE and DROP TABLE all SUCCEEDED. Listing warehouses: HTTP 200. After the tests the table held the seed row and the row inserted by this token, and none from tests 1 and 2.

## Test 4: jobs:read and clusters:read

- `jobs:read`: GET jobs/list HTTP 200. POST jobs/create HTTP 403 and POST jobs/delete HTTP 403, both `Provided access token has scope(s) [jobs:read] that cannot send a POST request to this endpoint`.
- `clusters:read`: GET clusters/list HTTP 200. POST clusters/delete HTTP 403 with the same wording for `[clusters:read]`.

## Test 5: unity-catalog:read

GET catalogs HTTP 200. POST schemas HTTP 403 `Provided access token has scope(s) [unity-catalog:read] that cannot send a POST request to this endpoint`.

## Test 6: missing scope

With a `sql` token: GET jobs/list HTTP 403 `Provided access token does not have required scopes: jobs`. GET clusters/list HTTP 403 `Provided access token does not have required scopes: clusters`.

## Test 7: propagation

A token created with `sql:read` was changed with PATCH to `jobs:read` (HTTP 200). Polling every 5 seconds, the warehouse list was refused after 305 seconds and the Jobs API started working after 311 seconds. The documentation says up to ten minutes. The PATCH response did not return the `scopes` field in the shape the script read, so the change was confirmed by behavior.

## Test 8: OAuth secret limited to sql:restricted-query

The service principal was created in the workspace. The secret was created with `POST /api/2.0/accounts/servicePrincipals/<id>/credentials/secrets` on the workspace host and `{"lifetime": "3600s", "scopes": ["sql:restricted-query"]}` (HTTP 200, response lists the scopes). That path is what the Databricks CLI command `service-principal-secrets-proxy create` calls.

| Token request scope | Result |
| --- | --- |
| `sql:restricted-query` | HTTP 200, granted scope `sql:restricted-query`, expires_in 3600. SELECT succeeded (after the service principal was given SQL access, CAN USE on the warehouse and SELECT on the table). List warehouses HTTP 403, list jobs HTTP 403 |
| `sql` | HTTP 403 `access_denied`: `Scopes 'sql' are not assigned to the client <id>; the client has scope(s) [sql:restricted-query] that cannot send this request` |
| `all-apis` | HTTP 403 `access_denied`: `Scopes 'all-apis' are not assigned to the client <id>` |
| `sql:restricted-query jobs:read` | HTTP 403 `access_denied`: `Scopes 'jobs:read' are not assigned to the client <id>` |

A wider request is refused. It is not narrowed silently. The first attempt, before the service principal had SQL access, returned `This API is disabled for users without the databricks-sql-access or workspace-consume entitlements`.

## Test 9: UI screenshots (screenshots/ui-*.png)

Taken in the browser on 2026-11-28. Taken: ui-01 (Developer page with Manage), ui-02 (Generate new token dialog), ui-03 (scope list), ui-04 (sql access levels, replaces the earlier screenshot), ui-05 (token created, value hidden), ui-06 (token list), ui-07 (Update token dialog, cancelled), ui-08 (service principal Secrets tab), ui-09 (Generate OAuth secret dialog with sql set to Restricted query, cancelled, no secret created).

Skipped: ui-10 (the OP_NOT_SUPPORTED_READ_ONLY error in the SQL editor). The SQL editor runs as the signed-in user and cannot use a personal access token, so the article keeps the curl output.

How values were kept off the images:
- ui-05: the token field shows dots, and the value on the page was overwritten with a placeholder by a script, without being read, before the screenshot. No token value was logged or saved.
- ui-06: the Token ID column was overwritten with a placeholder before the screenshot, and the crop holds the header and the new token's row only, not the other tokens in the workspace.
- Crops exclude the workspace URL, the signed-in user and the sidebar. No client IDs, service principal IDs or warehouse IDs appear. ui-09 was cancelled, so no secret was generated.
- Every image was checked by eye before it was kept.

Findings from the UI:
- Choosing BI Tools preselects `sql` with Read + Restricted query. Choosing Restricted query switches the scope type shown to Other APIs.
- The access levels for `sql` are Read, Restricted query, Read + Restricted query and Read + Restricted query + Write, as the documentation says.
- The token row menu has Update token and Revoke token. Update token changes the name and the scopes. Lifetime in the dialog is in whole days, minimum 1.
- The Generate OAuth secret dialog needs a Lifetime (days) between 1 and 730 and the same scope picker. It did not show an "all APIs" option on this workspace, although the documentation mentions one.
- The Auto-scope tokens switch is present and off.

UI tokens and service principal created for the screenshots: one personal access token named "reporting tool, read only" (1 day, `sql:restricted-query`) and one service principal. Both were removed at the end (see Cleanup).

## Example rerun (review note 4)

The example in the article sends the INSERT body from a file with `-d @insert.json` and uses single quotes in the SQL: `INSERT INTO <catalog>.<schema>.orders VALUES (2, 'x')`. It was rerun with a new 15 minute `sql:restricted-query` token. The `SELECT` returned the seed row and the state SUCCEEDED. The `INSERT` returned the state FAILED with `[OP_NOT_SUPPORTED_READ_ONLY] AppendData ...`, and the table still had one row afterwards. The token was revoked in the cleanup below.

## Test 10: edge cases from the documentation

- PAT with `all-apis:read`: HTTP 400 `Invalid scopes: all-apis:read`.
- PAT with `all-apis`: HTTP 400 `Invalid scopes: all-apis`.
- PAT with an unknown scope: HTTP 400 `Invalid scopes: not-a-scope`.
- PAT with an empty scopes array: HTTP 200, the response has no `scopes` and no `autoscope_state`. GET jobs/list works.
- PAT with only `authentication`: GET jobs/list HTTP 403 `does not have required scopes: jobs`. The same token created a new token with an empty scopes array (HTTP 200), and that token could call the Jobs API (HTTP 200).

## Test 11: plain sql:read

List SQL warehouses HTTP 200. SELECT through the Statement Execution API HTTP 403 `Provided access token has scope(s) [sql:read] that cannot send a POST request to this endpoint`. GET query history HTTP 403 `Provided access token does not have required scopes: query-history`.

## Differences from the documentation

1. The scope modifiers page says INSERT and UPDATE under `sql:restricted-query` fail with `[INSUFFICIENT_PERMISSIONS]`. Through the Statement Execution API the INSERT failed with `[OP_NOT_SUPPORTED_READ_ONLY]`, the same error as DDL.
2. The live `GET /api/2.0/token-scopes` lists only the `read` modifier and 61 scopes. The documentation lists two modifiers and 46 scopes in the reference.
3. The documentation does not show the missing-scope error. It is HTTP 403 with `does not have required scopes: <scope>`, or `has scope(s) [<scope>] that cannot send a <METHOD> request to this endpoint`.
4. The `sql` scope description in the reference mentions query history. The query history API needs the separate `query-history` scope.
5. The documentation does not say what happens when a token request asks for a wider scope. It is refused with HTTP 403 `access_denied`.
6. The documentation shows scoped secrets only in the UI. The workspace REST path above accepts `scopes` as well.

## Not tested

- Real BI tools (Tableau, Power BI), MCP clients and bundle deployments. Their scope needs are described from the documentation only.
- Auto-scoping, which needs 30 days of observation.
- Scopes without a documented operation list (`bundle`, `bundle-deployments`, `billing`).
- OAuth user-to-machine (U2M) token requests.

## Cleanup (first run)

`python tests/cleanup.py` revoked 19 test tokens, listed 0 test tokens afterwards, deleted the test service principal (which removes its secrets), dropped the test schema and removed the local token file. Four probe tokens had already expired and returned 404. Test 11 revoked its own token. See `cleanup_output.txt`.

## Cleanup (UI screenshots and example rerun)

`python tests/cleanup.py` revoked 2 more tokens (the token made in the UI and the token for the example rerun), listed 0 test tokens afterwards, deleted the second test service principal and dropped the test schema again. No OAuth secret was generated in the UI, and the secrets of the first service principal went with it. See `cleanup_output_2.txt`.
