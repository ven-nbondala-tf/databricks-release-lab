# Fact sheet: Databricks token scopes and scope modifiers

Date checked: 2026-11-28. Sources: official Azure Databricks docs (learn.microsoft.com) and the API scopes reference on docs.databricks.com. No token values recorded.

URL keys:
- SM = https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/scope-modifiers (ms.date 2026-11-19)
- PAT = https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat (ms.date 2026-11-19)
- M2M = https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-m2m (ms.date 2026-11-19)
- U2M = https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/oauth-u2m (ms.date 2026-11-23)
- REF = https://docs.databricks.com/api/workspace/scopes (API scopes reference, title "API scopes | Databricks API Reference")
- TOK = https://learn.microsoft.com/en-us/azure/databricks/admin/access-control/tokens
- RN = https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november

Caveat: the fetch tool summarizes pages with a small model. REF operation lists are as reported by that tool and should be spot-checked in a browser before quoting specific operation names in the article. All microsoft.com pages fetched without fallback to docs.databricks.com/aws.

## Main claims

| # | Claim | URL | Status | Date checked |
|---|---|---|---|---|
| 1 | Release note, "November 4, 2026": heading "Scope modifiers for personal access tokens and OAuth are generally available". Status = generally available. | RN | Confirmed | 2026-11-28 |
| 2 | Modifier definition: "A scope modifier narrows an API scope to a subset of its operations." Syntax: append after a colon, e.g. `clusters:read`. No modifier = every operation in the scope. | SM | Confirmed | 2026-11-28 |
| 3 | `:read` allows only the scope's read operations (`GET` and `HEAD` requests). Example: `clusters:read` lists/gets clusters, not create/edit/delete. Accepted by scopes generally (page names no restriction; UI offers Read for every scope). | SM | Confirmed (list of scopes that do not accept it: NOT FOUND) | 2026-11-28 |
| 4 | `:restricted-query` allows read-only SQL queries. Applies only to the `sql` scope. Can run `SELECT`/`DESCRIBE` via Statement Execution API and SQL drivers/connectors; cannot call other SQL APIs such as listing SQL warehouses. | SM | Confirmed | 2026-11-28 |
| 5 | Combined modifiers: `sql:read:restricted-query` allows the sql scope's read operations (e.g. listing SQL warehouses) plus read-only queries. | SM | Confirmed | 2026-11-28 |
| 6 | With `sql:restricted-query`, DDL fails with `[OP_NOT_SUPPORTED_READ_ONLY] ... is not supported in read-only session mode. SQLSTATE: 42KD1` (e.g. CREATE TABLE, DROP TABLE). | SM | Confirmed | 2026-11-28 |
| 7 | With `sql:restricted-query`, data changes (INSERT, UPDATE) fail with `[INSUFFICIENT_PERMISSIONS] Insufficient privileges`, "even on tables you own". | SM | Confirmed | 2026-11-28 |
| 8 | Where modifiers can be used: scoped PATs; scoped OAuth secrets for service principals; the `scope` parameter of an OAuth token request (user, service principal, or workload identity federation exchange). | SM | Confirmed | 2026-11-28 |
| 9 | UI access levels (PAT or OAuth secret, after adding a scope): Read = `<scope>:read`; Read + Write = `<scope>` (no modifier). | SM | Confirmed | 2026-11-28 |
| 10 | UI access levels for `sql` only: Restricted query = `sql:restricted-query`; Read + Restricted query = `sql:read:restricted-query`; Read + Restricted query + Write = `sql` (no modifier). | SM | Confirmed | 2026-11-28 |
| 11 | PAT UI flow: Settings > Developer > Access tokens > Manage > Generate new token; choose scope type "BI Tools" (Tableau, Power BI, SQL warehouses) or "Other APIs" (choose scopes manually). | PAT | Confirmed | 2026-11-28 |
| 12 | PATs: valid for one workspace; up to 600 PATs per user per workspace; revoked automatically after 90 days unused. Cannot automate account-level functionality. Databricks recommends OAuth over PATs. | PAT | Confirmed | 2026-11-28 |
| 13 | PAT lifetime: set in days at creation; workspace max default 730 days (two years); admin can set `maxTokenLifetimeDays` (applies to new tokens only; "0" reverts to 730). | PAT, TOK | Confirmed | 2026-11-28 |
| 14 | PAT API: `POST /api/2.0/token/create` with body fields `lifetime_seconds`, `scopes` (array), `autoscope_enabled`. Response has `token_value` and `token_info` (`token_id`, `creation_time`, `expiry_time`, `comment`, `scopes`, `last_accessed_time`). Example scopes `["sql","authentication"]` returned as `["authentication","sql"]` (sorted). | PAT | Confirmed | 2026-11-28 |
| 15 | PAT modifiers via API: `"scopes": ["clusters:read", "sql:read:restricted-query"]`. | PAT | Confirmed | 2026-11-28 |
| 16 | Update PAT scopes: `PATCH /api/2.0/token/<token_id>` with `{"token": {"scopes": [...]}, "update_mask": "scopes"}`. Caller must have the `authentication` scope. Service principal token variant noted as `PATCH /api/2.0/token/{token_id_sha256}`. | PAT | Confirmed | 2026-11-28 |
| 17 | Empty `scopes` array means full workspace access: "set `scopes` to an empty array" = the `all-apis` scope. | PAT, SM | Confirmed | 2026-11-28 |
| 18 | "The literal string `all-apis` is not an accepted scope value" for PATs (use `[]`). | PAT | Confirmed | 2026-11-28 |
| 19 | PATs do not support `all-apis:read`. OAuth does accept `all-apis:read` (read operations on every API the principal is authorized for). | SM | Confirmed | 2026-11-28 |
| 20 | Propagation: "Scope changes can take up to ten minutes to propagate." (stated in the PAT update section) | PAT | Confirmed | 2026-11-28 |
| 21 | Authentication scope warning (PAT): "Tokens with the `authentication` scope can create new tokens with any scope." Grant only to tokens that manage other tokens. Same warning for OAuth secrets. | PAT, M2M | Confirmed | 2026-11-28 |
| 22 | Authentication scope exception (OAuth): "An access token can't exceed the scopes of the secret it was minted from, except for a secret with the `authentication` scope." | SM | Confirmed | 2026-11-28 |
| 23 | Claim that `authentication` is "always added" or "does not restrict authentication" (scopes that never restrict authentication). | PAT, SM, M2M | NOT FOUND (only the "can create tokens with any scope" wording and the OAuth exception exist) | 2026-11-28 |
| 24 | `authentication` scope in REF covers: List/Create/Delete Service Principal Secret (Proxy), Create On Behalf Of Token, token management list/update/delete, Get Token, Create/Revoke/List/Update Token. | REF | Confirmed (via summarizer) | 2026-11-28 |
| 25 | Auto-scoping: observes token API usage for 30 days, then applies inferred scopes; runs once per token; token keeps `all-apis` during observation; reminder email 7 days before enforcement plus an enforcement email. | PAT | Confirmed | 2026-11-28 |
| 26 | Auto-scoping applies only to tokens with lifetime longer than 30 days; UI toggle "Auto-scope tokens" appears only when an admin enabled the auto-scoping preview for the workspace; per-token field `autoscope_enabled`. Admin controls preview via account console or workspace Previews page. | PAT | Confirmed | 2026-11-28 |
| 27 | Opting out of auto-scoping: set specific scopes before enforcement (stops it permanently); setting back to `all-apis` (`[]`) is a no-op and does not stop it; or admin turns the preview off. After enforcement it does not run again. | PAT | Confirmed | 2026-11-28 |
| 28 | Auto-scoping status: `GET /api/2.0/token/list` returns `autoscope_state` (e.g. `AUTOSCOPE_STATE_COMPLETED`), `inferred_scopes` for new tokens, `backfill_scopes` for existing tokens. | TOK | Confirmed | 2026-11-28 |
| 29 | Missing scope behaviour: "the request fails with an error indicating the missing scope." No HTTP status code and no exact error body shown. | PAT | Confirmed (generic only); HTTP code and exact text NOT FOUND | 2026-11-28 |
| 30 | `GET /api/2.0/token-scopes`: "To view all available scopes, use `GET /api/2.0/token-scopes`." Response shape not documented on the fetched pages. | PAT | Confirmed (existence); response shape NOT FOUND | 2026-11-28 |
| 31 | PATs vs OAuth secrets vs OAuth token requests: PAT scopes set at creation (UI or `scopes` array), editable later via PATCH. OAuth secret scopes set at generation and "can't be changed afterward" (use Clone in the Secrets table). Token request: `scope` param, space-separated. | PAT, M2M, SM | Confirmed | 2026-11-28 |
| 32 | Scoped OAuth secrets for service principals are supported. Default secret = `all-apis`. "A secret created without scopes, including every existing secret, keeps `all-apis` access." UI: Settings > Identity and access > Service principals > Manage > Secrets > Generate secret > Scopes; option "all APIs (not recommended)". | M2M | Confirmed | 2026-11-28 |
| 33 | Token minted from a scoped secret "can't exceed the secret's scopes" (limits blast radius). Exact response when a request asks for a wider scope (error vs silent narrowing, HTTP code): not documented. | M2M, SM | Confirmed (rule); behaviour on wider request NOT FOUND | 2026-11-28 |
| 34 | OAuth M2M token request examples: `grant_type=client_credentials&scope=clusters:read sql:read:restricted-query`; `scope=all-apis` for all APIs. Workspace endpoint `https://<databricks-instance>/oidc/v1/token`; account endpoint `https://accounts.azuredatabricks.net/oidc/accounts/<account-id>/v1/token`. Tokens valid one hour (`expires_in` 3600). | M2M | Confirmed | 2026-11-28 |
| 35 | OAuth U2M: authorize URL separates scopes with `+` (e.g. `scope=all-apis+offline_access`); token request uses spaces. Tip: replace `all-apis` with specific scopes, may include modifiers like `clusters:read`, `sql:restricted-query`. Response includes `scope`, `refresh_token`, token valid one hour. | U2M, SM | Confirmed | 2026-11-28 |
| 36 | OAuth secret limits: up to 5 secrets per service principal; max lifetime 730 days (UI) / "up to two years"; auto-deleted after 90 days unused. No documented max number of scopes per token or secret. | M2M | Confirmed; max scopes per token NOT FOUND | 2026-11-28 |
| 37 | The API scopes page URL linked from scope-modifiers and M2M is https://docs.databricks.com/api/workspace/scopes. The PAT page links a different path, https://docs.databricks.com/api/workspace/api/scopes (not fetched). | SM, M2M, PAT | DIFFERS (two link paths) | 2026-11-28 |

