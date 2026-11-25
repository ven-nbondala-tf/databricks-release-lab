-- DBUs for each run of the two demo jobs. Replace the job IDs with the IDs of your dev and prod jobs.
SELECT
  usage_metadata.job_run_id AS run_id,
  product_features.performance_target AS performance_mode,
  MIN(usage_start_time) AS first_record_start,
  MAX(ingestion_date) AS last_ingestion_date,
  ROUND(SUM(usage_quantity), 4) AS dbus
FROM system.billing.usage
WHERE billing_origin_product = 'JOBS'
  AND product_features.is_serverless
  AND usage_unit = 'DBU'
  AND usage_metadata.job_id IN ('<dev-job-id>', '<prod-job-id>')
GROUP BY ALL
ORDER BY first_record_start;
