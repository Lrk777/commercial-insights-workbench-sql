-- 02_clean_views.sql — typed staging + availability flags

CREATE OR REPLACE VIEW stg_invoice_lines AS
WITH typed AS (
  SELECT
    CAST(invoice_id AS VARCHAR) AS invoice_id,
    CAST(ordered_on AS DATE) AS ordered_on,
    DATE_TRUNC('week', CAST(ordered_on AS DATE))::DATE AS week_start,
    CAST(store_no AS VARCHAR) AS store_no,
    NULLIF(TRIM(CAST(store_name AS VARCHAR)), '') AS store_name,
    NULLIF(TRIM(CAST(store_city AS VARCHAR)), '') AS store_city,
    CAST(store_zip_code AS VARCHAR) AS store_zip_code,
    CAST(county_fips_code AS VARCHAR) AS county_fips_code,
    NULLIF(TRIM(CAST(county_name AS VARCHAR)), '') AS county_name,
    CAST(category_code AS VARCHAR) AS category_code,
    NULLIF(TRIM(CAST(category_name AS VARCHAR)), '') AS category_name,
    CAST(vendor_number AS VARCHAR) AS vendor_number,
    NULLIF(TRIM(CAST(vendor_name AS VARCHAR)), '') AS vendor_name,
    CAST(item_no AS VARCHAR) AS item_no,
    NULLIF(TRIM(CAST(im_desc AS VARCHAR)), '') AS item_desc,
    TRY_CAST(pack AS DOUBLE) AS pack,
    TRY_CAST(bottle_volume_ml AS DOUBLE) AS bottle_volume_ml,
    TRY_CAST(state_bottle_cost AS DOUBLE) AS state_bottle_cost,
    TRY_CAST(state_bottle_retail AS DOUBLE) AS state_bottle_retail,
    TRY_CAST(sales_bottles AS DOUBLE) AS sales_bottles,
    TRY_CAST(sales_dollars AS DOUBLE) AS sales_dollars,
    TRY_CAST(sales_liters AS DOUBLE) AS sales_liters,
    TRY_CAST(sales_gallons AS DOUBLE) AS sales_gallons,
    source_year
  FROM raw_invoice_lines
)
SELECT
  *,
  CASE WHEN state_bottle_cost IS NOT NULL AND state_bottle_cost > 0
            AND state_bottle_retail IS NOT NULL AND state_bottle_retail > 0
       THEN 1 ELSE 0 END AS has_margin_inputs,
  CASE WHEN state_bottle_cost IS NOT NULL AND state_bottle_cost > 0
            AND state_bottle_retail IS NOT NULL AND state_bottle_retail > 0
       THEN (state_bottle_retail - state_bottle_cost) / state_bottle_retail
       ELSE NULL END AS unit_margin_pct,
  CASE WHEN sales_bottles > 0 THEN sales_dollars / sales_bottles ELSE NULL END AS realized_dollars_per_bottle
FROM typed;
