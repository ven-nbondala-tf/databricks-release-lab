-- Step 5: roll back to standard updates.

-- Stop writing new column files.
ALTER TABLE <catalog>.<schema>.documents SET TBLPROPERTIES (
  'delta.enableColumnUpdates-preview' = 'false'
);

-- Rewrite data files that have column files. The updated values are kept.
REORG TABLE <catalog>.<schema>.documents APPLY (PURGE);
