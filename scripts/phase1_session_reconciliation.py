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
    return [
        int(sum(minutes(start) <= v <= minutes(end) for v in values))
        for start, end in intervals
    ]


def validate_manifest_mappings(rules):
    special_dates = [x["date"] for x in rules["special_sessions"]]
    control_dates = [x["date"] for x in rules["date_controls"]]

    duplicate_special = sorted(
        {d for d in special_dates if special_dates.count(d) > 1}
    )
    duplicate_controls = sorted(
        {d for d in control_dates if control_dates.count(d) > 1}
    )
    overlap = sorted(set(special_dates) & set(control_dates))

    if duplicate_special or duplicate_controls or overlap:
        raise ValueError(
            "Invalid G4 manifest mapping: "
            f"duplicate_special={duplicate_special}, "
            f"duplicate_controls={duplicate_controls}, "
            f"special_control_overlap={overlap}"
        )


def classify_normal(day, eligible_count, control):
    if control:
        expected = control["expected_classification"]
        if expected == "DATA_GAP_EXCLUDED":
            actual = (
                "DATA_GAP_EXCLUDED"
                if eligible_count < control["minimum_eligible_timestamps"]
                else "NORMAL_ELIGIBLE"
            )
        else:
            actual = (
                "NORMAL_ELIGIBLE"
                if eligible_count >= control["minimum_eligible_timestamps"]
                else "DATA_GAP_EXCLUDED"
            )
        return actual, control["policy"]

    return (
        "NORMAL_ELIGIBLE" if eligible_count >= 300 else "DATA_GAP_EXCLUDED",
        "DEFAULT_NORMAL_SESSION_RULE",
    )


def reconcile_special(day, values, rule):
    execution = rule["execution_intervals"]
    source = rule["source_observation_intervals"]
    execution_counts = interval_counts(values, execution)
    outside_execution = [v for v in values if not in_intervals(v, execution)]
    outside_source = [
        v for v in outside_execution if not in_intervals(v, source)
    ]
    covered = all(c > 0 for c in execution_counts)
    source_covered = len(outside_source) == 0
    status = (
        "SPECIAL_SESSION_RECONCILED"
        if covered and source_covered
        else "SPECIAL_SESSION_UNRECONCILED"
    )
    return status, {
        "execution_interval_counts": execution_counts,
        "execution_intervals_covered": covered,
        "outside_execution_timestamps": len(outside_execution),
        "outside_execution_first_last": (
            [min(outside_execution), max(outside_execution)]
            if outside_execution
            else None
        ),
        "outside_documented_source_window_timestamps": len(outside_source),
        "source_observation_intervals_cover_all_observations": source_covered,
    }


