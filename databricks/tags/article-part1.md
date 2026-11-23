# Databricks Data Tags Explained: Regular, Governed, System

Subtitle: Databricks data tags label tables, columns and more in Unity Catalog. Learn regular, governed and system tags, and how to search and enforce them.

Databricks data tags label the objects in Unity Catalog so you can find, govern and protect your data, and they come in three kinds: regular, governed and system tags. A tag on a table never shows up in the bill, and a tag on compute never controls who sees data, because data tags and cost tags are two separate systems. This guide, part 1 of 2, covers data tags: how to apply them, search them, restrict their values and use them in access policies. The complete code for this guide is on GitHub: [tags](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/tags).

[VIDEO: YouTube link]
Caption: Data tags explained in a short video, part 1 of 2.

Part 2 covers cost tags: [Databricks Cost Tags Explained: Default, Custom, Serverless](PART2_LINK).

[image: data-vs-cost-tags.png | Caption: Data tags and cost tags are two separate systems. | Alt: A table comparing data tags and cost tags. It has four rows: what they label, who sets them, where you see them and what they are for.]

## What are data tags in Databricks

Data tags are attributes made of a key and an optional value, and you use them to organize and categorize securable objects in Unity Catalog. They also make tables and views easier to find with workspace search.

- Regular tags work on catalogs, schemas, tables, columns, volumes, views, functions and more.
- Governed tags are account-level tags with enforced rules: you define the allowed values and control who can assign them.
- System tags are governed tags that Databricks defines. You cannot modify or delete them, and their keys use reserved prefixes: `system.`, `class.`, `sap.` and `ai.`.
- You set tags with `SET TAG` and `UNSET TAG` in Databricks Runtime 16.1 and above, or in Catalog Explorer.
- Tag propagation, which copies governed tags to derived tables and views, is in Beta.

The diagram shows where each kind of tag goes and what uses it.

[image: data-tags-overview.png | Caption: Regular, governed and system tags, where they go and what uses them. | Alt: A flow diagram. Regular tags, system tags and governed tags go to catalogs, schemas, tables, columns and volumes. Governed tags also go to dashboards, notebooks, apps and Genie Agents. Search, access policies, propagation and data classification use them.]

## When to use data tags

Use regular tags for simple labels that help people find data, such as the owning team or a domain. Use governed tags when the values must stay consistent or when only some people should be allowed to assign the tag, and when an access policy depends on the tag. System tags are read-only, so you use them to read what Databricks has recorded, such as the `class.` tags that data classification applies.

Tags describe data, they do not enforce anything on their own. Access control comes from Unity Catalog permissions and from policies that use governed tags. If you want to attribute spend to a team, you need cost tags instead, which part 2 covers.

## Prerequisites

- Databricks Runtime 16.1 or above to use `SET TAG` and `UNSET TAG`. SQL warehouses and serverless compute work too.
- To tag an object, you own it, or you have `APPLY TAG` on the object plus `USE CATALOG` and `USE SCHEMA` on its parents.
- To assign a governed tag, you also need the `ASSIGN` permission on that tag.
- To create governed tags, you need `CREATE`. Account admins have it, and workspace admins have `CREATE` by default.
- To attach an access policy, you need `MANAGE` on the catalog, schema or table, or you own it, and `EXECUTE` on the function the policy uses.
- For tag propagation, a workspace admin turns on the Tag propagation preview from the Previews page, and you need `MANAGE` on the tag.

## Step 1: Create the demo tables

Create a schema with a table that has an email and a phone column, and a second table. The data is made up.

```sql
CREATE SCHEMA IF NOT EXISTS <catalog>.tags_demo;

CREATE OR REPLACE TABLE <catalog>.tags_demo.sales_orders (
  order_id INT,
  customer_name STRING,
  email STRING,
  phone STRING,
  amount DOUBLE
);

INSERT INTO <catalog>.tags_demo.sales_orders VALUES
  (1, 'Ava Stone',   'ava.stone@example.com',   '555-0101', 120.50),
  (2, 'Ben Rivera',  'ben.rivera@example.com',  '555-0102', 89.99),
  (3, 'Cara Nguyen', 'cara.nguyen@example.com', '555-0103', 240.00),
  (4, 'Dev Patel',   'dev.patel@example.com',   '555-0104', 15.25),
  (5, 'Eli Brooks',  'eli.brooks@example.com',  '555-0105', 310.10);

CREATE OR REPLACE TABLE <catalog>.tags_demo.customers (
  customer_id INT,
  region STRING
);
```

## Step 2: Set regular tags

Tags on a parent are shared with its children, so you set a tag at the highest level that makes sense. This example tags the catalog, the schema, the table and one column.

```sql
SET TAG ON CATALOG <catalog> team = data_platform;
SET TAG ON SCHEMA <catalog>.tags_demo domain = sales;
SET TAG ON TABLE <catalog>.tags_demo.sales_orders cost_center = hr;
SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.email pii = email;
```

Open the table in Catalog Explorer. The Tags section lists the tag set on the table, and the catalog and schema tags appear next to it with a dashed outline to show that they are inherited.

