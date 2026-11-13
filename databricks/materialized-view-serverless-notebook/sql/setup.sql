-- Run once in the SQL editor. Change release_lab to your own catalog.

CREATE SCHEMA IF NOT EXISTS release_lab.mvst_demo;

-- The source table comes from the job-completion-triggers folder.
-- This fails with a clear message if the table is missing or empty.
SELECT assert_true(COUNT(*) > 0, 'release_lab.jct_demo.bronze_orders is missing or empty') AS source_ok
FROM release_lab.jct_demo.bronze_orders;
