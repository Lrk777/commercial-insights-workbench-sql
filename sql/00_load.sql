-- 00_load.sql — land year pins into one raw fact

CREATE OR REPLACE TABLE raw_invoice_lines AS
SELECT *, 2024 AS source_year
FROM read_csv_auto('data/raw/iowa_liquor_sales_2024.csv', header = true, sample_size = -1, ignore_errors = true)
UNION ALL
SELECT *, 2025 AS source_year
FROM read_csv_auto('data/raw/iowa_liquor_sales_2025.csv', header = true, sample_size = -1, ignore_errors = true);

SELECT source_year, COUNT(*) AS n_lines, ROUND(SUM(sales_dollars), 2) AS sales_dollars
FROM raw_invoice_lines
GROUP BY 1
ORDER BY 1;
