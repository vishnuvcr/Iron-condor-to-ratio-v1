"""Acquire and hash the official G6 source pages for reproducible provenance.

This step intentionally does not declare G6 PASS. It only captures source material
and acquisition metadata for later full-period parsing/validation.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

MANIFEST = Path("data/manifests/phase1_control_sources.json")
RAW = Path("data/raw/g6_sources")
OUT = Path("data/validation/phase1_g6_source_acquisition.json")


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Iron-condor-to-ratio-v1-research/1.0"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    sources = manifest.get("greek_sources", [])
    if not sources:
        raise SystemExit("No greek_sources in control manifest")

    RAW.mkdir(parents=True, exist_ok=True)
    records = []
    failures = 0

    for i, source in enumerate(sources):
        url = source["url"]
        started = datetime.now(timezone.utc).isoformat()
        rec = {
            "name": source["name"],
            "url": url,
            "started_at_utc": started,
            "status": "UNEXECUTED",
        }
        try:
            payload = fetch(url)
            filename = RAW / f"source_{i:02d}.html"
            filename.write_bytes(payload)
            rec.update({
                "status": "ACQUIRED",
                "path": str(filename),
                "bytes": len(payload),
                "sha256": sha256(payload),
            })
        except Exception as exc:
            failures += 1
            rec.update({
                "status": "ACQUISITION_FAILED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            })
        records.append(rec)
        time.sleep(0.25)

    checkout_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    report = {
        "execution_provenance": {
            "checked_out_commit_sha": checkout_sha,
            "artifact_binding": "Source-acquisition report is generated from the exact Git checkout used by this workflow."
        },
        "gate": "G6",
        "status": "ACQUISITION_COMPLETE" if failures == 0 else "ACQUISITION_INCOMPLETE",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_count": len(sources),
        "failure_count": failures,
        "records": records,
        "acceptance_boundary": (
            "This artifact establishes source acquisition/provenance only. "
            "It is not G6 PASS evidence. Full date-aligned r/q coverage and "
            "production IV/Greek reconstruction remain mandatory."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
