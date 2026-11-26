# Databricks Metric View Parameters: One Definition, Many Uses

Subtitle: Learn how Databricks metric view parameters work: define them in YAML, call them by name or position, and pass a value from a dashboard.

Databricks metric view parameters let one metric view definition return different results for different values, such as a discount rate or a start date. This guide adds parameters to a metric view, calls it by name, by position and with defaults, checks where the values land in the query plan, and passes a value from a dashboard with a value list. You also see the exact errors for the rules that trip people up. The complete code for this guide is on GitHub: [metric-views](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/metric-views).

[VIDEO: add the Part 2 video link here]
Caption: Databricks metric view parameters in a short video, part 2 of 2.

Part 1 explains how metric views work inside: [Databricks Metric Views Explained: How They Work Inside](add the Part 1 link after publishing).

## What are Databricks metric view parameters

A parameter is a named value that a caller passes when it queries a metric view. The definition uses the parameter in a measure, a filter, the source or a join, so one definition serves many variants.

- Parameters are generally available, according to the November 13, 2026 release note. The CREATE VIEW page still says Public Preview in its metric view section.
- Querying a metric view that defines parameters needs Databricks Runtime 18.2 or above, on a SQL warehouse or other compute. A SQL warehouse updates on its own.
- You call the metric view like a table-valued function and pass values by name, by position, or not at all to use the defaults.
- Each parameter has a name, a data type such as `double`, `int`, `string` or `date`, and an optional default.
- A dashboard can pass a value into a parameter through a filter widget.

The diagram shows one definition called four ways, with a different result for each value.

[image: parameters.png | Caption: One metric view definition, called by name, by position, with defaults and from a dashboard. | Alt: A flow diagram. Four callers, SQL by name, SQL by position, SQL with defaults and a dashboard filter, all call one metric view definition. It returns 192.9 billion for discount 0.15 and 226.9 billion for the default discount 0.]

## When to use metric view parameters

Use a parameter when callers need variants of the same metric: a discount scenario, a cutoff date, a window size. A parameter works inside the definition, in a measure, a filter or a join, so the metric changes and not just the rows you select afterwards. Without it you would create one metric view for each variant.

A normal dimension is better when a caller only needs to slice results. A metric view with parameters cannot be materialized, so use a metric view without parameters when you need a materialized aggregate.

## Prerequisites

- A SQL warehouse or other compute on Databricks Runtime 18.2 or above.
- `USE CATALOG`, `USE SCHEMA` and `CREATE TABLE` where you create the metric view, and `SELECT` on the source table.
- An AI/BI dashboard, for the last step.

This guide uses the `samples.tpch.orders` table. Part 1 shows how to set up a schema and a first metric view.

## Step-by-step guide

### Step 1: Add parameters to the definition

The `parameters` block goes before the fields and measures. This metric view has a `discount` parameter used in a measure and a `start_date` parameter used in the filter. Both have defaults.

```sql
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_discount
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: Order revenue with a discount parameter and a start date parameter
source: samples.tpch.orders
parameters:
  - name: discount
    data_type: double
    default: 0
  - name: start_date
    data_type: date
    default: DATE'1992-01-01'
filter: o_orderdate >= start_date
dimensions:
  - name: order_priority
    expr: o_orderpriority
  - name: order_year
    expr: year(o_orderdate)
measures:
  - name: total_revenue
    expr: SUM(o_totalprice)
  - name: discounted_revenue
    expr: SUM((1 - discount) * o_totalprice)
$$;
```

### Step 2: Call it by name, by position and with defaults

Name the parameter with `=>`.

```sql
SELECT order_priority,
       MEASURE(total_revenue) AS total,
       MEASURE(discounted_revenue) AS discounted
FROM <catalog>.metric_demo.orders_discount(discount => 0.15)
GROUP BY ALL
ORDER BY order_priority;
```

