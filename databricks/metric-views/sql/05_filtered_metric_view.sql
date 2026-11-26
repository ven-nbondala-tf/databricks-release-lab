-- Part 1: a YAML-level filter. It applies to every query on this metric view.
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
