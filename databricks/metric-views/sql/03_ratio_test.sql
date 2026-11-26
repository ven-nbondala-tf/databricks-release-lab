-- Part 1: a regular view with the ratio precomputed per year and nation.
CREATE OR REPLACE VIEW <catalog>.metric_demo.orders_ratio_view AS
SELECT
  year(o.o_orderdate) AS order_year,
  n.n_name AS nation,
  SUM(o.o_totalprice) / COUNT(DISTINCT o.o_custkey) AS revenue_per_customer
FROM samples.tpch.orders AS o
JOIN samples.tpch.customer AS c ON o.o_custkey = c.c_custkey
JOIN samples.tpch.nation AS n ON c.c_nationkey = n.n_nationkey
GROUP BY year(o.o_orderdate), n.n_name;
