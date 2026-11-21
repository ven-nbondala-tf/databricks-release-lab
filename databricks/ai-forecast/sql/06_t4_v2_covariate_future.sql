-- Test 4: version 2 with promo as a future covariate.
-- The history has sales. The forecast horizon rows have promo filled in and sales left NULL.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t4_v2_promo_future AS
SELECT * FROM AI_FORECAST(
  TABLE(
    SELECT ds, region, sales, promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds < DATE'2026-11-16'
    UNION ALL
    SELECT ds, region, CAST(NULL AS DOUBLE) AS sales, promo
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
