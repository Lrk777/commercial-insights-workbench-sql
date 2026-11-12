#!/usr/bin/env python3
"""Run the commercial insights SQL workbench in order."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
DB = ROOT / "workbench.duckdb"

ORDER = [
    "00_load.sql",
    "01_dq_checks.sql",
    "02_clean_views.sql",
    "03_mart_weekly_sales.sql",
    "10_scorecard_category_wow.sql",
    "11_scorecard_county_store.sql",
    "12_margin_coverage.sql",
    "13_vendor_concentration.sql",
    "14_wow_anomaly_flags.sql",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-samples", action="store_true")
    args = parser.parse_args()

    import duckdb

    raw = ROOT / "data" / "raw" / "iowa_liquor_sales_2024.csv"
    if not raw.exists():
        print("Missing raw data — run scripts/download_data.py first", file=sys.stderr)
        return 1

    con = duckdb.connect(str(DB))
    con.execute(f"SET file_search_path = '{ROOT.as_posix()}'")
    for name in ORDER:
        path = SQL / name
        print(f"→ {name}")
        con.execute(path.read_text())

    if args.export_samples:
        out = ROOT / "outputs" / "sample"
        out.mkdir(parents=True, exist_ok=True)
        exports = {
            "dq_exception_report.csv": "SELECT * FROM dq_results ORDER BY check_id",
            "category_scorecard_top20.csv": "SELECT * FROM scorecard_category_wow ORDER BY week_start DESC, sales_dollars DESC LIMIT 20",
            "vendor_concentration_top15.csv": "SELECT * FROM vendor_concentration ORDER BY sales_dollars DESC LIMIT 15",
            "wow_anomaly_flags.csv": "SELECT * FROM wow_anomaly_flags ORDER BY abs_wow_pct DESC LIMIT 30",
            "margin_coverage.csv": "SELECT * FROM margin_coverage ORDER BY sales_dollars DESC LIMIT 20",
            "county_scorecard_top20.csv": "SELECT * FROM scorecard_county ORDER BY sales_dollars DESC LIMIT 20",
        }
        for fname, q in exports.items():
            con.execute(q).fetchdf().to_csv(out / fname, index=False)
            print(f"exported outputs/sample/{fname}")

    print(f"Done → {DB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
