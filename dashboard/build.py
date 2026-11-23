"""Build dashboard/index.html from the committed sample outputs in outputs/sample (no network, no extra packages).

Usage: python dashboard/build.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from _lib import page

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "outputs" / "sample"


def title(name: str) -> str:
    """'SAZERAC COMPANY  INC' -> 'Sazerac Company Inc' (keeps short all-caps words like USA)."""
    words = " ".join(str(name).split()).split(" ")
    keep = {"USA", "US", "RTD", "&"}
    return " ".join(w if w.rstrip(",.") in keep else "-".join(p.capitalize() for p in w.split("-")) for w in words).replace("Cocktails/rtd", "Cocktails/RTD")


NOTE = {"2024+2025 pin": "pinned 2024–2025 extract", "invoice_id should be unique grain": "invoice_id should identify one invoice line",
        "geo scorecards need county": "county scorecards need it", "blocks trusted margin KPIs": "without it, margin can't be trusted",
        "sales-weighted cost coverage": "cost coverage weighted by sales"}


def build_data() -> dict:
    dq = pd.read_csv(S / "dq_exception_report.csv").set_index("check_name").metric_value
    ven = pd.read_csv(S / "vendor_concentration_top15.csv").sort_values("sales_rank")
    mar = pd.read_csv(S / "margin_coverage.csv").sort_values("sales_dollars", ascending=False)
    cty = pd.read_csv(S / "county_scorecard_top20.csv").sort_values("sales_rank")
    cat = pd.read_csv(S / "category_scorecard_top20.csv").sort_values("sales_dollars", ascending=False)
    flags = set(pd.read_csv(S / "wow_anomaly_flags.csv").category_name)
    total_sales = float(ven.sales_dollars.iloc[0] / ven.pct_of_total_sales.iloc[0] * 100)
    top5 = ven.head(5)
    return {
        "kpi": {"lines": int(dq["row_count"]), "stores": int(dq["distinct_stores"]),
                "top5_pct": round(float(top5.cumulative_pct_sales.iloc[-1]), 1), "top5_dollars": float(top5.sales_dollars.sum()),
                "total_dollars": total_sales, "cost_sales_pct": round(float(dq["pct_sales_dollars_with_cost_available"]), 1),
                "missing_cost_lines_pct": round(float(dq["pct_lines_missing_state_bottle_cost"]), 1),
                "dup_invoice_pct": round(float(dq["duplicate_invoice_id_rate_pct"]), 1)},
        "vendors": [{"name": title(r.vendor_name), "pct": float(r.pct_of_total_sales), "cum": float(r.cumulative_pct_sales),
                     "dollars": float(r.sales_dollars), "stores": int(r.n_stores)} for r in ven.itertuples()],
        "margin": [{"name": title(r.category_name), "lines": float(r.pct_lines_with_margin_inputs), "sales": float(r.pct_sales_with_margin_inputs),
                    "status": r.margin_reporting_status} for r in mar.itertuples()],
        "counties": [{"name": title(r.county_name), "pct": float(r.pct_of_sales), "dollars": float(r.sales_dollars),
                      "stores": float(r.avg_active_stores)} for r in cty.itertuples()],
        "week": str(cat.week_start.iloc[0]),
        "categories": [{"name": title(r.category_name), "wow": float(r.wow_sales_pct), "dollars": float(r.sales_dollars),
                        "prior": float(r.prior_week_sales), "flag": r.category_name in flags} for r in cat.itertuples()],
        "dq": [{"check": r.check_name.replace("_", " ").replace("pct", "%"), "value": float(r.metric_value),
                "note": "" if pd.isna(r.notes) else NOTE.get(r.notes, r.notes)} for r in pd.read_csv(S / "dq_exception_report.csv").itertuples()],
    }


BODY = """
<h1>Liquor sales reporting: what's safe to report this week</h1>
<p class="sub">A weekly BI reporting cycle on 5.69M invoice lines from Iowa's open liquor sales data (2024–2025). The data-quality checks decide what goes in the report and what gets held back.</p>
<div class="kpis">
 <div class="kpi"><div class="v" id="k1"></div><div class="l" id="k1l"></div></div>
 <div class="kpi"><div class="v" id="k2"></div><div class="l" id="k2l"></div></div>
 <div class="kpi"><div class="v" id="k3"></div><div class="l">of sales dollars have cost data, so margin is held back</div></div>
 <div class="kpi"><div class="v" id="k4"></div><div class="l">of lines share an invoice ID, so it isn't a unique key</div></div>
