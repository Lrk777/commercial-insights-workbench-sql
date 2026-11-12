# LinkedIn post (paste-ready)

I built a **Commercial Insights Analyst Workbench** in SQL — the Monday→Friday loop a junior BI / category / RGM analyst actually owns:

1. **DQ exception report** before any KPI  
2. **Metric dictionary** (what “margin” is allowed to mean)  
3. **Certified weekly marts**  
4. **Category & county scorecards with WoW variance**  
5. **Vendor concentration + anomaly flags**  
6. **Stakeholder memo**

Open data stand-in: Iowa Class-E liquor invoices (2024–2025, ~5.7M lines) via Iowa Data Hub + DuckDB.

Real findings from the run:
- **Don’t publish margin yet** — cost/retail missing on ~78% of lines (0% in 2024; ~51% in 2025). The SQL encodes a reporting gate (`do_not_report_margin`).  
- Top 5 vendors ≈ **56%** of dollars (Diageo + Sazerac alone ~38%).  
- Polk County ~**23%** of the county scorecard window — statewide KPIs are geo-skewed.  
- Year-end WoW “crashes” flagged as **calendar risk**, not automatic demand truth.

Repo: https://github.com/Lrk777/commercial-insights-workbench-sql  

#SQL #DuckDB #BusinessIntelligence #CategoryInsights #RGM #DataQuality #NewGrad2027

---

**60s interview talk-track**

“On a commercial insights seat I’d own the weekly certify-and-scorecard loop. In this workbench I landed a multi-year invoice extract, wrote the DQ exception report, refused to publish margin when cost coverage failed the gate, built category WoW and vendor concentration views, and wrote the stakeholder memo — including calling out a year-end week as a calendar artifact before anyone treats it as a demand crash.”
