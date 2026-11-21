-- Test 3: version 2 with US holidays.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t3_v2_holidays AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  holiday_region => 'US',
  version => '2'
);
