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
SESSION_RULES = ROOT / "data/manifests/phase1_session_rules.json"
REQUIRED_GROUPS = {
    "session_sources",
    "contract_sources",
    "risk_free_sources",
    "paytm_money_sources",
    "volatility_context_sources",
}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    session_rules = json.loads(SESSION_RULES.read_text(encoding="utf-8"))
    if "unresolved_dates" in session_rules:
        raise SystemExit("phase1_session_rules.json: unresolved_dates escape hatch is prohibited")
    for required in ("regular_execution_session", "special_sessions", "date_controls", "acceptance_rules"):
        if required not in session_rules:
            raise SystemExit(f"phase1_session_rules.json: missing {required}")
    special_dates = {x.get("date") for x in session_rules["special_sessions"]}
    for row in session_rules["special_sessions"]:
        if not row.get("source_evidence") or not row.get("source_observation_evidence"):
            raise SystemExit(f"special session {row.get('date')}: missing source_evidence")
        if not row.get("execution_intervals") or not row.get("source_observation_intervals"):
            raise SystemExit(f"special session {row.get('date')}: missing interval controls")
    for row in session_rules["date_controls"]:
        if row.get("date") in special_dates:
            raise SystemExit(f"date control {row.get('date')} duplicates a special session")
        if row.get("expected_classification") not in {"NORMAL_ELIGIBLE", "DATA_GAP_EXCLUDED"}:
            raise SystemExit(f"date control {row.get('date')}: invalid expected_classification")
    if "UNRECONCILED" not in session_rules["acceptance_rules"].get("unresolved_rule", ""):
        raise SystemExit("phase1_session_rules.json: unresolved-date acceptance rule missing")
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
                "session_rules": str(SESSION_RULES.relative_to(ROOT)),
                "groups": {g: len(data[g]) for g in sorted(REQUIRED_GROUPS)},
                "note": "control-plane validation only; no production gate is closed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
