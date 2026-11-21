-- Do the forecasts predict the holiday dips? Compare forecast and actual on the three holidays.
WITH forecasts AS (
  SELECT 'T1 version 1' AS test, ds, region, sales_forecast AS fc FROM <catalog>.forecast_demo.fc_t1_v1
  UNION ALL SELECT 'T2 version 2', ds, region, sales_forecast FROM <catalog>.forecast_demo.fc_t2_v2
  UNION ALL SELECT 'T3 version 2 + US holidays', ds, region, sales_forecast FROM <catalog>.forecast_demo.fc_t3_v2_holidays
)
SELECT
  f.test, f.region, f.ds,
  ROUND(a.sales, 1) AS actual,
  ROUND(f.fc, 1) AS forecast,
  ROUND(f.fc / a.sales, 2) AS forecast_over_actual
FROM forecasts f
JOIN <catalog>.forecast_demo.sales_daily a USING (ds, region)
WHERE f.ds IN (DATE'2026-11-26', DATE'2026-12-25', DATE'2027-01-01')
ORDER BY f.region, f.ds, f.test;
