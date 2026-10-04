#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

SCHEDULE = Path("data/costs/phase2_cost_schedule_legacy_pre2022.json")
START = date(2021, 1, 1)
END = date(2026, 9, 30)

REQUIRED = {
    ("BROKERAGE", "BUY"),
    ("BROKERAGE", "SELL"),
    ("NSE_TRANSACTION", "BUY"),
    ("NSE_TRANSACTION", "SELL"),
    ("IPFT", "BUY"),
    ("IPFT", "SELL"),
    ("SEBI", "BUY"),
    ("SEBI", "SELL"),
    ("STT", "BUY"),
    ("STT", "SELL"),
    ("STAMP_DUTY", "BUY"),
    ("STAMP_DUTY", "SELL"),
}

def parse_day(s: str) -> date:
    return date.fromisoformat(s)

def active(rule, d, side):
    start = parse_day(rule["effective_from"])
    end = parse_day(rule["effective_to"]) if rule.get("effective_to") else None
    return start <= d and (end is None or d < end) and (rule.get("side", "ALL") in {"ALL", side})

def rules_for(rows, charge_type, d, side):
    return [r for r in rows if r["charge_type"] == charge_type and active(r, d, side)]

def test_date_and_side_coverage(data):
    rows = data["rules"]
    d = START
    while d <= END:
        for charge_type, side in REQUIRED:
            hits = rules_for(rows, charge_type, d, side)
            assert len(hits) == 1, (d, charge_type, side, len(hits))
        d += timedelta(days=1)

def test_no_invalid_rates(data):
    for rule in data["rules"]:
        assert float(rule.get("rate", 0.0)) >= 0.0
        assert float(rule.get("fixed_per_order", 0.0)) >= 0.0
        if rule.get("method", "RATE") == "MONTHLY_SLAB":
            slabs = rule.get("slabs", [])
            assert slabs
            previous = 0.0
            for i, slab in enumerate(slabs):
                lower = float(slab["lower"])
                upper = slab.get("upper")
                assert lower >= previous
                if upper is not None:
                    upper = float(upper)
                    assert upper > lower
                    previous = upper
                else:
                    assert i == len(slabs) - 1
            assert previous > 0.0

def test_source_metadata(data):
    assert data["metadata"]["scenario"]
    assert data["metadata"]["brokerage_cohort"]
    assert len(data["metadata"]["sources"]) >= 8

if __name__ == "__main__":
    data = json.loads(SCHEDULE.read_text())
    test_date_and_side_coverage(data)
    test_no_invalid_rates(data)
    test_source_metadata(data)
    print("phase2 cost schedule validation passed")
