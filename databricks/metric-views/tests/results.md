# Test results

Run on November 26, 2026 on a serverless SQL warehouse, against `samples.tpch` and the schema `metric_demo` in a test catalog. These notes are not part of the articles. Raw outputs are in this folder; storage paths and generated IDs were removed.

## Availability

- `CREATE VIEW ... WITH METRICS`, `MEASURE()`, joins, window measures, filtered measures, composed measures, YAML filter, materialization, query-time joins and parameters all ran on the warehouse. No preview setting was turned on.

## Part 1

### 1. The metric view

`orders_metrics`: source `samples.tpch.orders`, a snowflake join (orders, customer, nation), dimensions `order_date`, `order_year`, `order_status`, `customer_key`, `customer_segment`, `nation`, measures `order_count`, `total_revenue`, `average_order_value` (composed), `revenue_per_customer` (ratio), `open_order_revenue` (filtered), `trailing_7_day_customers` (window). All six measures returned values. Example, ALGERIA: 297,584 orders, 44,997,918,062.31 revenue, 2,270,328.86 revenue per customer, 21,755,986,347.08 open order revenue. Window measure for 1995-03-01 to 1995-03-05: 21,144, 21,266, 21,447, 21,398, 21,400.

### 2. Ratio test (`ratio_by_nation.txt`)

- Regular view `orders_ratio_view` stores revenue per customer per year and nation. At that grain it agrees with the metric view (BRAZIL, all 7 years identical).
- Grouped by nation: the regular view (average of the stored ratio) gives about 381,000 for every nation. The metric view and a query on the base tables give about 2,270,000. Over all 25 nations: regular view wrong 25, metric view wrong 0 (tolerance 0.005).

### 3. Join planning with EXPLAIN FORMATTED

| Query | Tables scanned | Joins |
| --- | --- | --- |
| `GROUP BY order_year` | orders | none |
| `GROUP BY nation` | orders, customer, nation | PhotonShuffledHashJoin LeftOuter, PhotonBroadcastHashJoin LeftOuter |
| `GROUP BY customer_segment` | orders, customer, nation (the nation scan reads only `n_nationkey`) | same two |

- Without `rely`, each joined side sits under sort, window and filter nodes: 8 PhotonWindow nodes in the nation plan, 190 lines of output.
- With `rely: at_most_one_match: true` on both joins (`orders_metrics_rely`): 0 window nodes, 114 to 118 lines. The same tables are scanned, including `nation` for the `customer_segment` query.
- Files: `explain_fact_only.txt`, `explain_dimension.txt`, `explain_customer_dimension.txt`, `explain_rely_*.txt`.

### 4. Query profile

Query `SELECT nation, MEASURE(total_revenue) AS rev ... GROUP BY nation ORDER BY rev DESC`, 25 rows. Summary: 8,250,025 rows read (7,500,000 orders, 750,000 customer, 25 nation), 53.66 MB, 5 files, 100% from cache. The graph has 28 operators: three Scan Table, two Left Outer Join, and a Sort, Window and Filter chain on each joined side. The profile does not name tables on the nodes. Screenshot: screenshots/03-query-profile.png.

### 5. YAML-level filter (`filter_by_year.txt`)

`orders_since_1996` with `filter: o_orderdate >= DATE'1996-01-01'`. A query with no WHERE returns 1996 (1,141,556), 1997 (1,137,325) and 1998 (668,101): total 2,946,982, equal to the base table with the same condition. The base table has 7,500,000 orders.

### 6. Composability (`composed_*.txt`)

`orders_metrics_by_year` uses `orders_metrics` as its source with `revenue_per_order = MEASURE(revenue) / MEASURE(orders)`. BRAZIL by year equals `average_order_value` in the first view and a query on the base tables (1992: 151,541.42 in all three).

### 7. Joining a metric view to a table

The brief expected an error for a direct join. The documentation now describes query-time joins (Beta, listed under Runtime 19), and the join worked on the warehouse.

- Query-time join on `customer_key` (`join_query_time.txt`) and the CTE pattern (`join_cte.txt`) return the same rows as the `customer_segment` dimension in the view, for all five segments (AUTOMOBILE: 1,497,982 orders, 226,311,189,156.13 revenue).
- Errors found:
  - Measure without MEASURE(): `[METRIC_VIEW_MISSING_MEASURE_FUNCTION] The usage of measure column [total_revenue] of a metric view requires a MEASURE() (or AGG()) function to produce results. SQLSTATE: 42K0E`
  - Join on a column that is not a field: `[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column, variable, or function parameter with name `o`.`o_custkey` cannot be resolved. Did you mean one of the following? [`c`.`c_custkey`, `c`.`c_name`, `o`.`customer_key`, `c`.`c_phone`, `o`.`nation`]. SQLSTATE: 42703; line 1 pos 132`
  - A metric view with a one-to-many YAML join as the input of a query-time join (`customers_orders_metrics`): `[METRIC_VIEW_UNSUPPORTED_USAGE] The metric view usage is not supported.` followed by the logical plan (trimmed in `error_join_one_to_many_input.txt`).

