-- Part 1: a second metric view built on top of the first one.
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