def reconcile_observations(df, rules):
    validate_manifest_mappings(rules)

    special = {x["date"]: x for x in rules["special_sessions"]}
    controls = {x["date"]: x for x in rules["date_controls"]}

    working = df.copy()
    working["timestamp"] = pd.to_datetime(
        working["timestamp"], utc=True, errors="coerce"
    )
    working = working.dropna(subset=["timestamp"]).drop_duplicates("timestamp")
    local = working["timestamp"].dt.tz_convert(rules["timezone"])
    working["day"] = local.dt.strftime("%Y-%m-%d")
    working["minute"] = local.dt.hour * 60 + local.dt.minute

    observed_days = set(working["day"].tolist())
    manifest_days = set(special) | set(controls)
    all_days = sorted(observed_days | manifest_days)

    effective_from = rules["regular_execution_session"]["effective_from"]
    effective_to = rules["regular_execution_session"]["effective_to"]
    rows = []

    for day in all_days:
        group = working.loc[working["day"] == day]
        values = sorted(int(v) for v in group["minute"].tolist())
        count = len(values)

        if day in special and day in controls:
            raise ValueError(
                f"Canonical session mapping is not one-to-one for {day}: "
                "special_sessions and date_controls both claim the date"
            )

        if day in special:
            if not values:
                rows.append(
                    {
                        "day": day,
                        "observed_timestamps": 0,
                        "first_local_minute": None,
                        "last_local_minute": None,
                        "status": "UNRECONCILED",
                        "session_type": special[day]["type"],
                        "canonical_mapping": "SPECIAL_SESSION",
                        "policy": "SPECIAL_INTERVAL_CONTROL",
                        "expected_classification": "SPECIAL_SESSION_RECONCILED",
                        "control_mismatch": True,
                        "missing_manifest_session_observations": True,
                        "special_source": special[day].get("source"),
                        "special_source_evidence": special[day].get(
                            "source_evidence"
                        ),
                        "date_control_reason": None,
                    }
                )
                continue

            status, detail = reconcile_special(day, values, special[day])
            rows.append(
                {
                    "day": day,
                    "observed_timestamps": count,
                    "first_local_minute": values[0],
                    "last_local_minute": values[-1],
                    "status": status,
                    "session_type": special[day]["type"],
                    "canonical_mapping": "SPECIAL_SESSION",
                    "policy": "SPECIAL_INTERVAL_CONTROL",
                    "expected_classification": "SPECIAL_SESSION_RECONCILED",
                    "control_mismatch": status
                    != "SPECIAL_SESSION_RECONCILED",
                    "missing_manifest_session_observations": False,
                    "special_source": special[day].get("source"),
                    "special_source_evidence": special[day].get(
                        "source_evidence"
                    ),
                    "date_control_reason": None,
                    **detail,
                }
            )
            continue

        if day in controls and not values:
            rows.append(
                {
                    "day": day,
                    "observed_timestamps": 0,
                    "first_local_minute": None,
                    "last_local_minute": None,
                    "status": "UNRECONCILED",
                    "session_type": "NORMAL",
                    "canonical_mapping": "DATE_CONTROL",
                    "policy": controls[day]["policy"],
                    "expected_classification": controls[day][
                        "expected_classification"
                    ],
                    "control_mismatch": True,
                    "missing_manifest_session_observations": True,
                    "special_source": None,
                    "special_source_evidence": None,
                    "date_control_reason": controls[day].get("reason"),
                }
            )
            continue

        if not values:
            continue

        if not (effective_from <= day <= effective_to):
            status = "UNRECONCILED"
            policy = "OUTSIDE_EFFECTIVE_STUDY_RANGE"
            expected = None
            mismatch = True
            detail = {
                "eligible_regular_session_timestamps": 0,
                "out_of_execution_timestamps": count,
                "control_present": day in controls,
            }
            session_type = "OUT_OF_SCOPE"
            mapping = "UNCONTROLLED_OBSERVED_DATE"
        elif pd.Timestamp(day).weekday() >= 5:
            status = "UNRECONCILED"
            policy = "WEEKEND_WITHOUT_SPECIAL_SESSION_CONTROL"
            expected = None
            mismatch = True
            detail = {
                "eligible_regular_session_timestamps": 0,
                "out_of_execution_timestamps": count,
                "control_present": False,
            }
            session_type = "UNCONTROLLED"
            mapping = "UNCONTROLLED_OBSERVED_DATE"
        else:
            start = minutes(rules["regular_execution_session"]["start"])
            end = minutes(rules["regular_execution_session"]["end"])
            eligible = int(sum(start <= v <= end for v in values))
            status, policy = classify_normal(
                day, eligible, controls.get(day)
            )
            expected = controls.get(day, {}).get("expected_classification")
            mismatch = expected is not None and status != expected
            detail = {
                "eligible_regular_session_timestamps": eligible,
                "out_of_execution_timestamps": count - eligible,
                "control_present": day in controls,
            }
            session_type = "NORMAL"
            mapping = (
                "DATE_CONTROL"
                if day in controls
                else "REGULAR_SESSION_RULE"
            )

        rows.append(
            {
                "day": day,
                "observed_timestamps": count,
                "first_local_minute": values[0],
                "last_local_minute": values[-1],
                "status": status,
                "session_type": session_type,
                "canonical_mapping": mapping,
                "policy": policy,
                "expected_classification": expected,
                "control_mismatch": mismatch,
                "missing_manifest_session_observations": False,
                "special_source": None,
                "special_source_evidence": None,
                "date_control_reason": controls.get(day, {}).get("reason"),
                **detail,
            }
        )

    uncontrolled = [
        x
        for x in rows
        if x["status"]
        not in {
            "NORMAL_ELIGIBLE",
            "DATA_GAP_EXCLUDED",
            "SPECIAL_SESSION_RECONCILED",
        }
        or x["control_mismatch"]
    ]
    missing_manifest = [
        x for x in rows if x["missing_manifest_session_observations"]
    ]

    return {
        "status": "session_reconciliation_complete",
        "rule_source": str(RULES),
        "bidirectional_reconciliation": True,
        "observed_dates": len(observed_days),
        "manifest_control_dates": len(manifest_days),
        "counts": {
            "normal_eligible": sum(
                x["status"] == "NORMAL_ELIGIBLE" for x in rows
            ),
            "special_session_reconciled": sum(
                x["status"] == "SPECIAL_SESSION_RECONCILED"
                for x in rows
            ),
            "data_gap_excluded": sum(
                x["status"] == "DATA_GAP_EXCLUDED" for x in rows
            ),
            "unreconciled": len(uncontrolled),
            "missing_manifest_session_dates": len(missing_manifest),
        },
        "controlled_anomaly_dates": [
            x for x in rows if x["day"] in controls
        ],
        "missing_manifest_session_dates": missing_manifest,
        "unreconciled_dates": uncontrolled,
        "rows": rows,
        "acceptance": (
            "PASS_CANDIDATE_NO_UNRECONCILED_DATES"
            if not uncontrolled
            else "FAIL_UNRECONCILED_DATES_PRESENT"
        ),
    }


def main():
    if not INDEX.exists():
        raise SystemExit("Missing NIFTY index file")

    rules = json.loads(RULES.read_text())
    try:
        out = reconcile_observations(pd.read_parquet(INDEX), rules)
    except ValueError as exc:
        raise SystemExit(f"G4 manifest/reconciliation failed: {exc}") from exc

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))

    if out["unreconciled_dates"]:
        raise SystemExit(
            "G4 reconciliation failed: "
            f"{len(out['unreconciled_dates'])} "
            "unreconciled/mismatched date(s)"
        )


if __name__ == "__main__":
    main()
