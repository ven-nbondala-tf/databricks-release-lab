# Fact sheet: metric views

Official Azure Databricks documentation only, fetched November 26, 2026. Part 1 first, then part 2.

## Where the docs differ from the brief

- Query-time joins: the brief says metric views cannot be joined directly at query time. The docs now describe query-time joins (Beta, listed under Databricks Runtime 19); the CTE pattern is still documented for results that are already aggregated. See part 1 rows 47 to 49.
- Release status: the CREATE VIEW page says the metric view feature is in Public Preview; the overview, create, query and manage pages show no status; the November 13, 2026 release note says parameters are generally available. See part 2 rows 38 to 40.
- agg(): needs Databricks Runtime 18.1 and above (query, measure, agg and BI tools pages agree). MEASURE is supported from Runtime 16.4.
- Page names: the pages are under uc-semantics/metric-views/. The old metric-views/ paths redirect or return 404.

## Part 1: how metric views work


Fetched 2026-11-26 with the docfetch helper. Base: https://learn.microsoft.com/en-us/azure/databricks/ . Dates are the "Last updated on" value shown on each page.
Caveat: the helper strips leading whitespace, so YAML/SQL indentation in the code blocks below is re-created from the YAML structure. Keys, values and line order are as printed on the pages.

Page keys used in the URL column (all under https://learn.microsoft.com/en-us/azure/databricks/):
- OVR = uc-semantics/metric-views/  (2026-11-25)
- CRE = uc-semantics/metric-views/create  (2026-10-12)
- QRY = uc-semantics/metric-views/query  (2026-11-25)
- MOD = uc-semantics/metric-views/basic-modeling  (2026-10-29)
- JOI = uc-semantics/metric-views/joins  (2026-11-25)
- ADV = uc-semantics/metric-views/advanced-techniques  (2026-11-25)
- YML = uc-semantics/metric-views/yaml-reference  (2026-11-25)
- FEA = uc-semantics/metric-views/feature-availability  (2026-11-25)
- MAT = uc-semantics/metric-views/materialization  (2026-11-11)
- MAN = uc-semantics/metric-views/manage  (2026-10-29)
- BIT = uc-semantics/metric-views/bi-tools  (2026-11-23)
- AGM = uc-semantics/agent-metadata  (2026-10-09)
- REL = uc-semantics/metric-views/relationships  (2026-11-11)
- PAR = uc-semantics/metric-views/use-parameters  (2026-09-11)
- TUT = uc-semantics/metric-views/tpch-example  (2026-11-18)
- CVW = sql/language-manual/sql-ref-syntax-ddl-create-view  (2026-11-19)
- MSR = sql/language-manual/functions/measure  (2026-11-25)
- AGG = sql/language-manual/functions/agg  (2026-09-11)

## Table

| # | Claim | Status | URL | Date |
|---|---|---|---|---|
| 1 | "Metric views are the core implementation of Unity Catalog semantics in Unity Catalog. They provide a centralized way to define and manage business metrics by separating measure definitions from the fields (also called dimensions) used to group, filter, and aggregate them, so you can define metrics once and query them at runtime." | Confirmed | OVR | 2026-11-25 |
| 2 | "Standard views lock in aggregations and groupings at creation time. With a metric view, you define the metric once ... and users can group by any available field. The query engine generates the correct computation." | Confirmed | OVR | 2026-11-25 |
| 3 | Definition is YAML: top-level fields version (required), comment, source (required), parameters, filter, joins, fields (conditional, "The dimensions keyword is accepted as a synonym"), measures (conditional), materialization | Confirmed | YML | 2026-11-25 |
| 4 | Core components: "sources, joins, filters, fields, and measures" | Confirmed | MOD | 2026-10-29 |
| 5 | Fields: "metric view columns that you can use in SELECT, WHERE, and GROUP BY clauses at query time"; each expression "must return a scalar value"; can reference source columns or earlier fields. "fields and dimensions are equivalent keywords ... fields is the preferred term"; the low-code editor generates `dimensions` in YAML | Confirmed | YML, MOD | 2026-11-25 |
| 6 | Measures: "expressions that produce results without a pre-determined level of aggregation. They must be expressed using aggregate functions. To reference a measure in a query, use the MEASURE function. Measures can reference base columns in the source data, earlier-defined fields, or earlier-defined measures." | Confirmed | YML, MOD | 2026-11-25 |
| 7 | "All measure evaluations in a metric view query must use the MEASURE aggregate function. ... In Databricks Runtime 18.1 and above, you can also use agg." | Confirmed (18.1) | QRY | 2026-11-25 |
| 8 | MEASURE: "Applies to: Databricks SQL, Databricks Runtime 16.4 and above"; "In Databricks Runtime 18.1 and above, agg aggregate function is a synonym for this function." Syntax `measure ( measure_column ) [ FILTER ( WHERE cond ) ]`; "cannot be invoked as a window function using the OVER clause" | Confirmed (18.1) | MSR | 2026-11-25 |
| 9 | agg: "Applies to: Databricks SQL, Databricks Runtime 18.1 and above ... synonym for measure". Syntax `agg ( measure_column ) [ FILTER ( WHERE cond ) ]` | Confirmed (18.1) | AGG | 2026-09-11 |
| 10 | BI tools page writes the alias as "its AGG alias in Databricks Runtime 18.1 and above" | Confirmed (18.1) | BIT | 2026-11-23 |
| 11 | "When you query a metric view, SELECT * isn't supported. ... explicitly list each field and wrap each measure with the MEASURE() aggregate function." | Confirmed | QRY | 2026-11-25 |
| 12 | MEASURE "does not specify the aggregation. It inherits the definition of the aggregation from the metric view definition." | Confirmed | MSR | 2026-11-25 |
| 13 | FILTER on a measure: "the filter condition is applied to every aggregate function in the measure's definition"; if the aggregate already has FILTER, "combined with the existing one using AND"; for window measures "the FILTER clause is applied after the window aggregation, equivalent to placing the same condition in the query's WHERE clause"; "In Databricks Runtime versions below 18.1, a FILTER clause on a measure returns an error." | Confirmed | MSR | 2026-11-25 |
| 14 | Query evaluation, exact docs wording: "Query aggregates such as SUM(field) and COUNT(*) include rows repeated by the join and can double-count. MEASURE() preserves the source metric view's grain, so join repetitions do not inflate measures." (about query-time joins, Beta). "For unmatched outer-join groups, measures defined as COUNT(*) return 0, while measures defined as SUM(...) return NULL." The linked page "How measures are computed across joins" is part of "Join metric views in SQL", which was not reachable (see NOT FOUND) | Confirmed (partial) | MSR | 2026-11-25 |
| 15 | Beyond rows 2 and 14, no page read states an algorithm for how GROUP BY and measures are computed at query time (no "grouping first, then expression" description) | NOT FOUND | QRY, MSR, OVR | - |
| 16 | Star schema: "the source is the fact table and joins with one or more dimension tables using a LEFT OUTER JOIN. Metric views join the fact and dimension tables needed for the specific query, based on the selected fields and measures." (YAML page: "based on the selected columns") | Confirmed | JOI, MOD, YML | 2026-11-25 |
| 17 | Join columns via `on` (Boolean expression) or `using` (shared column names). "The join must follow a many-to-one relationship. In cases of many-to-many, the engine selects the first matching row from the joined dimension table." | Confirmed | JOI | 2026-11-25 |
| 18 | "By default, all joins are many-to-one, so each source row matches at most one row in the joined table." Joins in YAML "run when you query the metric view." | Confirmed | JOI | 2026-11-25 |
| 19 | Snowflake: "extends a star schema by normalizing dimension tables and connecting them to subdimensions. This creates a multi-level join structure." Nested `joins:` inside a join; nested columns referenced like `customer.nation.n_name` | Confirmed (17.3 per FEA) | JOI, YML, FEA | 2026-11-25 |
| 20 | One-to-many: `cardinality: one_to_many`; "require Databricks Runtime 18.1 or above and YAML specification version 1.1." Joined table is "a fact source that the engine aggregates independently at the source grain." Cardinality table: many_to_one allowed in fields Yes, measures Yes; one_to_many fields No, measures Yes | Confirmed (18.1) | JOI, YML, FEA | 2026-11-25 |
| 21 | One-to-many restrictions: fields can't reference a one-to-many join; "A single aggregation can't span sources"; "A join subtree can't mix cardinalities" (only top-level siblings can mix); a metric view with one-to-many YAML joins "cannot be an input to a query-time join" | Confirmed | JOI | 2026-11-25 |
| 22 | Sibling one-to-many joins: "The engine aggregates sibling joins separately and then blends them, so their rows never cross-multiply." Nested one-to-many: use `count(distinct orders.o_orderkey)` for the parent count | Confirmed | JOI | 2026-11-25 |
| 23 | Which joined tables a query reads: the only statements are (a) "Metric views join the fact and dimension tables needed for the specific query, based on the selected fields and measures" and (b) rely.at_most_one_match "allows the engine to skip unnecessary joins and reduce data scanned, especially for queries that filter on fields from the joined table." No page states more than that | Confirmed (limited) | JOI | 2026-11-25 |
| 24 | rely: `rely.at_most_one_match: true`. Many-to-one: each source row matches at most one joined row. One-to-many: each joined row matches at most one source row. "Databricks recommends setting rely on both cardinalities when the constraint holds." "This property is not validated at runtime. If the asserted side produces a fan-out, measures return incorrect results." Requires DBR 18.1 per FEA ("Join optimization with rely.at_most_one_match") | Confirmed (18.1) | JOI, YML, FEA | 2026-11-25 |
| 25 | A metric view with a one_to_many join: "its materializations qualify for exact match only. Rollup match is not available." | Confirmed | YML, MAT | 2026-11-25 |
| 26 | Joined tables can't include ARRAY or MAP columns (MOD, JOI); YML says only "MAP type columns" | DIFFERS (minor) | MOD, JOI, YML | 2026-10-29 / 2026-11-25 |
| 27 | YAML-level filter: "A filter in the YAML definition applies to all queries that reference the metric view. Write filters as SQL boolean expressions." Optional top-level `filter` | Confirmed | YML, MOD | 2026-11-25 |
| 28 | Filtered measures: `SUM(o_totalprice) FILTER (WHERE o_orderpriority = '1-URGENT')` listed as "Filtered measure with WHERE condition" | Confirmed | MOD | 2026-10-29 |
| 29 | Window measures: required fields `order` and `range` (current, cumulative, trailing, leading, all); optional `semiadditive` (first, last; default last) and `offset` | Confirmed | ADV | 2026-11-25 |
| 30 | Window `offset` modifier and `inclusive`/`exclusive` modifiers: DBR 18.1, YAML 1.1. Unitless numeric offset/range on a consecutive integer index: DBR 19 and YAML 1.1. `exclusive` is the default | Confirmed | ADV, FEA | 2026-11-25 |
| 31 | Window measure example: "trailing 7 day ... defines the window as the 7 days before each date, excluding the date itself." Default `semiadditive: last` "returns the last value in the 7-day window when date is not a grouping column." | Confirmed | ADV | 2026-11-25 |
| 32 | Window measures can't be rolled up in materialization: "The measure can't be a window measure" (for rollup match eligibility) | Confirmed | MAT | 2026-11-11 |
| 33 | Composability: "You can build new fields and measures that reference existing ones." Works "within a single metric view, and across metric views when one metric view is used as the source for another." Composed measure: `MEASURE(total_revenue) / MEASURE(order_count)` | Confirmed | ADV | 2026-11-25 |
| 34 | A metric view can be a source: "Supported sources include tables, views, metric views, and SQL queries." Inherit with `source.*` wildcard (DBR 18.2, YAML 1.1); "Azure Databricks expands wildcards when you create the metric view. To pick up fields or measures added to the parent metric view later, recreate the metric view with CREATE OR REPLACE or ALTER." | Confirmed (18.2) | YML | 2026-11-25 |
| 35 | Feature availability intro: "Metric views were introduced in Databricks Runtime 16.4." YAML spec "is versioned independently of Databricks Runtime." | Confirmed | FEA | 2026-11-25 |
| 36 | YAML versions: 1.1 adds agent metadata and `comment` on view, fields, measures; with DBR 18.1+: `cardinality` (one_to_many), `offset`, `inclusive`/`exclusive`; DBR 19+: unitless numeric offset/range. 0.1 = "Initial release". Wildcards, materialization refresh policy are also tagged YAML 1.1 in the table | Confirmed | FEA | 2026-11-25 |
| 37 | Agent metadata (also "semantic metadata"): display names (max 255 chars), format specifications, synonyms (up to 10 per field/measure, each max 255 chars), comment. "Requires Databricks Runtime 17.3 and YAML version 1.1." | Confirmed (17.3) | AGM, YML | 2026-10-09 |
| 38 | Who uses it: "visualization tools, such as AI/BI dashboards, and natural language tools, such as Genie Agents"; "Synonyms help LLM tools, such as Genie, discover fields ... and measures." | Confirmed | AGM | 2026-10-09 |
| 39 | Saving a 1.1 definition removes YAML comments: "any single-line comments (denoted with #) in the YAML definition are removed when the definition is saved." | Confirmed | AGM | 2026-10-09 |
| 40 | Materialization: "Lakeflow pipelines orchestrate user-defined materialized views for a given metric view. At query time, the query optimizer routes queries to the best materialized view using automatic aggregate-aware query matching (query rewriting)." Fast path reads materialized views; fallback path reads source. Status label (Beta/GA) is not printed on the page | Confirmed; status NOT FOUND | MAT | 2026-11-11 |
| 41 | Materialization requirements: "Your workspace must have serverless compute enabled to run Lakeflow pipelines." "A SQL warehouse or compute resource running Databricks Runtime 17.3 or above." | Confirmed | MAT | 2026-11-11 |
| 42 | Materialization blocked when the view or any source table uses RLS, column masks or ABAC; also invoker-dependent expressions (`current_user()`, `is_member()`); error condition METRIC_VIEW_MATERIALIZATION_WITH_INVOKER_DEPENDENT_EXPRESSIONS_NOT_SUPPORTED (SQLSTATE 42K0E) | Confirmed | MAT | 2026-11-11 |
| 43 | Where configured: top-level `materialization` field in the YAML: `schedule`, `mode: relaxed` ("always relaxed"), `materialized_views` (each `aggregated` or `unaggregated`); `refresh_policy` (DBR 18 LTS) | Confirmed | MAT, FEA | 2026-11-11 |
| 44 | How a query uses it: order is exact match, then rollup match, then unaggregated match, then source. Exact: GROUP BY "must exactly match the materialization dimensions" and measures a subset. Rollup: coarser grain, all measures additive, deterministic filters. Relaxed mode skips freshness, SQL settings and determinism checks, so "Queries that match a materialization use the last refresh. Queries that don't match fall back to source and return live data." | Confirmed | MAT | 2026-11-11 |
| 45 | "Query-time joins (Beta) bypass materializations and read live source data. These queries receive no materialization acceleration." | Confirmed | MAT | 2026-11-11 |
| 46 | Materialization limits: can't materialize a metric view that defines parameters; owner can't change after a materialization exists; "Databricks doesn't support group ownership of materialized metric views"; schedule doesn't support TRIGGER ON UPDATE; manual refresh via `REFRESH MATERIALIZED VIEW` (DBR 18.0) | Confirmed | MAT, MAN, FEA | 2026-11-11 |
| 47 | Metric views cannot be joined directly at query time, with CTE workaround: NOT what the docs now say. Docs say "Query-time joins (Beta) let you join a metric view directly with another metric view, table, or view ... Join on fields and wrap each measure in MEASURE()". Beta, DBR 19 per FEA. See verbatim blocks | DIFFERS from premise | QRY, FEA, MSR | 2026-11-25 |
| 48 | CTE pattern (still documented, for already aggregated results): "To join results that you have already aggregated, wrap the metric view query in a common table expression (CTE). The aggregated values become regular columns:" | Confirmed | QRY | 2026-11-25 |
| 49 | Query-time joins: Beta, listed under DBR 19 ("Query-time joins (Beta). See the requirements and limitations"). The "Join metric views in SQL" page with requirements, join types and restrictions was not reachable | Confirmed (Beta); details NOT FOUND | FEA, QRY | 2026-11-25 |
| 50 | Governance, create: SELECT on source; CREATE TABLE and USE SCHEMA on the schema; USE CATALOG on the catalog; CAN USE on a SQL warehouse or compute running DBR 17.3 or above (for that page's example). "Creating a metric view is supported on Databricks Runtime 16.4 and above." CREATE VIEW page: metastore admin, or USE CATALOG and USE SCHEMA plus CREATE TABLE in the target schema | Confirmed | CRE, CVW | 2026-10-12 / 2026-11-19 |
| 51 | Governance, query: "Any user with at least SELECT privileges can query the metric view." Same hierarchical permission model as other UC securables; `GRANT SELECT ON orders_metric_view to \`data-consumers\`;` | Confirmed | MAN | 2026-10-29 |
| 52 | Edit/ownership: "You must be the owner of a metric view to edit its definition." Collaborative editing by transferring ownership to a group (not for materialized metric views). Sharing metric views via OpenSharing: "This feature is in Beta." | Confirmed | MAN | 2026-10-29 |
| 53 | Lineage: "Use the Lineage tab in Catalog Explorer to identify dependencies" before dropping a metric view. No dedicated lineage section found | Confirmed (limited) | MAN | 2026-10-29 |
| 54 | Consumers table (Query page): AI/BI dashboards ("The MEASURE() function is applied automatically, and agent metadata ... is surfaced in the UI"), Genie Agents, Alerts, Query analysis, JDBC and ODBC, External BI tools, Excel Add-in, Google Sheets | Confirmed | QRY | 2026-11-25 |
| 55 | External BI patterns: custom SQL with MEASURE(), Tableau pass-through (RAWSQLAGG), wrapper view, BI compatibility mode, built-in partner integration, import with Genie Code `/importBI`. Power BI: publish as semantic model "(Private Preview)" or Native query with MEASURE() | Confirmed | BIT | 2026-11-23 |
| 56 | BI compatibility mode (what it is): for tools that "can't pass custom SQL queries to Azure Databricks and instead generate standard aggregations (SUM, COUNT) against measure columns. Azure Databricks rewrites the generated queries to apply the correct measure logic." Needs "A session configuration in Initial SQL for each connection." Requires DBR 18.0 per FEA | Confirmed (18.0) | BIT, FEA | 2026-11-23 |
| 57 | BI compatibility mode limits (from comparison table): "Measure columns must use SUM. AVG, Count (Distinct), Median, and other aggregations return incorrect results or errors." Data preview and extracts: "Measure columns show as null." The dedicated page "Use BI compatibility mode to query metric views" was not reachable | Confirmed (partial) | BIT | 2026-11-23 |
| 58 | Runtime/warehouse: "You can query metric views like standard views from any SQL editor attached to a SQL warehouse or compute resource running a supported runtime." "A SQL warehouse is automatically updated with the latest Databricks SQL compute version." Introduced DBR 16.4; TEMPORARY metric views 17.2; JDBC/ODBC via Thrift server 17.3; Snowflake schema 17.3; Parameters 18.2 | Confirmed | QRY, FEA | 2026-11-25 |
| 59 | Region or workspace requirements for metric views in general (other than serverless for materialization) | NOT FOUND | - | - |
| 60 | Release status of metric views as a whole: no page read says "generally available". CREATE VIEW METRICS clause carries "Important: This feature is in Public Preview." Overview, create, query, manage pages show no status label | DIFFERS / NOT FOUND (GA) | CVW, OVR | 2026-11-19 |
| 61 | Limitations (explicit lists): manage page "Metric views don't support data profiling."; parameters page lists (no materialization, default restrictions); CREATE VIEW: metric views do not support DEFAULT COLLATION and schema_binding clauses; no page titled "Limitations" for metric views as a whole | Confirmed (scattered) | MAN, PAR, CVW | various |
| 62 | String-like metric view fields are always STRING: "even when the source column is CHAR or VARCHAR. Because CHAR(n) space-padding is lost, comparisons can return different results." | Confirmed | MOD, YML | 2026-10-29 |
| 63 | Relationships between metric views: "This feature is in Beta." Metadata only ("don't affect materialization"), so AI assistants and BI tools choose the join path. Not a join | Confirmed (Beta) | REL | 2026-11-11 |
| 64 | Parameters: DBR 18.2; `parameters` block with name, data_type, default; query as table-valued function with named arguments. CREATE VIEW page: "Parameters require Databricks Runtime 18.2 and above" | Confirmed | PAR, CVW, YML | 2026-09-11 |
| 65 | Feature availability table (see full reproduction below) | Confirmed | FEA | 2026-11-25 |
| 66 | Metric view feature on describe: `DESCRIBE TABLE EXTENDED AS JSON` returns the full YAML definition in View Text; "Each column contains a metadata field that holds agent metadata." | Confirmed | QRY | 2026-11-25 |

## Feature availability table (reproduced fully from FEA)

Intro: "Metric views were introduced in Databricks Runtime 16.4. The following table lists minimum Databricks Runtime version requirements for specific features added in later versions."
Note: "You can also work with metric views on a SQL warehouse. A SQL warehouse is automatically updated with the latest Databricks SQL compute version, so you don't manage runtime versions the way you do for a cluster. See Channels."

| Databricks Runtime version | Features |
|---|---|
| 19 | Relationships between metric views (Beta) |
| 19 | Query-time joins (Beta). See the requirements and limitations. |
| 19 | Numeric offset and range on a consecutive integer index column (YAML specification 1.1) |
| 19 | Derived column names |
| 18 LTS | Materialization refresh policy (YAML specification 1.1) |
| 18.2 | Parameters |
| 18.2 | Wildcard expressions for fields and measures (YAML specification 1.1) |
| 18.1 | One-to-many joins (YAML specification 1.1) |
| 18.1 | Window measure offset modifier (YAML specification 1.1) |
| 18.1 | inclusive and exclusive modifiers on trailing and leading window ranges (YAML specification 1.1) |
| 18.1 | Join optimization with rely.at_most_one_match |
| 18.0 | BI compatibility mode |
| 18.0 | REFRESH MATERIALIZED VIEW |
| 17.3 | Snowflake schema |
| 17.3 | Agent metadata: comments, synonyms, formatting, display names (YAML specification 1.1) |
| 17.3 | Materialization |
| 17.3 | JDBC/ODBC support through Thrift server |
| 17.2 | TEMPORARY metric views |

Note: "Databricks Runtime 18 is newer than Databricks Runtime 18.0, 18.1, and 18.2. Features that would previously have shipped as a later numbered version now ship as dated updates to Databricks Runtime 18 instead. For details, see About unified release notes."

YAML specification versions: Version 1.1 "Adds support for agent metadata (display names, formatting, synonyms) and the optional comment field for metric views, fields (also called dimensions), and measures." Also adds (require DBR 18.1 or above): the cardinality field on joins including one_to_many; the offset field on window specifications; the inclusive and exclusive modifiers on trailing and leading range values; "Unitless numeric offset and range on a consecutive integer index column (requires Databricks Runtime 19 or above)." Version 0.1: "Initial release of the metric view YAML specification."

Note on row 22 of the table vs sections: the feature table lists "Snowflake schema" at 17.3 while the page text for CRE/MOD does not repeat it.

## Verbatim code blocks

### A. Smallest complete YAML example (ADV, composability, AOV; version, source, measures only)

```yaml
version: 1.1
source: samples.tpch.orders
measures:
  # Total Revenue
  - name: total_revenue
    expr: SUM(o_totalprice)
  # Order Count
  - name: order_count
    expr: COUNT(1)
  # Composed Measure: Average Order Value (AOV)
  - name: avg_order_value
    # Defines AOV as Total Revenue divided by Order Count
    expr: MEASURE(total_revenue) / MEASURE(order_count)
```

Even smaller, from AGM (display names): version 1.1, source samples.tpch.orders, one field and one measure:

```yaml
version: 1.1
source: samples.tpch.orders
fields:
  - name: order_date
    expr: o_orderdate
    display_name: 'Order Date'
measures:
  - name: total_revenue
    expr: SUM(o_totalprice)
    display_name: 'Total Revenue'
```

### B. Complete CREATE VIEW syntax (CVW)

```sql
-- Query-backed or metric view
CREATE [ OR REPLACE ] [ [ GLOBAL ] TEMPORARY ] VIEW [ IF NOT EXISTS ] view_name
    [ column_list ]
    [ with_clause |
      COMMENT view_comment |
      DEFAULT COLLATION collation_name |
      TBLPROPERTIES clause |
      { COPY | NOCOPY } * |
      LANGUAGE YAML ] [...]
    AS { query | $$ yaml_string $$ }

-- Temporary view backed by a data source
CREATE [ OR REPLACE ] [ GLOBAL ] TEMPORARY VIEW [ IF NOT EXISTS ] view_name
    [ column_list ]
    USING data_source [ OPTIONS ( option_key [ = ] option_value [, ...] ) ]

with_clause
    WITH { { schema_binding | METRICS } |
           ( { schema_binding | METRICS } [, ...] } )

schema_binding
    WITH SCHEMA { BINDING | COMPENSATION | [ TYPE ] EVOLUTION }

column_list
    ( { column_alias [ COMMENT column_comment ] } [, ...] )
```

METRICS parameter text: "Applies to: Databricks SQL, Databricks Runtime 16.4 and above, Unity Catalog only. Identifies the view as a metric view. The view must be defined with LANGUAGE YAML and the body of the view must be a valid yaml specification. Prior to Databricks Runtime 17.2, this clause is not supported for temporary views. A metric view does not support the DEFAULT COLLATION and schema_binding clauses. ... Important: This feature is in Public Preview."

### C. Full CREATE VIEW example (CVW, as printed; note the page's column list says `order_priority` while the YAML field is spelled `prder_priority`, a typo on the page)

```sql
-- Creates a Metric View as specified in the YAML definition, with three dimensions and four measures representing the count of orders.
> CREATE OR REPLACE VIEW region_sales_metrics
    (month COMMENT 'Month order was made',
     status,
     order_priority,
     count_orders COMMENT 'Count of orders',
     total_Revenue,
     total_revenue_per_customer,
     total_revenue_for_open_orders)
  WITH METRICS
  LANGUAGE YAML
  COMMENT 'A Metric View for regional sales metrics.'
  AS $$
    version: 0.1
    source: samples.tpch.orders
    filter: o_orderdate > '1990-01-01'
    dimensions:
      - name: month
        expr: date_trunc('MONTH', o_orderdate)
      - name: status
        expr: case
                when o_orderstatus = 'O' then 'Open'
                when o_orderstatus = 'P' then 'Processing'
                when o_orderstatus = 'F' then 'Fulfilled'
              end
      - name: prder_priority
        expr: split(o_orderpriority, '-')[1]
    measures:
      - name: count_orders
        expr: count(1)
      - name: total_revenue
        expr: SUM(o_totalprice)
      - name: total_revenue_per_customer
        expr: SUM(o_totalprice) / count(distinct o_custkey)
      - name: total_revenue_for_open_orders
        expr: SUM(o_totalprice) filter (where o_orderstatus='O')
  $$;
```

Full SQL example with joins from CRE (version 1.1, fields keyword):

```sql
CREATE OR REPLACE VIEW orders_metric_view WITH METRICS LANGUAGE YAML AS
$$
  version: 1.1
  comment: "Orders KPIs for sales analysis"
  source: samples.tpch.orders
  joins:
    - name: customer
      source: samples.tpch.customer
      'on': source.o_custkey = customer.c_custkey
      rely:
        at_most_one_match: true
  filter: source.o_orderdate > '1990-01-01'
  fields:
    - name: Order Month
      expr: DATE_TRUNC('MONTH', source.o_orderdate)
      comment: "Month of order"
    - name: Order Status
      expr: |-
        CASE
          WHEN source.o_orderstatus = 'O' THEN 'Open'
          WHEN source.o_orderstatus = 'P' THEN 'Processing'
          WHEN source.o_orderstatus = 'F' THEN 'Fulfilled'
        END
      comment: "Status of order"
    - name: Market Segment
      expr: customer.c_mktsegment
      comment: "Customer market segment"
  measures:
    - name: Order Count
      expr: COUNT(1)
      comment: "Total number of orders"
    - name: Total Revenue
      expr: SUM(source.o_totalprice)
      comment: "Sum of all order prices"
    - name: Total Revenue per Customer
      expr: SUM(source.o_totalprice) / COUNT(DISTINCT source.o_custkey)
      comment: "Average revenue per unique customer"
$$
```

### D. Query patterns (QRY)

```sql
SELECT
  `Order Month`,
  `Order Status`,
  MEASURE(`Order Count`),
  MEASURE(`Total Revenue`)
FROM orders_metric_view
GROUP BY ALL
ORDER BY `Order Month`;
```

Query-time join (Beta), verbatim text: "Query-time joins (Beta) let you join a metric view directly with another metric view, table, or view. For compute requirements, see Requirements. Join on fields and wrap each measure in MEASURE(). The following query groups order measures by a customer attribute from the joined table. The metric view must expose o_custkey as a field:"

```sql
SELECT
  c.c_mktsegment,
  MEASURE(o.`Order Count`) AS order_count,
  MEASURE(o.`Total Revenue`) AS total_revenue
FROM orders_metric_view o
JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
GROUP BY c.c_mktsegment
ORDER BY c.c_mktsegment;
```

CTE pattern, verbatim text: "To join results that you have already aggregated, wrap the metric view query in a common table expression (CTE). The aggregated values become regular columns:"

```sql
WITH orders AS (
  SELECT
    o_custkey,
    MEASURE(`Order Count`) AS order_count,
    MEASURE(`Total Revenue`) AS total_revenue
  FROM orders_metric_view
  GROUP BY o_custkey
)
SELECT
  c.c_mktsegment,
  orders.order_count,
  orders.total_revenue
FROM orders
JOIN samples.tpch.customer c ON orders.o_custkey = c.c_custkey
ORDER BY c.c_mktsegment;
```

### E. Joins + filter + filtered measure + window measure in one definition (TUT, "complete YAML definition"; also uses parameters, which is why discounted_revenue exists)

Page note in TUT: its path under the old name metric-views/create redirected here; the tutorial page is titled "Tutorial: build a metric view with joins and data modeling" (title read from the other pages' links; the fetched page body is this definition).

```yaml
version: 1.1
parameters:
  - name: discount
    data_type: double
    default: 0
source: SELECT * FROM samples.tpch.orders
joins:
  - name: customer
    source: samples.tpch.customer
    'on': o_custkey = c_custkey
    joins:
      - name: nation
        source: samples.tpch.nation
        'on': c_nationkey = n_nationkey
filter: o_orderdate >= '1995-01-01'
comment: |-
  Sales analytics metric view for order performance analysis.
  Joins orders with customers and geography.
  Owner: Analytics Team
  Last updated: 2025-01-15
fields:
  - name: order_date
    expr: o_orderdate
    display_name: Order Date
  - name: order_month
    expr: "DATE_TRUNC('MONTH', order_date)"
    display_name: Order Month
  - name: order_year
    expr: YEAR(order_date)
    display_name: Order Year
  - name: order_status
    expr: |-
      CASE o_orderstatus
        WHEN 'O' THEN 'Open'
        WHEN 'P' THEN 'Processing'
        WHEN 'F' THEN 'Fulfilled'
      END
    display_name: Order Status
    synonyms:
      - status
      - fulfillment status
  - name: order_priority
    expr: "SPLIT(o_orderpriority, '-')[0]"
    display_name: Priority
  - name: customer_name
    expr: customer.c_name
    display_name: Customer Name
  - name: market_segment
    expr: customer.c_mktsegment
    display_name: Market Segment
    synonyms:
      - segment
      - industry
  - name: customer_nation
    expr: customer.nation.n_name
    display_name: Country
    synonyms:
      - nation
      - country
measures:
  - name: order_count
    expr: COUNT(DISTINCT o_orderkey)
    display_name: Order Count
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: total_revenue
    expr: SUM(o_totalprice)
    display_name: Total Revenue
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
    synonyms:
      - revenue
      - sales
  - name: discounted_revenue
    expr: SUM(o_totalprice * (1 - discount))
    display_name: Discounted Revenue
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
  - name: unique_customers
    expr: COUNT(DISTINCT o_custkey)
    display_name: Unique Customers
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
  - name: avg_order_value
    expr: MEASURE(total_revenue) / MEASURE(order_count)
    display_name: Avg Order Value
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
    synonyms:
      - AOV
  - name: revenue_per_customer
    expr: MEASURE(total_revenue) / MEASURE(unique_customers)
    display_name: Revenue per Customer
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
  - name: open_order_revenue
    expr: SUM(o_totalprice) FILTER (WHERE o_orderstatus = 'O')
    display_name: Open Order Revenue
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
    synonyms:
      - backlog
  - name: fulfilled_order_revenue
    expr: SUM(o_totalprice) FILTER (WHERE o_orderstatus = 'F')
    display_name: Fulfilled Revenue
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
  - name: t7d_customers
    expr: COUNT(DISTINCT o_custkey)
    window:
      - order: order_date
        range: trailing 7 day
    display_name: 7-Day Rolling Customers
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
```

### F. Window measure examples (ADV)

Trailing 7 day (with filter):

```yaml
version: 1.1
source: samples.tpch.orders
filter: o_orderdate > DATE'1998-01-01'
fields:
  - name: date
    expr: o_orderdate
measures:
  - name: t7d_customers
    expr: COUNT(DISTINCT o_custkey)
    window:
      - order: date
        range: trailing 7 day
```

Year-over-year with offset:

```yaml
version: 1.1
source: main.default.monthly_sales
fields:
  - name: month
    expr: month
  - name: category
    expr: category
measures:
  - name: monthly_sales
    expr: SUM(sales)
    window:
      - order: month
        range: current
  - name: monthly_sales_py
    expr: SUM(sales)
    window:
      - order: month
        range: current
        offset: -12 month
  - name: yoy_growth
    expr: MEASURE(monthly_sales) - MEASURE(monthly_sales_py)
  - name: yoy_growth_pct
    expr: (MEASURE(monthly_sales) - MEASURE(monthly_sales_py))
          / NULLIF(MEASURE(monthly_sales_py), 0)
```

Cumulative and year-to-date:

```yaml
version: 1.1
source: samples.tpch.orders
filter: o_orderdate > DATE'1997-01-01'
fields:
  - name: date
    expr: o_orderdate
  - name: month
    expr: DATE_TRUNC('MONTH', date)
  - name: year
    expr: DATE_TRUNC('year', date)
measures:
  - name: ytd_sales
    expr: SUM(o_totalprice)
    window:
      - order: date
        range: cumulative
      - order: year
        range: current
```

### G. Joins examples (JOI)

Star (on clause):

```yaml
version: 1.1
source: samples.tpch.orders
joins:
  # The on clause supports a Boolean expression
  - name: customer
    source: samples.tpch.customer
    on: source.o_custkey = customer.c_custkey
fields:
  # Field referencing a join column using dot notation
  - name: Customer name
    expr: customer.c_name
  - name: Customer market segment
    expr: customer.c_mktsegment
measures:
  # Measure referencing a join column
  - name: Total revenue
    expr: SUM(o_totalprice)
  - name: Order count
    expr: COUNT(1)
```

Snowflake:

```yaml
source: samples.tpch.orders
joins:
  - name: customer
    source: samples.tpch.customer
    on: source.o_custkey = customer.c_custkey
    joins:
      - name: nation
        source: samples.tpch.nation
        on: customer.c_nationkey = nation.n_nationkey
        joins:
          - name: region
            source: samples.tpch.region
            on: nation.n_regionkey = region.r_regionkey
fields:
  - name: clerk
    expr: o_clerk
  - name: customer
    expr: customer
    comment: returns the full customer row as a struct
  - name: customer_name
    expr: customer.c_name
  - name: nation
    expr: customer.nation
  - name: nation_name
    expr: customer.nation.n_name
```

One-to-many:

```yaml
version: 1.1
source: samples.tpch.customer
joins:
  - name: nation
    source: samples.tpch.nation
    on: nation.n_nationkey = source.c_nationkey
    rely:
      at_most_one_match: true
  - name: orders
    source: samples.tpch.orders
    on: orders.o_custkey = source.c_custkey
    cardinality: one_to_many
    rely:
      at_most_one_match: true
fields:
  - name: customer_name
    expr: c_name
  - name: nation_name
    expr: nation.n_name
measures:
  - name: customer_count
    expr: count(*)
  - name: order_count
    expr: count(orders.o_orderkey)
  - name: total_order_revenue
    expr: sum(orders.o_totalprice)
```

### H. Materialization example (MAT)

```yaml
version: 1.1
source: prod.operations.orders_enriched_view
filter: revenue > 0
fields:
  - name: category
    expr: substring(category, 5)
  - name: color
    expr: color
measures:
  - name: total_revenue
    expr: SUM(revenue)
  - name: number_of_suppliers
    expr: COUNT(DISTINCT supplier_id)
materialization:
  schedule: every 6 hours
  mode: relaxed
  materialized_views:
    - name: baseline
      type: unaggregated
    - name: revenue_breakdown
      type: aggregated
      dimensions:
        - category
        - color
      measures:
        - total_revenue
      cluster_by:
        cols:
          - category
          - color
    - name: suppliers_by_category
      type: aggregated
      dimensions:
        - category
      measures:
        - number_of_suppliers
```

### I. BI wrapper view and Tableau pass-through (BIT)

```sql
CREATE VIEW main.sales.orders_report AS
SELECT
  `Order Month`,
  MEASURE(`Total Revenue`) AS `Total Revenue`,
  MEASURE(`Order Count`) AS `Order Count`
FROM main.sales.orders_metric_view
GROUP BY ALL;
```

```
RAWSQLAGG_REAL("MEASURE(%1)", [Total Revenue])
```

## NOT FOUND

- Query evaluation algorithm (how grouping and measures are computed at query time): only the sentences in rows 2, 12 and 14. Page "How measures are computed across joins" (inside "Join metric views in SQL") not reachable.
- Page "Join metric views in SQL" (query-time joins: requirements, supported join types, restrictions, one-to-many input restriction): path not found. Tried uc-semantics/metric-views/{join, joins-in-sql, join-in-sql, query-time-joins, sql-joins, join-metric-views(-in-sql)} (404, or `joins` which is the YAML joins page). Only referenced from other pages.
- Page "Use BI compatibility mode to query metric views" (supported scenarios, best practices, limitations): path not found (tried bi-compatibility, bi-compatibility-mode, bi-compat). Limits taken only from the BIT comparison table.
- Release status "generally available" for metric views as a whole, and for materialization (no status label printed).
- Region or workspace availability requirements for metric views.
- A single "Limitations" page for metric views.
- Dedicated lineage documentation for metric views (only the Lineage tab mention in MAN).
- "Tutorial: build a metric view with joins and data modeling" at its own path (guessed tutorial, tpch-tutorial; the helper's old path metric-views/create redirected to uc-semantics/metric-views/tpch-example, which holds the tutorial definition).
- Old paths from the task list: metric-views/ (redirected to uc-semantics/metric-views/), metric-views/create (redirected to tpch-example), metric-views/joins (redirected to basic-modeling#joins), metric-views/data-modeling (redirected to basic-modeling); metric-views/query, metric-views/yaml-reference, metric-views/feature-availability 404 at that path but exist under uc-semantics/metric-views/.

## DIFFERS

1. Premise vs docs: the brief says metric views cannot be joined at query time, with a CTE workaround. The docs now describe Beta query-time joins (QRY, MSR, FEA, MAT). The CTE pattern is documented only for already aggregated results.
2. Release status: CVW says the metric view feature "is in Public Preview"; OVR, CRE, QRY, MAN carry no status label; FEA lists Beta only for relationships and query-time joins; MAN says sharing is Beta; BIT says Power BI semantic model is Private Preview.
3. ARRAY/MAP in joined tables: MOD and JOI say ARRAY or MAP; YML says only MAP.
4. Create prerequisite runtime: CRE says creation "is supported on Databricks Runtime 16.4 and above" but its example needs 17.3; FEA says introduced 16.4; MAT says 17.3 for materialization. Consistent but easy to misquote.
5. Query-time joins runtime: FEA lists them under Databricks Runtime 19; no other page repeats a version for them.
6. CVW example has a typo (column list `order_priority`, YAML field `prder_priority`) and uses `version: 0.1` with `dimensions`; other pages use `version: 1.1` with `fields`.
7. YAML version for agent metadata: FEA/AGM say 1.1 required for display_name, format, synonyms; the CVW 0.1 examples have none of them (consistent, not a conflict).

## Page status and dates

Pages read (status label on page / Last updated):
- OVR: no status label / 2026-11-25
- CRE: none / 2026-10-12
- QRY: none; mentions "Query-time joins (Beta)" / 2026-11-25
- MOD: none / 2026-10-29
- JOI: none; mentions Beta for query-time joins and relationships / 2026-11-25
- ADV: none / 2026-11-25
- YML: none / 2026-11-25
- FEA: Beta for relationships and query-time joins / 2026-11-25
- MAT: no label; "Query-time joins (Beta)", "Jobs & Pipelines list (Beta)" / 2026-11-11
- MAN: sharing "This feature is in Beta" / 2026-10-29
- BIT: Power BI semantic model "(Private Preview)" / 2026-11-23
- AGM: none / 2026-10-09
- REL: "This feature is in Beta" / 2026-11-11
- PAR: none / 2026-09-11
- TUT: none / 2026-11-18
- CVW: METRICS clause "Public Preview" / 2026-11-19
- MSR: "Query-time joins are in Beta" / 2026-11-25
- AGG: none / 2026-09-11

## Part 2: parameters and dashboard value lists


Source: official Azure Databricks docs on learn.microsoft.com, fetched 2026-11-26. Base: https://learn.microsoft.com/en-us/azure/databricks/

Page keys:
- UP = uc-semantics/metric-views/use-parameters (last updated 2026-09-11)
- YR = uc-semantics/metric-views/yaml-reference (2026-11-25)
- Q = uc-semantics/metric-views/query (2026-11-25)
- MAT = uc-semantics/metric-views/materialization (2026-11-11)
- FA = uc-semantics/metric-views/feature-availability (2026-11-25)
- OV = uc-semantics/metric-views/ (2026-11-25)
- CV = sql/language-manual/sql-ref-syntax-ddl-create-view (2026-11-19)
- DS = dashboards/manage/data-modeling/datasets (2026-10-09)
- DP = dashboards/manage/filters/parameters (2026-11-19)
- LMV = dashboards/manage/data-modeling/local-metric-views (2026-11-19)
- RN = release-notes/product/2026/november (2026-11-25)

| # | Claim | Status | URL | Page date |
|---|---|---|---|---|
| 1 | YAML has a top-level `parameters` block: "named values that callers pass when they query the metric view as a table-valued function" | Confirmed | YR#parameters | 2026-11-25 |
| 2 | Field `name` (String): "Required. The parameter name. Reference the parameter by this name in field and measure expressions, and pass it as a named argument" | Confirmed | YR | 2026-11-25 |
| 3 | Field `data_type` (String): "Required. The SQL data type of the parameter, such as double, int, string, or date." | Confirmed | YR | 2026-11-25 |
| 4 | Field `default` (Varies): "Optional. The value used when a caller does not pass the parameter." | Confirmed | YR | 2026-11-25 |
| 5 | Only three fields documented: name, data_type, default ("Each parameter definition includes the following fields") | Confirmed | YR | 2026-11-25 |
| 6 | Supported data types: only "such as double, int, string, or date" listed; no complete list. Catalog Explorer editor offers Numeric (with Double) type | Confirmed (partial list) | YR, UP | 2026-11-25 |
| 7 | Default rule: "must be castable to data_type, and it can't reference another parameter or contain a subquery" | Confirmed | YR; UP#limitations | 2026-11-25 |
| 8 | Ordering rule: "If you set a default for one parameter, every parameter that follows it must also have a default." So a parameter with a default cannot be followed by one without. No error message text documented | Confirmed (error text NOT FOUND) | YR; UP#limitations | 2026-11-25 |
| 9 | Where to reference: "anywhere a constant SQL expression is valid, such as in filters, field and measure expressions, the source, and joins" | Confirmed | UP | 2026-09-11 |
| 10 | Also: "reference an integer parameter as the value of a window measure's range or offset" | Confirmed | UP; YR#pass-a-window-size-as-a-parameter | 2026-11-25 |
| 11 | Window size parameter rules: data_type integral (int, smallint, bigint); bare parameter name only (`trailing window_size day`, not `trailing window_size + 1 day`); no sign before name (put sign in the value); cannot be named after a window keyword (trailing, leading, day, month, year, inclusive, exclusive, offset); "The unit stays literal." Needs DBR 18.2+ | Confirmed | YR | 2026-11-25 |
| 12 | Where parameters cannot be referenced: no explicit "not allowed" list documented beyond the window and default rules | NOT FOUND | UP, YR | n/a |
| 13 | Call as table-valued function: "call the metric view as a table-valued function and pass parameters as arguments. You can pass arguments by name or by position, or omit them to use the default values." | Confirmed | UP#query-a-metric-view-with-parameters | 2026-09-11 |
| 14 | By name uses `=>`: `FROM catalog.schema.metric_view(discount => 0.15)` | Confirmed | UP | 2026-09-11 |
| 15 | By position: "list the values in the order the parameters are defined": `FROM catalog.schema.metric_view(0.15)` | Confirmed | UP | 2026-09-11 |
| 16 | Defaults: "The following queries are equivalent and use all default values": `metric_view()` and bare `metric_view` | Confirmed | UP | 2026-09-11 |
| 17 | Measures are still read with `MEASURE(...)` and `GROUP BY` in parameterized calls | Confirmed | UP, CV | 2026-09-11 |
| 18 | Query page mentions named arguments only: "pass each parameter as a named argument" (UP also allows position) | DIFFERS (minor) | Q#query-a-metric-view-with-parameters | 2026-11-25 |
| 19 | Requirement to query: "a SQL warehouse or other compute resource running Databricks Runtime 18.2 or above" | Confirmed | UP#requirements | 2026-09-11 |
| 20 | FA table lists "Parameters" under Databricks Runtime 18.2; note: SQL warehouse "is automatically updated with the latest Databricks SQL compute version, so you don't manage runtime versions" | Confirmed | FA | 2026-11-25 |
| 21 | CV: "Parameters require Databricks Runtime 18.2 and above."; example comment "requires DBR 18.2 and above" | Confirmed | CV | 2026-11-19 |
| 22 | Release note: "Querying a metric view that defines parameters requires Databricks Runtime 18.2 or above." | Confirmed | RN | 2026-11-25 |
| 23 | Create privileges: CREATE TABLE and USE SCHEMA on the schema, USE CATALOG on the parent catalog | Confirmed | UP#requirements | 2026-09-11 |
| 24 | Materialization: "You can't materialize a metric view that defines parameters." (listed under Limitations, YAML Materialization note, and Known restrictions). No error text documented | Confirmed (error text NOT FOUND) | UP; YR#materialization; MAT#known-restrictions | 2026-11-11 |
| 25 | Dashboard use: "You can pass parameter values from a SQL query or from an AI/BI dashboard. In a dashboard, connect a parameter to a filter widget to let viewers choose the value at runtime." | Confirmed | UP | 2026-09-11 |
| 26 | Dashboard dataset: reference the metric view in a SQL dataset, call as table-valued function, pass argument with `=>`, wrap each measure in MEASURE, backtick measure names with spaces | Confirmed | DS#pass-parameters-to-a-metric-view | 2026-10-09 |
| 27 | Viewer-selectable: "pass a dashboard parameter into the metric view argument ... Reference the dashboard parameter with the :keyword placeholder"; `metric_view(discount => :discount)` | Confirmed | DS | 2026-10-09 |
| 28 | Exposing: add `:discount` in the Data tab query; add a filter widget and connect it to the parameter. "If you don't expose the parameter on the dashboard, the query uses the parameter's default value from the Data tab." | Confirmed | DS | 2026-10-09 |
| 29 | Local metric view in a dashboard can define Parameters in the visual interface ("Named values that you pass in at query time") | Confirmed | LMV | 2026-11-19 |
| 30 | Value list definition: "a fixed, ordered set of values stored on a parameter. Viewers pick values from it in a Single value or Multiple values filter." | Confirmed | DP#add-a-value-list-to-a-parameter | 2026-11-19 |
| 31 | Value list is set in the Value section of the Parameter details dialog; type is String or Numeric (Integer or Decimal); "Other types don't show the Value section." | Confirmed | DP | 2026-11-19 |
| 32 | Local metric view value lists: "support string, integer, decimal, and double parameters"; "Renaming a parameter keeps its value list. Deleting a parameter deletes its value list." "In YAML mode, you can't edit value lists. Edit them in the visual interface instead." | Confirmed | LMV | 2026-11-19 |
| 33 | Limit: "A value list holds at most 50 values." Over 50: marked "Enter at most 50 values." | Confirmed | DP | 2026-11-19 |
| 34 | Not supported: "Date, Date and Time, and range parameters don't support them." No separate display names, no NULL entry | Confirmed | DP | 2026-11-19 |
| 35 | Not exported: "When you export a dashboard as a .lvdash.json file, or manage it with Git folders or bundles, its value lists aren't included." | Confirmed | DP | 2026-11-19 |
| 36 | Free typing: "A value list suggests values but doesn't restrict them. Viewers can type any value that fits the parameter's type and select it." | Confirmed | DP; RN | 2026-11-19 |
| 37 | Filter behavior: Single value filter becomes a drop-down when a parameter has a list; text entry, date picker, date range, range slider filters ignore it; duplicates shown once; default need not be in list | Confirmed | DP | 2026-11-19 |
| 38 | Release status, parameters: "Metric view parameters are generally available", November 13, 2026 | GA | RN | 2026-11-25 |
| 39 | Release status, value lists: "Value lists for AI/BI dashboard parameters are generally available", November 13, 2026; applies to "a SQL dataset or local metric view parameter" | GA | RN | 2026-11-25 |
| 40 | CV page: "Important: This feature is in Public Preview." appears in the metric view intro section, directly before the parameters paragraph | DIFFERS | CV | 2026-11-19 |
| 41 | UP page, YR parameters section, and DP show no Beta/Preview/GA badge | NOT FOUND (no badge) | UP, YR, DP | n/a |
| 42 | Limitations list on UP is only: no materialization; default value restrictions (castable, no other parameter, no subquery, trailing-defaults rule) | Confirmed | UP#limitations | 2026-09-11 |
| 43 | Local metric views do not support IDENTIFIER parameters (about dashboard SQL parameters, listed in LMV limitations) | Confirmed | LMV | 2026-11-19 |

## Verbatim code blocks

### YAML example (YR#parameters)
```yaml
version: 1.1
source: main.default.sales
parameters:
  - name: discount
    data_type: double
    default: 0
fields:
  - name: product
    expr: product
measures:
  - name: discountedSales
    expr: SUM((1 - discount) * amount)
```

### YAML window size example (YR)
```yaml
version: 1.1
source: samples.tpch.orders
parameters:
  - name: window_size
    data_type: int
    default: 7
fields:
  - name: order_date
    expr: o_orderdate
measures:
  - name: rolling_customers
    expr: COUNT(DISTINCT o_custkey)
    display_name: 'Rolling Customers'
    window:
      - order: order_date
        range: trailing window_size day
```

### UP: by name
```sql
SELECT product, MEASURE(discountedSales)
FROM catalog.schema.metric_view(discount => 0.15)
GROUP BY product;
```

### UP: by position
```sql
SELECT product, MEASURE(discountedSales)
FROM catalog.schema.metric_view(0.15)
GROUP BY product;
```

### UP: defaults (equivalent)
```sql
SELECT product, MEASURE(discountedSales) FROM catalog.schema.metric_view() GROUP BY product;
SELECT product, MEASURE(discountedSales) FROM catalog.schema.metric_view GROUP BY product;
```

### UP: measure from the low-code steps
```sql
SUM((1 - discount) * source.o_totalprice)
```
UP steps: Create > Metric view on samples.tpch.orders; Add parameter `discount`, Numeric, Double, default 0.15; measure `Discounted Sales` = above; measure `Total Sales` = SUM(source.o_totalprice); Save.

### CV: DDL and queries
```sql
CREATE OR REPLACE VIEW discounted_sales_metrics
  WITH METRICS
  LANGUAGE YAML
  AS $$
    version: 1.1
    source: samples.tpch.orders
    parameters:
      - name: discount
        data_type: double
        default: 0
    dimensions:
      - name: order_priority
        expr: o_orderpriority
    measures:
      - name: discounted_revenue
        expr: SUM((1 - discount) * o_totalprice)
  $$;

SELECT order_priority, measure(discounted_revenue)
  FROM discounted_sales_metrics(discount => 0.15)
  GROUP BY ALL;

SELECT order_priority, measure(discounted_revenue)
  FROM discounted_sales_metrics
  GROUP BY ALL;
```

### DS: dashboard fixed value
```sql
SELECT
  MEASURE(`Discounted Sales`),
  MEASURE(`Total Sales`)
FROM catalog.schema.metric_view(discount => 0.20)
```

### DS: dashboard parameter
```sql
SELECT
  MEASURE(`Discounted Sales`),
  MEASURE(`Total Sales`)
FROM catalog.schema.metric_view(discount => :discount)
```
DS steps: (1) Data tab: add the :discount parameter to the dataset query. (2) Add a filter widget to the canvas and connect it to the discount parameter. Viewer selection replaces :discount and reruns the query.

### DP: value list steps (SQL dataset, example query)
```sql
SELECT * FROM samples.tpch.customer WHERE c_mktsegment = :segment
```
Steps: Data tab, select dataset; click the gear next to the parameter name; confirm Type is String or Numeric; type values in the blank row at the bottom of Value (or paste, each line/cell is one value, commas do not split); drag to reorder; click outside the dialog to save.

## NOT FOUND
- Exact error text for the default-ordering rule (row 8).
- Exact error text when materializing a parameterized metric view (row 24).
- Complete list of allowed data types (row 6).
- Explicit list of places parameters cannot be used (row 12).
- Release status badge on UP, YR, DP (row 41).
- 404 paths: metric-views/parameters, metric-views/data-modeling/parameters, uc-semantics/metric-views/model, dashboards/manage/data-modeling/dataset-parameters, dashboards/manage/data-modeling/metric-views. Correct pages are under uc-semantics/metric-views/ and dashboards/manage/...

## DIFFERS
- CV states "This feature is in Public Preview" in the metric view section, while RN says parameters are GA (Nov 13, 2026). The Preview line sits before the parameters paragraph and likely covers metric views in general; treat as ambiguous.
- Q mentions named arguments only; UP documents name, position, and defaults.
- UP last updated 2026-09-11, before the GA note of 2026-11-13.
