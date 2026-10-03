# Phase 1 Execution Proxy Specification — Bid/Ask-Free Sensitivity Model

Updated: 2026-10-03

## Purpose

The primary study may proceed without historical bid/ask only after independent tester approval of this proxy methodology. This is an explicit methodology change, not a relabeling of OHLC/LTP as quotes.

The study is explicitly a **proxy-execution backtest**. It cannot establish historical live-market fills.

## Frozen decision/execution convention

The strategy state is evaluated only on a completed 1-minute observation bar.

For a decision generated at completed bar timestamp **t**:

1. All trigger variables and strike-selection inputs use information available at or before the close of bar t.
2. The order group is submitted after bar t completes.
3. Each leg's base execution price is the **open of the first eligible 1-minute option bar strictly after t** for the selected historical contract.
4. The execution search is session-aware and contract-aware. It may not cross a contract expiry or an invalid session boundary merely to obtain a later price.
5. A multi-leg adjustment is an **atomic execution group**. No leg is partially filled in the proxy model.
6. The group is filled only if **every required leg** has a valid next eligible bar, valid positive open price, valid effective-date contract metadata, and valid tick-size metadata at the selected execution timestamp.
7. If any required leg is missing, invalid, expired, or otherwise fails the execution-quality checks, **none of the legs is filled**. The intended order group is recorded as FAILED_INCOMPLETE_EXECUTION; no synthetic, interpolated, stale, or later-bar fill is created.
8. On FAILED_INCOMPLETE_EXECUTION, the strategy retains the **pre-adjustment position and state**. The trigger that generated the failed adjustment is marked **consumed** and is not automatically retried.
9. A new adjustment may be generated only after the relevant trigger condition has first returned to the non-trigger region and subsequently re-entered the trigger region. This prevents repeated fills from one persistent trigger.
10. If the failed group concerns a transition that would have replaced an existing position, the existing position remains unchanged. It continues under the ordinary state rules until a later valid trigger, expiry rule, or separately specified forced-close event occurs.
11. If no valid execution occurs before the existing contract expires, no proxy fill is invented. The position follows the separately frozen expiry/settlement rule; the failed adjustment remains a recorded execution-data gap.
12. Repeated missing bars do not cause repeated synthetic attempts. Each completed decision bar can create at most one new adjustment event, and only a fresh trigger re-entry can create another group.

This is the fail-closed missing-execution rule. It is deterministic for pending multi-leg orders, strategy state, repeated missing bars, session boundaries and expiry.

## Conservative slippage model

For each option-leg order, adverse slippage is applied to the next eligible option-bar open.

For a buy:

P_fill = P_base + S(P_base)

For a sell:

P_fill = P_base - S(P_base)

where:

S(P) = max(one_tick, s * P)

A fill is **invalid and rejected** when P_base <= 0, P_fill <= 0, the effective historical tick size is unavailable/invalid, or required contract metadata are unavailable.

There is therefore **no max(0, ...)** floor and zero-price fills can never be manufactured.

The primary scenario uses s = 10 basis points per leg, with sensitivity scenarios at 0, 5, 10, 20 and 50 bps.

At 0 bps, the proportional slippage term is zero, but the historical one-tick floor remains active under this frozen convention. The 0-bps label therefore means zero proportional slippage, not frictionless execution.

The one-tick floor must use effective historical NIFTY option tick-size metadata for the contract date; it must not be a contemporary constant. NSE currently documents ₹0.05 price steps for NIFTY index options, but the research must use effective historical contract metadata rather than project current rules backward. citeturn0search1

## Transaction costs

Brokerage, statutory charges, exchange/IPFT charges, GST, STT and stamp duty are applied separately from slippage using date-effective schedules.

Paytm Money brokerage is modeled according to the applicable customer/pricing chronology documented in the Phase 1 cost specification. Historical statutory/exchange rates must be date-aligned; current rates may not be retrospectively applied.

Costs are calculated per leg/order and recorded in the trade ledger.

## Missing-data and marketability rules

- A missing next-bar execution price produces no synthetic fill.
- Zero/negative option prices are invalid.
- Contract identity must match the effective historical contract master.
- Option expiry, strike, CE/PE and lot size must be date-correct.
- No look-ahead strike selection is permitted.
- No interpolation across a missing execution bar is permitted.
- No LTP, close, midpoint or OHLC value may be relabeled as bid/ask.
- If a leg cannot be executed under the frozen proxy convention, the **whole multi-leg group fails atomically**.
- A failed group leaves the prior strategy state unchanged and consumes the triggering event.
- A fresh trigger requires exit from and re-entry into the trigger region.
- Expiry/session handling cannot be bypassed to manufacture a later execution bar.

## Required execution-state ledger

Every adjustment event must record at minimum:

decision_timestamp, order_group_id, pre_state, intended_legs, eligible_execution_timestamp_per_leg, execution_status, failure_reason, post_state, trigger_consumed, and retry_eligible_after_rearm.

For a failed group, post_state == pre_state, execution_status == FAILED_INCOMPLETE_EXECUTION, and trigger_consumed == true.

## Sensitivity and robustness analysis

The primary result is reported with 10-bps proportional adverse slippage per leg.

| Scenario | Proportional slippage |
|---|---:|
| Diagnostic lower bound | 0 bps |
| Low | 5 bps |
| Primary | 10 bps |
| High | 20 bps |
| Stress | 50 bps |

The historical tick floor remains active in every scenario unless a separately approved methodology change says otherwise.

Results must report gross P&L, slippage drag, brokerage/statutory cost drag, net P&L, maximum drawdown, tail losses, turnover, failed/missing executions, capital/margin utilization and sensitivity to the slippage scenario.

## Interpretation boundary

The study can answer whether the strategy appears robust under the specified proxy-execution assumptions.

It cannot establish that the strategy achieved those historical fills in the live market.

Any comparison with a future bid/ask dataset is a separate validation study.

## Methodology-change control

This specification supersedes the earlier mandatory historical bid/ask requirement for the primary backtest **only if independently approved by the tester**.

E065 and E066 are now explicitly addressed. Phase 2 remains blocked until the corrected exact developer head is independently reviewed and approved.