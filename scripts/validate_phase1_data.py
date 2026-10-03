import json
from pathlib import Path
import pandas as pd

ROOT = Path("data/raw")
REPORT = Path("data/validation/phase1_validation_report.json")

EXPECTED = {
    "timestamp", "open", "high", "low", "close", "volume",
    "open_interest", "trading_day", "symbol", "strike",
    "option_type", "expiry"
}

def inspect_file(path: Path):
    df = pd.read_parquet(path)
    cols = set(df.columns)
    missing = sorted(EXPECTED - cols)
    out = {
        "file": str(path),
        "rows": int(len(df)),
        "columns": sorted(cols),
        "missing_required_columns": missing,
        "duplicate_rows": int(df.duplicated().sum()),
        "null_timestamp": int(df["timestamp"].isna().sum()) if "timestamp" in df else None,
        "nonpositive_prices": int((df["close"] <= 0).sum()) if "close" in df else None,
        "invalid_ohlc": int(((df["high"] < df["low"]) | (df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["low"] > df["open"]) | (df["low"] > df["close"])).sum()) if len(df) else None,
    }
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
        if r["missing_required_columns"] or r["duplicate_rows"] or r["null_timestamp"] or r["invalid_ohlc"]
    ]
    quality_flags = [r for r in reports if r["nonpositive_prices"]]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "status": "structural_validation_complete",
        "files": reports,
        "file_count": len(reports),
        "hard_failure_files": len(hard_bad),
        "quality_flag_files": len(quality_flags),
        "note": "Nonpositive prices are reported as quality flags rather than automatic hard failures because sparse option datasets may encode untraded/placeholder observations. Hard structural failures remain fatal."
    }, indent=2))
    if hard_bad:
        raise SystemExit(f"Structural validation failed for {len(hard_bad)} file(s)")

if __name__ == "__main__":
    main()