| order_priority | total | discounted |
| --- | --- | --- |
| 1-URGENT | 226.9 billion | 192.9 billion |
| 2-HIGH | 226.8 billion | 192.8 billion |
| 3-MEDIUM | 226.3 billion | 192.3 billion |
| 4-NOT SPECIFIED | 226.8 billion | 192.8 billion |
| 5-LOW | 226.6 billion | 192.6 billion |

To pass by position, list the values in the order the parameters are defined. This call returns the same discounted values.

```sql
SELECT order_priority, MEASURE(discounted_revenue) AS discounted
FROM <catalog>.metric_demo.orders_discount(0.15, DATE'1992-01-01')
GROUP BY ALL
ORDER BY order_priority;
```

To use the defaults, call the metric view with empty parentheses, or by its name alone. Both calls return the undiscounted revenue, because the default discount is 0, so `discounted` equals `total`, 226.9 billion for 1-URGENT.

```sql
SELECT order_priority, MEASURE(discounted_revenue) AS discounted
FROM <catalog>.metric_demo.orders_discount()
GROUP BY ALL;

SELECT order_priority, MEASURE(discounted_revenue) AS discounted
FROM <catalog>.metric_demo.orders_discount
GROUP BY ALL;
```

### Step 3: Use the date parameter

The `start_date` parameter is part of the YAML filter, so passing it moves the cutoff.

```sql
SELECT MEASURE(total_revenue) AS revenue
FROM <catalog>.metric_demo.orders_discount(start_date => DATE'1996-01-01');
```

The result is 445,319,338,080.77. A metric view with the date written into its filter and a query on the base table with the same condition return the same number.

### Step 4: See where the values land with EXPLAIN

EXPLAIN shows what the parameter values turn into.

```sql
EXPLAIN FORMATTED
SELECT order_priority, MEASURE(discounted_revenue)
FROM <catalog>.metric_demo.orders_discount(discount => 0.15, start_date => DATE'1996-01-01')
GROUP BY ALL;
```

In the plan, the date is a filter on the scan: `RequiredDataFilters: [isnotnull(o_orderdate), (o_orderdate >= 1996-01-01)]`. The discount is in the aggregate as a constant: `partial_sum((0.85 * cast(o_totalprice as double)))`. The plan shows the values as constants, not as parameters.

### Step 5: Pass a value from a dashboard

