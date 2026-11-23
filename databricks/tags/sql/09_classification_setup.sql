-- Data classification test copy, in a separate catalog so <catalog> is not scanned.
CREATE SCHEMA IF NOT EXISTS workspace.tags_class_demo;
CREATE OR REPLACE TABLE workspace.tags_class_demo.sales_orders AS
SELECT * FROM <catalog>.tags_demo.sales_orders;
