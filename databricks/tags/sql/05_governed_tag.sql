-- Governed tag with allowed values, then a valid and an invalid assignment.
CREATE GOVERNED TAG sensitivity DESCRIPTION 'Data sensitivity' VALUES ('high', 'low');

SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.email sensitivity = high;

-- Invalid value: not in the allowed list. Expected to fail.
SET TAG ON TABLE <catalog>.tags_demo.sales_orders sensitivity = medium;
