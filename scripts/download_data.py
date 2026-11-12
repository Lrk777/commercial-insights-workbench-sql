#!/usr/bin/env python3
"""Download Iowa Liquor Sales year pins from Iowa Data Hub and concat part CSVs."""

from __future__ import annotations

import io
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# Yearly public datasets on idh-be.iowa.gov (ZIP of CSV parts behind /rows.csv)
YEAR_DATASETS = {
    2024: 1261,
    2025: 1262,
}


def download_year(year: int, dataset_id: int) -> Path:
    url = f"https://idh-be.iowa.gov/api/v1/datasets/{dataset_id}/rows.csv"
    print(f"Downloading {year} from {url} …")
    req = urllib.request.Request(url, headers={"User-Agent": "commercial-insights-workbench/1.0"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        blob = resp.read()
    zf = zipfile.ZipFile(io.BytesIO(blob))
    tmp = RAW / f"_tmp_{year}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    zf.extractall(tmp)
    parts = sorted(tmp.glob("*.csv"))
    out = RAW / f"iowa_liquor_sales_{year}.csv"
    with out.open("w", encoding="utf-8") as w:
        for i, part in enumerate(parts):
            with part.open(encoding="utf-8", errors="replace") as r:
                header = r.readline()
                if i == 0:
                    w.write(header)
                shutil.copyfileobj(r, w)
    shutil.rmtree(tmp)
    print(f"  wrote {out.name} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for year, ds_id in YEAR_DATASETS.items():
        download_year(year, ds_id)
    print("Done. Raw CSVs are gitignored — see data/manifest.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
