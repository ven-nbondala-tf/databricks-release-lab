# Databricks Metric Views Explained: How They Work Inside

Subtitle: Learn how Databricks metric views work inside: dimensions, measures, joins, filters and materialization, checked with EXPLAIN and the query profile.

Databricks metric views define a business metric once, in YAML, so every query, dashboard and BI tool computes it the same way. This guide builds a metric view over the TPC-H orders data and then looks inside it with EXPLAIN and the query profile, so you can see what a query really does. You learn how measures are evaluated, how the joins are planned, how filters, composition and materialization behave, and which errors to expect. The complete code for this guide is on GitHub: [metric-views](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/metric-views).

[VIDEO: add the Part 1 video link here]
Caption: Databricks metric views explained in a short video, part 1 of 2.

Part 2 covers parameters: [Databricks Metric View Parameters: One Definition, Many Uses](add the Part 2 link after publishing).

## What is a Databricks metric view

A metric view is a Unity Catalog object that holds a semantic definition in YAML: a source, optional joins and a filter, the dimensions you group by and the measures you aggregate. You query it with the MEASURE function, and the measures are computed for the grouping you ask for.

- Dimensions are the columns you use in SELECT, WHERE and GROUP BY. The documentation calls them fields and accepts `dimensions` as a synonym.
- Measures are aggregate expressions such as `SUM` or `COUNT`. You read them with `MEASURE()`, or with `AGG()` in Databricks Runtime 18.1 and above.
- Creating and querying a metric view works from Databricks Runtime 16.4, on a SQL warehouse or other compute. Newer features need newer runtimes, and a SQL warehouse updates on its own.
- Dashboards, Genie, alerts, BI tools and plain SQL can all query a metric view.
- The November 13, 2026 release note says metric view parameters are generally available. The CREATE VIEW page still says Public Preview in its metric view section, and the overview, create and query pages show no status. Query-time joins are in Beta.

The diagram shows the path of a query: the consumer sends a grouping, the metric view definition supplies the joins, filter, dimensions and measures, and the plan reads the source tables the grouping needs.

[image: how-it-works.png | Caption: From consumer query to plan, through the metric view definition. | Alt: A flow diagram. Consumers send a query to the metric view definition, which feeds a plan for that grouping, and the plan reads the orders, customer and nation tables.]

## When to use metric views

Use a metric view when the same metric has to give the same answer no matter how it is grouped or where it is read: ratios, distinct counts and anything a dashboard, a Genie space and a notebook should agree on. The documentation puts it this way: standard views lock in aggregations and groupings at creation time, while with a metric view users can group by any available field.

A regular view is enough when you only need a fixed table shape, such as a cleaned table with no aggregation to reuse. If a metric is just a sum that nobody groups differently, a metric view adds little.

## Prerequisites

- A Unity Catalog workspace and a SQL warehouse. Parameters, query-time joins and some other features need newer runtimes, listed in the feature availability table below.
- `SELECT` on the source tables, `USE CATALOG` on the catalog, and `USE SCHEMA` and `CREATE TABLE` on the schema where you create the metric view.
- Serverless compute and Databricks Runtime 17.3 or above, only for materialization.

This guide uses the `samples.tpch` tables and a schema called `metric_demo`.

## Step-by-step guide

### Step 1: Define the metric view

The definition lives in a `CREATE VIEW ... WITH METRICS` statement. This one has a fact source, a snowflake join from orders to customer to nation, five dimensions, and six measures: a count, a sum, a ratio, a filtered measure, a window measure and a measure composed from two others.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Order metrics for the metric views guide
source: samples.tpch.orders
joins:
  - name: customer
    source: samples.tpch.customer
    on: source.o_custkey = customer.c_custkey
    joins:
      - name: nation
        source: samples.tpch.nation
        on: customer.c_nationkey = nation.n_nationkey
dimensions:
  - name: order_date
    expr: o_orderdate
  - name: order_year
    expr: year(o_orderdate)
  - name: order_status
    expr: o_orderstatus
  - name: customer_key
    expr: o_custkey
  - name: customer_segment
    expr: customer.c_mktsegment
  - name: nation
    expr: customer.nation.n_name
