# Stakeholder memo — Commercial Insights Workbench

**Pin:** Iowa Liquor Sales 2024 + 2025 (Iowa Data Hub) · run 2026-11-03  
**Audience style:** Friday note from a junior commercial / category analyst

## Certify / DQ first

1. **~5.69M invoice lines** across **2,353 stores**; categories are fully populated, counties almost fully (~0.04% missing).  
2. **Margin inputs are not certifiable for most of the pin:** **77.6%** of lines lack `state_bottle_cost` / retail. **2024 = 0% cost coverage; 2025 ≈ 51% of lines / 52% of $.** Every top category is flagged `do_not_report_margin` — so this week’s pack reports **sales, mix, and coverage**, not fake margin.  
3. **`invoice_id` is not a clean unique grain** (~25% duplicate rate in this extract). Treat it as a business key to investigate with the data owner before invoice-level reconciliations.

## Scorecard highlights

4. **Category dollars are concentrated:** American Vodkas (~$147M) and Canadian Whiskies (~$107M) lead the two-year pin; mix conversations should start there.  
5. **Vendor concentration is real:** Diageo Americas (~21% of $) + Sazerac (~16%) ≈ **38%** of dollars; top 5 vendors ≈ **56%**.  
6. **Geo:** On the trailing window used for the county pack, **Polk County alone is ~23% of $** — statewide averages will be Polk-weighted.  
7. **Latest week (2025-12-29) shows large negative WoW moves** across major categories (e.g. Straight Bourbon −52%, American Vodkas −40%). **Analyst caution:** this is a year-end / short week candidate — validate calendar completeness before calling a demand crash.

## Actions I’d take on the job

- Ask Revenue/data owner why **2024 cost/retail is empty** in the Hub extract before any margin dashboard.  
- Re-run WoW flags on the last **full** ISO week only.  
- Keep vendor concentration on the standing pack for supplier-risk conversations.
