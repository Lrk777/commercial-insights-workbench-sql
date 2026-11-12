# Data manifest

| Pin | Iowa Data Hub dataset ID | File | Rows (this build) |
|-----|--------------------------|------|-------------------|
| 2024 | [1261](https://data.iowa.gov/catalog/dataset/1261) | `iowa_liquor_sales_2024.csv` | ~3.20M |
| 2025 | [1262](https://data.iowa.gov/catalog/dataset/1262) | `iowa_liquor_sales_2025.csv` | ~2.49M |

**API:** `https://idh-be.iowa.gov/api/v1/datasets/{id}/rows.csv` (returns a ZIP of CSV parts)  
**Combined catalog (full history):** [1051 — liquor_sales_combined](https://data.iowa.gov/catalog/dataset/1051)  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) via Iowa Data Hub — attribute State of Iowa / Dept. of Revenue.  
**Pin date:** 2026-11-03  

Raw files are **gitignored**. Reproduce with `python3 scripts/download_data.py`.
