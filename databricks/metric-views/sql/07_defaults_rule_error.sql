-- Part 2: a parameter with a default followed by one without. Expected to fail.
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_bad_defaults
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: samples.tpch.orders
parameters:
  - name: discount
    data_type: double
    default: 0
  - name: start_date
    data_type: date
dimensions:
  - name: order_priority
    expr: o_orderpriority
measures:
  - name: discounted_revenue
    expr: SUM((1 - discount) * o_totalprice)
$$;
