-- Part 2: usage that carries a serverless usage policy, with its tags. Replace <policy-id>.
SELECT
  usage_date,
  billing_origin_product,
  custom_tags,
  usage_metadata.usage_policy_id AS usage_policy_id,
  ROUND(SUM(usage_quantity), 4) AS dbus
FROM system.billing.usage
WHERE usage_metadata.usage_policy_id = '<policy-id>'
GROUP BY ALL
ORDER BY usage_date DESC;
