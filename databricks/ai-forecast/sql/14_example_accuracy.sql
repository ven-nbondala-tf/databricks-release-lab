-- Example: forecast with planned promotions, then compare it with the held-out actuals.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_promo AS
SELECT * FROM AI_FORECAST(
  TABLE(
    SELECT ds, region, sales, promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds < DATE'2026-11-16'
    UNION ALL
    SELECT ds, region, CAST(NULL AS DOUBLE), promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds >= DATE'2026-11-16'
  ),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  covariate_col => 'promo',
  version => '2'
);

SELECT f.region,
       ROUND(AVG(ABS(f.sales_forecast - a.sales)), 2) AS mae
FROM <catalog>.forecast_demo.fc_promo f
JOIN <catalog>.forecast_demo.sales_daily a
  ON f.ds = a.ds AND f.region = a.region
GROUP BY f.region;
