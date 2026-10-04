#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from bisect import bisect_right
from typing import Iterable, Optional

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "timestamp", "expiry", "strike", "option_type", "open", "close", "volume",
    "underlying", "abs_delta", "tick_size", "lot_size",
    "session_eligible", "execution_eligible",
}

@dataclass(frozen=True)
class EngineConfig:
    delta_tolerance: float = 0.05
    ic_short_trigger: float = 0.10
    ratio_continuation_trigger: float = 0.20
    ratio_reversal_trigger: float = 1.20
    reversal_upper_reference: float = 1.30
    initial_long_delta: float = 0.50
    initial_short_delta: float = 0.40
    initial_hedge_delta: float = 0.10
    continuation_long_delta: float = 0.40
    continuation_short_delta: float = 0.30
    continuation_hedge_delta: float = 0.08
    entry_min_dte_days: int = 20
    slippage_bps: float = 10.0
    force_close_minutes_before_expiry: int = 1

@dataclass(frozen=True)
class LegIntent:
    contract_id: str
    side: str
    lots: int
    strike: float
    expiry: str
    option_type: str

@dataclass(frozen=True)
class Fill:
    order_group_id: str
    decision_timestamp: str
    execution_timestamp: str
    contract_id: str
    side: str
    lots: int
    lot_size: int
    base_open: float
    fill_price: float
    tick_size: float
    slippage: float
    premium_turnover: float
    status: str

@dataclass(frozen=True)
class Charge:
    order_group_id: str
    execution_timestamp: str
    contract_id: str
    charge_type: str
    amount: float
    basis: float
    rate: float
    fixed: float

@dataclass(frozen=True)
class Event:
    decision_timestamp: str
    order_group_id: str
    pre_state: str
    event_type: str
    trigger_metric: Optional[float]
    execution_status: str
    post_state: str
    trigger_consumed: bool
    retry_eligible_after_rearm: bool
    reason: str

@dataclass(frozen=True)
class ChargeRule:
    charge_type: str
    effective_from: date
    effective_to: Optional[date]
    fixed_per_order: float = 0.0
    rate: float = 0.0
    basis: str = "turnover"
    side: str = "ALL"
    taxable: bool = False

    def applies(self, d: date, side: str) -> bool:
        if d < self.effective_from:
            return False
        if self.effective_to is not None and d >= self.effective_to:
            return False
        return self.side == "ALL" or self.side == side

class CostSchedule:
    def __init__(self, rules: Iterable[ChargeRule], gst_rate: float = 0.18):
        self.rules = list(rules)
        self.gst_rate = float(gst_rate)

    @staticmethod
    def from_json(path: Path) -> "CostSchedule":
        raw = json.loads(path.read_text())
        rules = []
        for row in raw["rules"]:
            rules.append(
                ChargeRule(
                    charge_type=row["charge_type"],
                    effective_from=date.fromisoformat(row["effective_from"]),
                    effective_to=(
                        date.fromisoformat(row["effective_to"])
                        if row.get("effective_to") else None
                    ),
                    fixed_per_order=float(row.get("fixed_per_order", 0.0)),
                    rate=float(row.get("rate", 0.0)),
                    basis=row.get("basis", "turnover"),
                    side=row.get("side", "ALL"),
                    taxable=bool(row.get("taxable", False)),
                )
            )
        return CostSchedule(rules, gst_rate=float(raw.get("gst_rate", 0.18)))

    def _resolve(self, charge_type: str, d: date, side: str) -> ChargeRule:
        matches = [r for r in self.rules if r.charge_type == charge_type and r.applies(d, side)]
        if len(matches) != 1:
            raise RuntimeError(f"COST_RULE_RESOLUTION_FAILURE:{charge_type}:{d}:{side}:{len(matches)}")
        return matches[0]

    def calculate(
        self, execution_date: date, side: str, turnover: float, order_group_id: str,
        contract_id: str, brokerage_taxable: float = 0.0
    ) -> list[Charge]:
        out: list[Charge] = []
        taxable_services = 0.0
        for charge_type in ["BROKERAGE", "NSE_TRANSACTION", "IPFT", "SEBI"]:
            rule = self._resolve(charge_type, execution_date, side)
            basis = turnover if rule.basis == "turnover" else 1.0
            amount = rule.fixed_per_order + rule.rate * basis
            out.append(Charge(order_group_id, str(execution_date), contract_id, charge_type, amount, basis, rule.rate, rule.fixed_per_order))
            if rule.taxable:
                taxable_services += amount
        stt = self._resolve("STT", execution_date, side)
        stt_basis = turnover if stt.basis == "turnover" else 1.0
        stt_amount = stt.fixed_per_order + stt.rate * stt_basis
        out.append(Charge(order_group_id, str(execution_date), contract_id, "STT", stt_amount, stt_basis, stt.rate, stt.fixed_per_order))
        stamp = self._resolve("STAMP_DUTY", execution_date, side)
        stamp_basis = turnover if stamp.basis == "turnover" else 1.0
        stamp_amount = stamp.fixed_per_order + stamp.rate * stamp_basis
        out.append(Charge(order_group_id, str(execution_date), contract_id, "STAMP_DUTY", stamp_amount, stamp_basis, stamp.rate, stamp.fixed_per_order))
        gst_amount = self.gst_rate * taxable_services
        out.append(Charge(order_group_id, str(execution_date), contract_id, "GST", gst_amount, taxable_services, self.gst_rate, 0.0))
        return out

