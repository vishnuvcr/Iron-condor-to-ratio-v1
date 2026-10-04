#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from bisect import bisect_right
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "timestamp", "expiry", "strike", "option_type", "open", "close", "volume",
    "underlying", "abs_delta", "tick_size", "lot_size",
    "session_eligible", "execution_eligible", "expiry_close_ts",
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
    enable_transitions: bool = True


@dataclass(frozen=True)
class LegIntent:
    contract_id: str
    side: str
    lots: int
    strike: float
    expiry: str
    option_type: str
    expiry_close_ts: str


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
    method: str = "RATE"
    slabs: tuple[dict, ...] = ()

    def applies(self, d: date, side: str) -> bool:
        return (
            self.effective_from <= d
            and (self.effective_to is None or d < self.effective_to)
            and (self.side == "ALL" or self.side == side)
        )


class CostSchedule:
    REQUIRED_CHARGES = ("BROKERAGE", "NSE_TRANSACTION", "IPFT", "SEBI", "STT", "STAMP_DUTY")

    def __init__(self, rules: Iterable[ChargeRule], gst_rate: float = 0.18):
        self.rules = list(rules)
        self.gst_rate = float(gst_rate)

    @staticmethod
    def from_json(path: Path) -> "CostSchedule":
        raw = json.loads(path.read_text())
        rules = [
            ChargeRule(
                charge_type=row["charge_type"],
                effective_from=date.fromisoformat(row["effective_from"]),
                effective_to=date.fromisoformat(row["effective_to"]) if row.get("effective_to") else None,
                fixed_per_order=float(row.get("fixed_per_order", 0.0)),
                rate=float(row.get("rate", 0.0)),
                basis=row.get("basis", "turnover"),
                side=row.get("side", "ALL"),
                taxable=bool(row.get("taxable", False)),
                method=row.get("method", "RATE"),
                slabs=tuple(row.get("slabs", [])),
            )
            for row in raw["rules"]
        ]
        return CostSchedule(rules, gst_rate=float(raw.get("gst_rate", 0.18)))

    def _resolve(self, charge_type: str, d: date, side: str) -> ChargeRule:
        matches = [
            r for r in self.rules
            if r.charge_type == charge_type and r.applies(d, side)
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"COST_RULE_RESOLUTION_FAILURE:{charge_type}:{d}:{side}:{len(matches)}"
            )
        return matches[0]

    @staticmethod
    def _monthly_slab_charge(turnover: float, slabs: tuple[dict, ...]) -> float:
        remaining = float(turnover)
        total = 0.0
        for slab in slabs:
            lower = float(slab.get("lower", 0.0))
            upper = slab.get("upper")
            flat = float(slab.get("flat", 0.0))
            rate = float(slab.get("rate", 0.0))
            if turnover <= lower:
                continue
            if upper is None:
                total += flat + max(0.0, remaining) * rate
                remaining = 0.0
                break
            width = max(0.0, float(upper) - lower)
            used = min(max(0.0, remaining), width)
            total += flat
            total += used * rate
            remaining -= used
            if remaining <= 0:
                break
        return total

    def _fixed_charges_for_fill(self, fill_row: pd.Series) -> tuple[list[Charge], float]:
        execution_date = pd.Timestamp(fill_row["execution_timestamp"]).date()
        side = str(fill_row["side"])
        turnover = float(fill_row["premium_turnover"])
        group_id = str(fill_row["order_group_id"])
        contract_id = str(fill_row["contract_id"])
        out: list[Charge] = []
        taxable_services = 0.0

        for charge_type in ("BROKERAGE", "IPFT", "SEBI", "STT", "STAMP_DUTY"):
            rule = self._resolve(charge_type, execution_date, side)
            if rule.method == "MONTHLY_SLAB":
                raise RuntimeError(f"UNSUPPORTED_MONTHLY_SLAB_FOR:{charge_type}")
            basis = turnover if rule.basis == "turnover" else 1.0
            amount = rule.fixed_per_order + rule.rate * basis
            out.append(
                Charge(
                    group_id, str(execution_date), contract_id, charge_type,
                    amount, basis, rule.rate, rule.fixed_per_order,
                )
            )
            if rule.taxable:
                taxable_services += amount

        return out, taxable_services

    def calculate_for_fills(self, fills: pd.DataFrame) -> list[Charge]:
        if fills.empty:
            return []

        work = fills.copy()
        work["execution_timestamp"] = pd.to_datetime(
            work["execution_timestamp"], utc=True, errors="raise"
        )
        work["execution_date"] = work["execution_timestamp"].dt.date
        work["month"] = work["execution_timestamp"].dt.strftime("%Y-%m")
        work["premium_turnover"] = pd.to_numeric(
            work["premium_turnover"], errors="raise"
        ).abs()

        charge_rows: list[Charge] = []
        taxable_by_fill: dict[int, float] = {}

        for idx, row in work.iterrows():
            fixed, taxable = self._fixed_charges_for_fill(row)
            charge_rows.extend(fixed)
            taxable_by_fill[idx] = taxable

        work["nse_charge"] = 0.0
        for month, group in work.groupby("month", sort=True):
            execution_date = min(group["execution_date"])
            rule = self._resolve("NSE_TRANSACTION", execution_date, "ALL")
            total_turnover = float(group["premium_turnover"].sum())
            if rule.method == "MONTHLY_SLAB":
                monthly_total = self._monthly_slab_charge(total_turnover, rule.slabs)
                if total_turnover > 0:
                    work.loc[group.index, "nse_charge"] = (
                        group["premium_turnover"] / total_turnover * monthly_total
                    )
            else:
                work.loc[group.index, "nse_charge"] = (
                    float(rule.fixed_per_order)
                    + rule.rate * group["premium_turnover"]
                    if rule.basis == "turnover"
                    else float(rule.fixed_per_order) + rule.rate
                )

        for idx, row in work.iterrows():
            nse_rule = self._resolve("NSE_TRANSACTION", row["execution_date"], "ALL")
            amount = float(row["nse_charge"])
            basis = float(row["premium_turnover"]) if nse_rule.basis == "turnover" else 1.0
            charge_rows.append(
                Charge(
                    str(row["order_group_id"]), str(row["execution_date"]),
                    str(row["contract_id"]), "NSE_TRANSACTION", amount,
                    basis, nse_rule.rate, nse_rule.fixed_per_order,
                )
            )
            if nse_rule.taxable:
                taxable_by_fill[idx] = taxable_by_fill.get(idx, 0.0) + amount

        for idx, row in work.iterrows():
            gst_basis = float(taxable_by_fill.get(idx, 0.0))
            if gst_basis:
                charge_rows.append(
                    Charge(
                        str(row["order_group_id"]), str(row["execution_date"]),
                        str(row["contract_id"]), "GST", self.gst_rate * gst_basis,
                        gst_basis, self.gst_rate, 0.0,
                    )
                )

        return charge_rows



