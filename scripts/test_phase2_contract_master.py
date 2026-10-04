from pathlib import Path
import sys
sys.path.insert(0, "scripts")

from build_phase2_contract_master import lot_rule

def test_historical_monthly_lot_boundaries():
    assert lot_rule("2021-06-24")[0] == 75
    assert lot_rule("2021-07-29")[0] == 50
    assert lot_rule("2024-04-25")[0] == 50
    assert lot_rule("2024-05-30")[0] == 25
    assert lot_rule("2024-11-28")[0] == 25
    assert lot_rule("2024-12-26")[0] == 75
    assert lot_rule("2025-12-30")[0] == 75
    assert lot_rule("2026-01-29")[0] == 65