class OptionBook:
    def __init__(self, bars: pd.DataFrame):
        df = bars.copy()
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"MISSING_ENGINE_COLUMNS:{sorted(missing)}")
        df = normalize_bars(df)
        df["contract_id"] = df.get("contract_id", build_contract_ids(df))
        if df["contract_id"].duplicated(["timestamp", "contract_id"]).any():
            raise ValueError("DUPLICATE_BAR_CONTRACT_TIMESTAMP")
        self.df = df.sort_values(["contract_id", "timestamp"]).reset_index(drop=True)
        self.by_contract = {
            cid: g.reset_index(drop=True)
            for cid, g in self.df.groupby("contract_id", sort=False)
        }
        self.times = {
            cid: list(g["timestamp"])
            for cid, g in self.by_contract.items()
        }

    def next_execution_row(self, contract_id: str, decision_ts: pd.Timestamp) -> Optional[pd.Series]:
        g = self.by_contract.get(contract_id)
        if g is None:
            return None
        times = self.times[contract_id]
        idx = bisect_right(times, decision_ts.to_pydatetime())
        while idx < len(g):
            row = g.iloc[idx]
            idx += 1
            if bool(row["execution_eligible"]):
                expiry_close = pd.Timestamp(row["expiry"]).normalize() + pd.Timedelta(hours=15, minutes=30)
                if row["timestamp"] <= expiry_close:
                    return row
        return None

    def snapshot(self, ts: pd.Timestamp, contract_id: str) -> Optional[pd.Series]:
        g = self.by_contract.get(contract_id)
        if g is None:
            return None
        hit = g[g["timestamp"] == ts]
        if hit.empty:
            return None
        return hit.iloc[0]

