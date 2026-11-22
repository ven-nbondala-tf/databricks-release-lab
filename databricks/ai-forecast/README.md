# Forecast in Databricks SQL with ai_forecast

Article: [How to Forecast in Databricks SQL with ai_forecast](https://medium.com/@nagarajubru/how-to-forecast-databricks-sql-ai-forecast-f3dc5d7769d8)

Working code for the guide "How to Forecast in Databricks SQL with ai_forecast". It forecasts two years of generated daily sales with `ai_forecast` version 2, and compares version 1, version 2, holidays, covariates and `positive_only` on a 60 day held-out window.

## Prerequisites

- A Pro or Serverless SQL warehouse (AI Functions are not available on Classic SQL warehouses).
- Permission to create a schema in a Unity Catalog catalog.
- For some workspaces, including those with the compliance security profile, a workspace admin turns on "AI Forecast V2" on the Previews page.

## Setup

Replace `<catalog>` with your catalog name in every file in `sql/`, then run `01_setup.sql`. It creates the schema `forecast_demo`, the table `sales_daily` (730 days for two regions, with trend, weekly pattern, holiday dips and a promo flag) and the table `returns_daily` (a series that trends close to zero).

## How to run

Run the files in order. Each one matches a step or test in the article.

| File | What it does |
| --- | --- |
| `01_setup.sql` | Creates the schema and the test data |
| `02_probe.sql` | A tiny version 2 forecast to confirm it works on your warehouse |
| `03_t1_v1_defaults.sql` | Version 1 with defaults |
| `04_t2_v2_defaults.sql` | Version 2 with defaults |
| `05_t3_v2_holidays.sql` | Version 2 with `holiday_region => 'US'` |
| `06_t4_v2_covariate_future.sql` | Version 2 with promo as a future covariate |
| `07_t5_v2_covariate_past_only.sql` | Version 2 with promo as a past-only covariate |
| `08_t6_positive_only.sql` | The near-zero series without and with `positive_only` |
| `09_t7_grouping.sql` | One call per region, for comparison with `group_col` |
| `10_metrics.sql` | MAPE, MAE and interval coverage per forecast and region |
| `11_holiday_check.sql` | Forecast against actual on Thanksgiving, Christmas and New Year |
| `12_positive_only_check.sql` | Negative values and lower bounds with and without `positive_only` |
| `13_grouping_check.sql` | Grouped call against per-region calls |
| `14_example_accuracy.sql` | The promo forecast saved as a table, and its MAE per region |

## Expected result

Each forecast table holds 60 rows per region (2026-11-16 to 2027-01-14). `10_metrics.sql` returns these mean absolute errors:

| Forecast | East MAE | West MAE |
| --- | --- | --- |
| Version 1, defaults | 40.38 | 33.17 |
| Version 2, defaults | 36.94 | 32.53 |
| Version 2, holiday_region US | 33.77 | 31.29 |
| Version 2, promo as a future covariate | 21.74 | 16.68 |
| Version 2, promo as a past-only covariate | 37.67 | 32.75 |

The test data is generated with a fixed rule, so the values repeat on every run of the setup script. Forecast values can differ slightly between runs of the service.

## Cleanup

Run `15_cleanup.sql`. It drops the schema `forecast_demo` and every table in it.

## Diagrams

`diagrams/` holds the Mermaid source of the flow diagram, the two charts and the images used in the article.

## References

- [ai_forecast function](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/ai_forecast)
- [Transform unstructured data using AI Functions](https://learn.microsoft.com/en-us/azure/databricks/large-language-models/ai-functions)
- [November 2026 release notes](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november)
