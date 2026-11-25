-- DBUs and list cost per performance mode for the measured runs. Replace the job IDs.
-- Cost = DBUs x list price (system.billing.list_prices). It is the list price of the SKU in your cloud and region,
-- prices per DBU vary by cloud, region and tier, and it does not include discounts or credits. It is not an invoice.
SELECT
  u.product_features.performance_target AS performance_mode,
  COUNT(DISTINCT u.usage_metadata.job_run_id) AS runs,
  ROUND(SUM(u.usage_quantity), 4) AS dbus,
  ROUND(SUM(u.usage_quantity) / COUNT(DISTINCT u.usage_metadata.job_run_id), 4) AS dbus_per_run,
  MAX(lp.pricing.default) AS list_price_per_dbu_usd,
  ROUND(SUM(u.usage_quantity * lp.pricing.default), 4) AS list_cost_usd,
  ROUND(SUM(u.usage_quantity * lp.pricing.default) / COUNT(DISTINCT u.usage_metadata.job_run_id), 4) AS list_cost_per_run_usd
FROM system.billing.usage AS u
INNER JOIN system.billing.list_prices AS lp
  ON u.cloud = lp.cloud
  AND u.sku_name = lp.sku_name
  AND u.usage_start_time >= lp.price_start_time
  AND (u.usage_end_time <= lp.price_end_time OR lp.price_end_time IS NULL)
WHERE u.usage_metadata.job_run_id IN (<the 12 measured run ids>)
GROUP BY ALL
ORDER BY performance_mode;
