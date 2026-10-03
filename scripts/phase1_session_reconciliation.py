import json
from pathlib import Path

import pandas as pd

INDEX = Path("data/raw/index/NIFTY.parquet")
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase1_session_reconciliation.json")


def minutes(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def classify(day, first_minute, last_minute, count, eligible_count, special):
    if day in special:
        return "SPECIAL_SESSION", special[day]["type"]
    if eligible_count >= 300:
        return "NORMAL_ELIGIBLE", "NORMAL"
    return "DATA_GAP_EXCLUDED", "NORMAL_INCOMPLETE"


def main():
    if not INDEX.exists():
        raise SystemExit("Missing NIFTY index file")
    rules = json.loads(RULES.read_text())
    special = {x["date"]: x for x in rules["special_sessions"]}

    df = pd.read_parquet(INDEX)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).drop_duplicates("timestamp")
    local = df["timestamp"].dt.tz_convert("Asia/Kolkata")
    df["day"] = local.dt.strftime("%Y-%m-%d")
    df["minute"] = local.dt.hour * 60 + local.dt.minute

    rows = []
    for day, g in df.groupby("day", sort=True):
        first = int(g["minute"].min())
        last = int(g["minute"].max())
        count = int(g["timestamp"].nunique())
        eligible = int(((g["minute"] >= minutes("09:15")) & (g["minute"] <= minutes("15:30"))).sum())
        status, session_type = classify(day, first, last, count, eligible, special)
        rows.append({
            "day": day,
            "observed_timestamps": count,
            "first_local_minute": first,
            "last_local_minute": last,
            "eligible_regular_session_timestamps": eligible,
            "out_of_window_timestamps": count - eligible,
            "status": status,
            "session_type": session_type,
            "special_source": special.get(day, {}).get("source"),
            "execution_window": "09:15-15:30 unless explicitly classified as special session",
        })

    out = {
        "status": "session_reconciliation_diagnostic_complete",
        "rule_source": str(RULES),
        "observed_dates": len(rows),
        "counts": {
            "normal_eligible": sum(x["status"] == "NORMAL_ELIGIBLE" for x in rows),
            "special_session": sum(x["status"] == "SPECIAL_SESSION" for x in rows),
            "data_gap_excluded": sum(x["status"] == "DATA_GAP_EXCLUDED" for x in rows),
        },
        "unresolved_dates": [x for x in rows if x["status"] == "DATA_GAP_EXCLUDED"],
        "rows": rows,
        "acceptance": "PRE_REGISTERED_EXCLUSION_APPLIED; G4_REQUIRES_INDEPENDENT_REVIEW",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
