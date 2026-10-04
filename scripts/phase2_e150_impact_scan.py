#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path("data/raw/options/NIFTY")
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase2_e150_impact_scan.json")


def normalize_ts(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    if getattr(x.dt, "tz", None) is None:
        return x.dt.tz_localize("Asia/Kolkata")
    return x.dt.tz_convert("Asia/Kolkata")


def interval_bounds(expiry: pd.Timestamp, rules: dict) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    d = expiry.date().isoformat()
    horizon = pd.Timestamp(rules["study_data_end"]).date()
    if expiry.date() > horizon:
        raise SystemExit(f"E150_IMPACT_SESSION_HORIZON_EXCEEDED:{d}>{horizon}")
    special = {x["date"]: x for x in rules.get("special_sessions", [])}
    raw = special[d]["execution_intervals"] if d in special else [[rules["regular_execution_session"]["start"], rules["regular_execution_session"]["end"]]]
    base = pd.Timestamp(expiry).tz_localize("Asia/Kolkata")
    out = []
    for start, end in raw:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        out.append((base + pd.Timedelta(hours=sh, minutes=sm),
                    base + pd.Timedelta(hours=eh, minutes=em)))
    return out


def as_ist(value: pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    return ts.tz_localize("Asia/Kolkata") if ts.tzinfo is None else ts.tz_convert("Asia/Kolkata")


def executable(ts: pd.Timestamp, expiry: pd.Timestamp, intervals: list[tuple[pd.Timestamp, pd.Timestamp]]) -> bool:
    ts = as_ist(ts)
    expiry = as_ist(expiry)
    return ts.normalize() == expiry.normalize() and any(start <= ts <= end for start, end in intervals)


def classify_close_impact(old_close: pd.Timestamp, corrected_close: pd.Timestamp) -> str | None:
    old_present = pd.notna(old_close)
    corrected_present = pd.notna(corrected_close)
    if not old_present and not corrected_present:
        return None
    if old_present and corrected_present and as_ist(old_close) == as_ist(corrected_close):
        return None
    if old_present and corrected_present:
        return "changed"
    if old_present:
        return "old_only"
    return "corrected_only"


def main() -> None:
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
            df["timestamp"] = normalize_ts(df["timestamp"])
            df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
            df["option_type"] = df["option_type"].astype(str).str.upper().str.strip().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
            df = df[
                df["timestamp"].between(study_start, study_end)
                & df["expiry"].notna()
                & (df["expiry"] <= pd.Timestamp(rules["study_data_end"]).date())
                & df["strike"].notna()
                & df["option_type"].isin(["CE", "PE"])
                & (df["timestamp"].dt.normalize() == df["expiry"])
            ]
            for row in df.itertuples(index=False):
                exp = pd.Timestamp(row.expiry)
                intervals = interval_bounds(exp, rules)
                max_endpoint = max(end for _, end in intervals)
                key = (exp.date().isoformat(), float(row.strike), str(row.option_type))
                rec = groups.setdefault(key, {
                    "expiry": exp,
                    "old_close": pd.NaT,
                    "corrected_close": pd.NaT,
                    "old_candidate_count": 0,
                    "gap_candidate_count": 0,
                    "post_session_count": 0,
                })
                # Reproduce the pre-E151 semantics: accept any expiry-day
                # observation up to the latest interval endpoint, regardless
                # of membership in an interval.
                if row.timestamp <= max_endpoint:
                    rec["old_candidate_count"] += 1
                    if pd.isna(rec["old_close"]) or row.timestamp > rec["old_close"]:
                        rec["old_close"] = row.timestamp
                if executable(row.timestamp, exp, intervals):
                    if pd.isna(rec["corrected_close"]) or row.timestamp > rec["corrected_close"]:
                        rec["corrected_close"] = row.timestamp
                elif row.timestamp <= max_endpoint:
                    rec["gap_candidate_count"] += 1
                else:
                    rec["post_session_count"] += 1

    affected = []
    classification_counts = {"changed": 0, "old_only": 0, "corrected_only": 0}
    for key, rec in groups.items():
        old_close = rec["old_close"]
        corrected_close = rec["corrected_close"]
        old_present = pd.notna(old_close)
        corrected_present = pd.notna(corrected_close)
        category = classify_close_impact(old_close, corrected_close)
        if category is None:
            continue
        if category == "changed"
            extension_seconds = (old_close - corrected_close).total_seconds()
        elif category == "old_only":
            extension_seconds = None
        else:
            extension_seconds = None
        classification_counts[category] += 1
        affected.append({
            "contract_id": f"{key[0]}|{key[1]:.4f}|{key[2]}",
            "classification": category,
            "old_expiry_close_ts": str(old_close) if old_present else None,
            "corrected_expiry_close_ts": str(corrected_close) if corrected_present else None,
            "extension_seconds": extension_seconds,
            "gap_candidate_count": int(rec["gap_candidate_count"]),
            "post_session_count": int(rec["post_session_count"]),
        })

    result = {
        "status": "COMPLETE",
        "study_data_end": str(study_end),
        "source_files": len(files),
        "contracts_scanned": len(groups),
        "affected_contract_groups": len(affected),
        "affected_classification_counts": classification_counts,
        "affected_expiry_dates": sorted({x["contract_id"].split("|")[0] for x in affected}),
        "special_gap_affected_groups": sum(1 for x in affected if x["gap_candidate_count"] > 0),
        "max_extension_seconds": max((x["extension_seconds"] for x in affected), default=0.0),
        "examples": affected[:20],
        "interpretation": "Zero affected groups supports a non-material E150/E151 chronology assessment at the contract-close layer. Any changed, old-only, or corrected-only group is affected and requires affected production scenario reruns before final profitability inference.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
