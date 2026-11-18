-- Step 3: enable Efficient Column Updates on an existing table.
-- The table must already use column mapping in id mode.

-- First, turn on the table features it depends on.
ALTER TABLE <catalog>.<schema>.documents SET TBLPROPERTIES (
  'delta.feature.catalogManaged' = 'supported',
  'delta.enableRowTracking' = 'true',
  'delta.enableDeletionVectors' = 'true'
);

-- Then enable Efficient Column Updates.
ALTER TABLE <catalog>.<schema>.documents SET TBLPROPERTIES (
  'delta.enableColumnUpdates-preview' = 'true'
);
