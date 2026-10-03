import json
from pathlib import Path

import pandas as pd

INDEX = Path("data/raw/index/NIFTY.parquet")
RULES = Path("data/manifests/phase1_session_rules.json")
OUT = Path("data/validation/phase1_session_reconciliation.json")


def minutes(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def classify(day, first_minute, last_minute, count, special):
    if day in special:
        return "SPECIAL_SESSION", special[day]["type"]
    start = minutes("09:15")
    end = minutes("15:30")
    if first_minute >= start and last_minute <= end:
        return "NORMAL_IN_WINDOW", "NORMAL"
    if first_minute < start or last_minute > end:
        return "OUT_OF_WINDOW", "NORMAL_OR_UNRECONCILED"
    return "PARTIAL", "NORMAL"


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
        status, session_type = classify(day, first, last, count, special)
        rows.append({
            "day": day,
            "observed_timestamps": count,
            "first_local_minute": first,
            "last_local_minute": last,
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
            "normal_in_window": sum(x["status"] == "NORMAL_IN_WINDOW" for x in rows),
            "special_session": sum(x["status"] == "SPECIAL_SESSION" for x in rows),
            "out_of_window": sum(x["status"] == "OUT_OF_WINDOW" for x in rows),
            "partial": sum(x["status"] == "PARTIAL" for x in rows),
        },
        "unresolved_dates": [x for x in rows if x["status"] != "NORMAL_IN_WINDOW" and x["status"] != "SPECIAL_SESSION"],
        "rows": rows,
        "acceptance": "DIAGNOSTIC_ONLY_G4_REMAINS_OPEN",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
