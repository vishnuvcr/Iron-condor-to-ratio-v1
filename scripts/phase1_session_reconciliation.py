import json
from pathlib import Path

import pandas as pd

INDEX = Path("data/raw/index/NIFTY.parquet")
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase1_session_reconciliation.json")


def minutes(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def in_intervals(value, intervals):
    return any(minutes(start) <= value <= minutes(end) for start, end in intervals)


def interval_counts(values, intervals):
    return [int(sum(minutes(start) <= v <= minutes(end) for v in values)) for start, end in intervals]


def classify_normal(day, eligible_count, control):
    if control:
        expected = control["expected_classification"]
        if expected == "DATA_GAP_EXCLUDED":
            actual = "DATA_GAP_EXCLUDED" if eligible_count < control["minimum_eligible_timestamps"] else "NORMAL_ELIGIBLE"
        else:
            actual = "NORMAL_ELIGIBLE" if eligible_count >= control["minimum_eligible_timestamps"] else "DATA_GAP_EXCLUDED"
        return actual, control["policy"]
    return (
        "NORMAL_ELIGIBLE" if eligible_count >= 300 else "DATA_GAP_EXCLUDED",
        "DEFAULT_NORMAL_SESSION_RULE",
    )


def reconcile_special(day, values, rule):
    execution = rule["execution_intervals"]
    source = rule["source_observation_intervals"]
    execution_counts = interval_counts(values, execution)
    inside_execution = [v for v in values if in_intervals(v, execution)]
    outside_execution = [v for v in values if not in_intervals(v, execution)]
    outside_source = [v for v in outside_execution if not in_intervals(v, source)]
    covered = all(c > 0 for c in execution_counts)
    source_covered = len(outside_source) == 0
    status = "SPECIAL_SESSION_RECONCILED" if covered and source_covered else "SPECIAL_SESSION_UNRECONCILED"
    return status, {
        "execution_interval_counts": execution_counts,
        "execution_intervals_covered": covered,
        "outside_execution_timestamps": len(outside_execution),
        "outside_execution_first_last": (
            [min(outside_execution), max(outside_execution)] if outside_execution else None
        ),
        "outside_documented_source_window_timestamps": len(outside_source),
        "source_observation_intervals_cover_all_observations": source_covered,
    }


def main():
    if not INDEX.exists():
        raise SystemExit("Missing NIFTY index file")

    rules = json.loads(RULES.read_text())
    special = {x["date"]: x for x in rules["special_sessions"]}
    controls = {x["date"]: x for x in rules["date_controls"]}

    if "unresolved_dates" in rules:
        raise SystemExit("Invalid G4 manifest: unresolved_dates escape hatch is prohibited")

    df = pd.read_parquet(INDEX)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).drop_duplicates("timestamp")
    local = df["timestamp"].dt.tz_convert(rules["timezone"])
    df["day"] = local.dt.strftime("%Y-%m-%d")
    df["minute"] = local.dt.hour * 60 + local.dt.minute

    rows = []
    for day, g in df.groupby("day", sort=True):
        values = sorted(int(v) for v in g["minute"].tolist())
        first = values[0]
        last = values[-1]
        count = len(values)

        if day in special:
            status, detail = reconcile_special(day, values, special[day])
            session_type = special[day]["type"]
            expected = "SPECIAL_SESSION_RECONCILED"
            policy = "SPECIAL_INTERVAL_CONTROL"
            mismatch = status != expected
        else:
            start = minutes(rules["regular_execution_session"]["start"])
            end = minutes(rules["regular_execution_session"]["end"])
            eligible = int(sum(start <= v <= end for v in values))
            status, policy = classify_normal(day, eligible, controls.get(day))
            session_type = "NORMAL"
            expected = controls.get(day, {}).get("expected_classification")
            mismatch = expected is not None and status != expected
            detail = {
                "eligible_regular_session_timestamps": eligible,
                "out_of_execution_timestamps": count - eligible,
                "control_present": day in controls,
            }

        rows.append({
            "day": day,
            "observed_timestamps": count,
            "first_local_minute": first,
            "last_local_minute": last,
            "status": status,
            "session_type": session_type,
            "policy": policy,
            "expected_classification": expected,
            "control_mismatch": mismatch,
            "special_source": special.get(day, {}).get("source"),
            "special_source_evidence": special.get(day, {}).get("source_evidence"),
            "date_control_reason": controls.get(day, {}).get("reason"),
            **detail,
        })

    uncontrolled = [
        x for x in rows
        if x["status"] not in {"NORMAL_ELIGIBLE", "DATA_GAP_EXCLUDED", "SPECIAL_SESSION_RECONCILED"}
        or x["control_mismatch"]
    ]

    out = {
        "status": "session_reconciliation_complete",
        "rule_source": str(RULES),
        "observed_dates": len(rows),
        "counts": {
            "normal_eligible": sum(x["status"] == "NORMAL_ELIGIBLE" for x in rows),
            "special_session_reconciled": sum(x["status"] == "SPECIAL_SESSION_RECONCILED" for x in rows),
            "data_gap_excluded": sum(x["status"] == "DATA_GAP_EXCLUDED" for x in rows),
            "unreconciled": len(uncontrolled),
        },
        "controlled_anomaly_dates": [x for x in rows if x["day"] in controls],
        "unreconciled_dates": uncontrolled,
        "rows": rows,
        "acceptance": (
            "PASS_CANDIDATE_NO_UNRECONCILED_DATES"
            if not uncontrolled
            else "FAIL_UNRECONCILED_DATES_PRESENT"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    if uncontrolled:
        raise SystemExit(f"G4 reconciliation failed: {len(uncontrolled)} unreconciled/mismatched date(s)")


if __name__ == "__main__":
    main()