### 8. Materialization

`orders_materialized` with one aggregated materialized view (order_year, order_status; order_count, total_revenue), schedule every 6 hours, relaxed mode. Creating it started a pipeline update that completed in about 1 minute.

| Query | Plan scans |
| --- | --- |
| `GROUP BY order_year, order_status` (exact match) | table `__materialization_...`, 4 columns |
| `GROUP BY order_year` (rollup) | the same table, 2 columns |
| `GROUP BY order_priority` (not in the materialization) | `samples.tpch.orders` |

Status from the docs: the materialization page shows no status label. Requirements: serverless compute, Runtime 17.3 or above.

### 9. Catalog Explorer

- Details tab: the Definition panel shows the YAML back (56 lines), with the keys reordered and `on` quoted. Screenshot: screenshots/04-catalog-explorer-definition.png.
- Permissions tab: "No permissions granted yet." Not used in the article.
- Lineage tab: upstream orders, customer, nation (samples.tpch), downstream metric view `orders_metrics_by_year`. Screenshot: screenshots/06-lineage.png. The metric view card shows a tag `team: data_platform` that these scripts did not set.

## Part 2

1. `orders_discount` with `discount` (double, default 0) and `start_date` (date). By name `(discount => 0.15)`, by position `(0.15, DATE'1992-01-01')`, `()` and the bare name all ran. 1-URGENT: total 226,905,605,646, discounted with 0.15 192,869,764,799 (0.85 times total), defaults equal total.
2. Date parameter: `start_date => DATE'1996-01-01'` gives 445,319,338,080.77, equal to `orders_since_1996` and to the base table.
3. EXPLAIN: the date appears as a scan filter (`DictionaryFilters` and `RequiredDataFilters` contain `o_orderdate >= 1996-01-01`) and the discount appears in the aggregate as `0.85 * cast(o_totalprice as double)`.
4. Defaults rule, a default followed by a parameter without one: `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: This metric view has a parameter with a default, and any subsequent parameters without defaults are not allowed. SQLSTATE: 42K0E`
5. Date default as a string: `default: '1992-01-01'` and `default: 1992-01-01` both fail with `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: Parameter 'start_date' default value '1992-01-01' is not compatible with declared type 'date': IntegerType (of class org.apache.spark.sql.types.IntegerType$). SQLSTATE: 42K0E`. `DATE'1992-01-01'` and `DATE '1992-01-01'` work.
6. Materialization on a parameterized metric view: `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: Materialization is not supported on parameterized metric views.. SQLSTATE: 42K0E`
7. Dashboard:

Dashboard `metric_views_demo` (saved draft, not published): dataset `discounted_revenue` on `orders_discount(discount => :discount)`, parameter `discount` with type Numeric and numeric type Decimal and a value list of 0, 0.05, 0.1, 0.15, 0.2, a bar chart and a single value filter widget.
   - discount 0: 1-URGENT 226.91B, 2-HIGH 226.79B, 3-MEDIUM 226.29B, 4-NOT SPECIFIED 226.83B, 5-LOW 226.63B.
   - discount 0.15: 192.87B, 192.77B, 192.35B, 192.8B, 192.63B. The ratio for 1-URGENT is 0.850. The axis rescales (top tick 200B in both).
   - The dataset editor shows the parameter as a plain text box; the value list appears as a drop-down in the filter widget. The dialog labels the value list section "Domain" (the docs call it the Value section).
   - Screenshots: screenshots/07-dashboard-value-list.png, 08-dashboard-discount-0.png, 09-dashboard-discount-015.png.

## What differed from the documentation and the brief

- Query-time joins: the brief says metric views cannot be joined at query time. The documentation now describes query-time joins (Beta) and the CTE pattern for aggregated results. Both worked.
- Date default: the documentation says a default only has to be castable to the data type. A quoted date string is rejected, and a SQL date literal is accepted.
- `rely` and join pruning, as observed in our plans for the snowflake join (orders, customer, nation): `rely` removed the window nodes, and the `nation` scan for a customer-only query stayed with `rely` set. The documentation describes `rely` as a way to skip unnecessary joins; other join shapes and data can give other plans.
- Release status: the CREATE VIEW page calls the feature Public Preview, the November 13, 2026 release note says parameters are generally available, and the other pages show no status.
- Value list dialog: the section is labelled Domain in the dataset editor, and the documentation calls it the Value section.
- Not tested: semantic metadata (synonyms, display names), BI compatibility mode, agg() (Runtime 18.1 and above), sharing, relationships between metric views.
