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
        p.write_text(json.dumps({"study_data_end":"2026-07-02","regular_execution_session":{"start":"09:15","end":"15:30"},"special_sessions":[]}))
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


def test_special_session_gap_observation_is_rejected():
    import json
    import tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2024-03-02")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({"study_data_end":"2026-07-02","regular_execution_session":{"start":"09:15","end":"15:30"},
                                 "special_sessions":[{"date":"2024-03-02","execution_intervals":[["09:15","10:00"],["11:30","12:30"]]}]}))
        original = m.SESSION_RULES
        try:
            m.SESSION_RULES = p
            gap = expiry.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=10, minutes=30)
            valid = expiry.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=12, minutes=30)
            assert not m.expiry_timestamp_is_executable(gap, expiry)
            assert m.expiry_timestamp_is_executable(valid, expiry)
            assert pd.isna(m.update_expiry_close_ts(pd.NaT, gap, expiry))
            assert m.update_expiry_close_ts(pd.NaT, valid, expiry) == valid
        finally:
            m.SESSION_RULES = original


def test_special_session_gap_is_not_executable():
    import json, tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2024-03-02")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({
            "study_data_end":"2026-07-02",
            "regular_execution_session":{"start":"09:15","end":"15:30"},
            "special_sessions":[{"date":"2024-03-02","execution_intervals":[["09:15","10:00"],["11:30","12:30"]]}]
        }))
        original=m.SESSION_RULES
        try:
            m.SESSION_RULES=p
            gap=expiry.tz_localize("Asia/Kolkata")+pd.Timedelta(hours=10,minutes=30)
            second=expiry.tz_localize("Asia/Kolkata")+pd.Timedelta(hours=12,minutes=0)
            assert not m.expiry_timestamp_is_executable(gap, expiry)
            assert m.expiry_timestamp_is_executable(second, expiry)
            assert pd.isna(m.update_expiry_close_ts(pd.NaT, gap, expiry))
            assert m.update_expiry_close_ts(pd.NaT, second, expiry) == second
        finally:
            m.SESSION_RULES=original


def test_session_horizon_is_fail_closed():
    import json, tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2026-07-03")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({
            "study_data_end":"2026-07-02",
            "regular_execution_session":{"start":"09:15","end":"15:30"},
            "special_sessions":[]
        }))
        original=m.SESSION_RULES
        try:
            m.SESSION_RULES=p
            try:
                m.execution_intervals_for_date(expiry)
                raise AssertionError("expected session-horizon failure")
            except SystemExit as exc:
                assert "PHASE2_SESSION_RULE_HORIZON_EXCEEDED" in str(exc)
        finally:
            m.SESSION_RULES=original


def test_expiry_timezone_normalization_accepts_naive_and_aware_equivalents():
    import json
    import tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2025-10-30")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({"study_data_end":"2026-07-02","regular_execution_session":{"start":"09:15","end":"15:30"},"special_sessions":[]}))
        original = m.SESSION_RULES
        try:
            m.SESSION_RULES = p
            aware = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
            naive = pd.Timestamp("2025-10-30 15:30")
            assert m.expiry_timestamp_is_executable(aware, expiry)
            assert m.expiry_timestamp_is_executable(naive, expiry)
            assert m.update_expiry_close_ts(pd.NaT, aware, expiry) == aware
            assert m.update_expiry_close_ts(pd.NaT, naive, expiry) == aware.tz_localize(None)
        finally:
            m.SESSION_RULES = original


def test_expiry_timezone_mismatch_is_not_treated_as_calendar_mismatch():
    import json
    import tempfile
    import pandas as pd
    import build_phase2_contract_master as m
    expiry = pd.Timestamp("2025-10-30")
    with tempfile.TemporaryDirectory() as td:
        p = __import__("pathlib").Path(td) / "rules.json"
        p.write_text(json.dumps({"study_data_end":"2026-07-02","regular_execution_session":{"start":"09:15","end":"15:30"},"special_sessions":[]}))
        original = m.SESSION_RULES
        try:
            m.SESSION_RULES = p
            ts = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
            assert m.expiry_timestamp_is_executable(ts, expiry)
            assert not m.expiry_timestamp_is_executable(
                pd.Timestamp("2025-10-29 15:30", tz="Asia/Kolkata"), expiry
            )
        finally:
            m.SESSION_RULES = original
