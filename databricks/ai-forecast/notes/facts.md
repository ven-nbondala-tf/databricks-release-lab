# Fact sheet: ai_forecast version 2

Checked on November 21, 2026 against Azure Databricks documentation on learn.microsoft.com only. One line per claim. Status: CONFIRMED, NOT FOUND (no official wording found, so it stays out of the article unless marked as a test observation), or DIFFERS (two official pages say different things, both recorded).

Base URL: A = https://learn.microsoft.com/en-us/azure/databricks/

| Page | Title | ms.date |
| --- | --- | --- |
| A sql/language-manual/functions/ai_forecast | ai_forecast function | 2026-11-18 |
| A large-language-models/ai-functions | Transform unstructured data using AI Functions | 2026-11-20 |
| A release-notes/product/2026/november | November 2026 release notes | 2026-11-20 |

## Status and release notes

| Claim | Status | Source |
| --- | --- | --- |
| "Version 2 of the `ai_forecast` function is now generally available in Databricks SQL." Entry heading: "`ai_forecast` version 2 is now generally available", dated November 18, 2026. | CONFIRMED | A release-notes/product/2026/november |
| The release note adds that a research-optimized time series foundation model powers version 2, which adds built-in holiday support, external covariates, and non-negative forecasts. It names no warehouse type, region, runtime or preview setting. | CONFIRMED | A release-notes/product/2026/november |
| The function page: "Version 2 is generally available." Version 1 "is in Public Preview" and is HIPAA compliant. | CONFIRMED | A sql/language-manual/functions/ai_forecast |
| The release note gives no requirements; the function page does: "Pro or Serverless SQL warehouse", and for some workspaces, including those with the compliance security profile, a workspace admin must turn on "AI Forecast V2" from the Previews page. | DIFFERS. Both are recorded. The release note is silent, the function page adds the requirements. | both pages |
| "AI Functions are not available on Classic SQL warehouses." | CONFIRMED | A large-language-models/ai-functions |
| Databricks Runtime for ai_forecast specifically. | NOT FOUND. The overview names Runtime 15.4 LTS or above for AI Functions in general. A November 5, 2026 entry says the upcoming removal of AI Functions support on older runtimes "doesn't affect `ai_forecast`". That entry was in the summarized part of the page, not read verbatim. | A large-language-models/ai-functions; A release-notes/product/2026/november |
| Regions, Unity Catalog permissions, minimum history, maximum rows, timeout. | NOT FOUND | |
| Cost: AI Functions such as ai_forecast run "entirely on the compute you submit them from, with no separate inference cost." | CONFIRMED | A large-language-models/ai-functions |

## Versions

| Claim | Status | Source |
| --- | --- | --- |
| Allowed values of `version` are '1' and '2'. "If unspecified, defaults to version 1." | CONFIRMED | A sql/language-manual/functions/ai_forecast |
| "Azure Databricks recommends version 2 for most use cases." | CONFIRMED | same |
| Version 1 uses "a prophet-like piecewise linear and seasonality model". Version 2 uses "a time series foundation model". | CONFIRMED | same |
| "Version 1 is on a deprecation path. In an upcoming release, the default version changes to version 2." To keep version 1 behavior, pass `version => '1'`. | CONFIRMED | same |
| "The version 2 arguments (covariate_col, holiday_region, positive_only) require version => '2'." Version 1 also has `seed` and `parameters`, which the version 2 syntax omits. | CONFIRMED | same |

## Signature and arguments

Version 2 syntax, as written on the page:

```
ai_forecast(observed, horizon, time_col, value_col
  [, group_col] [, covariate_col] [, prediction_interval_width]
  [, frequency] [, holiday_region] [, positive_only] [, version])
```

| Claim | Status | Source |
| --- | --- | --- |
| `observed` is the table-valued input. `horizon` is a "timestamp-castable quantity". `time_col` must be DATE or TIMESTAMP. `value_col` is a string or array of strings, castable to DOUBLE. | CONFIRMED | A sql/language-manual/functions/ai_forecast |
| `group_col`: forecasts are generated "for each group independently". Without it, the whole input is one group. | CONFIRMED | same |
| `value_col` can hold up to 100 metrics within each group. | CONFIRMED | same |
| `covariate_col`: string or array of strings naming columns in `observed`. Future and past-only covariates are supported. | CONFIRMED | same |
| `holiday_region`: "a region code that enables automatic modeling of holiday effects for that region, such as 'US'." The full list of codes is not on the page. Default: no holiday effects. | CONFIRMED. List of codes NOT FOUND. | same |
| `positive_only`: constrains forecasts to non-negative values. "Default is FALSE." | CONFIRMED | same |
| `prediction_interval_width`: "a value between 0 and 1". Forecasted values have that probability of falling between the upper and lower columns. The default is not stated. | CONFIRMED. Default NOT FOUND. | same |
| `frequency`: a pandas offset alias such as 'D', 'W', 'ME', 'H'. In version 2 it "must match the inferred granularity of the input data within each group." | CONFIRMED | same |
| "The inferred frequency within a group is the mode of the most recent observations." | CONFIRMED | same |

## Horizon and output

| Claim | Status | Source |
| --- | --- | --- |
| `horizon` is "the right-exclusive end time of the forecasting results". Results span the time between the last observation and `horizon`. If `horizon` is before the last observation, no results are generated. | CONFIRMED | A sql/language-manual/functions/ai_forecast |
| Output columns: the time and group columns keep their names and types. For each value column v: `v_forecast`, `v_upper` and `v_lower`, all DOUBLE. | CONFIRMED | same |
| "The output table contains forecasted values only, spanning the range of time between the end of the observed data until horizon." | CONFIRMED | same |

## Covariates

| Claim | Status | Source |
| --- | --- | --- |
| Future covariates: "include rows in observed that cover the forecast horizon (dates after the last observation, up to horizon) with the covariate populated and the value_col column(s) left NULL." | CONFIRMED | A sql/language-manual/functions/ai_forecast |
| Past-only covariates: "Populate the covariate on historical rows only. If you do not supply covariate values over the forecast horizon, ai_forecast uses the covariate as past-only; this is not an error." | CONFIRMED | same |

## Official examples

The function page has six examples, three for version 2 (a basic forecast, holidays with `positive_only => true`, and a future covariate) and three for version 1. The version 2 examples forecast taxi revenue from `samples.nyctaxi.trips`. Missing or NULL entries are not turned into zeros, so values must be coalesced first if the true value is known.

## Test observations (not documentation)

| Observation | Where |
| --- | --- |
| Version 2 ran on a serverless SQL warehouse with no preview setting turned on. | tests/results.md |
| A query without `version` returned the same numbers as `version => '1'`, so the default is version 1. | tests/results.md |
| A version 2 argument without `version => '2'` fails with `PYTHON_TVF_UNSUPPORTED_ARGS_FOR_VERSION`. | tests/results.md |
| `horizon => '2026-11-10'` after data ending 2026-10-30 returned rows to 2026-11-09 (10 rows). | tests/results.md |
