-- Part 1: one metric view over TPC-H orders, with a snowflake join (orders, customer, nation).
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
