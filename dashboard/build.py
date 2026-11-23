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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root{--surface:#eef1f5;--card:#ffffff;--ink:#0f1b2d;--ink2:#46536a;--muted:#5f6b80;--grid:#e3e8ef;--line:#cfd7e2;
--c1:#1f4e8c;--c2:#d9480f;--c3:#0f8a6c;--gray:#b5bfcc;--lo:#c9d7ea;--ok:#0f7b3f;--hold:#c92a2a;--rev:#9a6700}
@media (prefers-color-scheme:dark){:root{--surface:#0b1220;--card:#121b2c;--ink:#e8eef7;--ink2:#a9b6c9;--muted:#8b98ad;--grid:#1e2a3d;--line:#2b3a52;
--c1:#5b8fd6;--c2:#e8692e;--c3:#2bb38d;--gray:#4a586e;--lo:#24385a;--ok:#3fbf73;--hold:#f06363;--rev:#e3b341}}
body{font-family:"IBM Plex Sans",system-ui,sans-serif}
main{max-width:1180px}
.top{background:#0f1b2d;color:#fff;border-radius:12px;padding:22px 26px;display:flex;flex-wrap:wrap;gap:12px 24px;justify-content:space-between;align-items:flex-end;margin-bottom:18px}
.top h1{color:#fff;font-size:26px;margin:4px 0 6px}.top .sub{color:#c7d2e3;margin:0;font-size:14px}
.eyebrow{font:500 12px "IBM Plex Mono",monospace;letter-spacing:.12em;color:#8fb3e8;text-transform:uppercase;margin:0}
.pill{font:500 13px "IBM Plex Mono",monospace;background:#1d3557;color:#fff;border-radius:999px;padding:8px 14px;white-space:nowrap}
.kpis{grid-template-columns:repeat(4,1fr)}.kpi{border-top:3px solid var(--c1);border-radius:8px}.kpi .v{font-size:30px;font-weight:700}
.kpi .l{font-size:13px}
.card{border-radius:8px}.card h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink2);margin-bottom:6px}
.board td,.board th{padding:10px 8px;font-size:14px;text-align:left;vertical-align:top}.board th{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.chip{display:inline-flex;align-items:center;gap:6px;font:600 12px "IBM Plex Mono",monospace;letter-spacing:.06em;border-radius:6px;padding:4px 9px;border:1.5px solid currentColor;white-space:nowrap}
.chip.ok{color:var(--ok)}.chip.hold{color:var(--hold)}.chip.rev{color:var(--rev)}
@media (max-width:760px){.top{padding:18px}}
</style>
<div class="top"><div><p class="eyebrow">Weekly reporting pack · Iowa liquor sales</p><h1>What's safe to report this week</h1><p class="sub">5.69M invoice lines, 2024–2025. Data-quality checks decide what goes in the report and what gets held back.</p></div><span class="pill" id="wk"></span></div>
<div class="kpis">
 <div class="kpi"><div class="l">Volume checked</div><div class="v" id="k1"></div><div class="l" id="k1l"></div></div>
 <div class="kpi"><div class="l">Top-5 vendor share</div><div class="v" id="k2"></div><div class="l" id="k2l"></div></div>
 <div class="kpi"><div class="l">Sales $ with cost data</div><div class="v" id="k3"></div><div class="l">below the 40% needed to report margin</div></div>
 <div class="kpi"><div class="l">Repeated invoice IDs</div><div class="v" id="k4"></div><div class="l">of lines, so invoice_id isn't a unique key</div></div>
</div>
<div class="grid">
 <div class="card wide"><h2>Report status this week</h2><div class="tablewrap"><table class="board"><thead><tr><th>Section</th><th>Status</th><th>Why</th></tr></thead><tbody id="board"></tbody></table></div></div>
 <div class="card"><h2>Vendor concentration</h2><p class="note">Share of sales dollars. The top 5 vendors (dark blue) hold more than half.</p><div id="c1"></div><details><summary>Table</summary><div id="t1"></div></details></div>
 <div class="card"><h2>Why margin is on hold</h2><p class="note">Share of invoice lines with cost and retail price, top 20 categories by sales. Rule: 80%+ = report, 40%+ = report with a caveat. Every category is below 40%.</p><div id="c2"></div><details><summary>Table</summary><div id="t2"></div></details></div>
 <div class="card"><h2>Sales by county</h2><p class="note">Share of sales dollars, top 20 counties. Polk is so large that any statewide average is mostly a Polk number.</p><div id="c3"></div><details><summary>Table</summary><div id="t3"></div></details></div>
 <div class="card"><h2 id="h4"></h2><p class="note">Week-over-week change in sales, top 20 categories. Orange = flagged for review: the drops line up with a short year-end week, not a fall in demand.</p><div id="c4"></div><details><summary>Table</summary><div id="t4"></div></details></div>
 <div class="card wide"><h2>Data-quality checks run before every report</h2><p class="note">These numbers decide what the weekly report can include.</p><div id="t5"></div></div>
</div>
<footer>Source: Iowa Department of Revenue, Alcoholic Beverages Division, Iowa Liquor Sales (data.iowa.gov, public domain), 2024–2025 extract. The dashboard reads the committed sample outputs. Built by Lavanya Kumar. Code and method: <a href="https://github.com/Lrk777/commercial-insights-workbench-sql">github.com/Lrk777/commercial-insights-workbench-sql</a>.</footer>
"""

SCRIPT = r"""
const p1 = v => v.toFixed(1) + "%", usd = v => "$" + (v >= 1e6 ? (v / 1e6).toFixed(1) + "M" : fmtN(v));
function render() {
  const K = D.kpi;
  $("#k1").textContent = (K.lines / 1e6).toFixed(2) + "M"; $("#k1l").textContent = "invoice lines from " + fmtN(K.stores) + " stores";
  $("#k2").textContent = p1(K.top5_pct); $("#k2l").textContent = "of sales from the top 5 vendors (" + usd(K.top5_dollars) + " of " + usd(K.total_dollars) + ")";
  $("#k3").textContent = p1(K.cost_sales_pct); $("#k4").textContent = p1(K.dup_invoice_pct);
  $("#wk").textContent = "Week of " + D.week;
  const nflag = D.categories.filter(c => c.flag).length, dq = Object.fromEntries(D.dq.map(d => [d.check, d.value]));
  const rows = [["Sales by vendor, category and county", "ok", "REPORT", "Category is never missing and county is missing on " + dq["% lines missing county"].toFixed(2) + "% of lines."],
    ["Margin by category", "hold", "HOLD", "Only " + p1(K.cost_sales_pct) + " of sales dollars have cost data; the rule needs 40%."],
    ["Invoice-level totals", "hold", "HOLD", p1(K.dup_invoice_pct) + " of lines share an invoice ID. Waiting for the data owner to confirm the grain."],
    ["Week-over-week change", "rev", "REVIEW", nflag + " of " + D.categories.length + " categories dropped sharply in a short year-end week."]];
  const tb = $("#board"); tb.replaceChildren(...rows.map(([sec, cls, lab, why]) => { const tr = document.createElement("tr");
    const a = document.createElement("td"); a.textContent = sec; a.style.fontWeight = "600";
    const b = document.createElement("td"); const chip = document.createElement("span"); chip.className = "chip " + cls; chip.textContent = (cls === "ok" ? "✓ " : cls === "hold" ? "■ " : "! ") + lab; b.appendChild(chip);
    const c = document.createElement("td"); c.textContent = why; c.style.color = "var(--ink2)"; tr.append(a, b, c); return tr; }));
  hbars("#c1", D.vendors.map((v, i) => ({label: v.name, v: v.pct, color: i < 5 ? css("--c1") : css("--gray"), strong: i < 5,
    extra: [[css("--gray"), "cumulative share", p1(v.cum)], [css("--gray"), "sales", usd(v.dollars)]]})), {left: 200, fmt: p1, metric: "share of sales"});
  table("#t1", ["Vendor", "Share", "Cumulative", "Sales", "Stores"], D.vendors.map(v => [v.name, p1(v.pct), p1(v.cum), usd(v.dollars), fmtN(v.stores)]));
  hbars("#c2", D.margin.map(m => ({label: m.name, v: m.lines, color: css("--c2"), extra: [[css("--gray"), "share of sales $ with cost", p1(m.sales)], [css("--gray"), "status", "do not report margin"]]})),
    {left: 210, fmt: p1, metric: "lines with cost data", max: 100, refs: [{v: 40, label: "40%"}, {v: 80, label: "80%"}]});
  table("#t2", ["Category", "% of lines", "% of sales $", "Status"], D.margin.map(m => [m.name, p1(m.lines), p1(m.sales), m.status.replace(/_/g, " ")]));
  hbars("#c3", D.counties.map((c, i) => ({label: c.name, v: c.pct, color: i === 0 ? css("--c1") : css("--lo"), strong: i === 0,
    extra: [[css("--gray"), "sales", usd(c.dollars)], [css("--gray"), "active stores (avg)", fmtN(c.stores, 1)]]})), {left: 120, fmt: p1, metric: "share of sales"});
  table("#t3", ["County", "Share", "Sales", "Active stores"], D.counties.map(c => [c.name, p1(c.pct), usd(c.dollars), fmtN(c.stores, 1)]));
  $("#h4").textContent = "Year-end week vs the week before";
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
