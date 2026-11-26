-- Part 1: a metric view with a one-to-many join (customer to orders). Used to test the documented restriction on query-time joins.
CREATE OR REPLACE VIEW <catalog>.metric_demo.customers_orders_metrics
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: samples.tpch.customer
joins:
  - name: orders
    source: samples.tpch.orders
    on: orders.o_custkey = source.c_custkey
    cardinality: one_to_many
dimensions:
  - name: customer_segment
    expr: c_mktsegment
  - name: nation_key
    expr: c_nationkey
measures:
  - name: customer_count
    expr: COUNT(DISTINCT c_custkey)
  - name: order_count
    expr: COUNT(orders.o_orderkey)
$$;