[image: 02-table-tags.png | Caption: The Tags section of the table. The dashed tags are inherited from the schema and the catalog. | Alt: The Policies and Tags sections of a table page. The Tags section shows cost_center hr with a solid outline, and domain sales and team data_platform with dashed outlines.]

## Step 3: Remove a tag

`UNSET TAG` takes the object and the tag key. Run it for the table tag and then read the tags again in Step 4.

```sql
UNSET TAG ON TABLE <catalog>.tags_demo.sales_orders cost_center;
```

## Step 4: Read tags with SQL

Unity Catalog has tag views in every catalog's `information_schema`: `catalog_tags`, `schema_tags`, `table_tags`, `column_tags` and `volume_tags`. The table tag view also holds tags on views.

```sql
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
```

After the `UNSET TAG` the result has the catalog tag `team`, the schema tag `domain` and the column tag `pii`, and the table tag `cost_center` is gone. The tag views only show rows for objects you can access.

## Step 5: Search by tag

Workspace search finds tables, views, volumes, functions, models, dashboards and Genie Agents by tag. Type `tag:<key>` or `tag:<key>:<value>` in the search bar. Set the table tag again and search for it.

```sql
SET TAG ON TABLE <catalog>.tags_demo.sales_orders cost_center = hr;
```

Searching for `tag:cost_center:hr` returns the table that carries the tag directly. Searching for the schema tag `tag:domain:sales` or the catalog tag `tag:team:data_platform` returns no tables, even though the table shows both as inherited. Catalogs, schemas and columns cannot be searched by tag.

[image: 05-search-by-tag.png | Caption: Searching for tag:cost_center:hr returns the table with that tag. | Alt: The workspace search results page for tag:cost_center:hr. One result, the sales_orders table in tags_demo, shows the tag cost_center hr.]

## Step 6: Create a governed tag

A governed tag defines the allowed values and records who may assign it. Creating one needs the `CREATE` permission.

```sql
CREATE GOVERNED TAG sensitivity
  DESCRIPTION 'Data sensitivity'
  VALUES ('high', 'low');

SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.email sensitivity = high;
```

Assigning a value that is not on the list fails, and the error names the allowed values.

```sql
SET TAG ON TABLE <catalog>.tags_demo.sales_orders sensitivity = medium;
```

```
[RequestId=<id> ErrorClass=INVALID_PARAMETER_VALUE.UC_TAG_POLICY_VALUE_NOT_ALLOWED] Tag value medium is not an allowed value for tag policy key sensitivity. Allowed values: [high, low].
```

[image: 06b-governed-tag-invalid-value-error.png | Caption: An invalid value for a governed tag fails with the allowed values in the message. | Alt: The SQL editor with a SET TAG statement and the error that the value medium is not an allowed value for the key sensitivity, with allowed values high and low.]

If you delete a governed tag, the tags stay on the objects but become ungoverned, which means anyone with `APPLY TAG` can then assign or change them.

## Step 7: Control who can assign a governed tag

Governed tag permissions are `CREATE`, `MANAGE` and `ASSIGN`. `CREATE` creates tags, `MANAGE` edits and deletes a tag and lets you delegate its permissions, and `ASSIGN` applies the tag to objects. `MANAGE` and `ASSIGN` can be granted for all governed tags in the account or for one tag, so you can let a team assign only the tags it needs.

In Catalog Explorer, open Govern, then Governed Tags, then the Account Permissions tab and choose Grant permissions. The permission list shows Create, Manage and Assign. Permission changes can take up to 30 seconds or longer to apply.

[image: 07-governed-tag-permissions.png | Caption: The Grant permissions dialog offers Create, Manage and Assign. | Alt: The Grant permissions dialog on the Governed Tags page. The permissions menu is open and lists Create, Manage and Assign with a short description of each.]

Governed tags are not limited to Unity Catalog objects. You can also put them on dashboards, notebooks, apps and Genie Agents, and you need `ASSIGN` on the tag plus edit access on the object.

## Step 8: Read system tags

System tags are governed tags that Databricks defines, and they appear next to your own. In the tag dialog, turn on Include system tags to see them in the key list. On the Governed Tags page, the System and User-Defined filters separate them from yours. Data classification, which scans tables and tags sensitive columns, applies system tags that start with `class.`, for example `class.email_address` and `class.us_ssn`.

The governed tags page in the Databricks documentation lists examples and the reserved prefixes, and the data classification page lists the `class.` tags, so link to those pages instead of copying a list.

## Step 9: Use a governed tag in an access policy

Attribute-based access control, ABAC, uses governed tags as attributes in policy conditions. This example sets a governed tag on the catalog and a second one on the `amount` column, then adds a row filter policy to the schema. The table has no `sensitivity` tag of its own, so the policy matches only through inheritance.

