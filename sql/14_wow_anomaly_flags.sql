-- 14 — WoW anomaly flags for the latest week (analyst "what moved?" pack)

CREATE OR REPLACE TABLE wow_anomaly_flags AS
WITH latest AS (
  SELECT MAX(week_start) AS week_start FROM scorecard_category_wow
),
flagged AS (
  SELECT
    s.week_start,
    s.category_name,
    s.sales_dollars,
    s.prior_week_sales,
    s.wow_sales_pct,
    s.pct_of_week_sales,
    ABS(s.wow_sales_pct) AS abs_wow_pct,
    CASE
      WHEN s.prior_week_sales IS NULL THEN 'new_or_missing_prior'
      WHEN ABS(s.wow_sales_pct) >= 40 AND s.sales_dollars >= 50000 THEN 'large_wow_move'
      WHEN ABS(s.wow_sales_pct) >= 25 AND s.sales_dollars >= 100000 THEN 'material_wow_move'
      ELSE 'normal'
    END AS flag
  FROM scorecard_category_wow s
  JOIN latest l USING (week_start)
)
SELECT *
FROM flagged
WHERE flag <> 'normal'
ORDER BY abs_wow_pct DESC;

SELECT * FROM wow_anomaly_flags LIMIT 30;
