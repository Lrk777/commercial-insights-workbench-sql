-- 13 — Vendor concentration (share of dollars) — supplier mix risk view

CREATE OR REPLACE TABLE vendor_concentration AS
WITH vend AS (
  SELECT
    COALESCE(vendor_name, '(missing vendor)') AS vendor_name,
    ROUND(SUM(sales_dollars), 2) AS sales_dollars,
    COUNT(DISTINCT store_no) AS n_stores,
    COUNT(DISTINCT category_name) AS n_categories
  FROM stg_invoice_lines
  GROUP BY 1
),
tot AS (
  SELECT SUM(sales_dollars) AS all_sales FROM vend
)
SELECT
  v.*,
  ROUND(100.0 * v.sales_dollars / t.all_sales, 2) AS pct_of_total_sales,
  RANK() OVER (ORDER BY v.sales_dollars DESC) AS sales_rank,
  ROUND(
    SUM(100.0 * v.sales_dollars / t.all_sales) OVER (ORDER BY v.sales_dollars DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
    2
  ) AS cumulative_pct_sales
FROM vend v CROSS JOIN tot t
ORDER BY v.sales_dollars DESC;

SELECT * FROM vendor_concentration WHERE sales_rank <= 15;
