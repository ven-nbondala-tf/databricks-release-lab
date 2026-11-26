-- Part 2: parameters. discount is used in a measure, start_date in the YAML-level filter.
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