measures:
  - name: order_count
    expr: COUNT(1)
  - name: total_revenue
    expr: SUM(o_totalprice)
  - name: average_order_value
    expr: MEASURE(total_revenue) / MEASURE(order_count)
  - name: revenue_per_customer
    expr: SUM(o_totalprice) / COUNT(DISTINCT o_custkey)
  - name: open_order_revenue
    expr: SUM(o_totalprice) FILTER (WHERE o_orderstatus = 'O')
  - name: trailing_7_day_customers
    expr: COUNT(DISTINCT o_custkey)
    window:
      - order: order_date
        range: trailing 7 day
        semiadditive: last
$$;
```

### Step 2: Query it with MEASURE

Every measure in a query goes through `MEASURE()`, and `SELECT *` is not supported, so you list the dimensions and measures you want.

```sql
SELECT nation,
       MEASURE(order_count) AS order_count,
       MEASURE(total_revenue) AS total_revenue,
       MEASURE(revenue_per_customer) AS revenue_per_customer,
       MEASURE(open_order_revenue) AS open_order_revenue
FROM <catalog>.metric_demo.orders_metrics
GROUP BY nation
ORDER BY nation;
```

The first three nations:

| nation | order_count | total_revenue | revenue_per_customer | open_order_revenue |
| --- | --- | --- | --- | --- |
| ALGERIA | 297,584 | 44,997,918,062.31 | 2,270,328.86 | 21,755,986,347.08 |
| ARGENTINA | 301,561 | 45,540,967,378.41 | 2,264,593.11 | 22,011,488,921.26 |
| BRAZIL | 299,249 | 45,292,664,787.14 | 2,267,921.73 | 21,979,984,403.29 |

The measure does not say how to aggregate. It inherits the aggregation from the metric view definition, so changing `GROUP BY nation` to `GROUP BY order_year` needs no other change.

### Step 3: Check that the ratio stays correct

A ratio is where a regular view goes wrong. This regular view stores revenue per customer for each year and nation, which is the grain it was built for.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_ratio_view AS
SELECT
  year(o.o_orderdate) AS order_year,
  n.n_name AS nation,
  SUM(o.o_totalprice) / COUNT(DISTINCT o.o_custkey) AS revenue_per_customer
FROM samples.tpch.orders AS o
JOIN samples.tpch.customer AS c ON o.o_custkey = c.c_custkey
JOIN samples.tpch.nation AS n ON c.c_nationkey = n.n_nationkey
GROUP BY year(o.o_orderdate), n.n_name;
```

At that grain, both agree. Group by nation only, and the regular view has to average the stored ratios, which is not the ratio of the totals. The metric view evaluates the measure's own expression for the grouping in the query.

```sql
WITH regular AS (
  SELECT nation, AVG(revenue_per_customer) AS regular_view
  FROM <catalog>.metric_demo.orders_ratio_view
  GROUP BY nation
),
metric AS (
  SELECT nation, MEASURE(revenue_per_customer) AS metric_view
  FROM <catalog>.metric_demo.orders_metrics
  GROUP BY nation
),
truth AS (
  SELECT n.n_name AS nation, SUM(o.o_totalprice) / COUNT(DISTINCT o.o_custkey) AS from_base_tables
  FROM samples.tpch.orders AS o
  JOIN samples.tpch.customer AS c ON o.o_custkey = c.c_custkey
  JOIN samples.tpch.nation AS n ON c.c_nationkey = n.n_nationkey
  GROUP BY n.n_name
)
SELECT nation, ROUND(regular_view, 2) AS regular_view,
       ROUND(metric_view, 2) AS metric_view,
       ROUND(from_base_tables, 2) AS from_base_tables
FROM regular JOIN metric USING (nation) JOIN truth USING (nation)
ORDER BY nation;
```

[image: regular-vs-metric-view.png | Caption: Revenue per customer by nation from a regular view, the metric view and the base tables. | Alt: A table with three columns of numbers for eight nations. The regular view column shows about 381,000 for every nation. The metric view and base tables columns agree and show about 2.27 million.]

