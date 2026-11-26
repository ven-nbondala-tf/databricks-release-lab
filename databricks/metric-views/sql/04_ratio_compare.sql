-- Part 1: group by nation only. Three answers: the regular view (average of the stored ratio),
-- the metric view, and the truth computed from the base tables.
WITH regular AS (
  SELECT nation, AVG(revenue_per_customer) AS regular_view
  FROM <catalog>.metric_demo.orders_ratio_view
  GROUP BY nation
),
metric AS (
  SELECT nation, MEASURE(revenue_per_customer) AS metric_view
  FROM <catalog>.metric_demo.orders_metrics
  GROUP BY nation
),
truth AS (
  SELECT n.n_name AS nation, SUM(o.o_totalprice) / COUNT(DISTINCT o.o_custkey) AS from_base_tables
  FROM samples.tpch.orders AS o
  JOIN samples.tpch.customer AS c ON o.o_custkey = c.c_custkey
  JOIN samples.tpch.nation AS n ON c.c_nationkey = n.n_nationkey
  GROUP BY n.n_name
)
SELECT nation,
       ROUND(regular_view, 2) AS regular_view,
       ROUND(metric_view, 2) AS metric_view,
       ROUND(from_base_tables, 2) AS from_base_tables
FROM regular JOIN metric USING (nation) JOIN truth USING (nation)
ORDER BY nation
LIMIT 8;
