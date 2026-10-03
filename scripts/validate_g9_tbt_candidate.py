"""Validate the Hugging Face NIFTY option TBT candidate for G9.

This is a candidate-data audit only. It does not accept the dataset as production
execution evidence. In particular, instrument identity, full study-window coverage,
contract-master reconciliation, and exchange provenance still require validation.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "huggingface_g9_tbt"
OUT = ROOT / "data" / "validation" / "g9_tbt_candidate_report.json"

REPO_ID = "antony9952/Nifty_option_TBT"
REVISION = "643b48383839947b5fe3ed9483c9f7c0f167e865"


def inspect_csv(path: Path) -> dict:
    row_count = 0
    schema = None
    schema_changes = []
    min_ts = None
    max_ts = None
    bidask_rows = 0
    non_bidask_rows = 0
    instrument_keys = set()
    sample_dates = set()

    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        schema = tuple(reader.fieldnames or ())
        for row in reader:
            row_count += 1
            current = tuple(reader.fieldnames or ())
            if current != schema and current not in schema_changes:
                schema_changes.append(current)

            ts = row.get("timestamp") or row.get("received_timestamp") or row.get("feed_timestamp")
            if ts:
                if min_ts is None or ts < min_ts:
                    min_ts = ts
                if max_ts is None or ts > max_ts:
                    max_ts = ts
                sample_dates.add(str(ts)[:10])

            if row.get("bid_price") not in (None, "") and row.get("ask_price") not in (None, ""):
                bidask_rows += 1
            else:
                non_bidask_rows += 1

            key = row.get("instrument_key")
            if key:
                instrument_keys.add(key)

    return {
        "file": str(path.relative_to(ROOT)),
        "rows": row_count,
        "columns": list(schema or ()),
        "bid_ask_columns_present": "bid_price" in (schema or ()) and "ask_price" in (schema or ()),
        "rows_with_bid_and_ask": bidask_rows,
        "rows_without_bid_and_ask": non_bidask_rows,
        "min_timestamp_text": min_ts,
        "max_timestamp_text": max_ts,
        "unique_observed_dates": sorted(sample_dates),
        "unique_instrument_keys": len(instrument_keys),
        "schema_changes_detected": [list(x) for x in schema_changes],
    }


def main() -> None:
    token = None
    import os
    token = os.environ.get("HF_TOKEN")

    local = snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=REVISION,
        local_dir=CACHE,
        cache_dir=ROOT / ".cache" / "huggingface",
        token=token,
        allow_patterns=["*.csv"],
    )

    files = sorted(Path(local).rglob("*.csv"))
    if not files:
        raise SystemExit("G9 TBT candidate: no CSV files acquired")

    reports = [inspect_csv(p) for p in files]
    bidask_files = [r for r in reports if r["bid_ask_columns_present"]]
    all_dates = sorted({d for r in reports for d in r["unique_observed_dates"]})
    total_rows = sum(r["rows"] for r in reports)

    result = {
        "status": "candidate_audit_complete",
        "repository": REPO_ID,
        "revision": REVISION,
        "file_count": len(reports),
        "total_rows": total_rows,
        "files_with_bid_ask_columns": len(bidask_files),
        "observed_dates": all_dates,
        "reports": reports,
        "production_acceptance": "BLOCKED",
        "blockers": [
            "candidate contains/advertises incompatible schemas across files",
            "instrument identity must be mapped to NIFTY contracts",
            "full 2021-2026 study-window coverage is not established",
            "historical exchange provenance and licensing must be independently validated",
            "quote timestamp/age/spread/depth quality rules remain to be tested",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if not bidask_files:
        raise SystemExit("G9 TBT candidate audit: no bid/ask-bearing file found")
    print(json.dumps({
        "status": result["status"],
        "files": len(reports),
        "rows": total_rows,
        "bidask_files": len(bidask_files),
        "observed_dates": all_dates,
        "production_acceptance": "BLOCKED",
    }, indent=2))


if __name__ == "__main__":
    main()
