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


def test_post_session_observation_cannot_extend_expiry_close_ts():
    import json
    import tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2025-10-30")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({"regular_execution_session":{"end":"15:30"},"special_sessions":[]}))
        original = m.SESSION_RULES
        try:
            m.SESSION_RULES = p
            valid = expiry.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=15, minutes=30)
            post = expiry.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=15, minutes=31)
            current = m.update_expiry_close_ts(pd.NaT, valid, expiry)
            assert current == valid
            assert m.update_expiry_close_ts(current, post, expiry) == valid
        finally:
            m.SESSION_RULES = original
