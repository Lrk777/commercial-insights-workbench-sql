-- 01_dq_checks.sql — Monday exception report (do not certify until reviewed)

CREATE OR REPLACE TABLE dq_results (
  check_id VARCHAR,
  check_name VARCHAR,
  metric_value DOUBLE,
  notes VARCHAR
);

DELETE FROM dq_results;

INSERT INTO dq_results
SELECT 'DQ01', 'row_count', COUNT(*)::DOUBLE, '2024+2025 pin'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ02', 'duplicate_invoice_id_rate_pct',
  100.0 * (COUNT(*) - COUNT(DISTINCT invoice_id)) / NULLIF(COUNT(*), 0),
  'invoice_id should be unique grain'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ03', 'pct_lines_missing_county',
  100.0 * AVG(CASE WHEN county_name IS NULL OR TRIM(CAST(county_name AS VARCHAR)) = '' THEN 1 ELSE 0 END),
  'geo scorecards need county'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ04', 'pct_lines_missing_category',
  100.0 * AVG(CASE WHEN category_name IS NULL OR TRIM(CAST(category_name AS VARCHAR)) = '' THEN 1 ELSE 0 END),
  NULL
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ05', 'pct_lines_missing_state_bottle_cost',
  100.0 * AVG(CASE WHEN TRY_CAST(state_bottle_cost AS DOUBLE) IS NULL OR TRY_CAST(state_bottle_cost AS DOUBLE) = 0 THEN 1 ELSE 0 END),
  'blocks trusted margin KPIs'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ06', 'pct_lines_missing_state_bottle_retail',
  100.0 * AVG(CASE WHEN TRY_CAST(state_bottle_retail AS DOUBLE) IS NULL OR TRY_CAST(state_bottle_retail AS DOUBLE) = 0 THEN 1 ELSE 0 END),
  'blocks trusted margin KPIs'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ07', 'pct_sales_dollars_with_cost_available',
  100.0 * SUM(CASE WHEN TRY_CAST(state_bottle_cost AS DOUBLE) IS NOT NULL AND TRY_CAST(state_bottle_cost AS DOUBLE) > 0 THEN TRY_CAST(sales_dollars AS DOUBLE) ELSE 0 END)
    / NULLIF(SUM(TRY_CAST(sales_dollars AS DOUBLE)), 0),
  'sales-weighted cost coverage'
FROM raw_invoice_lines;

INSERT INTO dq_results
SELECT 'DQ08', 'negative_or_zero_sales_dollars_lines',
  COUNT(*)::DOUBLE, NULL
FROM raw_invoice_lines
WHERE TRY_CAST(sales_dollars AS DOUBLE) IS NULL OR TRY_CAST(sales_dollars AS DOUBLE) <= 0;

INSERT INTO dq_results
SELECT 'DQ09', 'zero_bottle_lines',
  COUNT(*)::DOUBLE, NULL
FROM raw_invoice_lines
WHERE TRY_CAST(sales_bottles AS DOUBLE) IS NULL OR TRY_CAST(sales_bottles AS DOUBLE) <= 0;

INSERT INTO dq_results
SELECT 'DQ10', 'distinct_stores', COUNT(DISTINCT store_no)::DOUBLE, NULL
FROM raw_invoice_lines;

SELECT * FROM dq_results ORDER BY check_id;
