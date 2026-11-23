-- Regular tags on the catalog, schema, table and the email column.
SET TAG ON CATALOG <catalog> team = data_platform;
SET TAG ON SCHEMA <catalog>.tags_demo domain = sales;
SET TAG ON TABLE <catalog>.tags_demo.sales_orders cost_center = hr;
SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.email pii = email;
