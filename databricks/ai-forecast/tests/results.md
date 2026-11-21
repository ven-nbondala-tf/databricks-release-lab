# Test results

Run on November 21, 2026 on a Databricks Free Edition workspace, on a serverless SQL warehouse (2X-Small). These notes are not part of the article.

## Setup

- Schema `forecast_demo`. Table `sales_daily`: 730 days (2025-01-15 to 2027-01-14) for East (base 200) and West (base 150), with an upward trend, higher weekends, dips on US Thanksgiving, December 25 and January 1, a promo flag (about 15% of days) that raises sales by 30%, and noise of up to 5%.
- Table `returns_daily`: a series that trends down to near zero (13 zero days in the last 60 days, mean 0.259).
- Training data is every row before 2026-11-16. The last 60 days (2026-11-16 to 2027-01-14) are held out, and every forecast uses `horizon => '2027-01-15'`.

## Probe

- Version 2 ran on a serverless SQL warehouse with no preview setting turned on.
- With 30 days of data ending 2026-10-30 and `horizon => '2026-11-10'`, 10 rows came back (2026-10-31 to 2026-11-09), so the horizon is right-exclusive.
- A query without `version` returned a mean forecast of 164.503, the same as `version => '1'`. Version 2 returned 162.932. The default is version 1.
- `holiday_region` without `version => '2'` fails: `[TABLE_VALUED_FUNCTION_FAILED_TO_ANALYZE_IN_PYTHON] ... [PYTHON_TVF_UNSUPPORTED_ARGS_FOR_VERSION] The function AI_FORECAST was called with version => '1', which does not support the following argument(s): holiday_region. Please remove these arguments or call a version that supports them, then retry the query. SQLSTATE: 38000`. This was the only error in all runs.

## Accuracy on the 60 held-out days

| Test | Region | MAPE % | MAE | Inside interval % | Notes |
| --- | --- | --- | --- | --- | --- |
| T1 version 1, defaults | East | 13.77 | 40.38 | 85.0 | |
| T1 version 1, defaults | West | 14.54 | 33.17 | 90.0 | |
| T2 version 2, defaults | East | 12.32 | 36.94 | 83.3 | Modestly better than version 1 |
| T2 version 2, defaults | West | 13.98 | 32.53 | 85.0 | |
| T3 version 2, holiday_region US | East | 9.67 | 33.77 | 91.7 | Holiday dips partly predicted |
| T3 version 2, holiday_region US | West | 12.40 | 31.29 | 90.0 | |
| T4 version 2, promo as future covariate | East | 9.06 | 21.74 | 91.7 | MAE roughly halves versus T2 |
| T4 version 2, promo as future covariate | West | 9.25 | 16.68 | 95.0 | |
| T5 version 2, promo as past-only covariate | East | 12.49 | 37.67 | 86.7 | No gain versus T2 |
| T5 version 2, promo as past-only covariate | West | 13.83 | 32.75 | 86.7 | |

## Holiday days (forecast divided by actual)

Version 1 and version 2 forecast about 2.1 to 2.4 times the actual value on Thanksgiving, Christmas and New Year. Version 2 with `holiday_region => 'US'` forecast about 1.4 to 1.95 times. Example, East on 2026-11-26: actual 155.1, version 1 354.0, version 2 334.3, version 2 with holidays 270.4. The holiday effect is learned in part, not in full.

## T6 near-zero series (version 2)

- Without `positive_only`: 0 negative point forecasts (minimum 0.064), but all 60 lower bounds are negative (minimum -0.386).
- With `positive_only => TRUE`: lower bounds are clipped to 0.0, and the minimum forecast stays 0.064.

## T7 grouping

One call with `group_col => 'region'` and one call per region returned identical values (maximum absolute difference 0.0 for both regions).

## Run times

Each CREATE TABLE AS SELECT with ai_forecast took 4.3 to 5.2 seconds. Two per-region calls took 9.0 seconds in total, the one grouped call 4.8 seconds.

## What differed from the documentation

- The release note lists no requirements. The function page lists a Pro or Serverless SQL warehouse and, for some workspaces, an admin setting "AI Forecast V2" on the Previews page. Neither was needed here.
- Runtime, regions, minimum history, the `holiday_region` code list and the `prediction_interval_width` default are not documented.

## Not tested

- A Classic or Pro warehouse, the `frequency` argument, `prediction_interval_width`, holiday regions other than US, several value columns, weekly or monthly data, the admin Previews setting.
- Promo combined with holidays in one call.