def normalize_bars(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce").dt.tz_convert("Asia/Kolkata")
    out["expiry"] = pd.to_datetime(out["expiry"], errors="coerce").dt.normalize()
    for c in ["strike", "open", "close", "volume", "underlying", "abs_delta", "tick_size", "lot_size"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["option_type"] = out["option_type"].astype(str).str.upper().str.strip().replace({
        "CALL": "CE", "C": "CE", "PUT": "PE", "P": "PE"
    })
    out["session_eligible"] = out["session_eligible"].astype(bool)
    out["execution_eligible"] = out["execution_eligible"].astype(bool) & out["session_eligible"]
    if out["timestamp"].isna().any() or out["expiry"].isna().any():
        raise ValueError("INVALID_TIMESTAMP_OR_EXPIRY")
    return out

def build_contract_ids(df: pd.DataFrame) -> pd.Series:
    return (
        df["expiry"].dt.strftime("%Y-%m-%d") + "|" +
        df["strike"].map(lambda x: f"{x:.4f}") + "|" +
        df["option_type"]
    )

def select_target(
    snapshot: pd.DataFrame, expiry: pd.Timestamp, option_type: str,
    target_delta: float, tolerance: float
) -> Optional[pd.Series]:
    g = snapshot[(snapshot["expiry"] == expiry) & (snapshot["option_type"] == option_type)].copy()
    if g.empty:
        return None
    g["delta_error"] = (g["abs_delta"] - target_delta).abs()
    g = g[g["delta_error"] <= tolerance].copy()
    if g.empty:
        return None
    g["strike_distance"] = (g["strike"] - g["underlying"]).abs()
    return g.sort_values(
        ["delta_error", "volume", "strike_distance", "strike"],
        ascending=[True, False, True, True],
        kind="mergesort",
    ).iloc[0]

def choose_expiry(snapshot: pd.DataFrame, decision_ts: pd.Timestamp, min_dte_days: int) -> Optional[pd.Timestamp]:
    candidates = snapshot[
        (snapshot["expiry"] > decision_ts.normalize() + pd.Timedelta(days=min_dte_days)) &
        snapshot["session_eligible"]
    ]["expiry"].dropna().drop_duplicates().sort_values()
    return candidates.iloc[0] if not candidates.empty else None

def adverse_fill(base: float, side: str, tick: float, bps: float) -> Optional[float]:
    if not np.isfinite(base) or not np.isfinite(tick) or base <= 0 or tick <= 0:
        return None
    slip = max(tick, bps * base / 10_000.0)
    fill = base + slip if side == "BUY" else base - slip
    return float(fill) if fill > 0 and np.isfinite(fill) else None

class BacktestEngine:
    def __init__(self, bars: pd.DataFrame, costs: CostSchedule, config: EngineConfig = EngineConfig()):
        self.book = OptionBook(bars)
        self.costs = costs
        self.cfg = config
        self.fills: list[Fill] = []
        self.charges: list[Charge] = []
        self.events: list[Event] = []
        self.cash = 0.0
        self.month_attempted: set[str] = set()
        self.state = "FLAT"
        self.direction: Optional[str] = None
        self.position: list[LegIntent] = []
        self.rearm = True
        self.last_metric: Optional[float] = None

    def _snapshot_at(self, ts: pd.Timestamp) -> pd.DataFrame:
        return self.book.df[(self.book.df["timestamp"] == ts) & self.book.df["session_eligible"]]

    def _entry_expiry(self, snap: pd.DataFrame, ts: pd.Timestamp) -> Optional[pd.Timestamp]:
        return choose_expiry(snap, ts, self.cfg.entry_min_dte_days)

    def _build_ic(self, snap: pd.DataFrame, expiry: pd.Timestamp) -> Optional[list[LegIntent]]:
        legs = []
        specs = [("CE", "SELL", 0.30, -1), ("CE", "BUY", 0.10, 1),
                 ("PE", "SELL", 0.30, -1), ("PE", "BUY", 0.10, 1)]
        for ot, side, target, lots in specs:
            row = select_target(snap, expiry, ot, target, self.cfg.delta_tolerance)
            if row is None:
                return None
            legs.append(LegIntent(str(row["contract_id"]), side, lots, float(row["strike"]), str(row["expiry"].date()), ot))
        return legs

    def _build_ratio(self, snap: pd.DataFrame, expiry: pd.Timestamp, direction: str, continuation: bool = False) -> Optional[list[LegIntent]]:
        ot = "CE" if direction == "DOWN" else "PE"
        if continuation:
            ds = (self.cfg.continuation_long_delta, self.cfg.continuation_short_delta, self.cfg.continuation_hedge_delta)
        else:
            ds = (self.cfg.initial_long_delta, self.cfg.initial_short_delta, self.cfg.initial_hedge_delta)
        specs = [(ot, "BUY", ds[0], 1), (ot, "SELL", ds[1], -2), (ot, "BUY", ds[2], 1)]
        legs: list[LegIntent] = []
        for ot2, side, target, lots in specs:
            row = select_target(snap, expiry, ot2, target, self.cfg.delta_tolerance)
            if row is None:
                return None
            legs.append(LegIntent(str(row["contract_id"]), side, lots, float(row["strike"]), str(row["expiry"].date()), ot2))
        return legs

    @staticmethod
    def _qty_cash(lots: int, lot_size: int, price: float, side: str) -> float:
        qty = abs(lots) * lot_size
        return -qty * price if side == "BUY" else qty * price

    def _execute_group(self, decision_ts: pd.Timestamp, group_id: str, intended: list[LegIntent]) -> tuple[str, str, bool]:
        fills: list[Fill] = []
        charges: list[Charge] = []
        total_cash = 0.0
        for leg in intended:
            row = self.book.next_execution_row(leg.contract_id, decision_ts)
            if row is None:
                self.events.append(Event(str(decision_ts), group_id, self.state, "EXECUTION_ATTEMPT", None,
                                         "FAILED_INCOMPLETE_EXECUTION", self.state, True, False,
                                         f"MISSING_NEXT_ELIGIBLE_BAR:{leg.contract_id}"))
                return "FAILED_INCOMPLETE_EXECUTION", self.state, True
            fill_price = adverse_fill(float(row["open"]), leg.side, float(row["tick_size"]), self.cfg.slippage_bps)
            if fill_price is None:
                self.events.append(Event(str(decision_ts), group_id, self.state, "EXECUTION_ATTEMPT", None,
                                         "FAILED_INCOMPLETE_EXECUTION", self.state, True, False,
                                         f"INVALID_FILL_INPUT:{leg.contract_id}"))
                return "FAILED_INCOMPLETE_EXECUTION", self.state, True
            turnover = abs(leg.lots) * float(row["lot_size"]) * fill_price
            try:
                c = self.costs.calculate(
                    execution_date=pd.Timestamp(row["timestamp"]).date(),
                    side=leg.side,
                    turnover=turnover,
                    order_group_id=group_id,
                    contract_id=leg.contract_id,
                )
            except Exception as exc:
                self.events.append(Event(str(decision_ts), group_id, self.state, "EXECUTION_ATTEMPT", None,
                                         "FAILED_INCOMPLETE_EXECUTION", self.state, True, False,
                                         str(exc)))
                return "FAILED_INCOMPLETE_EXECUTION", self.state, True
            slippage = abs(fill_price - float(row["open"]))
            fills.append(Fill(group_id, str(decision_ts), str(row["timestamp"]), leg.contract_id, leg.side,
                              leg.lots, int(row["lot_size"]), float(row["open"]), fill_price,
                              float(row["tick_size"]), slippage, turnover, "FILLED"))
            charges.extend(c)
            total_cash += self._qty_cash(leg.lots, int(row["lot_size"]), fill_price, leg.side)
            total_cash -= sum(x.amount for x in c)
        self.fills.extend(fills)
        self.charges.extend(charges)
        self.cash += total_cash
        return "FILLED", "POST_STATE", False

    def _metric(self, ts: pd.Timestamp) -> Optional[float]:
        if not self.position:
            return None
        vals = []
        for leg in self.position:
            if leg.side != "SELL":
                continue
            row = self.book.snapshot(ts, leg.contract_id)
            if row is None or not np.isfinite(row["abs_delta"]):
                return None
            vals.append(float(row["abs_delta"]) * abs(leg.lots))
        return float(sum(vals)) if vals else None

    def _rearm_logic(self, metric: Optional[float], state: str) -> None:
        if metric is None:
            return
        if state == "IRON_CONDOR":
            if metric > self.cfg.ic_short_trigger:
                self.rearm = True
        elif state == "RATIO":
            if self.rearm is False and self.cfg.ratio_continuation_trigger < metric < self.cfg.ratio_reversal_trigger:
                self.rearm = True

    def _should_force_close(self, ts: pd.Timestamp) -> bool:
        if not self.position:
            return False
        expiry = min(pd.Timestamp(x.expiry) for x in self.position)
        cutoff = expiry.normalize() + pd.Timedelta(hours=15, minutes=30) - pd.Timedelta(minutes=self.cfg.force_close_minutes_before_expiry)
        return ts >= cutoff

    def _close_position(self, ts: pd.Timestamp, event_type: str) -> tuple[str, str, bool]:
        close_legs = [
            LegIntent(x.contract_id, "BUY" if x.side == "SELL" else "SELL", abs(x.lots),
                      x.strike, x.expiry, x.option_type)
            for x in self.position
        ]
        gid = f"{event_type}-{ts.strftime('%Y%m%dT%H%M%S')}"
        return self._execute_group(ts, gid, close_legs)

    def run(self) -> dict[str, pd.DataFrame]:
        times = self.book.df.loc[self.book.df["session_eligible"], "timestamp"].drop_duplicates().sort_values()
        prev_state = self.state
        for ts in times:
            snap = self._snapshot_at(ts)
            if snap.empty:
                continue
            month_key = ts.strftime("%Y-%m")
            if self.state == "FLAT":
                if month_key not in self.month_attempted:
                    expiry = self._entry_expiry(snap, ts)
                    self.month_attempted.add(month_key)
                    if expiry is not None:
                        intended = self._build_ic(snap, expiry)
                        if intended is not None:
                            gid = f"ENTRY-IC-{ts.strftime('%Y%m%dT%H%M%S')}"
                            status, _, consumed = self._execute_group(ts, gid, intended)
                            if status == "FILLED":
                                self.position = intended
                                self.state = "IRON_CONDOR"
                                self.direction = None
                                self.rearm = True
                                self.last_metric = None
                                self.events.append(Event(str(ts), gid, "FLAT", "ENTER_IRON_CONDOR", None, status, self.state, False, True, "MONTHLY_ENTRY"))
                            else:
                                self.events.append(Event(str(ts), gid, "FLAT", "ENTER_IRON_CONDOR", None, status, "FLAT", consumed, False, "ENTRY_FAILED"))
            elif self._should_force_close(ts):
                gid = f"EXPIRY-CLOSE-{ts.strftime('%Y%m%dT%H%M%S')}"
                pre = self.state
                status, _, consumed = self._close_position(ts, "EXPIRY_CLOSE")
                if status == "FILLED":
                    self.events.append(Event(str(ts), gid, pre, "EXPIRY_CLOSE", None, status, "FLAT", False, True, "FORCED_BEFORE_EXPIRY"))
                    self.position = []
                    self.state = "FLAT"
                    self.direction = None
                    self.rearm = True
                    self.last_metric = None
                else:
                    self.events.append(Event(str(ts), gid, pre, "EXPIRY_CLOSE", None, status, pre, consumed, False, "EXPIRY_CLOSE_FAILED"))
            elif self.state == "IRON_CONDOR":
                call = next((x for x in self.position if x.side == "SELL" and x.option_type == "CE"), None)
                put = next((x for x in self.position if x.side == "SELL" and x.option_type == "PE"), None)
                call_row = self.book.snapshot(ts, call.contract_id) if call else None
                put_row = self.book.snapshot(ts, put.contract_id) if put else None
                direction = None
                metric = None
                if call_row is not None and put_row is not None:
                    pc=float(call_row["abs_delta"]); pp=float(put_row["abs_delta"])
                    prior_call = self.last_metric
                    if self.last_metric is None:
                        self.last_metric = max(pc, pp)
                    if self.rearm and pc <= self.cfg.ic_short_trigger and (prior_call is None or prior_call > self.cfg.ic_short_trigger):
                        direction, metric = "DOWN", pc
                    elif self.rearm and pp <= self.cfg.ic_short_trigger and (prior_call is None or prior_call > self.cfg.ic_short_trigger):
                        direction, metric = "UP", pp
                    self.last_metric = max(pc, pp)
                if direction:
                    expiry = min(pd.Timestamp(x.expiry) for x in self.position)
                    intended = self._build_ratio(snap, expiry, direction, continuation=False)
                    if intended is not None:
                        gid = f"TRANSITION-{direction}-{ts.strftime('%Y%m%dT%H%M%S')}"
                        combined = sum(
                            float(self.book.snapshot(ts, x.contract_id)["abs_delta"]) * abs(x.lots)
                            for x in self.position if x.side=="SELL"
                        )
                        close_then_open = [
                            LegIntent(x.contract_id, "BUY" if x.side=="SELL" else "SELL", abs(x.lots), x.strike, x.expiry, x.option_type)
                            for x in self.position
                        ] + intended
                        status, _, consumed = self._execute_group(ts, gid, close_then_open)
                        self.events.append(Event(str(ts), gid, "IRON_CONDOR", "TRANSITION_TO_RATIO", combined, status,
                                                 "RATIO" if status=="FILLED" else "IRON_CONDOR", True if status!="FILLED" else False,
                                                 status=="FILLED", "SOURCE_TRANSITION"))
                        if status == "FILLED":
                            self.position=intended; self.state="RATIO"; self.direction=direction; self.rearm=True; self.last_metric=0.0
                        else:
                            self.rearm=False
            elif self.state == "RATIO":
                metric = self._metric(ts)
                if metric is None:
                    continue
                if not self.rearm and self.cfg.ratio_continuation_trigger < metric < self.cfg.ratio_reversal_trigger:
                    self.rearm = True
                if self.rearm and self.last_metric is not None:
                    if self.last_metric > self.cfg.ratio_continuation_trigger and metric <= self.cfg.ratio_continuation_trigger:
                        expiry=min(pd.Timestamp(x.expiry) for x in self.position)
                        intended=self._build_ratio(snap, expiry, self.direction or "DOWN", continuation=True)
                        if intended is not None:
                            gid=f"CONTINUE-{ts.strftime('%Y%m%dT%H%M%S')}"
                            close_then_open=[LegIntent(x.contract_id,"BUY" if x.side=="SELL" else "SELL",abs(x.lots),x.strike,x.expiry,x.option_type) for x in self.position]+intended
                            status,_,consumed=self._execute_group(ts,gid,close_then_open)
                            self.events.append(Event(str(ts),gid,"RATIO","CONTINUATION_RESET",metric,status,"RATIO" if status=="FILLED" else "RATIO",
                                                     False if status=="FILLED" else consumed,status=="FILLED","SAME_DIRECTION_RESET"))
                            if status=="FILLED":
                                self.position=intended; self.rearm=True
                            else:
                                self.rearm=False
                    elif self.last_metric < self.cfg.ratio_reversal_trigger and metric >= self.cfg.ratio_reversal_trigger:
                        expiry=min(pd.Timestamp(x.expiry) for x in self.position)
                        opposite="UP" if self.direction=="DOWN" else "DOWN"
                        intended=self._build_ratio(snap,expiry,opposite,continuation=False)
                        if intended is not None:
                            gid=f"REVERSAL-{ts.strftime('%Y%m%dT%H%M%S')}"
                            close_then_open=[LegIntent(x.contract_id,"BUY" if x.side=="SELL" else "SELL",abs(x.lots),x.strike,x.expiry,x.option_type) for x in self.position]+intended
                            status,_,consumed=self._execute_group(ts,gid,close_then_open)
                            self.events.append(Event(str(ts),gid,"RATIO","REVERSAL",metric,status,"RATIO" if status=="FILLED" else "RATIO",
                                                     False if status=="FILLED" else consumed,status=="FILLED","OPPOSITE_DIRECTION"))
                            if status=="FILLED":
                                self.position=intended; self.direction=opposite; self.rearm=True
                            else:
                                self.rearm=False
                self.last_metric=metric

        return {
            "fills": pd.DataFrame([asdict(x) for x in self.fills]),
            "charges": pd.DataFrame([asdict(x) for x in self.charges]),
            "events": pd.DataFrame([asdict(x) for x in self.events]),
        }

def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def save_outputs(out_dir: Path, result: dict[str, pd.DataFrame], config: EngineConfig, inputs: list[Path]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in result.items():
        df.to_parquet(out_dir / f"{name}.parquet", index=False)
    manifest={
        "engine_version":"phase2-engine-v1",
        "config":asdict(config),
        "git_sha":None,
        "input_files":[{"path":str(p),"sha256":file_sha256(p)} for p in inputs],
        "outputs":{name:str(out_dir/f"{name}.parquet") for name in result},
    }
    try:
        import subprocess
        import os
        manifest["git_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception:
        pass
    (out_dir/"manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
