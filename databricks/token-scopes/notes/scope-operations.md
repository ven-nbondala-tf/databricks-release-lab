# Scope operations, spot-checked against the API scopes reference

Source: https://docs.databricks.com/api/workspace/scopes (checked 2026-11-28). The page shows no HTTP method for any operation and says nothing about modifiers. Items marked (summary) were extracted by the fetch tool's summarizer, not read verbatim, so check them in a browser before quoting.

| Scope | Description on the page | Operations used in the guide |
| --- | --- | --- |
| `sql` | Databricks SQL assets, including warehouses, dashboards, queries and query history, and alerts | Execute Statement (v1, v2), Get Statement Result, Cancel Statement, List/Create/Get Queries, List/Create/Get Alerts, List/Create/Start Warehouses |
| `query-history` (summary) | Query history | List Queries |
| `alerts` | Databricks SQL alerts and alert destinations | List, Create, Update, Get, Trash Alert |
| `dashboards` | AI/BI Dashboards | List, Create, Get, Update, Trash, Publish, Revert Dashboard; schedules and subscriptions |
| `jobs` | Automated jobs and workflows | Create, List, Get, Update Job; Run Now; Submit Run; List/Get Runs; Cancel Run; Repair |
| `pipelines` (summary) | Pipelines, runs and other Delta Live Table resources | List, Create, Get, Edit, Delete, Start, Stop, Events, List Updates |
| `clusters` | Cluster management | Create, List, Get, Edit, Start, Restart, Resize, Delete Cluster |
| `workspace` | Notebooks, Git checkouts and secrets | Import, Export, List, Get Status, Delete, Mkdirs; Repos; Git credentials |
| `files` | Files in a filesystem-like interface | Upload, Download, Create, Put, Read, List, Get Metadata, Delete, Move |
| `unity-catalog` (summary) | Data governance with Unity Catalog | Catalogs, Schemas, Tables, Volumes, Storage Credentials (list, create, get) and more |
| `genie` | Genie conversational analytics spaces and queries | Start Conversation, Create/Get/List Messages, Execute Attachment Query, List Spaces, Create Space |
| `model-serving-inference` (summary) | Query model serving endpoints | Query |
| `vector-search` | Vector Search indexes | Endpoints, Create/Get/List/Query/Sync/Upsert/Scan Index |
| `identity`, `access-management`, `scim`, `settings`, `secrets` | Identity, permissions, security settings, secrets | See the page |
| `authentication` | Authentication settings and configurations | List, Create, Delete Service Principal Secret (Proxy) |
| `billing`, `bundle`, `bundle-deployments` | Not on the page | Listed by the live GET /api/2.0/token-scopes only |
