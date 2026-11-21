# How to Forecast in Databricks SQL with ai_forecast

Subtitle: Use ai_forecast version 2 in Databricks SQL to forecast daily sales with holidays, covariates and non-negative limits, using copyable queries.

Forecasting usually means exporting data, training a model and writing the results back, so many teams skip it. The `ai_forecast` function in Databricks SQL does the forecast in one query, and version 2 adds holiday support, covariates and non-negative forecasts on top of a time series foundation model. This guide builds a daily sales forecast step by step: you prepare the input, run a basic forecast, switch to version 2, add holidays, add a covariate and constrain the output to non-negative values. The complete code for this guide is on GitHub: [ai-forecast](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/ai-forecast).

[VIDEO: YouTube link]
Caption: A short walkthrough of forecasting with ai_forecast in Databricks SQL.

## What is ai_forecast in Databricks SQL

`ai_forecast` is a table-valued function that reads a table of history and returns forecasted values with an upper and a lower bound. You call it in the FROM clause, so the result is an ordinary table you can filter, join or save.

- Version 2 is generally available in Databricks SQL, announced on November 18, 2026. Version 1 is in Public Preview.
- Version 2 uses a time series foundation model. Version 1 uses a prophet-like piecewise linear and seasonality model.
- It forecasts one or more value columns, optionally per group, and supports holidays, covariates and non-negative forecasts in version 2.
- It runs on the compute you submit it from, with no separate inference cost.

The diagram shows what goes in and what comes out.

[image: ai-forecast-flow.png | Caption: The inputs and outputs of ai_forecast version 2. | Alt: A flow diagram. History rows, optional covariate rows and optional arguments feed ai_forecast with version 2. It returns forecast rows only, with a forecast, an upper and a lower column for each value column.]

## When to use ai_forecast

Use `ai_forecast` when your data is already in a table, you want a forecast from SQL, and a general-purpose model is accurate enough: sales, traffic, demand or revenue per day or another regular interval, for one series or many groups. It fits well inside a scheduled query, a dashboard dataset or a pipeline step.

Use a custom model when you need control over the model itself, such as custom features, your own training and evaluation loop, or a model registered and served separately. Forecasting in Databricks SQL with `ai_forecast` is a fast starting point, and a custom model is the next step when its accuracy is not enough.

## Prerequisites

- A Pro or Serverless SQL warehouse. AI Functions are not available on Classic SQL warehouses.
- Read access to the table with your history, and permission to create tables if you want to save the forecast.
- For some workspaces, including those with the compliance security profile, a workspace admin turns on "AI Forecast V2" on the Previews page. It was not needed on a serverless SQL warehouse in a Free Edition workspace.

## Step 1: Prepare the input

The function needs a time column of type DATE or TIMESTAMP, and a value column that can be cast to DOUBLE. Create a table with one row per day and region. The setup script in the repository builds two years of daily sales for two regions, a promo flag and a second series that trends close to zero.

```sql
CREATE SCHEMA IF NOT EXISTS <catalog>.forecast_demo;

CREATE OR REPLACE TABLE <catalog>.forecast_demo.sales_daily (
  ds DATE,
  region STRING,
  sales DOUBLE,
  promo BOOLEAN
);
```

The examples use the data before 2026-11-16 as history, and compare the forecast with the 60 days that follow. For your own data, pass all the history you have.

## Step 2: Run a basic forecast

A forecast needs the table, the end of the horizon, and the names of the time and value columns. Add `group_col` to forecast each region independently.

```sql
SELECT *
FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region'
);
```

The result has the columns `ds`, `region`, `sales_forecast`, `sales_upper` and `sales_lower`. The horizon is right-exclusive, so this query returns the 60 days from 2026-11-16 to 2027-01-14. The output contains forecasted rows only, not the history. This query uses version 1, because version 1 is the default when you do not pass `version`.

## Step 3: Switch to version 2

Version 2 is recommended for most use cases, and you select it with the `version` argument. Add it to the same query.

```sql
SELECT *
FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  version => '2'
);
```

Version 1 is on a deprecation path, and the default will change to version 2 in an upcoming release. Pass `version` explicitly so your results do not change when it does.

## Step 4: Add holidays

Holiday effects are modeled when you pass a region code, such as `'US'`. Use it when your series dips or peaks around public holidays.

```sql
SELECT *
FROM AI_FORECAST(
  TABLE(SELECT ds, region, sales
        FROM <catalog>.forecast_demo.sales_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  holiday_region => 'US',
  version => '2'
);
```

The chart compares the forecasts with the actual values for the East region. Sales dip on Thanksgiving, Christmas and New Year in the test data. The forecast with holidays predicts part of each dip, and the forecasts without holidays predict none.

[image: forecast-vs-actuals.png | Caption: Actual sales and forecasts for the 60 held-out days in the East region. | Alt: A line chart. The actual sales line dips sharply on Thanksgiving, Christmas and New Year. The version 1 and version 2 forecasts stay flat through those days. The version 2 forecast with US holidays dips on all three days, by less than the actual values. A shaded band shows the version 2 prediction interval.]

## Step 5: Add a covariate

A covariate is a column that explains the value, such as a promotion flag. To use one as a future covariate, add rows that cover the forecast horizon with the covariate filled in and the value column set to NULL.

