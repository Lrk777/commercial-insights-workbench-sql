-- 12 — Margin deep-dive: coverage first (job rule: don't publish margin on incomplete inputs)

CREATE OR REPLACE TABLE margin_coverage AS
SELECT
  COALESCE(category_name, '(missing category)') AS category_name,
  COUNT(*) AS n_lines,
  ROUND(SUM(sales_dollars), 2) AS sales_dollars,
  ROUND(100.0 * AVG(has_margin_inputs), 2) AS pct_lines_with_margin_inputs,
  ROUND(
    100.0 * SUM(CASE WHEN has_margin_inputs = 1 THEN sales_dollars ELSE 0 END)
      / NULLIF(SUM(sales_dollars), 0),
    2
  ) AS pct_sales_with_margin_inputs,
  ROUND(AVG(unit_margin_pct) FILTER (WHERE has_margin_inputs = 1), 4) AS avg_unit_margin_pct_when_available,
  CASE
    WHEN AVG(has_margin_inputs) >= 0.80 THEN 'ok_to_report_margin'
    WHEN AVG(has_margin_inputs) >= 0.40 THEN 'partial_coverage_flag'
    ELSE 'do_not_report_margin'
  END AS margin_reporting_status
FROM stg_invoice_lines
GROUP BY 1
HAVING SUM(sales_dollars) > 100000
ORDER BY sales_dollars DESC;

SELECT * FROM margin_coverage LIMIT 20;
