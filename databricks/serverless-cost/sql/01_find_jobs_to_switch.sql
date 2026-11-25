-- Jobs and pipelines still on performance optimized mode, ranked by list cost (last 30 days).
SELECT
  u.workspace_id,
  u.billing_origin_product AS product,
  u.usage_metadata.job_id AS job_id,
  u.usage_metadata.dlt_pipeline_id AS pipeline_id,
  MAX(u.usage_metadata.job_name) AS job_name,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS job_runs,
  SUM(u.usage_quantity) AS dbus,
  SUM(u.usage_quantity * lp.pricing.default) AS list_cost
FROM system.billing.usage AS u
INNER JOIN system.billing.list_prices AS lp
  ON u.cloud = lp.cloud
  AND u.sku_name = lp.sku_name
  AND u.usage_start_time >= lp.price_start_time
  AND (u.usage_end_time <= lp.price_end_time OR lp.price_end_time IS NULL)
WHERE
  u.billing_origin_product IN ('JOBS', 'DLT')
  AND u.product_features.is_serverless
  AND u.product_features.performance_target = 'PERFORMANCE_OPTIMIZED'
  AND u.usage_unit = 'DBU'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY
  u.workspace_id,
  u.billing_origin_product,
  u.usage_metadata.job_id,
  u.usage_metadata.dlt_pipeline_id
ORDER BY list_cost DESC
LIMIT 50;
