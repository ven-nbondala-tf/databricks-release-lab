# Databricks tags: data tags and cost tags

Working code and test notes for two articles:

- Part 1: Databricks Data Tags Explained: Regular, Governed, System
- Part 2: Databricks Cost Tags Explained: Default, Custom, Serverless

Data tags label Unity Catalog objects. Cost tags attribute compute spend. They are two separate systems: a tag on a table never shows up in the bill, and a tag on compute never controls who sees data.

The facts in the articles come from the Azure Databricks documentation, listed in `notes/facts.md`, and were confirmed with the tests in `tests/results.md`. The article drafts are `article-part1.md` and `article-part2.md`.

## Prerequisites

- A catalog where you can create schemas, and a SQL warehouse (serverless or pro).
- Databricks Runtime 16.1 or above, or a SQL warehouse, for `SET TAG` and `UNSET TAG`.
- For governed tags: the `CREATE` permission on governed tags (account admins have it, workspace admins have it by default).
- For the access policy: `MANAGE` on the schema, and `EXECUTE` on the function.
- For tag propagation: the Tag propagation preview turned on by a workspace admin, and `MANAGE` on the tag.
- For Part 2: permission to create a job, and read access to `system.billing.usage`. Serverless usage policies need a workspace admin.
- Databricks CLI 1.24.0 or above for the job commands.

## Setup

Replace `<catalog>` in the SQL files with your catalog name, then run `sql/01_setup.sql`. It creates the schema `tags_demo`, the table `sales_orders` (made-up email and phone values) and the table `customers`.

## How to run

Run the files in order. Each one matches a step in the articles.

| File | What it does |
| --- | --- |
| `sql/01_setup.sql` | Creates the schema and the demo tables |
| `sql/02_set_tags.sql` | Sets regular tags on the catalog, schema, table and a column |
| `sql/03_unset_tag.sql` | Removes the table tag |
| `sql/04_tag_views.sql` | Reads the tags from the `information_schema` tag views |
| `sql/05_governed_tag.sql` | Creates a governed tag, assigns a valid value and tries an invalid one |
| `sql/06_abac.sql` | Sets governed tags and creates a row filter policy |
| `sql/07_abac_check.sql` | Counts the rows you can see |
| `sql/08_abac_cleanup.sql` | Drops the policy |
| `sql/09_classification_setup.sql` | A copy of the table for a data classification test |
| `sql/10_propagation.sql` | Creates a derived table and a view from the tagged table |
| `sql/11_propagation_check.sql` | Shows the tags on the derived objects |
| `sql/12_billing_custom_tags.sql` | Groups `system.billing.usage` by a custom tag |
| `sql/13_table_tags_not_in_billing.sql` | Lists the keys in `custom_tags` |
| `sql/14_cleanup.sql` | Removes the demo objects |

For propagation, open the governed tag `sensitivity` in Catalog Explorer under Govern, then Governed Tags. Choose Enable under Tag propagation, switch it on and pick a default value before you run `sql/10_propagation.sql`.

For Part 2, create a job with custom tags. `src/tags_notebook.py` is a small notebook for it. Replace the notebook path and run:

```bash
databricks api post /api/2.2/jobs/create --json '{
  "name": "tags-demo-job",
  "tags": {"team": "data_platform", "project": "tags_demo"},
  "tasks": [{"task_key": "run", "notebook_task": {"notebook_path": "<notebook path>"}}]
}'
databricks api post /api/2.2/jobs/run-now --json '{"job_id": <job id>}'
```

## Expected result

- After `sql/02_set_tags.sql`, `sql/04_tag_views.sql` returns one row for each tag.
- The invalid value in `sql/05_governed_tag.sql` fails with `UC_TAG_POLICY_VALUE_NOT_ALLOWED` and the message lists the allowed values `high` and `low`.
- `sql/07_abac_check.sql` returns 5 rows before the policy and 3 rows after it, and 5 again once the catalog tag is removed.
- `sql/11_propagation_check.sql` shows `sensitivity = high` on the `email` column of the derived table and the view.
- A job tag named `Vendor` is rejected with `Invalid tags - the following custom keys conflict with the keys of Databricks default tags: Vendor.`
- Usage records for a new job can take several hours to appear in `system.billing.usage`.

## Cleanup

Run `sql/14_cleanup.sql`, then delete the job and the notebook:

```bash
databricks jobs delete <job id>
databricks workspace delete <notebook path>
```

## Diagrams

- `diagrams/data-tags-overview.mmd` and `.png`: where the three kinds of data tags go and what uses them.
- `diagrams/cost-tags-overview.mmd` and `.png`: default, custom and usage policy tags, and where they end up.
- `diagrams/data-vs-cost-tags.html` and `.png`: the comparison table, shared by both articles.
- `diagrams/linkedin-image-part1.html` and `linkedin-image-part2.html`: the LinkedIn images.

## References

- [Apply tags to Unity Catalog securable objects](https://learn.microsoft.com/en-us/azure/databricks/database-objects/tags)
- [Governed tags](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/)
- [Tag propagation](https://learn.microsoft.com/en-us/azure/databricks/admin/governed-tags/tag-propagation)
- [Use tags to attribute and track usage](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/usage-detail-tags)
- [Attribute usage with serverless usage policies](https://learn.microsoft.com/en-us/azure/databricks/admin/usage/budget-policies)
- [Billable usage system table reference](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing)
