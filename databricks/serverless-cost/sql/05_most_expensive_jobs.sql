-- Part 2: the ten serverless jobs with the most DBUs in the last 30 days, with job names.
WITH job_names AS (
  SELECT workspace_id, job_id, name,
         ROW_NUMBER() OVER (PARTITION BY workspace_id, job_id ORDER BY change_time DESC) AS rn
  FROM system.lakeflow.jobs
)
SELECT
  n.name AS job_name,
  u.usage_metadata.job_id AS job_id,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS runs,
  ROUND(SUM(u.usage_quantity), 2) AS dbus
FROM system.billing.usage AS u
LEFT JOIN job_names AS n
  ON u.workspace_id = n.workspace_id
  AND u.usage_metadata.job_id = n.job_id
  AND n.rn = 1
WHERE u.billing_origin_product = 'JOBS'
  AND u.product_features.is_serverless
  AND u.usage_unit = 'DBU'
  AND u.usage_date >= DATEADD(day, -30, current_date())
GROUP BY n.name, u.usage_metadata.job_id
ORDER BY dbus DESC
LIMIT 10;
