-- Part 2: materialization on a metric view that defines parameters. Expected to fail.
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_discount_materialized
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
  - name: order_year
    expr: year(o_orderdate)
measures:
  - name: discounted_revenue
    expr: SUM((1 - discount) * o_totalprice)
materialization:
  schedule: every 6 hours
  mode: relaxed
  materialized_views:
    - name: by_year
      type: aggregated
      dimensions:
        - order_year
      measures:
        - discounted_revenue
$$;
