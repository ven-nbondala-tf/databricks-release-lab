-- Step 4: add a column and backfill it.
ALTER TABLE <catalog>.<schema>.documents ADD COLUMN text_length INT;

UPDATE <catalog>.<schema>.documents
SET text_length = LENGTH(description);

-- Check the result.
SELECT document_id, description, text_length
FROM <catalog>.<schema>.documents
LIMIT 10;
