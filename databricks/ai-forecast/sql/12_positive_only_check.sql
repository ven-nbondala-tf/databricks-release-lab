-- Test 6: do any forecasts for the near-zero series go negative?
SELECT 'without positive_only' AS run, COUNT(*) AS days,
       SUM(CASE WHEN returns_forecast < 0 THEN 1 ELSE 0 END) AS negative_forecasts,
       SUM(CASE WHEN returns_lower < 0 THEN 1 ELSE 0 END) AS negative_lower_bounds,
       ROUND(MIN(returns_forecast), 3) AS min_forecast, ROUND(MIN(returns_lower), 3) AS min_lower
FROM <catalog>.forecast_demo.fc_t6_returns_default
UNION ALL
SELECT 'with positive_only', COUNT(*),
       SUM(CASE WHEN returns_forecast < 0 THEN 1 ELSE 0 END),
       SUM(CASE WHEN returns_lower < 0 THEN 1 ELSE 0 END),
       ROUND(MIN(returns_forecast), 3), ROUND(MIN(returns_lower), 3)
FROM <catalog>.forecast_demo.fc_t6_returns_positive;
