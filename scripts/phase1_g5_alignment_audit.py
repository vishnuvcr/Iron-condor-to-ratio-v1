import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
INDEX = RAW / "index" / "NIFTY.parquet"
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase1_g5_alignment_report.json")

OPTION_KEY = ["timestamp", "expiry", "strike", "option_type"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_ts(series):
    return pd.to_datetime(series, utc=True, errors="coerce")


def minute_value(ts):
    local = ts.dt.tz_convert("Asia/Kolkata")
    return local.dt.hour * 60 + local.dt.minute


def mins(value):
    h, m = map(int, value.split(":"))
    return h * 60 + m


def in_intervals(values, intervals):
    return any(mins(a) <= values <= mins(b) for a, b in intervals)


def build_eligible_index(index_df, rules):
    x = index_df.copy()
    x["timestamp"] = parse_ts(x["timestamp"])
    if x["timestamp"].isna().any():
        raise RuntimeError("G5: index contains unparseable timestamps")
    duplicate_timestamps = int(x.duplicated("timestamp", keep=False).sum())
    if duplicate_timestamps:
        raise RuntimeError(
            f"G5: index contains {duplicate_timestamps} duplicate timestamp rows"
        )
    x = x.sort_values("timestamp").reset_index(drop=True)
    local = x["timestamp"].dt.tz_convert(rules["timezone"])
    x["day"] = local.dt.strftime("%Y-%m-%d")
    x["minute"] = local.dt.hour * 60 + local.dt.minute

    special = {r["date"]: r for r in rules["special_sessions"]}
    controls = {r["date"]: r for r in rules["date_controls"]}
    start = mins(rules["regular_execution_session"]["start"])
    end = mins(rules["regular_execution_session"]["end"])
    eligible = []

    for day, g in x.groupby("day", sort=True):
        if day in special:
            intervals = special[day]["execution_intervals"]
            mask = g["minute"].map(
                lambda v: in_intervals(int(v), intervals)
            )
        else:
            if day in controls and controls[day]["expected_classification"] == "DATA_GAP_EXCLUDED":
                continue
            mask = g["minute"].between(start, end)
        eligible.append(g.loc[mask, "timestamp"])

    if not eligible:
        return set(), x
    return set(pd.concat(eligible).tolist()), x


def current_git_sha():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main():
    if not INDEX.exists():
        raise SystemExit("Missing NIFTY index file")
    if not RULES.exists():
        raise SystemExit("Missing Phase 1 session rules")

    rules = json.loads(RULES.read_text())
    index = pd.read_parquet(INDEX)
    eligible_index, index_diag = build_eligible_index(index, rules)
    index_timestamps = set(index_diag["timestamp"].tolist())

    option_files = sorted((RAW / "options" / "NIFTY").glob("*.parquet"))
    if not option_files:
        raise SystemExit("No NIFTY option files found")

    total = 0
    exact_duplicates = 0
    key_duplicates = 0
    aligned = 0
    in_session = 0
    in_session_aligned = 0
    outside_session = 0
    invalid_timestamp = 0
    missing_index_examples = []
    expiry_days = {}
    source_hashes = []

    for path in option_files:
        source_hashes.append({
            "file": str(path.relative_to(RAW)),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
        df = pd.read_parquet(path)
        total += len(df)
        if "timestamp" not in df.columns:
            raise RuntimeError(f"{path}: missing timestamp")
        missing_key = [c for c in OPTION_KEY if c not in df.columns]
        if missing_key:
            raise RuntimeError(f"{path}: missing G5 key columns {missing_key}")

        invalid_timestamp += int(parse_ts(df["timestamp"]).isna().sum())
        exact_duplicates += int(df.duplicated(keep=False).sum())
        key_duplicates += int(df.duplicated(OPTION_KEY, keep=False).sum())
        df["timestamp"] = parse_ts(df["timestamp"])
        df = df.dropna(subset=["timestamp"]).drop_duplicates(OPTION_KEY, keep="first")

        local = df["timestamp"].dt.tz_convert(rules["timezone"])
        df["day"] = local.dt.strftime("%Y-%m-%d")
        # Session eligibility is determined by the date-specific interval alone;
        # underlying alignment is then tested independently against the NIFTY grid.
        def session_eligible(ts):
            local = ts.tz_convert(rules["timezone"])
            day = local.strftime("%Y-%m-%d")
            minute = local.hour * 60 + local.minute
            if day in {r["date"]: r for r in rules["special_sessions"]}:
                rule = {r["date"]: r for r in rules["special_sessions"]}[day]
                return in_intervals(minute, rule["execution_intervals"])
            control = {r["date"]: r for r in rules["date_controls"]}.get(day)
            if control and control["expected_classification"] == "DATA_GAP_EXCLUDED":
                return False
            return mins(rules["regular_execution_session"]["start"]) <= minute <= mins(rules["regular_execution_session"]["end"])

        df["decision_eligible"] = df["timestamp"].map(session_eligible)
        df["aligned_to_nifty"] = df["timestamp"].isin(index_timestamps)

        aligned += int(df["aligned_to_nifty"].sum())
        in_session += int(df["decision_eligible"].sum())
        in_session_aligned += int(
            df.loc[df["decision_eligible"], "aligned_to_nifty"].sum()
        )
        outside_session += int((~df["decision_eligible"]).sum())

        miss = df.loc[
            df["decision_eligible"] & ~df["aligned_to_nifty"],
            ["timestamp", "expiry", "strike", "option_type"],
        ]
        # Only retain examples that are not explained by an in-session index timestamp.
        # The report is bounded; all counts remain complete.
        if len(missing_index_examples) < 100:
            for row in miss.head(100 - len(missing_index_examples)).itertuples(index=False):
                missing_index_examples.append({
                    "timestamp": str(row.timestamp),
                    "expiry": str(row.expiry),
                    "strike": float(row.strike),
                    "option_type": str(row.option_type),
                })

        for (expiry, day), g in df.groupby(["expiry", "day"], dropna=False):
            key = f"{expiry}|{day}"
            rec = expiry_days.setdefault(
                key,
                {
                    "expiry": str(expiry),
                    "day": str(day),
                    "option_rows": 0,
                    "decision_timestamps": 0,
                    "aligned_decision_timestamps": 0,
                },
            )
            rec["option_rows"] += int(len(g))
            rec["decision_timestamps"] += int(g["decision_eligible"].sum())
            rec["aligned_decision_timestamps"] += int(
                g.loc[g["decision_eligible"], "timestamp"].isin(eligible_index).sum()
            )

    report = {
        "execution_provenance": {
            "checked_out_commit_sha": current_git_sha(),
            "workflow_artifact_binding": "Report generated from the exact Git checkout used by this CI job; tester must compare this SHA with the workflow run checkout SHA and requested research ref."
        },
        "status": "PASS_CANDIDATE" if (
            invalid_timestamp == 0
            and in_session > 0
            and in_session_aligned == in_session
        ) else "FAIL",
        "gate": "G5",
        "method": {
            "option_key": OPTION_KEY,
            "underlying_key": ["timestamp"],
            "timezone": rules["timezone"],
            "decision_eligible_definition": (
                "A source option timestamp is decision-eligible when it falls "
                "inside the date-specific NSE execution interval encoded in "
                "phase1_session_rules.json. Alignment is tested separately by "
                "requiring the exact timestamp to exist in the NIFTY index grid."
            ),
            "outside_session_option_rows_are_retained": True,
            "no_interpolation": True,
        },
        "input_provenance": {
            "index_file": str(INDEX),
            "index_sha256": sha256_file(INDEX),
            "option_file_count": len(option_files),
            "option_files": source_hashes,
        },
        "counts": {
            "raw_option_rows": total,
            "exact_duplicate_rows_observed": exact_duplicates,
            "key_duplicate_rows_observed": key_duplicates,
            "invalid_option_timestamps": invalid_timestamp,
            "option_rows_with_timestamp_in_nifty_grid": aligned,
            "decision_eligible_option_rows": in_session,
            "decision_eligible_rows_with_nifty_timestamp": in_session_aligned,
            "decision_eligible_alignment_fraction": (
                in_session_aligned / in_session if in_session else None
            ),
            "outside_decision_session_rows": outside_session,
        },
        "index": {
            "rows": int(len(index_diag)),
            "unique_timestamps": int(index_diag["timestamp"].nunique()),
            "eligible_nifty_timestamps": len(eligible_index),
        },
        "missing_index_examples": missing_index_examples,
        "expiry_day_coverage": list(expiry_days.values()),
        "acceptance": {
            "rule": (
                "PASS candidate requires zero invalid option timestamps, "
                "zero duplicate underlying timestamps, and 100% alignment "
                "of decision-eligible option rows to an observed NIFTY "
                "timestamp. No missing timestamp is interpolated."
            ),
            "invalid_timestamp_check": invalid_timestamp == 0,
            "decision_alignment_check": (
                in_session > 0 and in_session_aligned == in_session
            ),
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str))

    if report["status"] != "PASS_CANDIDATE":
        raise SystemExit(
            "G5 alignment audit failed; see data/validation/phase1_g5_alignment_report.json"
        )


if __name__ == "__main__":
    main()

# Exact-tip CI control marker: validated by the Phase 1 workflow.
