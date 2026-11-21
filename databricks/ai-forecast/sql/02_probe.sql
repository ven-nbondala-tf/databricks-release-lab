-- Probe: a tiny version 2 forecast, then the same query without the version argument.
WITH t AS (
  SELECT date_add(DATE'2026-10-01', CAST(id AS INT)) AS ds,
         CAST(100 + id + 10 * (id % 7) AS DOUBLE) AS y
  FROM range(0, 30)
)
SELECT * FROM AI_FORECAST(
  TABLE(t),
  horizon => '2026-11-10',
  time_col => 'ds',
  value_col => 'y',
  version => '2'
);
