-- 10 — Standing category scorecard with week-over-week variance

CREATE OR REPLACE TABLE scorecard_category_wow AS
WITH base AS (
  SELECT * FROM mart_weekly_category
),
scored AS (
  SELECT
    week_start,
    category_name,
    sales_dollars,
    sales_liters,
    n_stores,
    pct_lines_with_margin_inputs,
    avg_unit_margin_pct,
    LAG(sales_dollars) OVER (PARTITION BY category_name ORDER BY week_start) AS prior_week_sales,
    ROUND(
      100.0 * (sales_dollars - LAG(sales_dollars) OVER (PARTITION BY category_name ORDER BY week_start))
        / NULLIF(LAG(sales_dollars) OVER (PARTITION BY category_name ORDER BY week_start), 0),
      2
    ) AS wow_sales_pct,
    ROUND(
      100.0 * sales_dollars / NULLIF(SUM(sales_dollars) OVER (PARTITION BY week_start), 0),
      2
    ) AS pct_of_week_sales
  FROM base
)
SELECT *
FROM scored
WHERE week_start >= DATE '2024-01-08';  -- allow one lag week

SELECT * FROM scorecard_category_wow
WHERE week_start = (SELECT MAX(week_start) FROM scorecard_category_wow)
ORDER BY sales_dollars DESC
LIMIT 15;
