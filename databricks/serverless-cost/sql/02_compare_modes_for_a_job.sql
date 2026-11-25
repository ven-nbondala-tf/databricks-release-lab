-- DBUs per run in each performance mode for one job. Replace <job-id>.
SELECT
  u.product_features.performance_target AS performance_mode,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS runs,
  SUM(u.usage_quantity) AS dbus,
  SUM(u.usage_quantity) / COUNT(DISTINCT u.usage_metadata.job_run_id) AS dbus_per_run
FROM system.billing.usage AS u
WHERE
  u.billing_origin_product = 'JOBS'
  AND u.product_features.is_serverless
  AND u.usage_unit = 'DBU'
  AND u.usage_metadata.job_id = '<job-id>'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY ALL;
