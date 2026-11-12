# Commercial Insights Analyst Workbench

SQL workbench that mirrors the **weekly job** of a junior **BI / category / RGM / commercial insights** analyst:

**DQ exception report → metric dictionary → certified weekly marts → scorecards (WoW) → margin coverage gate → vendor concentration → anomaly flags → stakeholder memo.**

Built so an interviewer recognizes the workflow — not a random cool dataset dump.

## Problem

Given a messy multi-year invoice extract, can you **certify** what is safe to report, publish a standing category/geo scorecard with week-over-week variance, and write a stakeholder note that refuses bad margin math?

## Why this project

Target roles (GTA): Category Insights · RGM · BI Analyst · Commercial Analytics.  
Public stand-in for an employer POS/invoice warehouse: **Iowa Class-E liquor sales** (store × category × vendor × week, with optional cost/retail).

Health analytics stay with my York capstone (Grace Hospital / Ontario home care). This repo is **commercial reporting discipline**.

## Stack

DuckDB · SQL (CTEs, windows, `CASE`, DQ tables) · Markdown metric dictionary + memo

## Data

| Pin | Source |
|-----|--------|
| 2024 + 2025 invoice lines | [Iowa Data Hub](https://data.iowa.gov/catalog/dataset/1051) yearly extracts (`1261`, `1262`) |

- ~**5.69M** lines · **2,353** stores (this pin)  
- License: CC BY 4.0 — attribute State of Iowa / Dept. of Revenue (`DATA_LICENSE.md`)  
- Raw CSVs **not** in git — `python3 scripts/download_data.py`

## Reproduce

```bash
python3 -m pip install -r requirements.txt
python3 scripts/download_data.py
python3 scripts/run_pipeline.py --export-samples
```

## Method (job sequence)

| Step | File | Job analog |
|------|------|------------|
| 1 | `sql/00_load.sql` | Land the period extract |
| 2 | `sql/01_dq_checks.sql` | Monday exception report |
| 3 | `sql/02_clean_views.sql` | Typed staging |
| 4 | `sql/03_mart_weekly_sales.sql` | Certified weekly marts |
| 5 | `sql/10–14_*.sql` | Scorecards, margin gate, vendors, anomalies |
| 6 | `docs/metric-dictionary.md` + `findings/` | Definitions + Friday memo |

## Key findings (from this pin’s run)

1. **Do not publish margin as a headline KPI** — **77.6%** of lines lack state bottle cost/retail; **2024 coverage = 0%**, **2025 ≈ 51% of lines / 52% of $**. Top categories are gated `do_not_report_margin`.  
2. **Vendor concentration:** Diageo Americas ~**21%** of $ + Sazerac ~**16%** ≈ **38%**; top 5 vendors ≈ **56%**.  
3. **Geo skew:** Polk County ~**23%** of the county scorecard window — statewide averages are Polk-weighted.  
4. **WoW anomalies on week 2025-12-29** look severe (e.g. Straight Bourbon −52%) — treated as **calendar / partial-week risk** until a full ISO week is confirmed.  
5. **`invoice_id` duplicate rate ~25%** — grain must be clarified with the data owner before invoice reconciliation.

Samples: `outputs/sample/` · Memo: `findings/weekly_insights_memo.md`

## Limitations

- US Class-E spirits invoices ≠ Canadian grocery POS — **process** transfers, not domain claim  
- State cost/retail ≠ true store margin  
- Year-end weeks can distort WoW  

## Author

**Lavanya Kumar** · Bachelor of Data Science (Honours), Computation · York University · Graduating April 2027  
GitHub: [Lrk777](https://github.com/Lrk777) · LinkedIn: [lavanya-kumar-610a07214](https://www.linkedin.com/in/lavanya-kumar-610a07214)
