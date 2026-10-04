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
    if d in special:
        return special[d]["execution_intervals"]
    return [[rules["regular_execution_session"]["start"], rules["regular_execution_session"]["end"]]]


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
    study_end = pd.Timestamp(rules["study_data_end"]).tz_localize("Asia/Kolkata") + pd.Timedelta(hours=23, minutes=59, seconds=59)
    files = sorted(ROOT.glob("*.parquet"))
    if not files:
        raise SystemExit("PHASE2_E150_IMPACT_SOURCE_EMPTY")

    expiry_stats = {}
    affected_expiries = set()
    affected_contract_groups = 0
    post_session_observations = 0
    gap_observations = 0

    for path in files:
        pf = pq.ParquetFile(path)
        if not {"timestamp", "expiry", "strike", "option_type"}.issubset(pf.schema.names):
            raise SystemExit(f"PHASE2_E150_IMPACT_SCHEMA_FAILURE:{path.name}")
        for batch in pf.iter_batches(batch_size=300_000, columns=["timestamp", "expiry", "strike", "option_type"]):
            df = batch.to_pandas()
            ts = pd.to_datetime(df["timestamp"], errors="coerce")
            ts = ts.dt.tz_localize("Asia/Kolkata") if ts.dt.tz is None else ts.dt.tz_convert("Asia/Kolkata")
            exp = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
            df["timestamp"], df["expiry"] = ts, exp
            df = df[ts.between(pd.Timestamp("2021-01-01", tz="Asia/Kolkata"), study_end) & exp.notna()]
            if df.empty:
                continue
            df["option_type"] = df["option_type"].astype(str).str.upper().str.strip().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
            df = df[df["option_type"].isin(["CE","PE"]) & df["strike"].notna()]
            if df.empty:
                continue
            df["expiry_key"] = df["expiry"].dt.date.astype(str)
            for (expiry_key, strike, opt), g in df.groupby(["expiry_key", "strike", "option_type"], sort=False):
                expiry_ts = pd.Timestamp(expiry_key)
                if expiry_ts > study_end.tz_localize(None).normalize():
                    continue
                if expiry_ts not in set(pd.to_datetime(list({expiry_key})).date):
                    pass
                if g["timestamp"].dt.normalize().max() != expiry_ts:
                    continue
                on_day = g[g["timestamp"].dt.normalize() == expiry_ts]
                if on_day.empty:
                    continue
                latest_raw = on_day["timestamp"].max()
                intervals = intervals_for_date(rules, expiry_key)
                eligible = on_day[on_day["timestamp"].map(lambda x: in_intervals(x, intervals))]
                if eligible.empty:
                    continue
                latest_valid = eligible["timestamp"].max()
                if latest_raw > latest_valid:
                    post_session_observations += 1
                    affected_expiries.add(expiry_key)
                    if any(in_intervals(x, intervals) is False for x in on_day["timestamp"] if x > latest_valid):
                        if expiry_key in {x["date"] for x in rules.get("special_sessions", [])}:
                            gap_observations += 1
                    affected_contract_groups += 1
                    expiry_stats.setdefault(expiry_key, {"contract_groups": 0, "latest_raw": str(latest_raw), "latest_valid": str(latest_valid)})
                    expiry_stats[expiry_key]["contract_groups"] += 1

    result = {
        "status": "COMPLETE",
        "study_data_end": str(study_end),
        "source_files": len(files),
        "affected_expiry_dates": sorted(affected_expiries),
        "affected_contract_groups": affected_contract_groups,
        "post_or_gap_affected_groups": post_session_observations,
        "special_session_gap_affected_groups": gap_observations,
        "expiry_detail": expiry_stats,
        "interpretation": "Affected groups require production scenario rerun before final profitability inference; zero affected groups supports documenting E150/E151 as non-material to observed contract timing, subject to final tester audit."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
