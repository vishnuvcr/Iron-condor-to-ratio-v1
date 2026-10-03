"""Validate Phase 1 control manifests without requiring market-data access.

This is a control-plane validator. It checks that source manifests are parseable,
URLs are explicit, and required gate-specific source categories exist. It does not
claim that the underlying datasets have been acquired or that any gate has passed.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/phase1_control_sources.json"
REQUIRED_GROUPS = {
    "session_sources",
    "contract_sources",
    "risk_free_sources",
    "paytm_money_sources",
    "volatility_context_sources",
}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    missing = REQUIRED_GROUPS.difference(data)
    if missing:
        raise SystemExit(f"missing required source groups: {sorted(missing)}")

    for group in sorted(REQUIRED_GROUPS):
        rows = data[group]
        if not isinstance(rows, list) or not rows:
            raise SystemExit(f"{group}: expected non-empty list")
        for row in rows:
            if not row.get("name"):
                raise SystemExit(f"{group}: source missing name")
            url = row.get("url")
            parsed = urlparse(url or "")
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise SystemExit(f"{group}: invalid URL for {row.get('name')!r}")

    print(
        json.dumps(
            {
                "status": "PASS",
                "manifest": str(MANIFEST.relative_to(ROOT)),
                "groups": {g: len(data[g]) for g in sorted(REQUIRED_GROUPS)},
                "note": "control-plane validation only; no production gate is closed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
