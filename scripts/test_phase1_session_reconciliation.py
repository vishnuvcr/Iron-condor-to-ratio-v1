import copy

import pandas as pd

from phase1_session_reconciliation import (
    reconcile_observations,
    validate_manifest_mappings,
)


def base_rules():
    return {
        "timezone": "Asia/Kolkata",
        "regular_execution_session": {
            "start": "09:15",
            "end": "15:30",
            "effective_from": "2021-05-07",
            "effective_to": "2026-07-02",
        },
        "special_sessions": [],
        "date_controls": [],
    }


def frame_for(day, hhmm_values):
    timestamps = [
        pd.Timestamp(f"{day} {value}", tz="Asia/Kolkata").tz_convert("UTC")
        for value in hhmm_values
    ]
    return pd.DataFrame({"timestamp": timestamps})


def test_missing_special_date_fails_closed():
    rules = base_rules()
    rules["special_sessions"] = [
        {
            "date": "2025-10-21",
            "type": "MUHURAT",
            "execution_intervals": [["13:45", "14:45"]],
            "source_observation_intervals": [["13:15", "15:15"]],
        }
    ]
    out = reconcile_observations(
        pd.DataFrame({"timestamp": pd.to_datetime([])}), rules
    )
    assert out["counts"]["missing_manifest_session_dates"] == 1
    assert out["counts"]["unreconciled"] == 1
    assert out["rows"][0]["day"] == "2025-10-21"
    assert out["rows"][0]["missing_manifest_session_observations"] is True


def test_unknown_observed_weekend_date_is_unreconciled():
    rules = base_rules()
    out = reconcile_observations(frame_for("2026-01-03", ["09:15"]), rules)
    assert out["counts"]["unreconciled"] == 1
    assert out["rows"][0]["canonical_mapping"] == "UNCONTROLLED_OBSERVED_DATE"


def test_duplicate_manifest_mapping_is_rejected():
    rules = base_rules()
    entry = {
        "date": "2025-10-21",
        "type": "MUHURAT",
        "execution_intervals": [["13:45", "14:45"]],
        "source_observation_intervals": [["13:15", "15:15"]],
    }
    rules["special_sessions"] = [copy.deepcopy(entry), copy.deepcopy(entry)]
    try:
        validate_manifest_mappings(rules)
    except ValueError:
        return
    raise AssertionError("duplicate special-session mapping was accepted")


def test_special_interval_failure_is_unreconciled():
    rules = base_rules()
    rules["special_sessions"] = [
        {
            "date": "2025-10-21",
            "type": "MUHURAT",
            "execution_intervals": [["13:45", "14:45"]],
            "source_observation_intervals": [["13:15", "15:15"]],
        }
    ]
    out = reconcile_observations(
        frame_for("2025-10-21", ["13:20", "15:00"]), rules
    )
    assert out["counts"]["unreconciled"] == 1
    assert out["rows"][0]["status"] == "SPECIAL_SESSION_UNRECONCILED"
    assert out["rows"][0]["execution_intervals_covered"] is False


def main():
    tests = [
        test_missing_special_date_fails_closed,
        test_unknown_observed_weekend_date_is_unreconciled,
        test_duplicate_manifest_mapping_is_rejected,
        test_special_interval_failure_is_unreconciled,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"All {len(tests)} Phase 1 session-reconciliation regression tests passed.")


if __name__ == "__main__":
    main()