</div>
<div class="grid">
 <div class="card"><h2>Vendor concentration</h2><p class="note">Share of sales dollars. The top 5 vendors (blue) hold more than half.</p><div id="c1"></div><details><summary>Table</summary><div id="t1"></div></details></div>
 <div class="card"><h2>Why margin is held back</h2><p class="note">Share of invoice lines with cost and retail price, top 20 categories by sales. Reporting rule: 80% or more = report, 40% or more = report with a caveat. Every category falls below 40%.</p><div id="c2"></div><details><summary>Table</summary><div id="t2"></div></details></div>
 <div class="card"><h2>Sales by county</h2><p class="note">Share of sales dollars, top 20 counties. Polk is so large that any statewide average is mostly a Polk number.</p><div id="c3"></div><details><summary>Table</summary><div id="t3"></div></details></div>
 <div class="card"><h2 id="h4"></h2><p class="note">Week-over-week change in sales, top 20 categories. Orange = flagged for review: the drops line up with a short year-end week, not a fall in demand.</p><div id="c4"></div><details><summary>Table</summary><div id="t4"></div></details></div>
 <div class="card wide"><h2>Data-quality checks run before every report</h2><p class="note">These numbers decide what the weekly report can include.</p><div id="t5"></div></div>
</div>
<footer>Source: Iowa Department of Revenue, Alcoholic Beverages Division, Iowa Liquor Sales (data.iowa.gov, public domain), 2024–2025 extract. The dashboard reads the committed sample outputs. Code and method: <a href="https://github.com/Lrk777/commercial-insights-workbench-sql">github.com/Lrk777/commercial-insights-workbench-sql</a>.</footer>
"""

SCRIPT = r"""
const p1 = v => v.toFixed(1) + "%", usd = v => "$" + (v >= 1e6 ? (v / 1e6).toFixed(1) + "M" : fmtN(v));
function render() {
  const K = D.kpi;
  $("#k1").textContent = (K.lines / 1e6).toFixed(2) + "M"; $("#k1l").textContent = "invoice lines from " + fmtN(K.stores) + " stores";
  $("#k2").textContent = p1(K.top5_pct); $("#k2l").textContent = "of sales from the top 5 vendors (" + usd(K.top5_dollars) + " of " + usd(K.total_dollars) + ")";
  $("#k3").textContent = p1(K.cost_sales_pct); $("#k4").textContent = p1(K.dup_invoice_pct);
  hbars("#c1", D.vendors.map((v, i) => ({label: v.name, v: v.pct, color: i < 5 ? css("--c1") : css("--gray"), strong: i < 5,
    extra: [[css("--gray"), "cumulative share", p1(v.cum)], [css("--gray"), "sales", usd(v.dollars)]]})), {left: 200, fmt: p1, metric: "share of sales"});
  table("#t1", ["Vendor", "Share", "Cumulative", "Sales", "Stores"], D.vendors.map(v => [v.name, p1(v.pct), p1(v.cum), usd(v.dollars), fmtN(v.stores)]));
  hbars("#c2", D.margin.map(m => ({label: m.name, v: m.lines, color: css("--c2"), extra: [[css("--gray"), "share of sales $ with cost", p1(m.sales)], [css("--gray"), "status", "do not report margin"]]})),
    {left: 210, fmt: p1, metric: "lines with cost data", max: 100, refs: [{v: 40, label: "40%"}, {v: 80, label: "80%"}]});
  table("#t2", ["Category", "% of lines", "% of sales $", "Status"], D.margin.map(m => [m.name, p1(m.lines), p1(m.sales), m.status.replace(/_/g, " ")]));
  hbars("#c3", D.counties.map((c, i) => ({label: c.name, v: c.pct, color: i === 0 ? css("--c1") : css("--lo"), strong: i === 0,
    extra: [[css("--gray"), "sales", usd(c.dollars)], [css("--gray"), "active stores (avg)", fmtN(c.stores, 1)]]})), {left: 120, fmt: p1, metric: "share of sales"});
  table("#t3", ["County", "Share", "Sales", "Active stores"], D.counties.map(c => [c.name, p1(c.pct), usd(c.dollars), fmtN(c.stores, 1)]));
  $("#h4").textContent = "Week of " + D.week + ": change vs the week before";
  const cats = D.categories.slice().sort((a, b) => a.wow - b.wow);
  hbars("#c4", cats.map(c => ({label: c.name, v: c.wow, color: c.flag ? css("--c2") : css("--gray"),
    extra: [[css("--gray"), "this week", usd(c.dollars)], [css("--gray"), "week before", usd(c.prior)]]})), {left: 210, fmt: v => (v > 0 ? "+" : "") + v.toFixed(0) + "%", metric: "change"});
  table("#t4", ["Category", "This week", "Week before", "Change", "Flagged"], cats.map(c => [c.name, usd(c.dollars), usd(c.prior), c.wow.toFixed(1) + "%", c.flag ? "yes" : ""]));
  table("#t5", ["Check", "Result", "Why it matters"], D.dq.map(d => [d.check, d.value > 1000 ? fmtN(d.value) : fmtN(d.value, d.value % 1 ? 2 : 0), d.note]));
}
render();
"""


def main() -> None:
    out = ROOT / "dashboard" / "index.html"
    out.write_text(page("Liquor sales reporting: what's safe to report", BODY, SCRIPT, build_data()), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