```sql
CREATE GOVERNED TAG amount_col DESCRIPTION 'Marks the order amount column';

SET TAG ON CATALOG <catalog> sensitivity = low;
SET TAG ON COLUMN <catalog>.tags_demo.sales_orders.amount amount_col;

CREATE OR REPLACE FUNCTION <catalog>.tags_demo.small_orders(amount DOUBLE)
  RETURNS BOOLEAN RETURN amount < 200;

CREATE OR REPLACE POLICY small_orders_only
ON SCHEMA <catalog>.tags_demo
COMMENT 'Show only orders under 200 on tables that inherit sensitivity = low'
ROW FILTER <catalog>.tags_demo.small_orders
TO `account users`
FOR TABLES
WHEN has_tag_value('sensitivity', 'low')
MATCH COLUMNS has_tag('amount_col') AS amt
USING COLUMNS (amt);
```

Tags set on a catalog or schema apply to the objects beneath them when policies are evaluated, but not to columns. In the test, `SELECT count(*) FROM <catalog>.tags_demo.sales_orders` returned 5 rows before the policy and 3 rows after it, the orders under 200. After `UNSET TAG ON CATALOG <catalog> sensitivity;` it returned 5 rows again right away.

ABAC runs on serverless compute, or on standard or dedicated compute with Databricks Runtime 16.4 or above.

## Step 10: Propagate a governed tag (Beta)

Tag propagation copies a governed tag from a source table or column to the tables and views you derive from it. It is off by default and you turn it on for each tag. Open the governed tag, find Tag propagation, choose Enable, switch it on and pick a default propagation value, which Databricks uses when sources disagree.

[image: 11a-configure-tag-propagation.png | Caption: Turning on tag propagation for a governed tag and choosing the default value. | Alt: The Configure tag propagation dialog with the toggle on and the default propagation value set to high.]

Then create a derived table and a view from the tagged table.

```sql
CREATE OR REPLACE TABLE <catalog>.tags_demo.orders_derived AS
SELECT order_id, email, amount FROM <catalog>.tags_demo.sales_orders;

CREATE OR REPLACE VIEW <catalog>.tags_demo.orders_view AS
SELECT order_id, email FROM <catalog>.tags_demo.sales_orders;
```

Both new objects had `sensitivity = high` on the `email` column when checked right after they were created. The `amount_col` tag, which did not have propagation turned on, did not appear on the new objects. Propagation runs on serverless compute or on classic compute with Databricks Runtime 19 or above, and it covers tables and views, not streaming tables or materialized views from Lakeflow Declarative Pipelines.

## Example: tag customer data and restrict what other users see

A team keeps orders in a shared catalog and wants other users to see only small orders. You tag the catalog and the `amount` column with governed tags, add the row filter policy from Step 9, and check the result with a count. After the policy, users in the account see the 3 orders under 200, and the owner of the policy can remove it with `DROP POLICY small_orders_only ON SCHEMA <catalog>.tags_demo;`.

The full example, including setup and cleanup, is in the [tags](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/tags) folder of the repository.

## Things to know

- Tag data is stored as plain text and may be replicated globally. Do not put personal or sensitive information in tag names or values.
- Regular tags and governed tags have different rules for allowed characters. Check the regular tags page and the governed tags page before you pick keys.
- Deleting a governed tag that a policy uses breaks queries. Every query on the object where the policy is attached fails with `INVALID_PARAMETER_VALUE.UC_ABAC_UNKNOWN_TAG_POLICY`, so remove the policy first.
- A new governed tag can take a moment before a policy can use it. The first `CREATE POLICY` right after `CREATE GOVERNED TAG` failed, and the same statement worked a minute later. Changes to tags can also take a few minutes to affect ABAC.
- The `UNSET TAG` page says a missing tag raises an exception. In testing, `UNSET TAG` on a tag that was already gone returned no error, so do not rely on an error to find missing tags.

## Best practices

- Use a governed tag for any tag that a policy depends on, so the values cannot drift.
- Set a tag on the catalog or schema when many tables share it, and on a column only when the column needs it.
- Grant `ASSIGN` for a single tag instead of for all governed tags.
- Describe each governed tag, and list its allowed values, so people know what to use.

## Summary

Data tags label Unity Catalog objects, and they come as regular tags for simple labels, governed tags with allowed values and permissions, and system tags that Databricks defines. The main point is that tags only describe data, and governed tags are what access policies and propagation use. Start with regular tags for discovery, and move to governed tags when a policy or a value list matters.

Which tag would you add to your tables first?

## References

- [Apply tags to Unity Catalog securable objects](https://learn.microsoft.com/en-us/azure/databricks/database-objects/tags), Microsoft Learn
- [Governed tags](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/), Microsoft Learn
- [Create and manage governed tags](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/manage-governed-tags), Microsoft Learn
- [Manage permissions on governed tags](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/manage-permissions), Microsoft Learn
- [Tag propagation](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/tag-propagation), Microsoft Learn
- [Data Classification](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/data-classification), Microsoft Learn
- [Supported classification tags](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/data-classification-tags), Microsoft Learn
- [Core concepts for attribute-based access control (ABAC)](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/abac/core-concepts), Microsoft Learn
- [SET TAG](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-set-tag), Microsoft Learn

## Medium settings

- SEO title: Databricks Data Tags Explained: Regular, Governed, System
- SEO description: same as the subtitle
- Slug: databricks-data-tags-regular-governed-system-tags
- Tags: Databricks, Data Engineering, Data Governance, Unity Catalog, SQL
