-- Test 6: the near-zero series, version 2, without and with positive_only.
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t6_returns_default AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, returns FROM <catalog>.forecast_demo.returns_daily WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'returns',
  version => '2'
);

CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_t6_returns_positive AS
SELECT * FROM AI_FORECAST(
  TABLE(SELECT ds, returns FROM <catalog>.forecast_demo.returns_daily WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'returns',
  positive_only => TRUE,
  version => '2'
);
