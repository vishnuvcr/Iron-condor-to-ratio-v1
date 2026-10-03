"""Regression tests for E065/E066 execution-proxy rules.

These tests encode the methodology contract without starting any backtest.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Leg:
    base: float | None
    tick: float | None


def sell_fill(base: float | None, tick: float | None, bps: float) -> float | None:
    if base is None or tick is None or base <= 0 or tick <= 0:
        return None
    fill = base - max(tick, bps * base / 10_000.0)
    return fill if fill > 0 else None


def buy_fill(base: float | None, tick: float | None, bps: float) -> float | None:
    if base is None or tick is None or base <= 0 or tick <= 0:
        return None
    fill = base + max(tick, bps * base / 10_000.0)
    return fill if fill > 0 else None


def atomic_group_status(legs: list[Leg]) -> tuple[str, str, bool]:
    """Return status, post-state, trigger-consumed for a multi-leg adjustment."""
    valid = all(
        leg.base is not None
        and leg.tick is not None
        and leg.base > 0
        and leg.tick > 0
        for leg in legs
    )
    if not valid:
        return "FAILED_INCOMPLETE_EXECUTION", "PRE_STATE", True
    return "FILLED", "POST_STATE", False


def test_sell_slippage_rejects_zero_or_negative_fill() -> None:
    assert sell_fill(0.05, 0.05, 20_000) is None
    assert sell_fill(0.05, 0.05, 50_000) is None
    assert sell_fill(0.05, 0.05, 0) is not None


def test_sell_slippage_does_not_clip_to_zero() -> None:
    # Old max(0, ...) behavior would return 0.0 here.
    assert sell_fill(0.10, 0.05, 20_000) is None


def test_buy_slippage_requires_positive_base_and_tick() -> None:
    assert buy_fill(0.0, 0.05, 10) is None
    assert buy_fill(1.0, 0.0, 10) is None
    assert buy_fill(1.0, 0.05, 10) > 1.0


def test_missing_leg_fails_entire_multi_leg_group() -> None:
    status = atomic_group_status([Leg(10.0, 0.05), Leg(None, 0.05), Leg(5.0, 0.05)])
    assert status == ("FAILED_INCOMPLETE_EXECUTION", "PRE_STATE", True)


def test_complete_group_fills_atomically() -> None:
    status = atomic_group_status([Leg(10.0, 0.05), Leg(2.0, 0.05), Leg(1.0, 0.05)])
    assert status == ("FILLED", "POST_STATE", False)


if __name__ == "__main__":
    tests = [
        test_sell_slippage_rejects_zero_or_negative_fill,
        test_sell_slippage_does_not_clip_to_zero,
        test_buy_slippage_requires_positive_base_and_tick,
        test_missing_leg_fails_entire_multi_leg_group,
        test_complete_group_fills_atomically,
    ]
    for test_fn in tests:
        test_fn()
    print(f"{len(tests)} execution-proxy regression tests passed")
