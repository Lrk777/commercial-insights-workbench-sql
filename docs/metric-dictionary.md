# Metric dictionary (stakeholder-facing)

| Metric | Grain | Definition | Caveats |
|--------|-------|------------|---------|
| `sales_dollars` | invoice line → aggregates | Sum of `sales_dollars` from Iowa Class-E invoice extract | Not consumer shelf scan; wholesale/invoice to licensees |
| `sales_liters` / `sales_bottles` | same | Volume sold on the invoice line | Prefer liters for mix when pack sizes differ |
| `week_start` | week | Monday-start week of `ordered_on` (`DATE_TRUNC('week', …)`) | Partial trailing weeks (e.g. year-end) can look like “crashes” — flag before acting |
| `wow_sales_pct` | category × week | `(this_week − prior_week) / prior_week` for same category | Requires prior week history; large moves at incomplete weeks are suspicious |
| `pct_of_week_sales` | category × week | Category $ / all category $ that week | Mix shift ≠ absolute growth |
| `has_margin_inputs` | line | Both `state_bottle_cost` and `state_bottle_retail` present and > 0 | **2024 pin: ~0% coverage; 2025: ~51% of lines** |
| `unit_margin_pct` | line | `(retail − cost) / retail` when inputs exist | State schedule construct — not store true P&L. **Do not publish category margin if coverage status ≠ ok_to_report_margin** |
| `margin_reporting_status` | category | `ok_to_report_margin` if ≥80% lines have inputs; `partial` 40–80%; else `do_not_report_margin` | Job rule baked into SQL |
| `pct_of_total_sales` (vendor) | vendor | Vendor $ / all $ in pin | Concentration ≠ preference ranking |
| `cumulative_pct_sales` | vendor rank order | Running share of dollars | Top-N dependency view |

**Certify rule:** No scorecard number goes to a stakeholder memo unless the related DQ check is understood (see `outputs/sample/dq_exception_report.csv`).
