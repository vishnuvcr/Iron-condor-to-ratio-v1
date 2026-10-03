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


def acquire_one(source: dict, destination: Path) -> tuple[str, dict]:
    """Accept a cache hit only when an immutable expected digest is configured and matches."""
    expected_sha256 = source.get("expected_sha256")
    if destination.exists() and destination.is_file() and destination.stat().st_size > 0:
        payload = destination.read_bytes()
        actual = sha256(payload)
        if not expected_sha256:
            raise RuntimeError("CACHE_PROVENANCE_UNVERIFIED: expected_sha256 is missing")
        if actual != expected_sha256:
            raise RuntimeError(
                f"CACHE_DIGEST_MISMATCH: expected={expected_sha256} actual={actual}"
            )
        return "CACHE_HIT_VALIDATED", {
            "path": str(destination),
            "bytes": len(payload),
            "sha256": actual,
        }

    payload = fetch(source["url"])
    actual = sha256(payload)
    if not expected_sha256:
        raise RuntimeError("SOURCE_PROVENANCE_UNVERIFIED: expected_sha256 is missing")
    if actual != expected_sha256:
        raise RuntimeError(
            f"SOURCE_DIGEST_MISMATCH: expected={expected_sha256} actual={actual}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return "ACQUIRED_VALIDATED", {
        "path": str(destination),
        "bytes": len(payload),
        "sha256": actual,
    }


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
            filename = RAW / f"source_{i:02d}.html"
            mode, meta = acquire_one(source, filename)
            rec.update({
                "status": mode,
                **meta,
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
