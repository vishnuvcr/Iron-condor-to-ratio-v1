#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

RAW_ROOT = Path("data/raw/options/NIFTY")
OUT = Path("data/raw/contracts/nifty_contract_master.parquet")
MANIFEST = Path("data/raw/contracts/nifty_contract_master_manifest.json")
STUDY_START = pd.Timestamp("2021-01-01", tz="Asia/Kolkata")
STUDY_END = None
TICK_SIZE = 0.05
SESSION_RULES = Path("data/manifests/phase1_session_rules.json")

LOT_RULES = [
    # Monthly NIFTY contracts used by this study.
    (pd.Timestamp("2021-01-01"), pd.Timestamp("2021-06-30"), 75, "2020-05-04"),
    (pd.Timestamp("2021-07-01"), pd.Timestamp("2024-04-25"), 50, "2021-06-25"),
    (pd.Timestamp("2024-04-26"), pd.Timestamp("2024-11-28"), 25, "2024-04-26"),
    (pd.Timestamp("2024-11-29"), pd.Timestamp("2025-12-30"), 75, "2024-11-20"),
    (pd.Timestamp("2025-12-31"), pd.Timestamp("2026-09-30"), 65, "2025-10-28"),
]

SOURCE_REFS = [
    "NSE FAOP47854 (2021-03-31)",
    "NSE FAOP61415 (2024-04-02)",
    "NSE FAOP64625 (2024-10-18)",
    "NSE FAOP70616 (2025-10-03)",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ist_ts(series: pd.Series) -> pd.Series:
    x = pd.to_datetime(series, errors="coerce")
    if getattr(x.dt, "tz", None) is None:
        return x.dt.tz_localize("Asia/Kolkata")
    return x.dt.tz_convert("Asia/Kolkata")


def load_study_end() -> pd.Timestamp:
    if not SESSION_RULES.exists():
        raise SystemExit("PHASE2_SESSION_RULES_MISSING_FOR_STUDY_HORIZON")
    rules = json.loads(SESSION_RULES.read_text())
    raw = rules.get("study_data_end")
    if not raw:
        raise SystemExit("PHASE2_SESSION_STUDY_HORIZON_MISSING")
    return pd.Timestamp(raw).tz_localize("Asia/Kolkata") + pd.Timedelta(hours=23, minutes=59, seconds=59)


def lot_rule(expiry: pd.Timestamp) -> tuple[int, str]:
    e = pd.Timestamp(expiry).normalize()
    for start, end, lot, effective in LOT_RULES:
        if start <= e <= end:
            return lot, effective
    raise RuntimeError(f"PHASE2_CONTRACT_LOT_RULE_MISSING:{e.date()}")


def execution_intervals_for_date(expiry: pd.Timestamp) -> list[list[str]]:
    rules = json.loads(SESSION_RULES.read_text())
    d = pd.Timestamp(expiry).date().isoformat()
    special = {x["date"]: x for x in rules.get("special_sessions", [])}
    intervals = special[d]["execution_intervals"] if d in special else [[rules["regular_execution_session"]["start"], rules["regular_execution_session"]["end"]]]
    if not intervals:
        raise SystemExit(f"PHASE2_EXPIRY_EXECUTION_INTERVAL_MISSING:{d}")
    return intervals


def timestamp_in_execution_interval(timestamp: pd.Timestamp, expiry: pd.Timestamp) -> bool:
    if timestamp.normalize() != expiry:
        return False
    local_time = timestamp.tz_convert("Asia/Kolkata").time()
    for start, end in execution_intervals_for_date(expiry):
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        start_t = pd.Timestamp(f"{expiry.date()} {start}", tz="Asia/Kolkata").time()
        end_t = pd.Timestamp(f"{expiry.date()} {end}", tz="Asia/Kolkata").time()
        if start_t <= local_time <= end_t:
            return True
    return False


def execution_intervals_for_date(expiry: pd.Timestamp) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Return explicitly permitted F&O execution intervals for an expiry date."""
    if not SESSION_RULES.exists():
        raise SystemExit("PHASE2_SESSION_RULES_MISSING_FOR_EXPIRY_CLOSE")
    rules = json.loads(SESSION_RULES.read_text())
    d = pd.Timestamp(expiry).date().isoformat()
    horizon = pd.Timestamp(rules["study_data_end"]).date()
    if pd.Timestamp(expiry).date() > horizon:
        raise SystemExit(f"PHASE2_SESSION_RULE_HORIZON_EXCEEDED:{d}>{horizon}")
    special = {x["date"]: x for x in rules.get("special_sessions", [])}
    raw = special[d]["execution_intervals"] if d in special else [[rules["regular_execution_session"]["start"], rules["regular_execution_session"]["end"]]]
    base = pd.Timestamp(expiry).tz_localize("Asia/Kolkata")
    intervals = []
    for start, end in raw:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        intervals.append((base + pd.Timedelta(hours=sh, minutes=sm),
                          base + pd.Timedelta(hours=eh, minutes=em)))
    if not intervals:
        raise SystemExit(f"PHASE2_EXPIRY_EXECUTION_INTERVAL_MISSING:{d}")
    return intervals


def expiry_timestamp_is_executable(timestamp: pd.Timestamp, expiry: pd.Timestamp) -> bool:
    if timestamp.normalize() != expiry:
        return False
    return any(start <= timestamp <= end for start, end in execution_intervals_for_date(expiry))


def expiry_execution_close_ts(expiry: pd.Timestamp) -> pd.Timestamp:
    """Return the latest endpoint of explicitly permitted execution intervals."""
    return max(end for _, end in execution_intervals_for_date(expiry))


def update_expiry_close_ts(current: pd.Timestamp, row_timestamp: pd.Timestamp, expiry: pd.Timestamp) -> pd.Timestamp:
    if expiry_timestamp_is_executable(row_timestamp, expiry):
        if pd.isna(current) or row_timestamp > current:
            return row_timestamp
    return current

def list_files() -> list[Path]:
    files = sorted(RAW_ROOT.glob("*.parquet"))
    if not files:
        raise SystemExit("PHASE2_OPTION_SOURCE_EMPTY")
    return files


def collect_monthly_expiries(files: list[Path]) -> set[pd.Timestamp]:
    expiries: set[pd.Timestamp] = set()
    for path in files:
        pf = pq.ParquetFile(path)
        if "expiry" not in pf.schema.names or "timestamp" not in pf.schema.names:
            raise SystemExit(f"PHASE2_OPTION_SCHEMA_FAILURE:{path.name}")
        for batch in pf.iter_batches(batch_size=300_000, columns=["timestamp", "expiry"]):
            df = batch.to_pandas()
            ts = ist_ts(df["timestamp"])
            exp = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
            mask = ts.between(STUDY_START, STUDY_END) & exp.notna() & (exp <= STUDY_END.normalize())
            if mask.any():
                expiries.update(exp.loc[mask].tolist())
    if not expiries:
        raise SystemExit("PHASE2_NO_EXPIRIES")
    frame = pd.DataFrame({"expiry": sorted(expiries)})
    frame["month"] = frame["expiry"].dt.to_period("M")
    monthly = frame.groupby("month")["expiry"].max()
    return set(monthly.tolist())


def main() -> None:
    global STUDY_END
    STUDY_END = load_study_end()
    files = list_files()
    monthly_expiries = collect_monthly_expiries(files)

    acc: dict[str, dict] = {}
    for path in files:
        pf = pq.ParquetFile(path)
        required = {"timestamp", "expiry", "strike", "option_type"}
        if not required.issubset(pf.schema.names):
            raise SystemExit(f"PHASE2_OPTION_SCHEMA_FAILURE:{path.name}")

        for batch in pf.iter_batches(
            batch_size=300_000,
            columns=["timestamp", "expiry", "strike", "option_type"],
        ):
            df = batch.to_pandas()
            df["timestamp"] = ist_ts(df["timestamp"])
            df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
            df["option_type"] = (
                df["option_type"].astype(str).str.upper().str.strip()
                .replace({"CALL":"CE", "C":"CE", "PUT":"PE", "P":"PE"})
            )
            df = df[
                df["timestamp"].between(STUDY_START, STUDY_END)
                & (df["expiry"] <= STUDY_END.normalize())
                & df["expiry"].isin(monthly_expiries)
                & df["strike"].notna()
                & df["option_type"].isin(["CE", "PE"])
            ]
            for row in df.itertuples(index=False):
                expiry = pd.Timestamp(row.expiry)
                contract_id = (
                    expiry.strftime("%Y-%m-%d")
                    + "|"
                    + f"{float(row.strike):.4f}"
                    + "|"
                    + str(row.option_type)
                )
                item = acc.setdefault(
                    contract_id,
                    {
                        "contract_id": contract_id,
                        "symbol": "NIFTY",
                        "option_type": str(row.option_type),
                        "strike": float(row.strike),
                        "expiry": expiry,
                        "contract_start": row.timestamp,
                        "contract_end": row.timestamp,
                        "expiry_close_ts": pd.NaT,
                    },
                )
                item["contract_start"] = min(item["contract_start"], row.timestamp)
                item["contract_end"] = max(item["contract_end"], row.timestamp)
                item["expiry_close_ts"] = update_expiry_close_ts(
                    item["expiry_close_ts"], row.timestamp, expiry
                )

    rows = []
    for item in acc.values():
        lot, effective = lot_rule(item["expiry"])
        if pd.isna(item["expiry_close_ts"]):
            raise SystemExit(f"PHASE2_EXPIRY_CLOSE_MISSING:{item['contract_id']}")
        item["contract_end"] = item["contract_end"] + pd.Timedelta(minutes=1)
        item["lot_size"] = lot
        item["tick_size"] = TICK_SIZE
        item["source_reference"] = "; ".join(SOURCE_REFS)
        item["source_effective_date"] = pd.Timestamp(effective)
        rows.append(item)

    out = pd.DataFrame(rows).sort_values(["expiry", "strike", "option_type"])
    if out.empty:
        raise SystemExit("PHASE2_CONTRACT_MASTER_EMPTY")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)

    manifest = {
        "status": "PHASE2_MONTHLY_CONTRACT_MASTER_RECONSTRUCTED",
        "study_start": str(STUDY_START),
        "study_end": str(STUDY_END),
        "study_horizon_source": "data/manifests/phase1_session_rules.json:study_data_end",
        "monthly_expiries": len(monthly_expiries),
        "contracts": len(out),
        "lot_sizes": sorted(out["lot_size"].unique().tolist()),
        "tick_sizes": sorted(out["tick_size"].unique().tolist()),
        "source_files": len(files),
        "source_sha256": {str(p): sha256(p) for p in files},
        "method": "deterministic reconstruction from pinned NIFTY 1-minute option bars plus official NSE lot-size chronology; expiry-close requires interval membership and is bounded by the session-rule data horizon",
        "source_references": SOURCE_REFS,
        "output_sha256": sha256(OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, default=str))


if __name__ == "__main__":
    main()