An AI/BI dashboard dataset can call the metric view and pass a dashboard parameter to it. The dataset query uses the `:discount` placeholder for the metric view argument. For more on how dashboards behave, see [How Databricks Dashboards Handle Permissions and Refresh](https://medium.com/@nagarajubru/databricks-dashboards-permissions-refresh-553e82f3e4a1).

```sql
SELECT order_priority, MEASURE(discounted_revenue) AS discounted_revenue
FROM <catalog>.metric_demo.orders_discount(discount => :discount)
GROUP BY ALL
ORDER BY order_priority;
```

Add the dataset in the Data tab. The `:discount` placeholder creates a dashboard parameter. In the parameter details, choose Numeric with the Decimal type, and add the values for the value list in the order you want them to appear. The dialog labels this section Domain.

[image: 07-dashboard-value-list.png | Caption: The parameter details of the discount parameter, with a value list of five values. | Alt: The Parameter details panel for the discount keyword, with type Numeric and numeric type Decimal, and a Domain list with the values 0, 0.05, 0.1, 0.15 and 0.2.]

In the dataset editor, the parameter input is a plain text box. The value list shows up as a drop-down in the filter widget on the canvas. Add a bar chart with `order_priority` on the x axis and `discounted_revenue` on the y axis, and a single value filter widget connected to the `discount` parameter.

With 0 selected, the bars show the undiscounted revenue.

[image: 08-dashboard-discount-0.png | Caption: The dashboard with the discount filter set to 0. | Alt: A bar chart of discounted revenue for five order priorities with labels from 226.29 to 226.91 billion, next to a discount filter set to 0.]

With 0.15 selected, the same chart shows 85 percent of those values.

[image: 09-dashboard-discount-015.png | Caption: The dashboard with the discount filter set to 0.15. | Alt: The same bar chart with labels from 192.35 to 192.87 billion, next to a discount filter set to 0.15.]

For 1-URGENT the bar goes from 226.91 billion to 192.87 billion. The chart axis rescales and its top tick is 200 billion in both views, so the bars look alike and the data labels carry the difference.

## Example: discount scenarios for one revenue metric

A finance team wants to see revenue with a discount applied, and the discount changes from one scenario to the next. They define `discounted_revenue` once and let each caller pass its own value. The same definition answers all three calls:

| Call | 1-URGENT revenue |
| --- | --- |
| `orders_discount()` | 226.9 billion |
| `orders_discount(discount => 0.15)` | 192.9 billion |
| `orders_discount(discount => 0.2)` | 181.5 billion |

The dashboard in step 5 gives the same values. Choosing 0 gives the undiscounted figure and choosing 0.15 gives 192.9 billion for 1-URGENT.

The full example, including setup and cleanup, is in the [metric-views](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/metric-views) folder of the repository.

## Things to know

- Give every parameter after the first default a default too. The documentation says that if you set a default for one parameter, every parameter that follows must also have one. A default followed by a parameter without one fails: `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: This metric view has a parameter with a default, and any subsequent parameters without defaults are not allowed. SQLSTATE: 42K0E`.
- Write a date default as a SQL date literal. A default of `'1992-01-01'` or `1992-01-01` fails, although the documentation says only that the default must be castable to the data type: `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: Parameter 'start_date' default value '1992-01-01' is not compatible with declared type 'date': IntegerType (of class org.apache.spark.sql.types.IntegerType$). SQLSTATE: 42K0E`. `DATE'1992-01-01'` works.
- Do not materialize a metric view that defines parameters. Adding a `materialization` block fails: `[METRIC_VIEW_INVALID_VIEW_DEFINITION] The metric view definition is invalid. Reason: Materialization is not supported on parameterized metric views.. SQLSTATE: 42K0E`.
- Treat a value list as a suggestion. The documentation says a value list holds at most 50 values, works with string and numeric parameters but not date parameters, and does not stop viewers from typing any value that fits the type. Value lists are not included when you export a dashboard as a `.lvdash.json` file.
- Check the runtime. Querying a metric view that defines parameters needs Databricks Runtime 18.2 or above, and a SQL warehouse updates on its own.

## Best practices

- Give every parameter a default, so a plain `SELECT` on the metric view still works.
- Pass parameters by name, so a query keeps working if you add a parameter later.
- Use a parameter for a variant of the metric and a dimension for a slice of the rows.
- Keep a version without parameters if you need materialization.

## Summary

Parameters let one metric view definition serve many variants: you declare them in the YAML, call the metric view by name, by position or with defaults, and pass values from a dashboard through a filter widget. EXPLAIN shows the values as constants in the plan, and the errors above mark the rules to follow for defaults, date literals and materialization. Use parameters when callers need different versions of the same metric, and use dimensions when they only need slices.

Which scenario in your reports could become a parameter?

## References

- [Use parameters with metric views](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/use-parameters), Microsoft Learn
- [Metric view YAML reference](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/yaml-reference), Microsoft Learn
- [Query a metric view](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/query), Microsoft Learn
- [Materialization for metric views](https://learn.microsoft.com/en-us/azure/databricks/uc-semantics/metric-views/materialization), Microsoft Learn
- [Dashboard datasets](https://learn.microsoft.com/en-us/azure/databricks/dashboards/manage/data-modeling/datasets), Microsoft Learn
- [Dashboard parameters](https://learn.microsoft.com/en-us/azure/databricks/dashboards/manage/filters/parameters), Microsoft Learn
- [Azure Databricks release notes, November 2026](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november), Microsoft Learn

## Medium settings

- SEO title: Databricks Metric View Parameters: One Definition, Many Uses
- SEO description: same as the subtitle
- Slug: databricks-metric-view-parameters-one-definition-many-uses
- Tags: Databricks, Data Engineering, Semantic Layer, Business Intelligence, Unity Catalog
