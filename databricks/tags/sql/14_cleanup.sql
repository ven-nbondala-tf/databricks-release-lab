-- Cleanup for the tags demo. Replace <catalog> with your catalog.
DROP POLICY IF EXISTS small_orders_only ON SCHEMA <catalog>.tags_demo;
DROP SCHEMA IF EXISTS <catalog>.tags_demo CASCADE;
DROP SCHEMA IF EXISTS workspace.tags_class_demo CASCADE;

UNSET TAG ON CATALOG <catalog> team;

-- Governed tags (needs MANAGE on each tag). Dropping a governed tag leaves its assignments as ungoverned tags.
DROP GOVERNED TAG sensitivity;
DROP GOVERNED TAG amount_col;
