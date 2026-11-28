# Databricks token scopes

Working code for the guide "Databricks Token Scopes Explained: Least-Privilege Access". It creates short-lived test tokens with different scopes and records what each one can and cannot do.

Scope modifiers (`:read`, `:restricted-query`) are generally available as of November 4, 2026.

## What is here

| Path | What it holds |
| --- | --- |
| `article.md` | The article draft |
| `notes/facts.md` | Documentation fact sheet, one row per claim, with URLs |
| `notes/token-scopes.json` | Response of `GET /api/2.0/token-scopes` from a workspace (61 scopes, no secrets) |
| `tests/` | The test scripts, their output and `results.md` |
| `screenshots/` | `ui-01` to `ui-09`: the token and service principal secret screens, with token values and IDs hidden |
| `diagrams/` | The scope and modifier diagram |
| `decision-table.png`, `linkedin-image.png` | Visuals for the article and the post |

## Prerequisites

- An Azure Databricks workspace and a token that can create tokens (your own personal access token works).
- A SQL warehouse (a serverless warehouse is fine) and a catalog where you can create a schema.
- Python 3.9 or above. The scripts use only the standard library.

## Setup

```bash
export DATABRICKS_HOST=<workspace-url>        # for example https://adb-1234567890123456.7.azuredatabricks.net
export DATABRICKS_TOKEN=<your-personal-access-token>
export WAREHOUSE_ID=<warehouse-id>
export CATALOG=<catalog>
```

Test token values are stored in `tests/.tokens.json`, which is ignored by git. The scripts never print a token.

## Run the tests

```bash
python tests/run_tests.py > tests/output.txt     # tests 1 to 6, creates a schema <catalog>.token_scopes_test
python tests/test7_propagation.py                # test 7, takes about five minutes
python tests/test8_setup.py && python tests/test8_oauth_secret.py   # test 8, creates a test service principal first
python tests/test10_extras.py                    # empty scopes array, all-apis:read, authentication scope
python tests/test11_sql_read.py                  # plain sql:read
```

### The calls behind the tests

Create a scoped token:

```bash
curl -s -X POST "$DATABRICKS_HOST/api/2.0/token/create" \
  -H "Authorization: Bearer <admin-or-owner-token>" -H "Content-Type: application/json" \
  -d '{"lifetime_seconds": 3600, "comment": "token-scopes test: t1", "scopes": ["sql:restricted-query"]}'
```

Run SQL with the scoped token (SELECT works, INSERT, CREATE TABLE and DROP TABLE fail):

```bash
curl -s -X POST "$DATABRICKS_HOST/api/2.0/sql/statements" -H "Authorization: Bearer <scoped-token>" \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": "<warehouse-id>", "wait_timeout": "30s", "statement": "SELECT * FROM <catalog>.token_scopes_test.t"}'
```

List SQL warehouses (fails for `sql:restricted-query`, works for `sql:read:restricted-query`):

```bash
curl -s -H "Authorization: Bearer <scoped-token>" "$DATABRICKS_HOST/api/2.0/sql/warehouses"
```

Jobs, with `jobs:read` (GET works, POST fails) and with a `sql` token (missing scope):

```bash
curl -s -H "Authorization: Bearer <scoped-token>" "$DATABRICKS_HOST/api/2.1/jobs/list?limit=1"
curl -s -X POST -H "Authorization: Bearer <scoped-token>" -H "Content-Type: application/json" \
  -d '{"name": "should-not-exist", "tasks": []}' "$DATABRICKS_HOST/api/2.1/jobs/create"
```

Unity Catalog, with `unity-catalog:read`:

```bash
curl -s -H "Authorization: Bearer <scoped-token>" "$DATABRICKS_HOST/api/2.1/unity-catalog/catalogs"
curl -s -X POST -H "Authorization: Bearer <scoped-token>" -H "Content-Type: application/json" \
  -d '{"name": "should_fail", "catalog_name": "<catalog>"}' "$DATABRICKS_HOST/api/2.1/unity-catalog/schemas"
```

Change the scopes of a token, then wait up to ten minutes:

```bash
curl -s -X PATCH "$DATABRICKS_HOST/api/2.0/token/<token-id>" \
  -H "Authorization: Bearer <admin-or-owner-token>" -H "Content-Type: application/json" \
  -d '{"token": {"scopes": ["jobs:read"]}, "update_mask": "scopes"}'
```

Create a scoped OAuth secret for a service principal and request a token (the secret path is the one the Databricks CLI uses for `service-principal-secrets-proxy create`):

```bash
curl -s -X POST "$DATABRICKS_HOST/api/2.0/accounts/servicePrincipals/<service-principal-id>/credentials/secrets" \
  -H "Authorization: Bearer <admin-token>" -H "Content-Type: application/json" \
  -d '{"lifetime": "3600s", "scopes": ["sql:restricted-query"]}'

curl -s -X POST "$DATABRICKS_HOST/oidc/v1/token" -u "<client-id>:<client-secret>" \
  -d "grant_type=client_credentials&scope=sql:restricted-query"
```

## Expected result

`tests/results.md` lists every call and its exact response. In short: `sql:restricted-query` runs SELECT and DESCRIBE and refuses INSERT, CREATE TABLE, DROP TABLE and listing warehouses. A token request for a wider scope than the secret allows is refused with `access_denied`.

## Cleanup

Revoke every test token, delete the test service principal and drop the test schema:

```bash
python tests/cleanup.py
```

The script revokes the tokens saved in `tests/.tokens.json` and every token whose comment starts with `token-scopes` or `reporting tool, read only` (the token made in the UI). Expired tokens return 404 and are skipped. Check Settings, Developer, Access tokens afterwards.
