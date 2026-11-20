-- Test data for the dashboard guide
CREATE SCHEMA IF NOT EXISTS <catalog>.dash_demo;

CREATE OR REPLACE TABLE <catalog>.dash_demo.sales AS
SELECT
  id AS order_id,
  element_at(array('North','South','East','West'), CAST(id % 4 + 1 AS INT)) AS region,
  element_at(array('Laptop','Phone','Tablet'), CAST(id % 3 + 1 AS INT)) AS product,
  CAST(50 + (id * 37) % 450 AS INT) AS amount,
  date_add(DATE'2026-10-01', CAST(id % 30 AS INT)) AS order_date
FROM range(0, 200);
