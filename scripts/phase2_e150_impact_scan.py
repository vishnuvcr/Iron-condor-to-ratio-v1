#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path("data/raw/options/NIFTY")
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase2_e150_impact_scan.json")


def intervals_for_date(rules, d):
    special = {x["date"]: x for x in rules.get("special_sessions", [])}
    return special[d]["execution_intervals"] if d in special else [[rules["regular_execution_session"]["start"], rules["regular_execution_session"]["end"]]]


def in_intervals(ts, intervals):
    t = ts.time()
    for start, end in intervals:
        if pd.Timestamp(f"{ts.date()} {start}", tz="Asia/Kolkata").time() <= t <= pd.Timestamp(f"{ts.date()} {end}", tz="Asia/Kolkata").time():
            return True
    return False


def main():
    if not ROOT.exists():
        raise SystemExit("PHASE2_E150_IMPACT_SOURCE_MISSING")
    rules = json.loads(RULES.read_text())
    study_start = pd.Timestamp("2021-01-01", tz="Asia/Kolkata")
    study_end = pd.Timestamp(rules["study_data_end"]).tz_localize("Asia/Kolkata") + pd.Timedelta(hours=23, minutes=59, seconds=59)
    files = sorted(ROOT.glob("*.parquet"))
    if not files:
        raise SystemExit("PHASE2_E150_IMPACT_SOURCE_EMPTY")

    groups = {}
    for path in files:
        pf = pq.ParquetFile(path)
        required = {"timestamp", "expiry", "strike", "option_type"}
        if not required.issubset(pf.schema.names):
            raise SystemExit(f"PHASE2_E150_IMPACT_SCHEMA_FAILURE:{path.name}")
        for batch in pf.iter_batches(batch_size=300_000, columns=["timestamp", "expiry", "strike", "option_type"]):
            df = batch.to_pandas()
            ts = pd.to_datetime(df["timestamp"], errors="coerce")
            ts = ts.dt.tz_localize("Asia/Kolkata") if ts.dt.tz is None else ts.dt.tz_convert("Asia/Kolkata")
            exp = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
            df["timestamp"], df["expiry"] = ts, exp
            df = df[ts.between(study_start, study_end) & exp.notna()]
            if df.empty:
                continue
            df["option_type"] = df["option_type"].astype(str).str.upper().str.strip().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
            df = df[df["option_type"].isin(["CE", "PE"]) & df["strike"].notna()]
            for row in df.itertuples(index=False):
                if row.timestamp.normalize() != row.expiry:
                    continue
                expiry_key = row.expiry.date().isoformat()
                key = (expiry_key, float(row.strike), str(row.option_type))
                bucket = groups.setdefault(key, {"latest_raw": None, "latest_valid": None})
                if bucket["latest_raw"] is None or row.timestamp > bucket["latest_raw"]:
                    bucket["latest_raw"] = row.timestamp
                if in_intervals(row.timestamp, intervals_for_date(rules, expiry_key)):
                    if bucket["latest_valid"] is None or row.timestamp > bucket["latest_valid"]:
                        bucket["latest_valid"] = row.timestamp

    affected = {}
    special_dates = {x["date"] for x in rules.get("special_sessions", [])}
    affected_groups = 0
    special_gap_groups = 0
    for (expiry_key, strike, opt), bucket in groups.items():
        raw, valid = bucket["latest_raw"], bucket["latest_valid"]
        if raw is None or valid is None or raw <= valid:
            continue
        affected_groups += 1
        entry = affected.setdefault(expiry_key, {"contract_groups": 0, "latest_raw": str(raw), "latest_valid": str(valid)})
        entry["contract_groups"] += 1
        entry["latest_raw"] = max(entry["latest_raw"], str(raw))
        entry["latest_valid"] = max(entry["latest_valid"], str(valid))
        if expiry_key in special_dates:
            special_gap_groups += 1

    result = {
        "status": "COMPLETE",
        "study_data_end": str(study_end),
        "source_files": len(files),
        "affected_expiry_dates": sorted(affected),
        "affected_contract_groups": affected_groups,
        "special_session_affected_groups": special_gap_groups,
        "expiry_detail": affected,
        "interpretation": "Any affected group can change expiry-close timing and therefore requires affected production scenario reruns before final profitability inference. Zero affected groups supports a non-material E150/E151 assessment, subject to independent tester audit."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
