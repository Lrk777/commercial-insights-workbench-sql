-- 11 — County scorecard (latest complete weeks) + top stores

CREATE OR REPLACE TABLE scorecard_county AS
WITH recent AS (
  SELECT *
  FROM mart_weekly_county
  WHERE week_start >= (SELECT MAX(week_start) - INTERVAL 12 WEEK FROM mart_weekly_county)
),
agg AS (
  SELECT
    county_name,
    ROUND(SUM(sales_dollars), 2) AS sales_dollars,
    ROUND(SUM(sales_liters), 2) AS sales_liters,
    ROUND(AVG(n_stores), 1) AS avg_active_stores
  FROM recent
  GROUP BY 1
)
SELECT
  *,
  ROUND(100.0 * sales_dollars / SUM(sales_dollars) OVER (), 2) AS pct_of_sales,
  RANK() OVER (ORDER BY sales_dollars DESC) AS sales_rank,
  NTILE(10) OVER (ORDER BY sales_dollars DESC) AS sales_decile
FROM agg;

CREATE OR REPLACE TABLE scorecard_top_stores AS
SELECT
  store_no,
  ANY_VALUE(store_name) AS store_name,
  ANY_VALUE(store_city) AS store_city,
  ANY_VALUE(county_name) AS county_name,
  ROUND(SUM(sales_dollars), 2) AS sales_dollars,
  ROUND(SUM(sales_liters), 2) AS sales_liters,
  COUNT(DISTINCT week_start) AS active_weeks
FROM stg_invoice_lines
WHERE ordered_on >= DATE '2025-01-01'
GROUP BY store_no
ORDER BY sales_dollars DESC
LIMIT 25;

SELECT * FROM scorecard_county ORDER BY sales_rank LIMIT 10;
SELECT * FROM scorecard_top_stores LIMIT 10;