## Scope reference (REF): every scope, 46 entries plus a duplicate "knowledge"

Page intro: "API scopes restrict which Databricks REST API endpoints a token can access." Each scope lists operations by display name (endpoint paths not shown by the summarizer). The SCIM "Me" operation (`/api/scim/v1/me`) appears under every scope. Status for every row: Confirmed (via summarizer, spot-check advised). Date checked 2026-11-28. URL: REF.

| # | Scope | Display name and what it covers | Operations covered |
|---|---|---|---|
| S1 | `ai-functions` | AI Functions: classification, extraction, batch jobs | Ai Classify, Ai Decide, Ai Extract, Ai Parse Document, List/Create/Get/Cancel Batch |
| S2 | `ai-search` | AI Search indexes and endpoints | Endpoint create/get/update/delete/list; Index create/get/delete/list/query/scan/sync; Upsert Data; Remove Data |
| S3 | `dashboards` | AI/BI Dashboards incl. publishing, schedules, subscriptions | List/Create/Migrate/Update/Get/Trash/Publish/Unpublish/Revert Dashboard; Get Published Dashboard (+Token Info); schedule and subscription CRUD |
| S4 | `access-management` | Users, service principals, groups, permissions | Restricted Sharing Group list/create/get/delete; Get/Set/Update Object Permissions; List Permission Levels; List Assignable Roles For Resource Proxy; Get/Update Rule Set Proxy |
| S5 | `agent-kit` | AgentKit: durable memory and session state for agents | Memory Store CRUD and permissions; Session Store CRUD and permissions; Memory create/get/update/delete/list/search/extract; Session create/get/list/fork/update/delete; session items append/clear/pop/list |
| S6 | `alerts` | Databricks SQL alerts | List, Create, Update, Get, Trash Alert |
| S7 | `apps` | Databricks Apps, spaces, deployments, scan findings | Space CRUD; App create/update/get/list/delete/start/stop; App deployments; Async Update App; Get App Update; thumbnail update/delete; deployment scan findings |
| S8 | `authentication` | Auth settings, service principal secrets, access tokens | List/Create/Delete Service Principal Secret Proxy; Create On Behalf Of Token; token management list/update; Delete/Get/Create/Revoke/List/Update Token |
| S9 | `cleanrooms` | Clean rooms, assets, auto-approval rules, task runs | Clean Room CRUD; Asset create/list/update/delete/get; Asset Review; Asset Revisions; Auto Approval Rule CRUD; Output Catalog; notebook task runs; task runs |
| S10 | `clusters` | Compute: clusters, policies, policy families, compliance | Cluster Policies (create/delete/edit/get/list); Clusters (create/edit/delete/get/list/start/restart/resize/pin/unpin/permanent delete/change owner/events/node types/zones/spark versions/update); compliance enforce/get/list/cancel; Policy Families list/get |
| S11 | `command-execution` | Run commands/code on clusters, execution contexts | Cancel, Execute, Get Command Status, Create, Destroy, Get Context Status |
| S12 | `dataclassification` | Data classification for Unity Catalog catalogs | Create/Get/Update/Delete Catalog Config; Rescan Catalog |
| S13 | `dataquality` | Data quality monitoring for UC objects | Monitor CRUD/list; Refresh create/get/update/delete/cancel/list |
| S14 | `sql` | Databricks SQL: warehouses, queries, execution, alerts | Alerts CRUD; Queries create/list/update/get/trash; Statement Execution v1 and v2 (Execute Statement, Get Statement Result, Cancel Statement, Get Result Data); Warehouses (list/create/get/delete/edit/start/stop, workspace warehouse config get/set); Default Warehouse Override create/list/update/delete/get |
| S15 | `workspace` | Workspace entities: Git credentials, repos, workspace files | Git Credentials CRUD/list; Repos CRUD/list; Workspace Files Delete, Export, Get Status, Import, List, Mkdirs |
| S16 | `sharing` | Delta Sharing: providers, recipients, shares, federation policies | Federation Policy CRUD/list; Provider CRUD/list/shares/assets; Retrieve Access Token; Get Activation Url Info; Recipient CRUD/list/rotate token/share permissions; Share CRUD/list/permissions |
| S17 | `domains` | Domains for organizing data assets | List, Create, Update, Get, Delete Domain |
| S18 | `environments` | Workspace base environments for serverless | Workspace Base Environment list/create/get/update/delete/refresh; default get/update; Get Operation |
| S19 | `files` | File management (filesystem-style) | Add Block, Close, Create, Delete, Get Status, List, Mkdirs, Move, Put, Read, Create/Delete Directory, Get Directory Metadata, List Directory Contents, Get File Metadata, Upload File, Delete File, Download File |
| S20 | `genie` | Genie spaces, conversations, messages, evaluations | Space create/get/list/update/trash; conversations and messages; attachment query execute/result; full query result download; comments; feedback; eval runs/results; visualization download |
| S21 | `global-init-scripts` | Global init scripts | List, Create, Get, Update, Delete Global Init Script |
| S22 | `identity` | Users, groups, service principals, workspace assignments | Group, Service Principal, User (Proxy) create/list/get/update/delete/resolve; external group/SP/user get; direct group members; transitive parent groups; workspace assignment CRUD; workspace identity/access detail |
| S23 | `instance-pools` | Instance pools | Create, Delete, Edit, Get, List Instance Pool |
| S24 | `instance-profiles` | Instance profiles | Add, Edit, List, Remove Instance Profile |
| S25 | `jobs` | Jobs and Workflows: jobs, runs, policy compliance | Create/Delete/Get/List/Reset/Update Job; Run Now; Cancel Run; Cancel All Runs; Delete Run; Export Run; Get Run; Get Run Output; List Runs; Repair; Submit Run; compliance enforce/get/list |
| S26 | `knowledge` | Knowledge pages and asset links (listed twice on page; second entry described as rich-text wiki pages for UC objects, same operations) | List/Create/Get/Update/Delete Page; Create/Get/Delete Asset Link |
| S27 | `knowledge-assistants` | Knowledge Assistants, examples, knowledge sources | Assistant CRUD/list; Example CRUD/list; Knowledge Source CRUD/list; Sync Knowledge Sources |
| S28 | `lakewatch` | Lakewatch data sources, parsers, detection rules, per-catalog config | Datasource, Parser, Parser Version, Builtin Parser, Rule create/get/list/update/delete; alert/common/datasource/rule config get/update |
| S29 | `libraries` | Libraries on clusters | All Cluster Statuses, Cluster Status, Install Libraries, Uninstall Libraries |
| S30 | `mlflow` | MLflow experiments, runs, logged models, feature store, model registry | Experiments, runs, logged models, issues; Features, materialized features, streams; Model Registry (models, versions, tags, comments, webhooks, transition requests) |
| S31 | `marketplace` | Marketplace, provider and consumer | Exchanges, filters, listings, files, providers, provider analytics dashboards, installations, personalization requests, consumer listings and providers |
| S32 | `model-serving` | Model serving endpoints and querying | Inference Endpoint CRUD/list, provisioned throughput, AI gateway, config, rate limits, tags, notifications, telemetry, schema, logs, metrics; Query |
| S33 | `model-serving-inference` | Query model serving endpoints for inference | Query |
| S34 | `networking` | Network connectivity, IP access lists | List/Create/Get/Update/Delete/Replace Ip Access List |
| S35 | `notifications` | Notification destinations | List/Create/Get/Update/Delete Notification Destination |
| S36 | `pipelines` | Pipelines (Delta Live Tables), runs, events | List, Create, Get, Edit, Delete, Clone, Apply Environment, Events, Stop, List Updates, Start, Get Update |
| S37 | `postgres` | Postgres database instances, projects, branches | Database API (instances, catalogs, synced tables, tables, credentials); Postgres API (projects, branches, endpoints, databases, roles, snapshots, migrations, CDF, assessments, catalogs, synced tables) |
| S38 | `query-history` | Query history | List Queries |
| S39 | `scim` | Users, service principals, groups, permissions | Permissions get/set/update/levels; Group, Service Principal, User create/list/get/update/patch/delete |
| S40 | `sandbox` | Sandboxes | Execute Command Sync, List Commands, List/Create/Get/Update/Delete/Start/Stop Sandbox |
| S41 | `secrets` | Secrets, secret scopes, ACLs | Acl get/put/delete/list; Secret get/put/delete/list; Scope create/delete/list |
| S42 | `settings` | Security settings for accounts and workspaces | List Workspace Settings Metadata, Get Public Workspace Setting, Patch Public Workspace Setting |
| S43 | `supervisor-agents` | Supervisor Agents, examples, tools | Supervisor Agent CRUD/list; Example CRUD/list; Tool CRUD/list |
| S44 | `tags` | Tag policies and tag assignments | Tag Assignment CRUD/list; Tag Policy CRUD/list |
| S45 | `unity-catalog` | Data governance: metastores, catalogs, schemas, tables, volumes, credentials, etc. | AI Gateway (MCP/model provider/model services, skills); Software Artifacts; ABAC Policies; Artifact Allowlists; Catalogs; Connections; Credentials (incl. temporary credentials); Entity Tag Assignments; External Lineage; External Locations; External Metadata; Functions; Grants; Metastores; Online Tables; Registered Models; Resource Quotas; Access Requests; Schemas; Secrets; System Schemas; Tables; Volumes; Wikis; Workspace Bindings |
| S46 | `vector-search` | Vector Search endpoints and indexes | Endpoint list/create/get/delete/patch/budget policy; metrics; Vector Index list/create/get/delete/query/query next page/scan/sync/upsert/delete data |

Note: `sql`, `clusters`, `jobs`, `unity-catalog`, `files` are all full scopes in the reference (prefix-looking names are not special). Full per-operation lists are long; re-fetch REF when writing the article table.

## Open questions

- Exact error body and HTTP status when a token lacks the needed scope: not on any fetched page. Must be captured by testing, and kept in tests/ notes only.
- Response shape of `GET /api/2.0/token-scopes` is undocumented here. Test it.
- Behaviour when an OAuth token request asks for a scope wider than the secret allows (error, HTTP code, or silent narrowing): not documented.
- Which scopes accept `:read`: pages imply all, but no explicit statement. Test with one or two.
- Whether `authentication` is "always added" to tokens: not documented, only "can create tokens with any scope".
- Max number of scopes per token: not documented.
- Propagation time (ten minutes) is documented only for PAT scope updates, not for OAuth secrets (immutable) or modifier changes in general.
- REF link paths differ (`/api/workspace/scopes` vs `/api/workspace/api/scopes`); confirm which is canonical.
- The `knowledge` scope appears twice on REF with different descriptions; confirm manually.
