-- Usage grouped by a custom tag. Records can take several hours to arrive.
SELECT custom_tags['project'] AS project,
       billing_origin_product,
       ROUND(SUM(usage_quantity), 4) AS dbus
FROM system.billing.usage
WHERE usage_date >= DATE'2026-11-01'
  AND custom_tags['project'] IS NOT NULL
GROUP BY ALL
ORDER BY dbus DESC;
