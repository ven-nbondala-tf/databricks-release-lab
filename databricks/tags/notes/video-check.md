# Video check

Both videos checked against the Azure Databricks docs on 2026-11-22. Items that need a fix in a video are marked CORRECT THE VIDEO.

## Needs fixing in the videos

1. **Part 1, item 5 (system tag prefixes): CORRECT THE VIDEO.** The docs list four reserved prefixes: `system.`, `class.`, `sap.` and `ai.`. The video names three and leaves out `ai.`. Source: governed tags page (admin/governed-tags/). I checked the sentence myself: "System tags use reserved prefixes like system., class., sap., and ai.".
2. **Part 2, item 6 (x_ prefix): CONFIRMED WITH A LIMIT, say it carefully.** The x_ prefix is added to workspace, cluster and pool tags during propagation when the key matches a default tag. A tag added through a compute policy is not renamed: the cluster or pool fails with an invalid settings error. If the video says every custom tag with a default key gets x_, add the compute policy exception.
3. **Part 2, item 4 (custom_tags column): CONFIRMED FOR custom AND usage policy TAGS ONLY.** No page says default tags appear in `custom_tags`. Do not say they do.

## Item by item

| # | Statement | Verdict |
| --- | --- | --- |
| 1 | Default tags include Vendor, ClusterId and Creator, and SQL warehouses get SqlEndpointId | CONFIRMED. Also ClusterName, RunName and JobId for jobs compute. Serverless has no default tag keys listed, only usage policy tags (NOT FOUND). |
| 2 | Budgets can be filtered by a tag | CONFIRMED. The budget Resource tags section scopes a budget to custom tags. Custom tags only, not default tags. No release status stated for tag scoping. |
| 3 | Tags on compute appear in Azure cost analysis | CONFIRMED. Default tags propagate, workspace, pool and cluster custom tags become Azure VM resource tags, usage policy tags also propagate. Exception: cluster tags of pool-backed clusters do not reach VMs. No delay stated. |
| 4 | Custom and usage policy tags appear in custom_tags | CONFIRMED for those two kinds. Default tags in that column: NOT FOUND. |
| 5 | System tags use system., class., sap. and class tags come from data classification | CORRECTED, see above. The class tags statement is CONFIRMED. |
| 6 | A custom tag with a default tag's key gets an x_ prefix | CONFIRMED with the compute policy exception, see above. |
| 7 | Propagation is Beta, on serverless and on classic compute with Databricks Runtime 19 and above | CONFIRMED. Also needs a workspace admin to turn on the Tag propagation preview and per-tag enablement. |
| 8 | Dashboards, notebooks, apps and Genie Agents can carry governed tags | CONFIRMED. No release status stated. |

## Other things the docs say that the videos may want to reflect

- Serverless usage policies are in Public Preview. The page title says "usage policies" and the URL still says budget-policies. The `budget_policy_id` column is marked deprecated in favor of `usage_policy_id`.
- Budget threshold webhooks are in Beta.
- `system.billing.usage` freshness differs between two pages: "updates every few hours" on the budgets page and "typically available within 12 hours" on the billing table page.
- Governed tags and Data Classification themselves have no GA or Preview label in the docs (NOT FOUND).
- Tag search: the tags page says a search returns a tagged catalog plus the schemas and tables beneath it, the search page says catalogs, schemas and columns cannot be searched by tag. The test (item 5) will show which is right.
