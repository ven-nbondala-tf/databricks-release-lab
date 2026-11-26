-- Part 1: a query-time join (Beta). Join on a field of the metric view and wrap each measure in MEASURE().
SELECT c.c_mktsegment,
       MEASURE(o.order_count) AS order_count,
       MEASURE(o.total_revenue) AS total_revenue
FROM <catalog>.metric_demo.orders_metrics AS o
JOIN samples.tpch.customer AS c ON o.customer_key = c.c_custkey
GROUP BY c.c_mktsegment
ORDER BY c.c_mktsegment;
