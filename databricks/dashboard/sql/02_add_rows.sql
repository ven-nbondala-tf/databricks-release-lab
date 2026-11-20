-- Stand-in for a pipeline run: new North rows.
INSERT INTO <catalog>.dash_demo.sales
SELECT 1000 + id, 'North', 'Laptop', 1000, DATE'2026-11-20' FROM range(0, 10);

-- A second batch for the scheduled run: new West rows.
INSERT INTO <catalog>.dash_demo.sales
SELECT 2000 + id, 'West', 'Phone', 2000, DATE'2026-11-20' FROM range(0, 5);
