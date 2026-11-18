# Test results

Run on November 18, 2026 on a serverless SQL warehouse, in a scratch schema that was dropped afterwards. These notes are not part of the article. The article is an explainer based on the documentation and claims no test result.

## Availability check

The statement from the docs was run unchanged apart from the table name.

```sql
CREATE TABLE release_lab.ecu_demo.documents_test (
  document_id BIGINT,
  description STRING
)
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported',
  'delta.enableRowTracking' = 'true',
  'delta.enableDeletionVectors' = 'true',
  'delta.columnMapping.mode' = 'id',
  'delta.enableColumnUpdates-preview' = 'true'
);
```

Result: the statement succeeded and no error was returned. `SHOW TBLPROPERTIES` listed `delta.enableColumnUpdates-preview = true`. `DESCRIBE DETAIL` showed reader version 3 and writer version 7, and the table features appendOnly, catalogManaged, columnMapping, deletionVectors, domainMetadata, inCommitTimestamp, invariants, rowTracking and vacuumProtocolCheck. No column-updates feature appeared in that list, before or after the backfill.

## Backfill example from the docs

5,000 rows were inserted in two batches (2,500 rows each, 8 files per batch). Then the docs example was run.

```sql
ALTER TABLE release_lab.ecu_demo.documents_test ADD COLUMN text_length INT;

UPDATE release_lab.ecu_demo.documents_test
SET text_length = LENGTH(description);
```

DESCRIBE HISTORY before the update:

| Version | Operation | Notes |
| --- | --- | --- |
| 0 | CREATE TABLE | |
| 1 | WRITE | 8 files, 2,500 rows |
| 2 | WRITE | 8 files, 2,500 rows |
| 3 | ADD COLUMNS | text_length INT |

DESCRIBE HISTORY after the update:

| Version | Operation | Metrics |
| --- | --- | --- |
| 4 | UPDATE | numUpdatedRows 5000, numRemovedFiles 16, numAddedFiles 1, numAddedBytes 30388, numRemovedBytes 88869, numCopiedRows 0 |

DESCRIBE DETAIL: 16 files and 88,869 bytes before, 1 file and 30,388 bytes after.

The values are correct: 5,000 of 5,000 rows have `text_length = LENGTH(description)`, with no nulls. The docs check query returned the expected rows.

## What this shows

- The property is accepted on this workspace and the data result is correct.
- The update removed all 16 data files and wrote one new file. That is the pattern of a standard update that rewrites files. Nothing in the history, the file counts or the feature list shows separate column files. The docs say Databricks can fall back to a standard update, and that the result is the same.
- I could not tell why the fallback happened. Possible reasons are that the preview is not turned on for this workspace (it has no Previews page), that the table is too small, or that the SQL warehouse does not use the feature. None of these was confirmed.
- No workaround was tried, as agreed.

## Not tested

- The rollback steps (`'delta.enableColumnUpdates-preview' = 'false'` and `REORG TABLE ... APPLY (PURGE)`).
- Enabling the feature on an existing table.
- MERGE, change data feed, UniForm and Lakeflow pipelines.
- A table with an embedding column, and a larger table.

## Retry on larger tables (November 18, 2026)

Two tables with the same schema (`document_id BIGINT`, `description STRING`, `embedding ARRAY<FLOAT>` with 128 floats), 100,000 rows each, loaded in four batches (32 data files each, about 46.5 MB). One had `delta.enableColumnUpdates-preview = true`, the other did not. Both got `ALTER TABLE ... ADD COLUMN text_length INT` and the docs `UPDATE`.

| Table | Files before | Files after | Removed | Added | Bytes added |
| --- | --- | --- | --- | --- | --- |
| ECU property set | 32 | 1 | 32 files, 46,563,571 bytes | 1 file | 46,441,235 |
| Property not set | 32 | 1 | 32 files, 46,563,253 bytes | 1 file | 46,440,953 |

Both updates rewrote the whole table. The ECU table behaved the same as the standard table: no sign of separate column files in DESCRIBE HISTORY, DESCRIBE DETAIL or the table feature list. The values were correct in both.

The same test was repeated on serverless notebook compute, which reports `dbr_version` 19.15.x (Runtime 19 or above, as the docs require). Result: 32 files removed, 1 added (46,440,939 bytes), 100,000 of 100,000 values correct, and no column-updates entry in the table features.

Conclusion: on this workspace the property is accepted, but Efficient Column Updates did not take effect on the SQL warehouse (DBSQL 2026.45) or on serverless compute with Runtime 19.15. The docs require an admin to turn on Efficient Column Updates on the Previews page, and this workspace has no Previews page, so the preview was most likely not enabled. That was not confirmed. No workaround was tried. The feature could not be demonstrated here, so the article claims no test result and uses no screenshots of results.

Test tables, the scratch schema and the probe notebook were removed afterwards.
