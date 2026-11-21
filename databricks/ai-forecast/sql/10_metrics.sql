-- Accuracy of each forecast on the 60 held-out days (2026-11-16 to 2027-01-14).
-- MAPE is the mean absolute percentage error, MAE the mean absolute error.
WITH forecasts AS (
  SELECT 'T1 version 1, defaults' AS test, ds, region, sales_forecast AS fc, sales_lower AS lo, sales_upper AS hi
  FROM <catalog>.forecast_demo.fc_t1_v1
  UNION ALL
  SELECT 'T2 version 2, defaults', ds, region, sales_forecast, sales_lower, sales_upper
  FROM <catalog>.forecast_demo.fc_t2_v2
  UNION ALL
  SELECT 'T3 version 2, holiday_region US', ds, region, sales_forecast, sales_lower, sales_upper
  FROM <catalog>.forecast_demo.fc_t3_v2_holidays
  UNION ALL
  SELECT 'T4 version 2, promo as future covariate', ds, region, sales_forecast, sales_lower, sales_upper
  FROM <catalog>.forecast_demo.fc_t4_v2_promo_future
  UNION ALL
  SELECT 'T5 version 2, promo as past-only covariate', ds, region, sales_forecast, sales_lower, sales_upper
  FROM <catalog>.forecast_demo.fc_t5_v2_promo_past
),
actuals AS (
  SELECT ds, region, sales FROM <catalog>.forecast_demo.sales_daily WHERE ds >= DATE'2026-11-16'
)
SELECT
  f.test,
  f.region,
  COUNT(*) AS days,
  ROUND(AVG(ABS(a.sales - f.fc) / a.sales) * 100, 2) AS mape_pct,
  ROUND(AVG(ABS(a.sales - f.fc)), 2) AS mae,
  ROUND(AVG(CASE WHEN a.sales BETWEEN f.lo AND f.hi THEN 1.0 ELSE 0.0 END) * 100, 1) AS inside_interval_pct
FROM forecasts f
JOIN actuals a USING (ds, region)
GROUP BY f.test, f.region
ORDER BY f.test, f.region;
