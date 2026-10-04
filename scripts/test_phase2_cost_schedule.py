#!/usr/bin/env python3
import json
from pathlib import Path

SCHEDULE=Path("data/costs/phase2_cost_schedule_legacy_pre2022.json")

def rule(rows, charge_type, effective_from):
    hit=[r for r in rows if r["charge_type"]==charge_type and r["effective_from"]==effective_from]
    assert len(hit)==1, (charge_type,effective_from,len(hit))
    return hit[0]

def test_flat_nse_unit_conversion():
    rows=json.loads(SCHEDULE.read_text())["rules"]
    assert abs(rule(rows,"NSE_TRANSACTION","2024-10-01")["rate"] - 3503/10_000_000) < 1e-15
    assert abs(rule(rows,"NSE_TRANSACTION","2026-03-01")["rate"] - 3552.99/10_000_000) < 1e-15

def test_ipft_unit_conversion():
    rows=json.loads(SCHEDULE.read_text())["rules"]
    assert abs(rule(rows,"IPFT","2023-04-01")["rate"] - 50/10_000_000) < 1e-18
    assert abs(rule(rows,"IPFT","2026-03-01")["rate"] - 0.01/10_000_000) < 1e-18

def test_stt_percent_conversion():
    rows=json.loads(SCHEDULE.read_text())["rules"]
    assert abs(rule(rows,"STT","2023-04-01")["rate"] - 0.001) < 1e-15
    assert abs(rule(rows,"STT","2026-04-01")["rate"] - 0.0015) < 1e-15

def test_stamp_duty_conversion():
    rows=json.loads(SCHEDULE.read_text())["rules"]
    assert abs(rule(rows,"STAMP_DUTY","2021-01-01")["rate"] - 0.00003) < 1e-15

if __name__=="__main__":
    for fn in [
        test_flat_nse_unit_conversion,
        test_ipft_unit_conversion,
        test_stt_percent_conversion,
        test_stamp_duty_conversion,
    ]:
        fn()
    print("phase2 cost schedule unit tests passed")


def test_monthly_slab_math():
    from phase2_backtest_engine import CostSchedule
    slabs=(
        {"lower":0,"upper":30_000_000,"flat":2500,"rate":0},
        {"lower":30_000_000,"upper":1_000_000_000,"flat":0,"rate":0.0005},
        {"lower":1_000_000_000,"upper":7_500_000_000,"flat":0,"rate":0.000475},
    )
    assert CostSchedule._monthly_slab_charge(20_000_000,slabs) == 2500
    assert abs(CostSchedule._monthly_slab_charge(50_000_000,slabs) - (2500 + 20_000_000*0.0005)) < 1e-9
