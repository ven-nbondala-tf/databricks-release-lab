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

## Test 9: screenshot

`screenshots/token-dialog-access-levels.png` shows the Generate new token dialog with the `sql` scope. The access levels offered are Read, Restricted query, Read + Restricted query, Read + Restricted query + Write. Choosing BI Tools preselects `sql` with Read + Restricted query. The dialog was closed with Cancel and no token was created from it. The Auto-scope tokens switch is present and off.

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

## Cleanup

`python tests/cleanup.py` revoked 19 test tokens, listed 0 test tokens afterwards, deleted the test service principal (which removes its secrets), dropped the test schema and removed the local token file. Four probe tokens had already expired and returned 404. Test 11 revoked its own token. See `cleanup_output.txt`.
