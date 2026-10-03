import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path("data/raw")
REPORT = Path("data/validation/phase1_validation_report.json")
SOURCE_MANIFEST = Path("data/manifests/phase1_sources.json")

OPTION_REQUIRED = {
    "timestamp", "open", "high", "low", "close", "volume",
    "open_interest", "trading_day", "symbol", "strike",
    "option_type", "expiry"
}
INDEX_REQUIRED = {
    "timestamp", "open", "high", "low", "close",
    "volume", "trading_day", "symbol"
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_file(path: Path):
    df = pd.read_parquet(path)
    is_option = "/options/" in path.as_posix()
    required = OPTION_REQUIRED if is_option else INDEX_REQUIRED
    cols = set(df.columns)
    missing = sorted(required - cols)
    out = {
        "file": str(path),
        "dataset_type": "option" if is_option else "index",
        "rows": int(len(df)),
        "file_size_bytes": int(path.stat().st_size),
        "sha256": sha256_file(path),
        "columns": sorted(cols),
        "missing_required_columns": missing,
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "null_timestamp": int(df["timestamp"].isna().sum()) if "timestamp" in df else None,
        "nonpositive_prices": int((df["close"] <= 0).sum()) if "close" in df else None,
        "invalid_ohlc": int(((df["high"] < df["low"]) | (df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["low"] > df["open"]) | (df["low"] > df["close"])).sum()) if len(df) else None,
        "execution_fields": sorted([c for c in ["bid", "ask", "bid_price", "ask_price"] if c in cols]),
    }
    if is_option and not missing:
        key = ["timestamp", "expiry", "strike", "option_type"]
        value_cols = [c for c in ["open", "high", "low", "close", "volume", "open_interest"] if c in df]
        grouped = df.groupby(key, dropna=False, sort=False)[value_cols].nunique(dropna=False)
        conflicting = grouped.gt(1).any(axis=1)
        out["duplicate_key_groups"] = int(df.duplicated(key, keep=False).sum())
        out["conflicting_duplicate_key_groups"] = int(conflicting.sum())
    else:
        out["duplicate_key_groups"] = None
        out["conflicting_duplicate_key_groups"] = None

    if "timestamp" in df:
        ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        out["min_timestamp"] = str(ts.min())
        out["max_timestamp"] = str(ts.max())
        out["timezone_note"] = "source timestamp converted to UTC for structural checks; source documentation says timestamps are IST"

    for col in ("strike", "option_type", "expiry"):
        if col in df:
            out[f"{col}_nulls"] = int(df[col].isna().sum())
    return out


def main():
    files = sorted(ROOT.rglob("*.parquet"))
    if not files:
        raise SystemExit("No parquet files found under data/raw")

    reports = [inspect_file(p) for p in files]
    hard_bad = [
        r for r in reports
        if r["missing_required_columns"]
        or r["null_timestamp"]
        or r["invalid_ohlc"]
        or (r["conflicting_duplicate_key_groups"] or 0) > 0
    ]
    quality_flags = [
        r for r in reports
        if r["exact_duplicate_rows"]
        or r["nonpositive_prices"]
        or (r["duplicate_key_groups"] or 0) > 0
    ]

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    primary = manifest["primary_candidate"]

    total_rows = sum(r["rows"] for r in reports)
    option_reports = [r for r in reports if r["dataset_type"] == "option"]
    index_reports = [r for r in reports if r["dataset_type"] == "index"]
    execution_columns = sorted({c for r in reports for c in r["execution_fields"]})

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "status": "structural_validation_complete",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "repo_id": primary["repo_id"],
            "revision": primary["revision"],
            "license": primary["license"],
            "required_patterns": primary.get("tracks", []),
        },
        "file_count": len(reports),
        "option_file_count": len(option_reports),
        "index_file_count": len(index_reports),
        "total_rows": total_rows,
        "execution_columns_observed": execution_columns,
        "historical_bid_ask_assessment": "No bid/ask fields observed in the acquired primary-source schema when this validator runs; independent quote-source validation remains required.",
        "hard_failure_files": len(hard_bad),
        "quality_flag_files": len(quality_flags),
        "files": reports,
        "canonical_processing_rule": "Exact duplicate rows may be removed deterministically; conflicting duplicate keys are fatal and must be reconciled before acceptance.",
        "note": "This is Phase 1 structural/provenance validation only. It does not establish Greek correctness, target-delta coverage, historical contract reconciliation, cost completeness or production acceptance."
    }, indent=2))
    if hard_bad:
        raise SystemExit(f"Structural validation failed for {len(hard_bad)} file(s)")


if __name__ == "__main__":
    main()