The regular view is wrong for all 25 nations, about 381 thousand against about 2.27 million. The metric view matches the base tables for all 25.

### Step 4: See which tables a query reads with EXPLAIN

The documentation says a metric view joins the fact and dimension tables needed for the specific query. EXPLAIN shows what that means for a plan. First a query that uses only a fact column:

```sql
EXPLAIN FORMATTED
SELECT order_year, MEASURE(total_revenue) AS rev
FROM <catalog>.metric_demo.orders_metrics
GROUP BY order_year;
```

[image: 01-explain-fact-only.png | Caption: The plan for a query on a fact column scans one table. | Alt: An EXPLAIN plan tree with a single scan node on samples.tpch.orders, followed by a partial aggregate, a shuffle and a final aggregate.]

The plan has one scan, of `samples.tpch.orders`. Then a query that groups by `nation`, a column that comes from the joined tables:

```sql
EXPLAIN FORMATTED
SELECT nation, MEASURE(total_revenue) AS rev
FROM <catalog>.metric_demo.orders_metrics
GROUP BY nation;
```

[image: 02-explain-dimension.png | Caption: The plan for a query on a nation column scans three tables. | Alt: An EXPLAIN plan tree with scan nodes on orders, customer and nation joined by two left outer join nodes.]

This plan scans `orders`, `customer` and `nation`, joined with two left outer joins, a broadcast hash join and a shuffled hash join. That matches the documentation, which says the fact table joins its dimension tables with a left outer join.

Two more observations from our plans, for this snowflake join of orders, customer and nation:

- A query on `customer_segment`, a column of `customer` only, also scanned `nation`. The nation scan read only the join key, `n_nationkey`.
- With `rely: at_most_one_match` set on both joins, the `nation` query plan has no window nodes, where the plan without it has eight. The documentation describes `rely` as a way to skip unnecessary joins. In our plans the `nation` scan for the `customer_segment` query was still there with `rely` set. Other join shapes and data can give other plans.

### Step 5: Read the query profile

Run the nation query as a normal SELECT, then open its query profile from Query History. The profile shows the same plan with row counts.

```sql
SELECT nation, MEASURE(total_revenue) AS rev
FROM <catalog>.metric_demo.orders_metrics
GROUP BY nation
ORDER BY rev DESC;
```

[image: 03-query-profile.png | Caption: The query profile of the nation query, with the row counts between operators. | Alt: A query profile graph with 28 operators. A scan of 7.50 million rows feeds a left outer join, and a second input of 750 thousand rows comes from a join with a 25 row scan, each side passing through sort, window and filter operators.]

The summary reads 8,250,025 rows, which is 7,500,000 from `orders`, 750,000 from `customer` and 25 from `nation`. The graph has three Scan Table operators, two Left Outer Join operators, and a Sort, Window and Filter chain on each joined side. The profile does not name the tables on its nodes, so use EXPLAIN to see which scan is which.

### Step 6: Add a filter to the definition

A filter in the YAML applies to every query on the metric view, whatever the query asks for. This metric view keeps only orders from 1996 on.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_since_1996
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Same metrics, but only orders from 1996 on
source: samples.tpch.orders
filter: o_orderdate >= DATE'1996-01-01'
dimensions:
  - name: order_year
    expr: year(o_orderdate)
measures:
  - name: order_count
    expr: COUNT(1)
  - name: total_revenue
    expr: SUM(o_totalprice)
$$;
```

A query with no WHERE clause returns 1996, 1997 and 1998 only, with 1,141,556, 1,137,325 and 668,101 orders. The total is 2,946,982 orders, which equals the count in the base table with the same date condition. The base table holds 7,500,000 orders.

### Step 7: Build a metric view on another metric view

A metric view can be the source of another one, and measures can reference measures. This one reads from the first metric view and composes a revenue per order measure from two of its measures.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_metrics_by_year
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: A metric view that uses another metric view as its source
source: <catalog>.metric_demo.orders_metrics
dimensions:
  - name: order_year
    expr: order_year
  - name: nation
    expr: nation
measures:
  - name: revenue
    expr: MEASURE(total_revenue)
  - name: orders
    expr: MEASURE(order_count)
  - name: revenue_per_order
    expr: MEASURE(revenue) / MEASURE(orders)
$$;
```

