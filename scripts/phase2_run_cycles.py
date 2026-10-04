#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from phase2_backtest_engine import BacktestEngine, CostSchedule, EngineConfig


RULES_PATH = Path("data/manifests/phase1_session_rules.json")
UNDERLYING_PATH = Path("data/raw/index/NIFTY.parquet")
NORMALIZED_ROOT = Path("data/processed/phase2/options")


def eligible_entry_dates(index: pd.DataFrame, rules: dict, allowed_days: set[str]) -> pd.Series:
    ts_col = next(c for c in index.columns if c.lower() in {"timestamp", "datetime", "date"})
    ts = pd.to_datetime(index[ts_col], errors="coerce")
    if getattr(ts.dt, "tz", None) is None:
        ts = ts.dt.tz_localize("Asia/Kolkata")
    else:
        ts = ts.dt.tz_convert("Asia/Kolkata")
    local = ts.dt.tz_localize(None)
    day = local.dt.strftime("%Y-%m-%d")
    minute = local.dt.hour * 60 + local.dt.minute
    regular = rules["regular_execution_session"]
    sh, sm = map(int, regular["start"].split(":"))
    eh, em = map(int, regular["end"].split(":"))
    eligible = (
        (local.dt.weekday < 5)
        & (minute >= sh * 60 + sm)
        & (minute <= eh * 60 + em)
    )

    special = {x["date"]: x for x in rules["special_sessions"]}
    for d, rule in special.items():
        mask = day.eq(d)
        if not mask.any():
            continue
        allowed = pd.Series(False, index=ts.index)
        for start, end in rule["execution_intervals"]:
            sh, sm = map(int, start.split(":"))
            eh, em = map(int, end.split(":"))
            allowed |= (minute >= sh * 60 + sm) & (minute <= eh * 60 + em)
        eligible.loc[mask] = allowed.loc[mask]

    controls = {x["date"]: x for x in rules["date_controls"]}
    for d, control in controls.items():
        if control.get("expected_classification") == "DATA_GAP_EXCLUDED":
            eligible.loc[day.eq(d)] = False

    days = pd.DataFrame({"day": local.dt.normalize(), "eligible": eligible})
    days["day_str"] = days["day"].dt.strftime("%Y-%m-%d")
    days = days[days["day_str"].isin(allowed_days)]
    return days.loc[days["eligible"]].groupby("day")["day"].min()


def build_expiry_schedule(expiry_dates: list[pd.Timestamp], entry_days: pd.Series, min_dte: int) -> pd.DataFrame:
    frame = pd.DataFrame({"expiry": pd.to_datetime(sorted(expiry_dates))})
    frame["year"] = frame["expiry"].dt.year
    frame["month"] = frame["expiry"].dt.month
    monthly = frame.groupby(["year", "month"], as_index=False)["expiry"].max().sort_values("expiry")

    rows = []
    for entry_day in entry_days:
        cutoff = pd.Timestamp(entry_day).normalize() + pd.Timedelta(days=min_dte)
        candidates = monthly[monthly["expiry"] >= cutoff]
        if candidates.empty:
            continue
        chosen = candidates.iloc[0]["expiry"]
        rows.append({
            "entry_month": pd.Timestamp(entry_day).strftime("%Y-%m"),
            "entry_day": str(pd.Timestamp(entry_day).date()),
            "expiry": str(pd.Timestamp(chosen).date()),
            "min_dte_days": min_dte,
        })
    schedule = pd.DataFrame(rows)
    if schedule.empty:
        raise RuntimeError("PHASE2_ENTRY_SCHEDULE_EMPTY")
    return schedule.drop_duplicates("entry_month", keep="first")


def run_cycle(normalized_file: Path, entry_day: str, costs: CostSchedule, slippage_bps: float, enable_transitions: bool) -> dict[str, pd.DataFrame]:
    bars = pd.read_parquet(normalized_file)
    start = pd.Timestamp(entry_day).tz_localize("Asia/Kolkata")
    expiry = pd.to_datetime(bars["expiry"]).dropna().min()
    end = pd.Timestamp(expiry).tz_localize("Asia/Kolkata") + pd.Timedelta(days=1)
    bars = bars[(bars["timestamp"] >= start) & (bars["timestamp"] < end)]
    if bars.empty:
        raise RuntimeError(f"PHASE2_CYCLE_EMPTY:{normalized_file.name}:{entry_day}")

    engine = BacktestEngine(
        bars,
        costs,
        EngineConfig(
            entry_min_dte_days=20,
            slippage_bps=slippage_bps,
            enable_transitions=enable_transitions,
        ),
    )
    result = engine.run()
    if bool(result["metadata"].iloc[0]["terminal_unclosed"]):
        raise RuntimeError(f"PHASE2_TERMINAL_UNCLOSED_POSITION:{normalized_file.name}:{entry_day}")
    for name, frame in result.items():
        if "metadata" in name:
            continue
        frame["cycle_entry_day"] = entry_day
        frame["cycle_expiry"] = str(pd.Timestamp(expiry).date())
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalized-root", default=str(NORMALIZED_ROOT))
    ap.add_argument("--costs", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--slippage-bps", type=float, default=10.0)
    ap.add_argument("--static-ic", action="store_true")
    args = ap.parse_args()

    rules = json.loads(RULES_PATH.read_text())
    recon_path = Path("data/validation/phase1_session_reconciliation.json")
    if not recon_path.exists():
        raise SystemExit("PHASE2_G4_RECONCILIATION_MISSING")
    recon = json.loads(recon_path.read_text())
    allowed_days = {
        row["day"] for row in recon.get("rows", [])
        if row["status"] in {"NORMAL_ELIGIBLE", "SPECIAL_SESSION_RECONCILED"}
    }
    if not allowed_days:
        raise SystemExit("PHASE2_G4_NO_ALLOWED_DAYS")
    index = pd.read_parquet(UNDERLYING_PATH)
    entry_days = eligible_entry_dates(index, rules, allowed_days)

    root = Path(args.normalized_root)
    files = sorted(root.glob("*.parquet"))
    if not files:
        raise SystemExit("PHASE2_NORMALIZED_INPUT_EMPTY")

    expiries = [pd.to_datetime(f.stem, errors="raise") for f in files]
    schedule = build_expiry_schedule(expiries, entry_days, 20)
    costs = CostSchedule.from_json(Path(args.costs))

    outputs = {"fills": [], "charges": [], "events": [], "metadata": []}
    for row in schedule.itertuples(index=False):
        file = root / f"{row.expiry}.parquet"
        if not file.exists():
            raise RuntimeError(f"PHASE2_SCHEDULED_EXPIRY_FILE_MISSING:{file}")
        result = run_cycle(file, row.entry_day, costs, args.slippage_bps, enable_transitions=not args.static_ic)
        for key in outputs:
            if key in result and not result[key].empty:
                outputs[key].append(result[key])

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for key, parts in outputs.items():
        frame = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        frame.to_parquet(out / f"{key}.parquet", index=False)
    schedule.to_parquet(out / "entry_schedule.parquet", index=False)

    manifest = {
        "status": "PHASE2_CYCLE_RUN_COMPLETE",
        "slippage_bps": args.slippage_bps,
        "strategy_mode": "STATIC_IRON_CONDOR" if args.static_ic else "IRON_CONDOR_TO_RATIO",
        "cycles_scheduled": int(len(schedule)),
        "cycles_with_output": int(sum(bool(v) for v in outputs["metadata"])),
        "input_partitions": int(len(files)),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
