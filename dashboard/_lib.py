"""Shared page shell, styles and chart helpers for the project dashboards (no external libraries).

Charts are hand-drawn SVG: thin marks, one axis, direct labels, hover tooltips, a table view under every chart,
and light/dark colour steps chosen for each mode.
"""

from __future__ import annotations

import json

CSS = r"""
:root{--surface:#fcfcfb;--card:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#6f6e69;--grid:#e6e5e1;--line:#d6d5d0;
--c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a;--c4:#eda100;--c5:#e87ba4;--gray:#b9b8b3;--lo:#c9d9ef}
@media (prefers-color-scheme:dark){:root{--surface:#1a1a19;--card:#232322;--ink:#f0efec;--ink2:#c3c2b7;--muted:#9a9993;--grid:#33332f;--line:#44443f;
--c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181;--gray:#6b6a64;--lo:#2c3d55}}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--surface);color:var(--ink)}
main{max-width:1080px;margin:0 auto;padding:24px 20px 48px}h1{font-size:22px;margin:0 0 4px}.sub{color:var(--ink2);margin:0 0 18px;max-width:820px}
.controls{display:flex;gap:10px;align-items:center;margin:0 0 10px;flex-wrap:wrap}select{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}.kpi{background:var(--card);border:1px solid var(--grid);border-radius:10px;padding:14px}
.kpi .v{font-size:26px;font-weight:650;letter-spacing:-.01em}.kpi .l{color:var(--ink2);font-size:12.5px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.card{background:var(--card);border:1px solid var(--grid);border-radius:10px;padding:14px 16px;min-width:0}
.card.wide{grid-column:1/-1}.card h2{font-size:15px;margin:0 0 2px}.card p.note{color:var(--ink2);margin:0 0 8px;font-size:12.5px}
svg{display:block;width:100%;height:auto;overflow:visible}svg text{fill:var(--ink2);font-size:11px}
.gridline{stroke:var(--grid)}.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin:2px 0 6px}.legend i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:5px;border-radius:2px}
.tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12px;box-shadow:0 4px 14px rgba(0,0,0,.12);display:none;z-index:9;max-width:320px}
.tip b{font-size:13px;color:var(--ink)}.tip .r{display:flex;gap:6px;align-items:center;color:var(--ink2)}.tip .r i{width:12px;height:3px;display:inline-block;flex:none}
details{margin-top:8px;font-size:12.5px;color:var(--ink2)}table{border-collapse:collapse;width:100%;margin-top:6px}td,th{padding:3px 6px;border-bottom:1px solid var(--grid);text-align:right}td:first-child,th:first-child{text-align:left}
.tablewrap{overflow-x:auto}footer{margin-top:22px;color:var(--muted);font-size:12px}a{color:var(--c1)}
@media (max-width:760px){.kpis{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}}
"""

