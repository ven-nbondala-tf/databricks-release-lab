-- Test 7: one call per region, to compare with the single grouped call in test 2.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t7_east AS
SELECT 'East' AS region, * FROM AI_FORECAST(
  TABLE(SELECT ds, sales FROM <catalog>.forecast_demo.sales_daily
        WHERE region = 'East' AND ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  version => '2'
);

CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t7_west AS
SELECT 'West' AS region, * FROM AI_FORECAST(
  TABLE(SELECT ds, sales FROM <catalog>.forecast_demo.sales_daily
        WHERE region = 'West' AND ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  version => '2'
);
