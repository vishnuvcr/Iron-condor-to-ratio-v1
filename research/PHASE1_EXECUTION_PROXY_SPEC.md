# Phase 1 Execution Proxy Specification — Bid/Ask-Free Sensitivity Model

Updated: 2026-10-03

## Purpose

The research methodology is formally changed so that historical bid/ask is **not a mandatory data requirement** for the primary backtest.

This is a methodological change, not a data substitution. The research will not describe OHLC or LTP as historical bid/ask, midpoint, or executable quotes.

The resulting study will be explicitly described as a **proxy-execution backtest**. Historical bid/ask-dependent claims will not be made.

## Frozen decision/execution convention

The strategy state is evaluated only on a completed 1-minute observation bar.

For a decision generated at completed bar timestamp (t):

1. All trigger variables and strike-selection inputs must use information available at or before the close of bar (t).
2. The order is submitted after bar (t) is complete.
3. The base execution price is the **open of the next eligible 1-minute option bar**, (t+1), for the selected historical contract.
4. If the next eligible bar is missing, the trade is not silently filled. The event is recorded as an execution-data gap and handled by a pre-registered missing-execution rule.
5. The base price is not called bid, ask, midpoint, or executable market price.

This convention prevents using the completed decision bar's closing price as though it were a contemporaneous executable quote and prevents use of information from after the decision bar except the explicitly modeled next-bar execution observation.

## Conservative slippage model

For each option-leg order, adverse slippage is applied to the next-bar open.

For a buy:

[
P_{fill}=P_{base}+S(P_{base})
]

For a sell:

[
P_{fill}=max(0,P_{base}-S(P_{base}))
]

where:

[
S(P)=max(	ext{one tick},; sP)
]

The primary scenario uses a pre-registered slippage rate (s=10) basis points per leg, with sensitivity scenarios at 0, 5, 10, 20 and 50 basis points.

The one-tick floor uses the effective historical NIFTY option tick-size rule applicable to the contract date. If the price is non-positive or the required contract/tick metadata are unavailable, the fill is invalid rather than fabricated.

The 0-bps scenario is a diagnostic lower-cost bound, not an assertion of frictionless execution.

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
- If a leg cannot be executed under the frozen proxy convention, the strategy state records the failed execution explicitly.

## Sensitivity and robustness analysis

The primary result is reported with 10-bps adverse slippage per leg.

Required sensitivity runs:

| Scenario | Slippage |
|---|---:|
| Diagnostic lower bound | 0 bps |
| Low | 5 bps |
| Primary | 10 bps |
| High | 20 bps |
| Stress | 50 bps |

Additional robustness analyses must vary execution timing within the permitted observable-bar convention where data support it, without selecting the favorable result after observing outcomes.

Results must report:

- gross P&L;
- slippage drag;
- brokerage/statutory cost drag;
- net P&L;
- maximum drawdown;
- tail losses;
- turnover;
- number of failed/missing executions;
- capital/margin utilization;
- sensitivity of conclusions to the slippage scenario.

## Interpretation boundary

The study can answer whether the strategy appears robust under the **specified proxy-execution assumptions**.

It cannot establish that the strategy achieved those historical fills in the live market.

Any comparison with a future bid/ask dataset must be treated as a separate validation study.

## Methodology-change control

This document supersedes the previous requirement that historical bid/ask be mandatory for the primary backtest. The research plan and Phase 1 gate documentation must reference this specification.

Phase 2 remains blocked until an independent tester reviews and approves this methodology change.
