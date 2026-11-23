-- Part 1 setup: schema, sales_orders (fake email and phone) and a second table.
CREATE SCHEMA IF NOT EXISTS <catalog>.tags_demo;

CREATE OR REPLACE TABLE <catalog>.tags_demo.sales_orders (
  order_id INT,
  customer_name STRING,
  email STRING,
  phone STRING,
  amount DOUBLE
);

INSERT INTO <catalog>.tags_demo.sales_orders VALUES
  (1, 'Ava Stone',   'ava.stone@example.com',   '555-0101', 120.50),
  (2, 'Ben Rivera',  'ben.rivera@example.com',  '555-0102', 89.99),
  (3, 'Cara Nguyen', 'cara.nguyen@example.com', '555-0103', 240.00),
  (4, 'Dev Patel',   'dev.patel@example.com',   '555-0104', 15.25),
  (5, 'Eli Brooks',  'eli.brooks@example.com',  '555-0105', 310.10);

CREATE OR REPLACE TABLE <catalog>.tags_demo.customers (
  customer_id INT,
  region STRING
);

INSERT INTO <catalog>.tags_demo.customers VALUES (1, 'West'), (2, 'East'), (3, 'West');