For Brazil, the revenue per order by year matches the `average_order_value` measure of the first view and a query on the base tables, for all seven years. For 1992 it is 151,541.42 in all three.

### Step 8: Join a metric view to another table

Query-time joins are in Beta, and the documentation lists them under Databricks Runtime 19. You join a metric view to a table on one of its fields and wrap each measure in `MEASURE()`. The metric view has to expose the join column as a field, here `customer_key`.

```sql
SELECT c.c_mktsegment,
       MEASURE(o.order_count) AS order_count,
       MEASURE(o.total_revenue) AS total_revenue
FROM <catalog>.metric_demo.orders_metrics AS o
JOIN samples.tpch.customer AS c ON o.customer_key = c.c_custkey
GROUP BY c.c_mktsegment
ORDER BY c.c_mktsegment;
```

For results that you have already aggregated, the documentation uses a common table expression (CTE). The aggregated values become regular columns.

```sql
WITH orders AS (
  SELECT customer_key,
         MEASURE(order_count) AS order_count,
         MEASURE(total_revenue) AS total_revenue
  FROM <catalog>.metric_demo.orders_metrics
  GROUP BY customer_key
)
SELECT c.c_mktsegment,
       SUM(orders.order_count) AS order_count,
       SUM(orders.total_revenue) AS total_revenue
FROM orders
JOIN samples.tpch.customer AS c ON orders.customer_key = c.c_custkey
GROUP BY c.c_mktsegment
ORDER BY c.c_mktsegment;
```

Both queries, and a query on the `customer_segment` dimension in the metric view itself, return the same five rows. For AUTOMOBILE: 1,497,982 orders and 226,311,189,156.13 in revenue.

### Step 9: Materialize an aggregate

Materialization precomputes an aggregate. You add a `materialization` block to the definition, and Lakeflow pipelines refresh the materialized views on the schedule you set. It needs serverless compute.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_materialized
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Orders metrics with a materialized aggregate
source: samples.tpch.orders
dimensions:
  - name: order_year
    expr: year(o_orderdate)
  - name: order_status
    expr: o_orderstatus
  - name: order_priority
    expr: o_orderpriority
measures:
  - name: order_count
    expr: COUNT(1)
  - name: total_revenue
    expr: SUM(o_totalprice)
materialization:
  schedule: every 6 hours
  mode: relaxed
  materialized_views:
    - name: by_year_status
      type: aggregated
      dimensions:
        - order_year
        - order_status
      measures:
        - order_count
        - total_revenue
