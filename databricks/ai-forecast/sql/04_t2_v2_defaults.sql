-- Test 2: version 2 with defaults.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t2_v2 AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  version => '2'
);
