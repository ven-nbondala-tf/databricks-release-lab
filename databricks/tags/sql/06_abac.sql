-- ABAC: a row filter policy driven by a governed tag set on the CATALOG.
-- The table has no sensitivity tag of its own, so the policy only matches through inheritance.
CREATE GOVERNED TAG amount_col DESCRIPTION 'Marks the order amount column';

SET TAG ON CATALOG <catalog> sensitivity = low;
SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.amount amount_col;

CREATE OR REPLACE FUNCTION <catalog>.tags_demo.small_orders(amount DOUBLE)
  RETURNS BOOLEAN RETURN amount < 200;

CREATE OR REPLACE POLICY small_orders_only
ON SCHEMA <catalog>.tags_demo
COMMENT 'Show only orders under 200 on tables that inherit sensitivity = low'
ROW FILTER <catalog>.tags_demo.small_orders
TO `account users`
FOR TABLES
WHEN has_tag_value('sensitivity', 'low')
MATCH COLUMNS has_tag('amount_col') AS amt
USING COLUMNS (amt);
