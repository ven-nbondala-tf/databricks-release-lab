-- Test 5: version 2 with promo as a past-only covariate (no rows for the horizon).
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t5_v2_promo_past AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales, promo
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  covariate_col => 'promo',
  version => '2'
);
