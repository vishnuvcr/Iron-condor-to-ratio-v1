import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path("data/raw")
OUT = Path("data/processed/phase1_deduplicated")
REPORT = Path("data/validation/phase1_dedup_report.json")

OPTION_KEY = ["timestamp", "expiry", "strike", "option_type"]
INDEX_KEY = ["timestamp"]


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def process(path):
    df = pd.read_parquet(path)
    is_option = "/options/" in path.as_posix()
    key = OPTION_KEY if is_option else INDEX_KEY
    before = len(df)

    # Exact duplicates only. Conflicting duplicate keys are rejected.
    value_cols = [c for c in ["open", "high", "low", "close", "volume", "open_interest"] if c in df]
    if is_option:
        grouped = df.groupby(key, dropna=False, sort=False)[value_cols].nunique(dropna=False)
        conflicts = int(grouped.gt(1).any(axis=1).sum())
        if conflicts:
            raise SystemExit(f"Conflicting duplicate keys in {path}: {conflicts}")
        deduped = df.drop_duplicates(keep="first")
    else:
        grouped = df.groupby(key, dropna=False, sort=False)[value_cols].nunique(dropna=False)
        conflicts = int(grouped.gt(1).any(axis=1).sum())
        if conflicts:
            raise SystemExit(f"Conflicting duplicate timestamps in {path}: {conflicts}")
        deduped = df.drop_duplicates(keep="first")

    out = OUT / path.relative_to(ROOT)
    out.parent.mkdir(parents=True, exist_ok=True)
    deduped.to_parquet(out, index=False)

    return {
        "source_file": str(path),
        "output_file": str(out),
        "source_rows": before,
        "output_rows": len(deduped),
        "exact_duplicate_rows_removed": before - len(deduped),
        "source_sha256": sha256_file(path),
        "output_sha256": sha256_file(out),
        "conflicting_duplicate_keys": conflicts,
    }


def main():
    files = sorted(ROOT.rglob("*.parquet"))
    if not files:
        raise SystemExit("No parquet files found")
    reports = [process(p) for p in files]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "status": "deterministic_exact_deduplication_complete",
        "input_file_count": len(reports),
        "input_rows": sum(x["source_rows"] for x in reports),
        "output_rows": sum(x["output_rows"] for x in reports),
        "rows_removed": sum(x["exact_duplicate_rows_removed"] for x in reports),
        "conflicting_duplicate_keys": sum(x["conflicting_duplicate_keys"] for x in reports),
        "rule": "Remove exact duplicate rows only; conflicting duplicate keys are fatal.",
        "files": reports,
    }, indent=2))


if __name__ == "__main__":
    main()
