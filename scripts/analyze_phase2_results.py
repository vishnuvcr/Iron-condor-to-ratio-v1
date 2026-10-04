#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def signed_cash(row: pd.Series) -> float:
    qty = abs(int(row["lots"])) * int(row["lot_size"])
    value = qty * float(row["fill_price"])
    return -value if row["side"] == "BUY" else value


def summarize(result_dir: Path, seed: int = 20261004) -> dict:
    fills = pd.read_parquet(result_dir / "fills.parquet") if (result_dir / "fills.parquet").exists() else pd.DataFrame()
    charges = pd.read_parquet(result_dir / "charges.parquet") if (result_dir / "charges.parquet").exists() else pd.DataFrame()
    events = pd.read_parquet(result_dir / "events.parquet") if (result_dir / "events.parquet").exists() else pd.DataFrame()

    if fills.empty:
        return {
            "status": "NO_FILLED_TRADES",
            "net_pnl": 0.0,
            "gross_trade_cash": 0.0,
            "cost_drag": 0.0,
            "slippage_drag": 0.0,
            "cycles": 0,
            "adjustment_events": 0,
            "failed_events": 0,
        }

    fills["gross_cash"] = fills.apply(signed_cash, axis=1)
    gross = float(fills["gross_cash"].sum())
    slippage_drag = float((fills["slippage"] * abs(fills["lots"]) * fills["lot_size"]).sum())
    cost_drag = float(charges["amount"].sum()) if not charges.empty else 0.0
    net = gross - cost_drag

    cycle = (
        fills.groupby(["cycle_entry_day", "cycle_expiry"], dropna=False)["gross_cash"]
        .sum()
        .rename("gross_cash")
        .reset_index()
    )
    if not charges.empty:
        group_cost = charges.groupby("order_group_id")["amount"].sum().rename("group_cost")
        group_cycle = fills[["order_group_id", "cycle_entry_day", "cycle_expiry"]].drop_duplicates("order_group_id")
        group_cost = group_cycle.join(group_cost, on="order_group_id")
        cycle_cost = group_cost.groupby(["cycle_entry_day", "cycle_expiry"])["group_cost"].sum().reset_index(name="cost")
        cycle = cycle.merge(cycle_cost, on=["cycle_entry_day","cycle_expiry"], how="left")
    else:
        cycle["cost"] = 0.0
    cycle["cost"] = cycle["cost"].fillna(0.0)
    cycle["net_pnl"] = cycle["gross_cash"] - cycle["cost"]
    cycle = cycle.sort_values("cycle_entry_day").reset_index(drop=True)
    cycle["cum_net_pnl"] = cycle["net_pnl"].cumsum()
    cycle["drawdown"] = cycle["cum_net_pnl"] - cycle["cum_net_pnl"].cummax()

    rng = np.random.default_rng(seed)
    values = cycle["net_pnl"].to_numpy(dtype=float)
    if len(values):
        boot = []
        for _ in range(20000):
            boot.append(float(rng.choice(values, size=len(values), replace=True).mean()))
        ci_low, ci_high = np.quantile(boot, [0.025, 0.975])
        mean_cycle = float(values.mean())
    else:
        ci_low = ci_high = mean_cycle = np.nan

    failed = int((events["execution_status"] == "FAILED_INCOMPLETE_EXECUTION").sum()) if not events.empty else 0
    transitions = int(events["event_type"].isin({"TRANSITION_TO_RATIO","CONTINUATION_RESET","REVERSAL"}).sum()) if not events.empty else 0

    return {
        "status": "OK",
        "net_pnl": float(net),
        "gross_trade_cash": gross,
        "cost_drag": cost_drag,
        "slippage_drag": slippage_drag,
        "cycles": int(len(cycle)),
        "mean_cycle_pnl": mean_cycle,
        "mean_cycle_pnl_bootstrap_95_low": float(ci_low),
        "mean_cycle_pnl_bootstrap_95_high": float(ci_high),
        "max_drawdown_rupees": float(cycle["drawdown"].min()) if not cycle.empty else 0.0,
        "adjustment_events": transitions,
        "failed_events": failed,
        "filled_legs": int(len(fills)),
        "total_premium_turnover": float(fills["premium_turnover"].sum()),
        "win_rate_cycles": float((cycle["net_pnl"] > 0).mean()) if not cycle.empty else np.nan,
        "profit_factor_cycles": (
            float(cycle.loc[cycle["net_pnl"] > 0, "net_pnl"].sum()
            / abs(cycle.loc[cycle["net_pnl"] < 0, "net_pnl"].sum()))
            if (cycle["net_pnl"] < 0).any() else np.inf
        ),
    }, cycle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    root = Path(args.results_root)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    summaries = []
    for d in sorted(root.glob("phase2-backtest-*/slippage-*bps")):
        if not d.is_dir():
            continue
        result = summarize(d)
        summary = result[0] if isinstance(result, tuple) else result
        summaries.append({"scenario": d.name, **summary})
        if isinstance(result, tuple):
            result[1].to_parquet(out / f"{d.name}_cycle_pnl.parquet", index=False)

    df = pd.DataFrame(summaries)
    df.to_csv(out / "phase2_summary.csv", index=False)
    (out / "phase2_summary.json").write_text(json.dumps(summaries, indent=2, default=str))


if __name__ == "__main__":
    main()
