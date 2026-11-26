-- Part 1: the CTE pattern, for results that are already aggregated.
WITH orders AS (
  SELECT customer_key,
         MEASURE(order_count) AS order_count,
         MEASURE(total_revenue) AS total_revenue
  FROM <catalog>.metric_demo.orders_metrics
  GROUP BY customer_key
)
SELECT c.c_mktsegment,
       SUM(orders.order_count) AS order_count,
       SUM(orders.total_revenue) AS total_revenue
FROM orders
JOIN samples.tpch.customer AS c ON orders.customer_key = c.c_custkey
GROUP BY c.c_mktsegment
ORDER BY c.c_mktsegment;