def _to_ist_timestamp(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    if getattr(parsed.dt, "tz", None) is None:
        return parsed.dt.tz_localize("Asia/Kolkata")
    return parsed.dt.tz_convert("Asia/Kolkata")


def normalize_bars(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    missing = REQUIRED_COLUMNS - set(out.columns)
    if missing:
        raise ValueError(f"MISSING_ENGINE_COLUMNS:{sorted(missing)}")

    out["timestamp"] = _to_ist_timestamp(out["timestamp"])
    out["expiry"] = pd.to_datetime(out["expiry"], errors="coerce").dt.normalize()
    out["expiry_close_ts"] = _to_ist_timestamp(out["expiry_close_ts"])

    for col in (
        "strike", "open", "close", "volume", "underlying",
        "abs_delta", "tick_size", "lot_size",
    ):
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out["option_type"] = (
        out["option_type"].astype(str).str.upper().str.strip()
        .replace({"CALL": "CE", "C": "CE", "PUT": "PE", "P": "PE"})
    )
    if (~out["option_type"].isin(["CE", "PE"])).any():
        raise ValueError("INVALID_OPTION_TYPE")

    out["session_eligible"] = out["session_eligible"].astype(bool)
    out["execution_eligible"] = (
        out["execution_eligible"].astype(bool) & out["session_eligible"]
    )
    if (
        out["timestamp"].isna().any()
        or out["expiry"].isna().any()
        or out["expiry_close_ts"].isna().any()
    ):
        raise ValueError("INVALID_TIMESTAMP_OR_EXPIRY_OR_CLOSE")

    return out


def build_contract_ids(df: pd.DataFrame) -> pd.Series:
    return (
        df["expiry"].dt.strftime("%Y-%m-%d")
        + "|"
        + df["strike"].map(lambda x: f"{x:.4f}")
        + "|"
        + df["option_type"]
    )


def select_target(
    snapshot: pd.DataFrame,
    expiry: pd.Timestamp,
    option_type: str,
    target_delta: float,
    tolerance: float,
) -> Optional[pd.Series]:
    g = snapshot[
        (snapshot["expiry"] == expiry)
        & (snapshot["option_type"] == option_type)
        & np.isfinite(snapshot["abs_delta"])
    ].copy()
    if g.empty:
        return None

    g["delta_error"] = (g["abs_delta"] - target_delta).abs()
    g = g[g["delta_error"] <= tolerance].copy()
    if g.empty:
        return None

    g["strike_distance"] = (g["strike"] - g["underlying"]).abs()
    g["volume"] = g["volume"].fillna(-np.inf)
    return g.sort_values(
        ["delta_error", "volume", "strike_distance", "strike"],
        ascending=[True, False, True, True],
        kind="mergesort",
    ).iloc[0]


def choose_expiry(
    snapshot: pd.DataFrame,
    decision_ts: pd.Timestamp,
    min_dte_days: int,
) -> Optional[pd.Timestamp]:
    """Select the nearest expiry that is the latest listed expiry in its month.

    This operationalizes "monthly" without projecting the historical weekday
    convention backward. The raw contract expiry field remains authoritative.
    """
    cutoff = decision_ts.normalize() + pd.Timedelta(days=min_dte_days)
    candidates = (
        snapshot[
            (snapshot["expiry"] >= cutoff)
            & snapshot["session_eligible"]
        ]["expiry"]
        .dropna()
        .drop_duplicates()
        .sort_values()
    )
    if candidates.empty:
        return None
    frame = pd.DataFrame({"expiry": candidates})
    frame["year"] = frame["expiry"].dt.year
    frame["month"] = frame["expiry"].dt.month
    monthly = (
        frame.groupby(["year", "month"], as_index=False)["expiry"]
        .max()
        .sort_values("expiry")
    )
    return monthly.iloc[0]["expiry"] if not monthly.empty else None


def adverse_fill(
    base: float,
    side: str,
    tick: float,
    bps: float,
) -> Optional[float]:
    if not np.isfinite(base) or not np.isfinite(tick):
        return None
    if base <= 0 or tick <= 0 or bps < 0:
        return None
    slip = max(tick, bps * base / 10_000.0)
    fill = base + slip if side == "BUY" else base - slip
    return float(fill) if fill > 0 and np.isfinite(fill) else None


class OptionBook:
    def __init__(self, bars: pd.DataFrame):
        df = normalize_bars(bars)
        if "contract_id" not in df.columns:
            df["contract_id"] = build_contract_ids(df)

        if df.duplicated(subset=["timestamp", "contract_id"]).any():
            raise ValueError("DUPLICATE_BAR_CONTRACT_TIMESTAMP")

        self.df = df.sort_values(["contract_id", "timestamp"]).reset_index(drop=True)
        self.by_contract = {
            cid: g.reset_index(drop=True)
            for cid, g in self.df.groupby("contract_id", sort=False)
        }
        self.times = {cid: list(g["timestamp"]) for cid, g in self.by_contract.items()}

    def next_execution_row(
        self, contract_id: str, decision_ts: pd.Timestamp
    ) -> Optional[pd.Series]:
        g = self.by_contract.get(contract_id)
        if g is None:
            return None

        times = self.times[contract_id]
        idx = bisect_right(times, pd.Timestamp(decision_ts))

        while idx < len(g):
            row = g.iloc[idx]
            idx += 1
            if not bool(row["execution_eligible"]):
                continue
            if row["timestamp"] > row["expiry_close_ts"]:
                return None
            return row
        return None

    def snapshot(self, ts: pd.Timestamp, contract_id: str) -> Optional[pd.Series]:
        g = self.by_contract.get(contract_id)
        if g is None:
            return None
        hit = g[g["timestamp"] == ts]
        return hit.iloc[0] if not hit.empty else None


class BacktestEngine:
    def __init__(
        self,
        bars: pd.DataFrame,
        costs: CostSchedule,
        config: EngineConfig = EngineConfig(),
    ):
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
        self.last_call_delta: Optional[float] = None
        self.last_put_delta: Optional[float] = None
        self.last_execution_reason = ""
        self.terminal_unclosed = False

    @staticmethod
    def _qty_cash(lots: int, lot_size: int, price: float, side: str) -> float:
        quantity = abs(lots) * lot_size
        return -quantity * price if side == "BUY" else quantity * price

    def _snapshot_at(self, ts: pd.Timestamp) -> pd.DataFrame:
        return self.book.df[
            (self.book.df["timestamp"] == ts)
            & self.book.df["session_eligible"]
        ]

    def _entry_expiry(
        self, snapshot: pd.DataFrame, ts: pd.Timestamp
    ) -> Optional[pd.Timestamp]:
        return choose_expiry(snapshot, ts, self.cfg.entry_min_dte_days)

    def _build_ic(
        self, snapshot: pd.DataFrame, expiry: pd.Timestamp
    ) -> Optional[list[LegIntent]]:
        specs = [
            ("CE", "SELL", 0.30, -1),
            ("CE", "BUY", 0.10, 1),
            ("PE", "SELL", 0.30, -1),
            ("PE", "BUY", 0.10, 1),
        ]
        legs: list[LegIntent] = []
        for option_type, side, target, lots in specs:
            row = select_target(
                snapshot, expiry, option_type, target, self.cfg.delta_tolerance
            )
            if row is None:
                return None
            legs.append(
                LegIntent(
                    str(row["contract_id"]), side, lots, float(row["strike"]),
                    str(row["expiry"].date()), option_type, str(row["expiry_close_ts"]),
                )
            )
        return legs

    def _build_ratio(
        self,
        snapshot: pd.DataFrame,
        expiry: pd.Timestamp,
        direction: str,
        continuation: bool = False,
    ) -> Optional[list[LegIntent]]:
        option_type = "CE" if direction == "DOWN" else "PE"
        if continuation:
            targets = (
                self.cfg.continuation_long_delta,
                self.cfg.continuation_short_delta,
                self.cfg.continuation_hedge_delta,
            )
        else:
            targets = (
                self.cfg.initial_long_delta,
                self.cfg.initial_short_delta,
                self.cfg.initial_hedge_delta,
            )

        specs = [
            (option_type, "BUY", targets[0], 1),
            (option_type, "SELL", targets[1], -2),
            (option_type, "BUY", targets[2], 1),
        ]
        legs: list[LegIntent] = []
        for opt, side, target, lots in specs:
            row = select_target(
                snapshot, expiry, opt, target, self.cfg.delta_tolerance
            )
            if row is None:
                return None
            legs.append(
                LegIntent(
                    str(row["contract_id"]), side, lots, float(row["strike"]),
                    str(row["expiry"].date()), opt, str(row["expiry_close_ts"]),
                )
            )
        return legs

    def _execute_group(
        self,
        decision_ts: pd.Timestamp,
        group_id: str,
        intended: list[LegIntent],
    ) -> tuple[str, bool]:
        staged_fills: list[Fill] = []
        staged_charges: list[Charge] = []
        staged_cash = 0.0
        self.last_execution_reason = ""

        for leg in intended:
            row = self.book.next_execution_row(leg.contract_id, decision_ts)
            if row is None:
                self.last_execution_reason = f"MISSING_NEXT_ELIGIBLE_BAR:{leg.contract_id}"
                return "FAILED_INCOMPLETE_EXECUTION", True

            fill_price = adverse_fill(
                float(row["open"]), leg.side, float(row["tick_size"]), self.cfg.slippage_bps
            )
            if fill_price is None:
                self.last_execution_reason = f"INVALID_FILL_INPUT:{leg.contract_id}"
                return "FAILED_INCOMPLETE_EXECUTION", True

            turnover = abs(leg.lots) * float(row["lot_size"]) * fill_price
            staged_fills.append(
                Fill(
                    group_id,
                    str(decision_ts),
                    str(row["timestamp"]),
                    leg.contract_id,
                    leg.side,
                    leg.lots,
                    int(row["lot_size"]),
                    float(row["open"]),
                    fill_price,
                    float(row["tick_size"]),
                    abs(fill_price - float(row["open"])),
                    turnover,
                    "FILLED",
                )
            )
            staged_cash += self._qty_cash(
                leg.lots, int(row["lot_size"]), fill_price, leg.side
            )

        self.fills.extend(staged_fills)
        self.charges.extend(staged_charges)
        self.cash += staged_cash
        return "FILLED", False

    def _position_metric(self, ts: pd.Timestamp, position: list[LegIntent]) -> Optional[float]:
        metric = 0.0
        found_short = False
        for leg in position:
            if leg.side != "SELL":
                continue
            found_short = True
            row = self.book.snapshot(ts, leg.contract_id)
            if row is None or not np.isfinite(row["abs_delta"]):
                return None
            metric += float(row["abs_delta"]) * abs(leg.lots)
        return metric if found_short else None

    def _arm_if_reentered(self, metric: Optional[float]) -> None:
        if metric is None or self.rearm:
            return
        if self.state == "IRON_CONDOR" and metric > self.cfg.ic_short_trigger:
            self.rearm = True
        elif (
            self.state == "RATIO"
            and self.cfg.ratio_continuation_trigger < metric < self.cfg.ratio_reversal_trigger
        ):
            self.rearm = True

    def _expiry_cutoff(self) -> Optional[pd.Timestamp]:
        if not self.position:
            return None
        values = [pd.Timestamp(x.expiry_close_ts) for x in self.position]
        return min(values) - pd.Timedelta(minutes=self.cfg.force_close_minutes_before_expiry)

    def _should_force_close(self, ts: pd.Timestamp) -> bool:
        cutoff = self._expiry_cutoff()
        return cutoff is not None and ts >= cutoff

    def _close_position(
        self, ts: pd.Timestamp, event_type: str
    ) -> tuple[str, bool, str]:
        close_legs = [
            LegIntent(
                x.contract_id,
                "BUY" if x.side == "SELL" else "SELL",
                abs(x.lots),
                x.strike,
                x.expiry,
                x.option_type,
                x.expiry_close_ts,
            )
            for x in self.position
        ]
        gid = f"{event_type}-{ts.strftime('%Y%m%dT%H%M%S')}"
        status, consumed = self._execute_group(ts, gid, close_legs)
        return status, consumed, gid

    def _set_ratio_metric(self, ts: pd.Timestamp) -> None:
        self.last_metric = self._position_metric(ts, self.position)

    def run(self) -> dict[str, pd.DataFrame]:
        times = (
            self.book.df.loc[self.book.df["session_eligible"], "timestamp"]
            .drop_duplicates()
            .sort_values()
        )

        for ts in times:
            snapshot = self._snapshot_at(ts)
            if snapshot.empty or self.terminal_unclosed:
                continue

            month_key = ts.strftime("%Y-%m")

            if self.state == "FLAT":
                if month_key not in self.month_attempted:
                    # The first eligible entry opportunity is consumed once, even if
                    # an expiry or target contract is unavailable. This prevents
                    # repeated same-month entry attempts from missing data.
                    self.month_attempted.add(month_key)
                    gid = f"ENTRY-IC-{ts.strftime('%Y%m%dT%H%M%S')}"
                    expiry = self._entry_expiry(snapshot, ts)
                    if expiry is None:
                        self.events.append(
                            Event(
                                str(ts), gid, "FLAT", "MONTHLY_ENTRY_SKIPPED", None,
                                "NOT_ATTEMPTED", "FLAT", True, False,
                                "NO_VALID_MONTHLY_EXPIRY",
                            )
                        )
                    else:
                        intended = self._build_ic(snapshot, expiry)
                        if intended is None:
                            self.events.append(
                                Event(
                                    str(ts), gid, "FLAT", "ENTER_IRON_CONDOR", None,
                                    "FAILED_INCOMPLETE_EXECUTION", "FLAT", True, False,
                                    "TARGET_CONTRACT_UNAVAILABLE",
                                )
                            )
                        else:
                            status, consumed = self._execute_group(ts, gid, intended)
                            if status == "FILLED":
                                self.position = intended
                                self.state = "IRON_CONDOR"
                                self.direction = None
                                self.rearm = True
                                self._set_ic_reference(snapshot, ts)
                                self.events.append(
                                    Event(
                                        str(ts), gid, "FLAT", "ENTER_IRON_CONDOR", None,
                                        status, self.state, False, True, "MONTHLY_ENTRY",
                                    )
                                )
                            else:
                                self.events.append(
                                    Event(
                                        str(ts), gid, "FLAT", "ENTER_IRON_CONDOR", None,
                                        status, "FLAT", consumed, False,
                                        self.last_execution_reason or "ENTRY_FAILED",
                                    )
                                )

            elif self._should_force_close(ts):
                pre_state = self.state
                status, consumed, gid = self._close_position(ts, "EXPIRY_CLOSE")
                if status == "FILLED":
                    self.events.append(
                        Event(
                            str(ts), gid, pre_state, "EXPIRY_CLOSE", None,
                            status, "FLAT", False, True, "FORCED_BEFORE_EXPIRY",
                        )
                    )
                    self.position = []
                    self.state = "FLAT"
                    self.direction = None
                    self.rearm = True
                    self.last_metric = None
                    self.last_call_delta = None
                    self.last_put_delta = None
                else:
                    self.events.append(
                        Event(
                            str(ts), gid, pre_state, "EXPIRY_CLOSE", None,
                            status, pre_state, consumed, False,
                            self.last_execution_reason or "EXPIRY_CLOSE_FAILED",
                        )
                    )
                    self.terminal_unclosed = True

            elif self.state == "IRON_CONDOR" and self.cfg.enable_transitions:
                call = next(
                    (x for x in self.position if x.side == "SELL" and x.option_type == "CE"),
                    None,
                )
                put = next(
                    (x for x in self.position if x.side == "SELL" and x.option_type == "PE"),
                    None,
                )
                call_row = self.book.snapshot(ts, call.contract_id) if call else None
                put_row = self.book.snapshot(ts, put.contract_id) if put else None

                if call_row is not None and put_row is not None:
                    call_delta = float(call_row["abs_delta"])
                    put_delta = float(put_row["abs_delta"])
                    self._arm_if_reentered(max(call_delta, put_delta))

                    direction = None
                    trigger_metric = None
                    if self.rearm:
                        if (
                            self.last_call_delta is not None
                            and self.last_call_delta > self.cfg.ic_short_trigger
                            and call_delta <= self.cfg.ic_short_trigger
                        ):
                            direction = "DOWN"
                            trigger_metric = call_delta
                        elif (
                            self.last_put_delta is not None
                            and self.last_put_delta > self.cfg.ic_short_trigger
                            and put_delta <= self.cfg.ic_short_trigger
                        ):
                            direction = "UP"
                            trigger_metric = put_delta

                    self.last_call_delta = call_delta
                    self.last_put_delta = put_delta

                    if direction is not None:
                        expiry = min(pd.Timestamp(x.expiry) for x in self.position)
                        ratio = self._build_ratio(snapshot, expiry, direction, continuation=False)
                        gid = f"TRANSITION-{direction}-{ts.strftime('%Y%m%dT%H%M%S')}"
                        combined = call_delta if direction == "DOWN" else put_delta
                        if ratio is None:
                            status, consumed = "FAILED_INCOMPLETE_EXECUTION", True
                            self.last_execution_reason = "TARGET_CONTRACT_UNAVAILABLE"
                        else:
                            close_then_open = [
                                LegIntent(
                                    x.contract_id,
                                    "BUY" if x.side == "SELL" else "SELL",
                                    abs(x.lots),
                                    x.strike,
                                    x.expiry,
                                    x.option_type,
                                    x.expiry_close_ts,
                                )
                                for x in self.position
                            ] + ratio
                            status, consumed = self._execute_group(ts, gid, close_then_open)

                        if status == "FILLED":
                            self.position = ratio
                            self.state = "RATIO"
                            self.direction = direction
                            self.rearm = True
                            self._set_ratio_metric(ts)
                        else:
                            self.rearm = False

                        self.events.append(
                            Event(
                                str(ts), gid, "IRON_CONDOR", "TRANSITION_TO_RATIO",
                                combined, status,
                                "RATIO" if status == "FILLED" else "IRON_CONDOR",
                                consumed if status != "FILLED" else False,
                                status == "FILLED",
                                self.last_execution_reason or "SOURCE_TRANSITION",
                            )
                        )

            elif self.state == "RATIO":
                metric = self._position_metric(ts, self.position)
                if metric is None:
                    continue

                self._arm_if_reentered(metric)

                if self.rearm and self.last_metric is not None:
                    if (
                        self.last_metric > self.cfg.ratio_continuation_trigger
                        and metric <= self.cfg.ratio_continuation_trigger
                    ):
                        expiry = min(pd.Timestamp(x.expiry) for x in self.position)
                        ratio = self._build_ratio(snapshot, expiry, self.direction or "DOWN", continuation=True)
                        gid = f"CONTINUE-{ts.strftime('%Y%m%dT%H%M%S')}"

                        if ratio is None:
                            status, consumed = "FAILED_INCOMPLETE_EXECUTION", True
                            self.last_execution_reason = "TARGET_CONTRACT_UNAVAILABLE"
                        else:
                            close_then_open = [
                                LegIntent(
                                    x.contract_id,
                                    "BUY" if x.side == "SELL" else "SELL",
                                    abs(x.lots),
                                    x.strike,
                                    x.expiry,
                                    x.option_type,
                                    x.expiry_close_ts,
                                )
                                for x in self.position
                            ] + ratio
                            status, consumed = self._execute_group(ts, gid, close_then_open)

                        self.events.append(
                            Event(
                                str(ts), gid, "RATIO", "CONTINUATION_RESET", metric, status,
                                "RATIO", consumed if status != "FILLED" else False,
                                status == "FILLED",
                                self.last_execution_reason or "SAME_DIRECTION_RESET",
                            )
                        )
                        if status == "FILLED":
                            self.position = ratio
                            self.rearm = True
                            self._set_ratio_metric(ts)
                        else:
                            self.rearm = False

                    elif (
                        self.last_metric < self.cfg.ratio_reversal_trigger
                        and metric >= self.cfg.ratio_reversal_trigger
                    ):
                        expiry = min(pd.Timestamp(x.expiry) for x in self.position)
                        opposite = "UP" if self.direction == "DOWN" else "DOWN"
                        ratio = self._build_ratio(snapshot, expiry, opposite, continuation=False)
                        gid = f"REVERSAL-{ts.strftime('%Y%m%dT%H%M%S')}"

                        if ratio is None:
                            status, consumed = "FAILED_INCOMPLETE_EXECUTION", True
                            self.last_execution_reason = "TARGET_CONTRACT_UNAVAILABLE"
                        else:
                            close_then_open = [
                                LegIntent(
                                    x.contract_id,
                                    "BUY" if x.side == "SELL" else "SELL",
                                    abs(x.lots),
                                    x.strike,
                                    x.expiry,
                                    x.option_type,
                                    x.expiry_close_ts,
                                )
                                for x in self.position
                            ] + ratio
                            status, consumed = self._execute_group(ts, gid, close_then_open)

                        self.events.append(
                            Event(
                                str(ts), gid, "RATIO", "REVERSAL", metric, status,
                                "RATIO", consumed if status != "FILLED" else False,
                                status == "FILLED",
                                self.last_execution_reason or "OPPOSITE_DIRECTION",
                            )
                        )
                        if status == "FILLED":
                            self.position = ratio
                            self.direction = opposite
                            self.rearm = True
                            self._set_ratio_metric(ts)
                        else:
                            self.rearm = False

                if self.last_metric is None or not any(
                    e.execution_status == "FILLED"
                    and e.decision_timestamp == str(ts)
                    and e.event_type in {"CONTINUATION_RESET", "REVERSAL"}
                    for e in self.events
                ):
                    self.last_metric = metric

        fill_frame = pd.DataFrame([asdict(x) for x in self.fills])
        self.charges = self.costs.calculate_for_fills(fill_frame)
        self.cash -= sum(c.amount for c in self.charges)

        metadata = pd.DataFrame([{
            "engine_version": "phase2-engine-v1",
            "state": self.state,
            "terminal_unclosed": self.terminal_unclosed,
            "gross_cash": self.cash + sum(c.amount for c in self.charges),
            "cash": self.cash,
            "fills": len(self.fills),
            "charges": len(self.charges),
            "events": len(self.events),
            "monthly_exchange_charge_method": "EXACT_MONTHLY_TOTAL_ALLOCATED_PRO_RATA_TO_LEG_TURNOVER",
        }])

        return {
            "fills": pd.DataFrame([asdict(x) for x in self.fills]),
            "charges": pd.DataFrame([asdict(x) for x in self.charges]),
            "events": pd.DataFrame([asdict(x) for x in self.events]),
            "metadata": metadata,
        }

    def _set_ic_reference(self, snapshot: pd.DataFrame, ts: pd.Timestamp) -> None:
        call = next(
            (x for x in self.position if x.side == "SELL" and x.option_type == "CE"),
            None,
        )
        put = next(
            (x for x in self.position if x.side == "SELL" and x.option_type == "PE"),
            None,
        )
        call_row = self.book.snapshot(ts, call.contract_id) if call else None
        put_row = self.book.snapshot(ts, put.contract_id) if put else None
        self.last_call_delta = float(call_row["abs_delta"]) if call_row is not None else None
        self.last_put_delta = float(put_row["abs_delta"]) if put_row is not None else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_outputs(
    out_dir: Path,
    result: dict[str, pd.DataFrame],
    config: EngineConfig,
    inputs: list[Path],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in result.items():
        frame.to_parquet(out_dir / f"{name}.parquet", index=False)

    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = None

    manifest = {
        "engine_version": "phase2-engine-v1",
        "config": asdict(config),
        "git_sha": git_sha,
        "input_files": [
            {"path": str(path), "sha256": file_sha256(path)}
            for path in inputs
        ],
        "outputs": {
            name: str(out_dir / f"{name}.parquet")
            for name in result
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
