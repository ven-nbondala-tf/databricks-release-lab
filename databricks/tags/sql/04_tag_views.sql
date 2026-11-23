SELECT 'catalog' AS level, catalog_name, NULL AS schema_name, NULL AS object_name, tag_name, tag_value
FROM <catalog>.information_schema.catalog_tags WHERE catalog_name = '<catalog>'
UNION ALL
SELECT 'schema', catalog_name, schema_name, NULL, tag_name, tag_value
FROM <catalog>.information_schema.schema_tags WHERE schema_name = 'tags_demo'
UNION ALL
SELECT 'table', catalog_name, schema_name, table_name, tag_name, tag_value
FROM <catalog>.information_schema.table_tags WHERE schema_name = 'tags_demo'
UNION ALL
SELECT 'column', catalog_name, schema_name, concat(table_name, '.', column_name), tag_name, tag_value
FROM <catalog>.information_schema.column_tags WHERE schema_name = 'tags_demo';
