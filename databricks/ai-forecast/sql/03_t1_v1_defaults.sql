-- Test 1: version 1 with defaults. Forecast the 60 held-out days (2026-11-16 to 2027-01-14).
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t1_v1 AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region'
);
