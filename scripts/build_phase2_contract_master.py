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
STUDY_END = pd.Timestamp("2026-09-30 23:59:59", tz="Asia/Kolkata")
TICK_SIZE = 0.05

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


def lot_rule(expiry: pd.Timestamp) -> tuple[int, str]:
    e = pd.Timestamp(expiry).normalize()
    for start, end, lot, effective in LOT_RULES:
        if start <= e <= end:
            return lot, effective
    raise RuntimeError(f"PHASE2_CONTRACT_LOT_RULE_MISSING:{e.date()}")


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
            mask = ts.between(STUDY_START, STUDY_END) & exp.notna()
            if mask.any():
                expiries.update(exp.loc[mask].tolist())
    if not expiries:
        raise SystemExit("PHASE2_NO_EXPIRIES")
    frame = pd.DataFrame({"expiry": sorted(expiries)})
    frame["month"] = frame["expiry"].dt.to_period("M")
    monthly = frame.groupby("month")["expiry"].max()
    return set(monthly.tolist())


def main() -> None:
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
                if row.timestamp.normalize() == expiry:
                    if pd.isna(item["expiry_close_ts"]) or row.timestamp > item["expiry_close_ts"]:
                        item["expiry_close_ts"] = row.timestamp

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
        "monthly_expiries": len(monthly_expiries),
        "contracts": len(out),
        "lot_sizes": sorted(out["lot_size"].unique().tolist()),
        "tick_sizes": sorted(out["tick_size"].unique().tolist()),
        "source_files": len(files),
        "source_sha256": {str(p): sha256(p) for p in files},
        "method": "deterministic reconstruction from pinned NIFTY 1-minute option bars plus official NSE lot-size circular chronology; raw-bar lifecycle and expiry-close timestamps retained",
        "source_references": SOURCE_REFS,
        "output_sha256": sha256(OUT),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, default=str))


if __name__ == "__main__":
    main()
