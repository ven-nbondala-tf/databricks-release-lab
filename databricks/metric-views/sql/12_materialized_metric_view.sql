-- Part 1: a metric view with materialization (aggregated materialized view by order year and status).
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
