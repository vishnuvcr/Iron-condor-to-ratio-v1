import json
from pathlib import Path
import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/validation/phase1_session_outlier_report.json")
INDEX = RAW / "index" / "NIFTY.parquet"

def main():
    df = pd.read_parquet(INDEX)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"]).drop_duplicates("timestamp")
    local = df["timestamp"].dt.tz_convert("Asia/Kolkata")
    df["day"] = local.dt.date
    df["minute"] = local.dt.hour * 60 + local.dt.minute
    rows = []
    for day, g in df.groupby("day"):
        n = int(g["timestamp"].nunique())
        if n < 300 or n > 390:
            rows.append({
                "day": str(day),
                "timestamps": n,
                "first_local": str(local.loc[g.index].min()),
                "last_local": str(local.loc[g.index].max()),
                "first_minute": int(g["minute"].min()),
                "last_minute": int(g["minute"].max()),
                "unique_minutes": int(g["minute"].nunique()),
                "close_nonnull": int(g["close"].notna().sum()),
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "status": "session_outlier_characterization_complete",
        "total_trading_days": int(df["day"].nunique()),
        "outlier_rule": "timestamp count <300 or >390",
        "outlier_day_count": len(rows),
        "outliers": rows,
        "interpretation": "No dates are excluded by this diagnostic. Outliers must be reconciled against exchange session/holiday/early-close metadata before any exclusion rule is frozen."
    }, indent=2))

if __name__ == "__main__":
    main()
