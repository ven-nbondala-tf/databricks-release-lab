-- Run once in the SQL editor. Change release_lab to your own catalog.

CREATE SCHEMA IF NOT EXISTS release_lab.ops;
CREATE SCHEMA IF NOT EXISTS release_lab.failure_demo;

-- Where the investigator writes its reports
CREATE TABLE IF NOT EXISTS release_lab.ops.incident_reports (
  job_id        STRING,
  run_id        STRING,
  failed_task   STRING,
  error_summary STRING,
  root_cause    STRING,
  evidence      STRING,
  suggested_fix STRING,
  confidence    STRING,
  created_at    TIMESTAMP
);

-- Source data for the demo job
CREATE OR REPLACE TABLE release_lab.failure_demo.customers (
  customer_id STRING,
  name        STRING,
  region      STRING
);

INSERT INTO release_lab.failure_demo.customers VALUES
  ('C-1001', 'Asha', 'west'),
  ('C-1002', 'Ben', 'east'),
  ('C-1003', 'Chen', 'west'),
  ('C-1004', 'Dina', 'north');

CREATE OR REPLACE TABLE release_lab.failure_demo.orders_raw (
  order_id    INT,
  customer_id STRING,
  amount      DOUBLE,
  order_date  DATE
) TBLPROPERTIES (
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5'
);

INSERT INTO release_lab.failure_demo.orders_raw VALUES
  (1, 'C-1001', 120.50, DATE'2026-11-10'),
  (2, 'C-1002', 80.00, DATE'2026-11-10'),
  (3, 'C-1003', 45.25, DATE'2026-11-11'),
  (4, 'C-1004', 210.00, DATE'2026-11-11');

-- An upstream team renamed this column. The history keeps the evidence.
ALTER TABLE release_lab.failure_demo.orders_raw RENAME COLUMN amount TO order_amount;