JS = r"""
const $ = s => document.querySelector(s), NS = "http://www.w3.org/2000/svg";
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const el = (t, a = {}, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
const txt = (p, x, y, s, a = {}) => { const t = el("text", Object.assign({x, y}, a), p); t.textContent = s; return t; };
const fmtN = (v, d = 0) => v == null || isNaN(v) ? "—" : v.toLocaleString("en-CA", {minimumFractionDigits: d, maximumFractionDigits: d});
const tip = $("#tip");
function showTip(ev, title, rows) { tip.replaceChildren(); const b = document.createElement("b"); b.textContent = title; tip.appendChild(b);
  for (const [c, label, val] of rows) { const r = document.createElement("div"); r.className = "r"; const i = document.createElement("i"); i.style.background = c; r.appendChild(i);
    const s = document.createElement("span"); s.textContent = label + ": "; const v = document.createElement("strong"); v.textContent = val; r.append(s, v); tip.appendChild(r); }
  tip.style.display = "block"; const w = tip.offsetWidth; tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px"; tip.style.top = (ev.clientY + 14) + "px"; }
const hideTip = () => tip.style.display = "none";
function hover(node, fn) { node.setAttribute("tabindex", 0);
  node.addEventListener("pointermove", fn); node.addEventListener("pointerleave", hideTip); node.addEventListener("blur", hideTip);
  node.addEventListener("focus", () => { const r = node.getBoundingClientRect(); fn({clientX: r.right, clientY: r.top}); }); }
function table(target, head, rows) { const t = document.createElement("table"); const tr = t.insertRow(); head.forEach(h => { const th = document.createElement("th"); th.textContent = h; tr.appendChild(th); });
  rows.forEach(r => { const row = t.insertRow(); r.forEach((c, j) => { const td = row.insertCell(); td.textContent = c;
    if (j > 0 && c !== "" && isNaN(parseFloat(String(c).replace(/[$,%+−\-]/g, "")))) td.style.textAlign = "left"; }); }); if (rows.length) head.forEach((_, j) => { const c = rows[0][j]; if (j > 0 && c !== "" && isNaN(parseFloat(String(c).replace(/[$,%+−\-]/g, "")))) tr.cells[j].style.textAlign = "left"; });
  const w = document.createElement("div"); w.className = "tablewrap"; w.appendChild(t); $(target).replaceChildren(w); }
function niceStep(range, n = 5) { const raw = range / n, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p; return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * p; }

/* Multi-series line chart. xs: labels; series: [{name, color, vals (null = gap), width}]. */
function lineChart(target, xs, series, o = {}) {
  const W = 1000, H = o.height || 280, m = {l: 54, r: o.right || 120, t: 12, b: 26}, n = xs.length;
  const all = series.flatMap(s => s.vals).filter(v => v != null && !isNaN(v));
  let lo = o.min != null ? o.min : Math.min(0, ...all), hi = Math.max(...all); const st = niceStep(hi - lo); hi = Math.ceil(hi / st) * st; lo = Math.floor(lo / st) * st;
  const x = i => m.l + i * (W - m.l - m.r) / Math.max(1, n - 1), y = v => m.t + (hi - v) * (H - m.t - m.b) / ((hi - lo) || 1);
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.label || "Line chart"});
  for (let v = lo; v <= hi + 1e-9; v += st) { el("line", {x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), class: "gridline"}, s); txt(s, m.l - 6, y(v) + 4, (o.fmtAxis || fmtN)(v), {"text-anchor": "end"}); }
  const every = Math.ceil(n / (o.maxTicks || 12)); xs.forEach((lab, i) => { if (i % every === 0 || i === n - 1) txt(s, x(i), H - 6, o.xFmt ? o.xFmt(lab) : lab, {"text-anchor": "middle"}); });
  const ends = [];
  series.forEach(se => { let d = "", pen = false; se.vals.forEach((v, i) => { if (v == null || isNaN(v)) { pen = false; return; } d += (pen ? "L" : "M") + x(i) + "," + y(v); pen = true; });
    el("path", {d, fill: "none", stroke: se.color, "stroke-width": se.width || 2, "stroke-linejoin": "round", "stroke-linecap": "round"}, s);
    se.vals.forEach((v, i) => { const prev = se.vals[i - 1], next = se.vals[i + 1]; if (v != null && (prev == null) && (next == null)) el("circle", {cx: x(i), cy: y(v), r: 3.5, fill: se.color}, s); });
    let li = se.vals.length - 1; while (li >= 0 && se.vals[li] == null) li--; if (li >= 0) ends.push({y: y(se.vals[li]), x: x(li), label: se.name + " " + (o.fmt || fmtN)(se.vals[li]), strong: se.strong}); });
  ends.sort((a, b) => a.y - b.y); for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 13) ends[i].y = ends[i - 1].y + 13;
  if (!o.noEndLabels) ends.forEach(e => txt(s, W - m.r + 8, e.y + 4, e.label, {style: e.strong ? "fill:var(--ink);font-weight:600" : ""}));
  (o.marks || []).forEach(mk => { const i = xs.indexOf(mk.at); if (i < 0) return; el("line", {x1: x(i), x2: x(i), y1: m.t, y2: H - m.b, stroke: css("--line"), "stroke-dasharray": "3 3"}, s); txt(s, x(i) + 4, m.t + 10, mk.label); });
  const hair = el("line", {y1: m.t, y2: H - m.b, stroke: css("--ink2"), "stroke-width": 1, opacity: 0}, s);
  const hit = el("rect", {x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent"}, s);
  const at = i => { hair.setAttribute("x1", x(i)); hair.setAttribute("x2", x(i)); hair.setAttribute("opacity", .5); };
  hover(hit, ev => { const r = s.getBoundingClientRect(), px = (ev.clientX - r.left) * W / r.width;
    const i = Math.max(0, Math.min(n - 1, Math.round((px - m.l) / ((W - m.l - m.r) / Math.max(1, n - 1))))); at(i);
    showTip(ev, o.xFmt ? o.xFmt(xs[i]) : String(xs[i]), series.filter(se => se.vals[i] != null).map(se => [se.color, se.name, (o.fmt || fmtN)(se.vals[i])])); });
  hit.addEventListener("pointerleave", () => hair.setAttribute("opacity", 0));
  $(target).replaceChildren(s);
}

/* Horizontal bars: rows [{label, v, color, strong, extra:[[color,label,value]]}]. Handles negatives. */
function hbars(target, rows, o = {}) {
  const W = Math.max(420, Math.round($(target).clientWidth || 480)), bh = o.bh || 18, gap = 6, m = {l: o.left || 150, r: 70, t: 4, b: (o.refs || []).length ? 20 : 6}, H = m.t + m.b + rows.length * (bh + gap);
  const vals = rows.map(r => r.v).concat((o.refs || []).map(rf => rf.v)), mn = Math.min(0, ...vals), mx = Math.max(o.max ?? 0, ...vals), x = v => m.l + (v - mn) * (W - m.l - m.r) / ((mx - mn) || 1);
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.label || "Bar chart"});
  el("line", {x1: x(0), x2: x(0), y1: 0, y2: H, stroke: css("--line")}, s);
  (o.refs || []).forEach(rf => { el("line", {x1: x(rf.v), x2: x(rf.v), y1: 0, y2: H, stroke: css("--muted"), "stroke-dasharray": "2 4", opacity: .7}, s); if (rf.label) txt(s, x(rf.v) + 4, H - 2, rf.label); });
  rows.forEach((r, i) => { const yy = m.t + i * (bh + gap), x0 = x(Math.min(0, r.v)), w = Math.max(1, Math.abs(x(r.v) - x(0)));
    txt(s, m.l - 8, yy + bh * .72, r.label, {"text-anchor": "end", style: r.strong ? "fill:var(--ink);font-weight:600" : ""});
    const b = el("rect", {x: x0, y: yy, width: w, height: bh, rx: 3, fill: r.color}, s);
    txt(s, Math.max(x(r.v), x(0)) + 5, yy + bh * .72, (o.fmt || fmtN)(r.v));
    hover(b, ev => showTip(ev, r.label, [[r.color, o.metric || "value", (o.fmt || fmtN)(r.v)]].concat(r.extra || []))); });
  $(target).replaceChildren(s);
}

/* Dumbbell: rows [{label, a, b}] drawn on one axis; a = before (gray), b = after (series colour). */
function dumbbell(target, rows, o = {}) {
  const W = Math.max(460, Math.round($(target).clientWidth || 520)), rh = 20, m = {l: o.left || 190, r: 30, t: 22, b: 4}, H = m.t + m.b + rows.length * rh;
  const lo = o.min ?? 0, hi = o.max ?? 1, x = v => m.l + (v - lo) * (W - m.l - m.r) / (hi - lo);
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.label || "Before and after"});
  for (let v = lo; v <= hi + 1e-9; v += (o.step || .25)) { el("line", {x1: x(v), x2: x(v), y1: m.t - 4, y2: H, class: "gridline"}, s); txt(s, x(v), 12, (o.fmtAxis || o.fmt)(v), {"text-anchor": "middle"}); }
  rows.forEach((r, i) => { const yy = m.t + i * rh + rh / 2;
    txt(s, m.l - 8, yy + 4, r.label, {"text-anchor": "end"});
    el("line", {x1: x(r.a), x2: x(r.b), y1: yy, y2: yy, stroke: css("--line"), "stroke-width": 2}, s);
    el("circle", {cx: x(r.a), cy: yy, r: 5, fill: css("--gray")}, s);
    el("circle", {cx: x(r.b), cy: yy, r: 5, fill: o.color || css("--c1")}, s);
    const hit = el("rect", {x: m.l, y: yy - rh / 2, width: W - m.l - m.r, height: rh, fill: "transparent"}, s);
    hover(hit, ev => showTip(ev, r.label, [[css("--gray"), o.aName || "before", o.fmt(r.a)], [o.color || css("--c1"), o.bName || "after", o.fmt(r.b)]].concat(r.extra || []))); });
  $(target).replaceChildren(s);
}

/* Point + interval per row: rows [{label, v, lo, hi, color, strong}]. */
function intervals(target, rows, o = {}) {
  const W = Math.max(420, Math.round($(target).clientWidth || 480)), rh = 34, m = {l: o.left || 120, r: 60, t: 22, b: 4}, H = m.t + m.b + rows.length * rh;
  const lo = o.min ?? 0, hi = o.max ?? 100, x = v => m.l + (v - lo) * (W - m.l - m.r) / (hi - lo);
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.label || "Estimates with ranges"});
  for (let v = lo; v <= hi; v += (o.step || 25)) { el("line", {x1: x(v), x2: x(v), y1: m.t - 4, y2: H, class: "gridline"}, s); txt(s, x(v), 12, String(v), {"text-anchor": "middle"}); }
  rows.forEach((r, i) => { const yy = m.t + i * rh + rh / 2;
    txt(s, m.l - 10, yy + 4, r.label, {"text-anchor": "end", style: r.strong ? "fill:var(--ink);font-weight:600" : ""});
    el("line", {x1: x(r.lo), x2: x(r.hi), y1: yy, y2: yy, stroke: r.color, "stroke-width": 3, "stroke-linecap": "round", opacity: .45}, s);
    el("circle", {cx: x(r.v), cy: yy, r: 7, fill: r.color, stroke: css("--card"), "stroke-width": 2}, s);
    txt(s, x(r.hi) + 8, yy + 4, (o.fmt || fmtN)(r.v), {style: "fill:var(--ink);font-weight:600"});
    const hit = el("rect", {x: m.l, y: yy - rh / 2, width: W - m.l - m.r, height: rh, fill: "transparent"}, s);
    hover(hit, ev => showTip(ev, r.label, [[r.color, o.metric || "estimate", (o.fmt || fmtN)(r.v)], [r.color, o.rangeName || "range", (o.fmt || fmtN)(r.lo) + " – " + (o.fmt || fmtN)(r.hi)]].concat(r.extra || []))); });
  $(target).replaceChildren(s);
}

/* Vertical bars over categories (e.g. weekdays): rows [{label, v, color}]. */
function vbars(target, rows, o = {}) {
  const W = 1000, H = o.height || 240, m = {l: 54, r: 10, t: 16, b: 26}, n = rows.length, vals = rows.map(r => r.v);
  let hi = Math.max(...vals); const st = niceStep(hi); hi = Math.ceil(hi / st) * st;
  const bw = (W - m.l - m.r) / n, y = v => m.t + (hi - v) * (H - m.t - m.b) / hi;
  const s = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.label || "Bar chart"});
  for (let v = 0; v <= hi + 1e-9; v += st) { el("line", {x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), class: "gridline"}, s); txt(s, m.l - 6, y(v) + 4, (o.fmtAxis || fmtN)(v), {"text-anchor": "end"}); }
  rows.forEach((r, i) => { const xx = m.l + i * bw + bw * .18, w = bw * .64;
    const b = el("rect", {x: xx, y: y(r.v), width: w, height: Math.max(1, y(0) - y(r.v)), rx: 3, fill: r.color}, s);
    txt(s, xx + w / 2, H - 8, r.label, {"text-anchor": "middle"});
    hover(b, ev => showTip(ev, r.label, [[r.color, o.metric || "value", (o.fmt || fmtN)(r.v)]].concat(r.extra || []))); });
  $(target).replaceChildren(s);
}
"""


def page(title: str, body: str, script: str, data: dict) -> str:
    return ("<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{title}</title><style>{CSS}</style></head><body><main>{body}</main>"
            "<div class=\"tip\" id=\"tip\"></div><script>\nconst D = "
            + json.dumps(data, separators=(",", ":"), allow_nan=False)
            + ";\n" + JS + "\n" + script
            + "\nmatchMedia('(prefers-color-scheme: dark)').addEventListener('change', render);"
            + "\nlet _rt; addEventListener('resize', () => { clearTimeout(_rt); _rt = setTimeout(render, 150); });\n"
            "</script></body></html>\n")
