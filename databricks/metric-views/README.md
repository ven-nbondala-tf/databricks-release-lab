# Metric views: how they work, and parameters

Working code and test notes for two guides:

- Part 1: Databricks Metric Views Explained: How They Work Inside
- Part 2: Databricks Metric View Parameters: One Definition, Many Uses

The SQL builds one metric view over the `samples.tpch` tables, then looks inside it with EXPLAIN and the query profile, and adds parameters in a second metric view that a dashboard calls.

## What is in this folder

| Path | Purpose |
| --- | --- |
| `sql/00_setup.sql` | Creates the schema |
| `sql/02_create_orders_metrics.sql` | The main metric view: snowflake join, dimensions, a ratio, a filtered measure, a window measure, a composed measure |
| `sql/03_ratio_test.sql`, `sql/04_ratio_compare.sql` | A regular view with the ratio precomputed, and the comparison with the metric view |
| `sql/05_filtered_metric_view.sql` | A YAML-level filter |
| `sql/06_create_parameterized_metric_view.sql` | Part 2: the parameterized metric view |
| `sql/07_defaults_rule_error.sql` | Part 2: a default followed by a parameter without one (fails) |
| `sql/08_composed_metric_view.sql` | A metric view built on another metric view |
| `sql/09_query_time_join.sql`, `sql/10_cte_pattern.sql` | Joining a metric view to a table, two ways |
| `sql/11_create_orders_metrics_rely.sql` | The same metric view with `rely` on both joins |
| `sql/12_materialized_metric_view.sql` | A metric view with a materialized aggregate |
| `sql/13_materialization_with_parameters_error.sql` | Part 2: materialization on a parameterized metric view (fails) |
| `sql/14_customers_orders_one_to_many.sql` | A metric view with a one-to-many join |
| `sql/cleanup.sql` | Drops everything |
| `diagrams/` | Mermaid sources, HTML and PNG for the two diagrams and the comparison image |
| `tests/` | Saved outputs of the queries, EXPLAIN plans and error messages, plus `results.md` |

## Prerequisites

- A Unity Catalog workspace and a SQL warehouse on a recent runtime. Parameters need Databricks Runtime 18.2 or above and query-time joins are listed under Runtime 19. The feature availability page says a SQL warehouse is automatically updated with the latest Databricks SQL compute version.
- Read access to `samples.tpch`.
- `USE CATALOG` on your catalog and `USE SCHEMA` and `CREATE TABLE` on the schema `metric_demo`.
- Materialization needs serverless compute.

## Setup

1. Replace `<catalog>` with your catalog in every file in `sql/`.
2. Run `sql/00_setup.sql`.
3. Run the files in `sql/` in numeric order. Files `02` to `14` each create a view or run a query. Files `07` and `13` are expected to fail, and the error messages are saved in `tests/`.

## How to run

Run each file in the SQL editor, or from the terminal with the helper in `tests/sql.py`:

```bash
export WAREHOUSE_ID=<warehouse-id>
python3 tests/sql.py "SELECT order_year, MEASURE(order_count) FROM <catalog>.metric_demo.orders_metrics GROUP BY order_year"
```

The queries used in the articles are quoted in `tests/results.md`.

## Expected result

- The regular view gives a wrong revenue per customer when you group by nation, for all 25 nations. The metric view matches a query on the base tables for all 25.
- A query on fact columns only reads `orders`. A query on a nation or customer column reads `orders`, `customer` and `nation`.
- The parameterized metric view returns the same values by name, by position and with defaults, and `discount => 0.15` returns 85 percent of the undiscounted revenue.
- The two failing files return the errors saved in `tests/error_defaults_order.txt` and `tests/error_materialization_parameters.txt`.

## Dashboard

Create a dashboard dataset with this query, add a value list to the `discount` parameter and connect it to a filter widget:

```sql
SELECT order_priority, MEASURE(discounted_revenue) AS discounted_revenue
FROM <catalog>.metric_demo.orders_discount(discount => :discount)
GROUP BY ALL
ORDER BY order_priority;
```

## Cleanup

Run `sql/cleanup.sql` with your catalog name. Delete the dashboard in the UI.
