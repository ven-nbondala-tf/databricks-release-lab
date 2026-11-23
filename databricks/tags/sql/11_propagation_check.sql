SELECT table_name, column_name, tag_name, tag_value
FROM <catalog>.information_schema.column_tags
WHERE schema_name = 'tags_demo' AND tag_name = 'sensitivity'
ORDER BY table_name, column_name;