$$;
```

Creating the metric view starts a pipeline update. Once it has finished, EXPLAIN shows which queries use the materialized result. The documentation says the optimizer tries an exact match, then a rollup match, then an unaggregated match, and then the source.

- Grouping by `order_year` and `order_status` is an exact match. The plan scans a table named `__materialization_...` in the schema, and reads only the four columns the query needs.
- Grouping by `order_year` alone is a rollup of the same aggregate. The plan scans the same table.
- Grouping by `order_priority`, which is not in the materialized aggregate, falls back to the source. The plan scans `samples.tpch.orders`.

Query-time joins bypass materializations and read live source data.

### Step 10: Check governance in Catalog Explorer

Catalog Explorer shows a metric view like other Unity Catalog objects, with Overview, Details, Permissions and Lineage tabs. The Details tab shows the definition back as YAML, 56 lines for this metric view. The keys come back in a different order than you wrote them, and `on` is quoted.

[image: 04-catalog-explorer-definition.png | Caption: The YAML definition on the Details tab of the metric view. | Alt: The Definition panel in Catalog Explorer showing the YAML of the orders metrics view, with the joins, six dimensions and six measures.]

The Lineage tab lists the three source tables as upstream and the composed metric view from step 7 as downstream. The documentation recommends the Lineage tab to find dependencies before you drop a metric view.

[image: 06-lineage.png | Caption: The lineage graph of the metric view. | Alt: A lineage graph with the orders, nation and customer tables on the left, the orders metrics view in the middle and the orders metrics by year view on the right.]

The `team: data_platform` tag on the metric view cards is inherited from the catalog, where the tag is set. The first part of the tags series, [Databricks Data Tags Explained: Regular, Governed, System](https://medium.com/@nagarajubru/databricks-data-tags-regular-governed-system-tags-a091a37e6884), explains how tags work.

## Example: one revenue definition for every consumer

A team wants one definition of revenue that the dashboard, the Genie space and an analyst's notebook all use. They define `total_revenue` and `revenue_per_customer` once in `orders_metrics`, and every consumer reads it with `MEASURE()`.

The metric view also carries semantic metadata for the consumers that need it. With YAML specification 1.1 and Databricks Runtime 17.3 or above, fields and measures can have display names, formats, synonyms and comments, and the documentation says tools such as Genie use synonyms to find fields and measures. AI/BI dashboards apply `MEASURE()` automatically and show the metadata in the interface. External BI tools can use custom SQL with `MEASURE()`, a wrapper view, or BI compatibility mode, which rewrites the standard aggregations a tool generates against measure columns. In that mode, measure columns must use `SUM`.

The check that matters is that every route returns the same number. The metric view, the query-time join, the CTE pattern and the base tables all returned 226,311,189,156.13 of revenue for the AUTOMOBILE segment.

The full example, including setup and cleanup, is in the [metric-views](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/metric-views) folder of the repository.

## Things to know

- Wrap every measure in `MEASURE()`. A query that reads a measure without it fails: `[METRIC_VIEW_MISSING_MEASURE_FUNCTION] The usage of measure column [total_revenue] of a metric view requires a MEASURE() (or AGG()) function to produce results. SQLSTATE: 42K0E`.
- Expose the join column as a field before you join at query time. Joining on a source column that is not a field fails: `[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column, variable, or function parameter with name `o`.`o_custkey` cannot be resolved. Did you mean one of the following? [`c`.`c_custkey`, `c`.`c_name`, `o`.`customer_key`, `c`.`c_phone`, `o`.`nation`]. SQLSTATE: 42703`.
- Do not use a metric view with one-to-many YAML joins as an input to a query-time join. The documentation lists it as unsupported, and the query fails with `[METRIC_VIEW_UNSUPPORTED_USAGE] The metric view usage is not supported.`, followed by the logical plan. Query-time joins are in Beta, and the documentation lists them under Databricks Runtime 19.
- Set `rely: at_most_one_match` on a join only when it is true. The documentation says it is not validated at runtime, and measures are incorrect if the joined side fans out.

## Best practices

- Define ratios as measures in the metric view, not as columns in a view, so they stay correct for any grouping.
- Run EXPLAIN on the queries your dashboards send, and check which tables each one reads.
- Put filters that should always apply in the YAML, and keep query filters for the rest.
- Use the CTE pattern for results that are already aggregated, and a query-time join when you want the measures computed for the joined grouping.
- Check the feature availability table before you rely on a feature, because it lists the runtime each one needs.

## Summary

A metric view stores dimensions, measures, joins and filters in one YAML definition, and a query computes the measures for the grouping it asks for. In our tests, a fact-only query read one table, a ratio measure stayed correct where a regular view did not, and a materialized aggregate was used only when the grouping matched. Use metric views when the same metric must give the same answer in every tool, and read part 2 for parameters.

Which of your dashboard metrics would you define as a measure first?

## References

- [Unity Catalog metric views](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/), Microsoft Learn
- [Metric view YAML reference](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/yaml-reference), Microsoft Learn
- [Query a metric view](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/query), Microsoft Learn
- [Metric view feature availability](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/feature-availability), Microsoft Learn
- [Materialization for metric views](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/materialization), Microsoft Learn
- [CREATE VIEW](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-create-view), Microsoft Learn

## Medium settings

- SEO title: Databricks Metric Views Explained: How They Work Inside
- SEO description: same as the subtitle
- Slug: databricks-metric-views-explained-how-they-work-inside
- Tags: Databricks, Data Engineering, Semantic Layer, Business Intelligence, Unity Catalog
