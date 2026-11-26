-- Removes everything the guide creates. The materialized metric view owns a pipeline that is dropped with it.
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_materialized;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_discount;
DROP VIEW IF EXISTS <catalog>.metric_demo.customers_orders_metrics;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_metrics_by_year;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_metrics_rely;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_since_1996;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_ratio_view;
DROP VIEW IF EXISTS <catalog>.metric_demo.orders_metrics;
DROP VIEW IF EXISTS <catalog>.metric_demo.probe_metrics;
DROP SCHEMA IF EXISTS <catalog>.metric_demo CASCADE;
