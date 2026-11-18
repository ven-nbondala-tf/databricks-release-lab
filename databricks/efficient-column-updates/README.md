# Efficient Column Updates in Databricks Delta Lake

Efficient Column Updates (ECU) lets Databricks backfill a new Delta Lake column without rewriting the unchanged columns of every affected data file. The new values go to separate column files, and queries still return one table. The feature is in Beta.

This folder holds the SQL used in the article. It is based on the official documentation: [Efficient column updates](https://learn.microsoft.com/en-us/azure/databricks/tables/features/efficient-column-updates).

## What it does

Adding a column only changes the table schema. Filling it can require rewriting the data files that hold the affected rows, including large columns such as text or embeddings that did not change. With ECU, the original files are kept and the new column values are written to separate Parquet files.

## Requirements

- A workspace admin turns on Efficient Column Updates on the Previews page.
- Databricks Runtime 19 or above to read from or write to the table.
- A Unity Catalog managed Delta Lake table with catalog commits enabled.
- Row tracking and deletion vectors enabled on the table.
- Column mapping in `id` mode, set when the table is created.

## How to run

Replace `<catalog>` and `<schema>` in the SQL files, then run them in this order.

| File | What it does |
| --- | --- |
| `sql/01_create_table.sql` | Creates a new table with ECU enabled |
| `sql/02_enable_on_existing_table.sql` | Enables ECU on an existing table that already uses column mapping in id mode |
| `sql/03_add_and_backfill.sql` | Adds `text_length` and backfills it with `UPDATE` |
| `sql/04_roll_back.sql` | Stops new column files and consolidates existing ones |

Use either the first or the second file to enable the feature, not both.

## Expected result

After the backfill, the check query returns each document with its `text_length`, and queries see one table. Enabling ECU does not guarantee that every `UPDATE` uses it. In some cases Databricks falls back to a standard update that rewrites the affected data files. The update still succeeds and returns the same results.

## Limitations

- `MERGE` does not use ECU.
- It is incompatible with write-time change data feed and with Universal Format (UniForm).
- Apache Iceberg managed tables and Lakeflow pipelines are not supported.
- `DROP FEATURE` cannot remove it. Databricks recommends avoiding it on critical tables.
- After a rollback the feature stays in the table protocol, so reads and writes still need Runtime 19 or above.

## Cleanup

Drop the table you created:

```sql
DROP TABLE <catalog>.<schema>.documents;
```

## Diagrams

- `diagrams/ecu-backfill.mmd` is the Mermaid source for the comparison of a backfill with and without ECU.
- `diagrams/ecu-when-to-use.html` is the source for the comparison table image.