```sql
SELECT *
FROM AI_FORECAST(
  TABLE(
    SELECT ds, region, sales, promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds < DATE'2026-11-16'
    UNION ALL
    SELECT ds, region, CAST(NULL AS DOUBLE) AS sales, promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds >= DATE'2026-11-16'
  ),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  covariate_col => 'promo',
  version => '2'
);
```

If you fill the covariate only on the history rows, `ai_forecast` treats it as a past-only covariate. That is not an error, but the forecast gains little, because the model cannot see the promotions that are planned.

## Step 6: Constrain the forecast to non-negative values

Set `positive_only` for series that cannot go below zero, such as returns, units or counts. Without it, the lower bound of the interval can fall below zero even when the forecast itself does not.

```sql
SELECT *
FROM AI_FORECAST(
  TABLE(SELECT ds, returns
        FROM <catalog>.forecast_demo.returns_daily
        WHERE ds < DATE'2026-11-16'),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'returns',
  positive_only => TRUE,
  version => '2'
);
```

The chart shows a daily returns series that trends close to zero. In the test, none of the point forecasts were negative either way. Without `positive_only`, all 60 lower bounds were below zero, and with it the lower bounds stop at zero.

[image: positive-only.png | Caption: The same near-zero series forecast without and with positive_only. | Alt: Two line charts of daily returns with a forecast line and a shaded interval. In the left chart the lower edge of the interval goes below zero. In the right chart the lower edge stops at zero.]

## Example: forecast sales by region with planned promotions

A retailer plans promotions for the next 60 days and wants the sales forecast per region to reflect them. The input is the history plus the planned horizon rows with `promo` set and `sales` NULL, which is the query in Step 5. You save the result so a dashboard can read it.

```sql
CREATE OR REPLACE TABLE <catalog>.forecast_demo.fc_promo AS
SELECT * FROM AI_FORECAST(
  TABLE(
    SELECT ds, region, sales, promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds < DATE'2026-11-16'
    UNION ALL
    SELECT ds, region, CAST(NULL AS DOUBLE), promo
    FROM <catalog>.forecast_demo.sales_daily
    WHERE ds >= DATE'2026-11-16'
  ),
  horizon => '2027-01-15',
  time_col => 'ds',
  value_col => 'sales',
  group_col => 'region',
  covariate_col => 'promo',
  version => '2'
);
```

To measure accuracy, join the forecast to the actual values for the same days. The table shows the mean absolute error (MAE) for the 60 held-out days. Version 2 with defaults is modestly better than version 1, holidays help on the holiday days, and the promo covariate gives the largest gain.

| Forecast | East MAE | West MAE |
| --- | --- | --- |
| Version 1, defaults | 40.38 | 33.17 |
| Version 2, defaults | 36.94 | 32.53 |
| Version 2 with holiday_region US | 33.77 | 31.29 |
| Version 2 with promo as a future covariate | 21.74 | 16.68 |
| Version 2 with promo as a past-only covariate | 37.67 | 32.75 |

These numbers come from generated data, so use them to compare the options, not to predict your own accuracy. The full example, including setup and cleanup, is in the [ai-forecast](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/ai-forecast) folder of the repository.

## Things to know

- Version 1 is the default. Pass `version => '2'` to use version 2, and do it even after the default changes so your queries state what they use.
- The version 2 arguments `covariate_col`, `holiday_region` and `positive_only` work only with version 2. With version 1, the query fails with `PYTHON_TVF_UNSUPPORTED_ARGS_FOR_VERSION`. Add `version => '2'` to fix it.
- The horizon is right-exclusive, and the output holds forecast rows only. To plot history and forecast together, UNION the history with the result.
- A future covariate needs rows for the horizon with the covariate filled in and the value column NULL. Without them the covariate is past-only and adds little.
- The frequency is the mode of the most recent observations in each group. If you set `frequency`, it must match the granularity of your data.

## Best practices

- Hold out the last part of your history, forecast it and compare, as the tables in this guide do, before you trust a forecast.
- Pass `holiday_region` when your series follows public holidays, and `positive_only` when it cannot go below zero.
- Add `group_col` instead of writing one call per group. A grouped call returns the same values as separate calls.
- Save the forecast in a table and schedule the query, so dashboards read a table instead of calling the function.

## Summary

`ai_forecast` returns a forecast with an upper and a lower bound from a single SQL query, and version 2 adds holidays, covariates and non-negative forecasts. The main takeaway is that you must pass `version => '2'` to use them, and that planned covariate values give the biggest gain. Use it when your history is in a table and you want a forecast from SQL without training a model.

Which series in your workspace would you forecast first?

## References

- [ai_forecast function](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/ai_forecast), Microsoft Learn
- [Transform unstructured data using AI Functions](https://learn.microsoft.com/en-us/azure/databricks/large-language-models/ai-functions), Microsoft Learn
- [November 2026 release notes](https://learn.microsoft.com/en-us/azure/databricks/release-notes/product/2026/november), Microsoft Learn

## Medium settings

- SEO title: How to Forecast in Databricks SQL with ai_forecast
- SEO description: same as the subtitle
- Slug: how-to-forecast-databricks-sql-ai-forecast
- Tags: Databricks, Data Engineering, Forecasting, SQL, Time Series
