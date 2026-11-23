-- Propagation: sensitivity is set on sales_orders.email. Create a derived table and a view, then look at their tags.
CREATE OR REPLACE TABLE <catalog>.tags_demo.orders_derived AS
SELECT order_id, email, amount FROM <catalog>.tags_demo.sales_orders;

CREATE OR REPLACE VIEW <catalog>.tags_demo.orders_view AS
SELECT order_id, email FROM <catalog>.tags_demo.sales_orders;
