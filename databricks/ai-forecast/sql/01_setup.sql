-- Test data for the ai_forecast guide: two years of daily sales for two regions,
-- plus one small series that sits close to zero.
CREATE SCHEMA IF NOT EXISTS <catalog>.forecast_demo;

CREATE OR REPLACE TABLE <catalog>.forecast_demo.sales_daily AS
WITH days AS (
  SELECT date_add(DATE'2025-01-15', CAST(id AS INT)) AS ds, id AS i FROM range(0, 730)
),
regions AS (
  SELECT * FROM VALUES ('East', 200.0), ('West', 150.0) AS r(region, base)
),
x AS (
  SELECT
    d.ds, d.i, r.region, r.base,
    pmod(hash(d.ds, r.region), 100) < 15 AS promo_flag,
    (month(d.ds) = 11 AND dayofweek(d.ds) = 5 AND day(d.ds) BETWEEN 22 AND 28)
      OR (month(d.ds) = 12 AND day(d.ds) = 25)
      OR (month(d.ds) = 1 AND day(d.ds) = 1) AS is_holiday,
    dayofweek(d.ds) IN (1, 7) AS is_weekend,
    (pmod(hash(d.ds, r.region, 7), 1000) / 1000.0 - 0.5) * 0.10 AS noise
  FROM days d CROSS JOIN regions r
)
SELECT
  ds,
  region,
  ROUND(base * (1 + 0.001 * i) * IF(is_weekend, 1.25, 1.0) * IF(is_holiday, 0.45, 1.0)
        * IF(promo_flag, 1.30, 1.0) * (1 + noise), 2) AS sales,
  CAST(promo_flag AS INT) AS promo
FROM x;

CREATE OR REPLACE TABLE <catalog>.forecast_demo.returns_daily AS
WITH days AS (
  SELECT date_add(DATE'2025-01-15', CAST(id AS INT)) AS ds, id AS i FROM range(0, 730)
)
SELECT
  ds,
  GREATEST(0, ROUND(1.6 - 0.0021 * i
    + 0.8 * (pmod(hash(ds, 11), 1000) / 1000.0 - 0.5)
    + IF(dayofweek(ds) IN (1, 7), 0.25, 0), 2)) AS returns
FROM days;
