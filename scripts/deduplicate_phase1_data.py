import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path("data/raw")
OUT = Path("data/processed/phase1_deduplicated")
REPORT = Path("data/validation/phase1_dedup_report.json")

OPTION_KEY = ["timestamp", "expiry", "strike", "option_type"]
INDEX_KEY = ["timestamp"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def process(path: Path):
    rel = path.relative_to(ROOT)
    out = OUT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(path)
    is_option = "/options/" in path.as_posix()
    key = OPTION_KEY if is_option else INDEX_KEY
    missing = [c for c in key if c not in df.columns]
    if missing:
        raise RuntimeError(f"{path}: missing deduplication key columns: {missing}")

    dup_mask = df.duplicated(key, keep=False)
    if dup_mask.any():
        value_cols = [c for c in ["open", "high", "low", "close", "volume", "open_interest"] if c in df.columns]
        grouped = df.loc[dup_mask].groupby(key, dropna=False, sort=False)[value_cols].nunique(dropna=False)
        conflicting = int(grouped.gt(1).any(axis=1).sum())
        if conflicting:
            raise RuntimeError(f"{path}: {conflicting} conflicting duplicate key groups")

    before = len(df)
    exact_dups = int(df.duplicated(keep=False).sum())
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    after = len(df)
    df.to_parquet(out, index=False)
    return {
        "file": str(rel),
        "dataset_type": "option" if is_option else "index",
        "input_rows": before,
        "output_rows": after,
        "exact_duplicate_rows_removed": before - after,
        "exact_duplicate_rows_observed": exact_dups,
        "input_sha256": sha256_file(path),
        "output_sha256": sha256_file(out),
    }


def main():
    files = sorted(ROOT.rglob("*.parquet"))
    if not files:
        raise SystemExit("No parquet files found under data/raw")
    records = [process(p) for p in files]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "status": "deterministic_deduplication_complete",
        "input_file_count": len(records),
        "output_file_count": len(records),
        "input_rows": sum(r["input_rows"] for r in records),
        "output_rows": sum(r["output_rows"] for r in records),
        "exact_duplicate_rows_removed": sum(r["exact_duplicate_rows_removed"] for r in records),
        "records": records,
        "rule": "Exact duplicate rows are removed deterministically with keep=first after conflicting duplicate-key groups have been rejected."
    }, indent=2))


if __name__ == "__main__":
    main()
