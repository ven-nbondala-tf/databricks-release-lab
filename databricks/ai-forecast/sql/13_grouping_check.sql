-- Test 7: is one grouped call the same as one call per region?
SELECT
  g.region,
  COUNT(*) AS days,
  ROUND(MAX(ABS(g.sales_forecast - p.sales_forecast)), 6) AS max_abs_difference
FROM <catalog>.forecast_demo.fc_t2_v2 g
JOIN (
  SELECT * FROM <catalog>.forecast_demo.fc_t7_east
  UNION ALL
  SELECT * FROM <catalog>.forecast_demo.fc_t7_west
) p USING (ds, region)
GROUP BY g.region
ORDER BY g.region;
