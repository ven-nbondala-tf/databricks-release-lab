-- Total serverless job and pipeline DBUs by performance mode (last 30 days).
SELECT
  product_features.performance_target,
  billing_origin_product,
  SUM(usage_quantity) AS total_dbu
FROM system.billing.usage
WHERE
  product_features.is_serverless
  AND billing_origin_product IN ('JOBS', 'DLT')
  AND usage_unit = 'DBU'
  AND usage_date >= DATEADD(day, -30, current_date)
GROUP BY 1, 2
ORDER BY total_dbu DESC;
