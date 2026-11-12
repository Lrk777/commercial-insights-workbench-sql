-- 03_mart_weekly_sales.sql — certified weekly grains for scorecards

CREATE OR REPLACE TABLE mart_weekly_category AS
SELECT
  week_start,
  COALESCE(category_name, '(missing category)') AS category_name,
  COUNT(*) AS n_lines,
  COUNT(DISTINCT store_no) AS n_stores,
  COUNT(DISTINCT vendor_number) AS n_vendors,
  SUM(sales_bottles) AS sales_bottles,
  SUM(sales_liters) AS sales_liters,
  ROUND(SUM(sales_dollars), 2) AS sales_dollars,
  ROUND(100.0 * AVG(has_margin_inputs), 2) AS pct_lines_with_margin_inputs,
  ROUND(AVG(unit_margin_pct) FILTER (WHERE has_margin_inputs = 1), 4) AS avg_unit_margin_pct
FROM stg_invoice_lines
GROUP BY 1, 2;

CREATE OR REPLACE TABLE mart_weekly_county AS
SELECT
  week_start,
  COALESCE(county_name, '(missing county)') AS county_name,
  COUNT(*) AS n_lines,
  COUNT(DISTINCT store_no) AS n_stores,
  ROUND(SUM(sales_dollars), 2) AS sales_dollars,
  SUM(sales_liters) AS sales_liters
FROM stg_invoice_lines
GROUP BY 1, 2;

CREATE OR REPLACE TABLE mart_weekly_vendor AS
SELECT
  week_start,
  COALESCE(vendor_name, '(missing vendor)') AS vendor_name,
  vendor_number,
  ROUND(SUM(sales_dollars), 2) AS sales_dollars,
  SUM(sales_liters) AS sales_liters,
  COUNT(DISTINCT store_no) AS n_stores
FROM stg_invoice_lines
GROUP BY 1, 2, 3;

SELECT 'mart_weekly_category' AS mart, COUNT(*) AS n FROM mart_weekly_category
UNION ALL SELECT 'mart_weekly_county', COUNT(*) FROM mart_weekly_county
UNION ALL SELECT 'mart_weekly_vendor', COUNT(*) FROM mart_weekly_vendor;
