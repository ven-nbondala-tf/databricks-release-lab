-- Step 2: create a new table with Efficient Column Updates enabled.
-- column mapping in id mode must be set here, at creation.
CREATE TABLE <catalog>.<schema>.documents (
  document_id BIGINT,
  description STRING,
  embedding ARRAY<FLOAT>
)
TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported',
  'delta.enableRowTracking' = 'true',
  'delta.enableDeletionVectors' = 'true',
  'delta.columnMapping.mode' = 'id',
  'delta.enableColumnUpdates-preview' = 'true'
);
