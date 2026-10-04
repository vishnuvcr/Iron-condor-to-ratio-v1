#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from datetime import date
from pathlib import Path
import pandas as pd
import requests

START = date(2021, 1, 1)
END = date(2026, 9, 30)
RAW = Path("data/raw/g6_sources/rbi_bulletin_table26")
XLSX = RAW / "table-26-auctions-of-government-of-india-treasury-bills.xlsx"
META = RAW / "source_provenance.json"
OUT = Path("data/processed/g6/risk_free.csv")
REPORT = Path("data/validation/phase1_g6_rbi_acquisition.json")

# Immutable RBI Bulletin mirror commit in the Reserve Bank Innovation Hub repository.
SOURCE_COMMIT = "0db4ddb88c3119347e809af78c93beb4d1c874d4"
SOURCE_BLOB_SHA1 = "ff603b132a2aa2aee8b1bc08d0d1e68879af2ea7"
SOURCE_URL = (
    "https://raw.githubusercontent.com/Reserve-Bank-Innovation-Hub/"
    "dbie.rbihub.in/0db4ddb88c3119347e809af78c93beb4d1c874d4/"
    "data/publications/monthly-rbi-bulletin/government-accounts-and-treasury-bills/"
    "table-26-auctions-of-government-india-treasury-bills.xlsx"
)
# The canonical path above is corrected below to the exact GitHub filename.
SOURCE_URL = SOURCE_URL.replace("government-india-treasury-bills.xlsx", "government-of-india-treasury-bills.xlsx")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_blob_sha1(b: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def parse_date(x):
    try:
        v = pd.to_datetime(str(x).strip(), dayfirst=True, errors="coerce")
        if pd.isna(v):
            return None
        return v.date()
    except Exception:
        return None

def parse_num(x):
    s = str(x if x is not None else "").strip().replace(",", "")
    if s in {"", "-", "N/A", "nan"}:
        return None
    try:
        v = float(s)
        return v if pd.notna(v) else None
    except Exception:
        return None

def parse_sheet(xlsx_path: Path) -> pd.DataFrame:
    raw = pd.read_excel(xlsx_path, sheet_name=0, header=None, dtype=object)
    rows = []
    for i in range(len(raw)):
        row = raw.iloc[i].tolist()
        if len(row) < 13:
            continue
        d = parse_date(row[1])
        if d is None or not (START <= d <= END):
            continue
        y = parse_num(row[12])
        if y is None:
            continue
        rows.append({
            "date": d,
            "yield_pct": y,
            "source": "RBI Bulletin Table 26 — 91-day Government of India Treasury Bills",
            "source_commit": SOURCE_COMMIT,
            "source_blob_sha1": SOURCE_BLOB_SHA1,
            "auction_date_semantics": "RBI auction date; used as conservative eligibility date; same-day trading use is prohibited by strict-prior join.",
        })
    if not rows:
        raise RuntimeError("RBI_BULLETIN_NO_91D_ROWS")
    df = pd.DataFrame(rows)
    g = df.groupby("date").yield_pct.agg(["min", "max"])
    if (g["min"] != g["max"]).any():
        raise RuntimeError("RBI_BULLETIN_CONFLICTING_DUPLICATES")
    return df.drop_duplicates("date").sort_values("date")

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    cache_hit = False
    network_acquired = False
    if XLSX.exists() and META.exists():
        b = XLSX.read_bytes()
        m = json.loads(META.read_text())
        if m.get("source_commit") != SOURCE_COMMIT or m.get("source_blob_sha1") != SOURCE_BLOB_SHA1:
            raise RuntimeError("CACHE_PROVENANCE_MISMATCH")
        if git_blob_sha1(b) != SOURCE_BLOB_SHA1:
            raise RuntimeError("CACHE_GIT_BLOB_SHA1_MISMATCH")
        cache_hit = True
    else:
        r = requests.get(SOURCE_URL, headers={"User-Agent": "Iron-condor-to-ratio-v1-research/1.0"}, timeout=30)
        r.raise_for_status()
        b = r.content
        if git_blob_sha1(b) != SOURCE_BLOB_SHA1:
            raise RuntimeError(f"RBI_BULLETIN_IMMUTABLE_BLOB_MISMATCH:computed_git_blob_sha1={git_blob_sha1(b)}:bytes={len(b)}")
        RAW.mkdir(parents=True, exist_ok=True)
        XLSX.write_bytes(b)
        META.write_text(json.dumps({
            "source_url": SOURCE_URL,
            "source_commit": SOURCE_COMMIT,
            "source_blob_sha1": SOURCE_BLOB_SHA1,
            "retrieved_at": "runtime",
            "sha256": sha256_bytes(b),
        }, indent=2))
        network_acquired = True

    df = parse_sheet(XLSX)
    df.to_csv(OUT, index=False)
    REPORT.write_text(json.dumps({
        "status": "ACQUISITION_COMPLETE",
        "source": "RBI Bulletin Table 26 via immutable Reserve Bank Innovation Hub mirror",
        "source_url": SOURCE_URL,
        "source_commit": SOURCE_COMMIT,
        "source_blob_sha1": SOURCE_BLOB_SHA1,
        "source_sha256": sha256_bytes(XLSX.read_bytes()),
        "rows": len(df),
        "min_date": str(df.date.min()),
        "max_date": str(df.date.max()),
        "cache_hit": cache_hit,
        "network_acquired": network_acquired,
        "no_lookahead": "RBI auction date is used only as a conservative eligibility date; strict-prior excludes same-day observations.",
        "output_sha256": sha256_bytes(OUT.read_bytes()),
    }, indent=2, default=str))

if __name__ == "__main__":
    main()
