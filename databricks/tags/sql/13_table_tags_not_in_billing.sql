-- Which tag keys appear in custom_tags? None of the table tags do.
SELECT k AS tag_key, COUNT(*) AS records
FROM (SELECT EXPLODE(MAP_KEYS(custom_tags)) AS k FROM system.billing.usage WHERE custom_tags IS NOT NULL)
GROUP BY k
ORDER BY records DESC;
