# Tester Report — Bid/Ask-Free Execution Methodology

Updated: 2026-10-03

## Scope
Developer methodology-change head audited: 010e40bdba5c92ba9f109e720e30e2f6a7125cfd.

The tester independently reviewed the new execution-proxy specification and its integration into RESEARCH_PLAN.md and Phase 1 controls.

## Positive findings
- The change is explicit rather than a silent OHLC/LTP substitution.
- The study is correctly relabeled as proxy-execution research.
- Decisions are frozen to completed 1-minute bars.
- Execution is delayed to the next eligible option bar open, avoiding use of the decision bar's close as an alleged executable quote.
- Slippage is pre-registered at 0/5/10/20/50 bps, with 10 bps as the primary scenario.
- A historical one-tick floor is specified.
- Brokerage/statutory/exchange costs remain separate and date-effective.
- The specification explicitly prohibits relabeling OHLC/LTP as bid/ask.
- The interpretation boundary correctly states that the study cannot establish historical live-market fills.
- Phase 2 remains blocked pending tester review.

## Finding E065 — Missing-next-bar execution rule is not fully deterministic
The specification says that when the next eligible option bar is missing, the event is recorded as an execution-data gap and handled by a pre-registered missing-execution rule, but it does not actually define that rule.

This matters because the treatment can materially change strategy state and P&L. The methodology must specify, before backtesting, exactly what happens to the pending order, other legs of the same multi-leg adjustment, the strategy state/trigger, subsequent bars, expiry/session-end cases, and repeated missing bars.

Required correction: define a deterministic fail-closed rule, such as recording the intended order, not filling it, marking the adjustment as failed/incomplete, and defining whether the strategy remains in the prior state or transitions to a separately specified unresolved state. The chosen rule must be fixed before Phase 2.

Disposition: OPEN.

## Finding E066 — Sell-side slippage formula conflicts with invalid-price rule
The specification currently defines the sell fill as max(0, P_base - S(P_base)) but later states that zero/negative option prices are invalid.

If slippage exceeds the base price, the formula can generate zero, which the same specification says is invalid. The mathematical convention should instead fail the fill whenever the adverse adjusted price is non-positive, rather than manufacture a zero-price fill.

Required correction: define sell fills as P_fill = P_base - S(P_base) and reject the fill when P_fill <= 0; apply the same explicit positivity rule to buy fills.

Disposition: OPEN.

## Additional tester observations
1. The one-tick floor must be tied to the effective historical contract/tick-size metadata already required by G8; it must not be a contemporary constant.
2. The next-bar selection must be deterministic across session boundaries and contract expiry.
3. Slippage sensitivity is useful, but the final manuscript must clearly label the 0-bps case as a lower-bound diagnostic rather than realistic execution.
4. The primary 10-bps assumption should remain fixed before any performance results are inspected.
5. Any future bid/ask dataset can be used for a separate external validation study, but must not retroactively change the primary proxy result selection.

## Gate determination
| Item | Tester status |
|---|---|
| Methodology change | NOT YET APPROVED |
| G9 | BLOCKED — methodology correction required |
| G13 | BLOCKED |
| G14 | BLOCKED |
| Phase 2 | BLOCKED |

No backtest or profitability analysis is authorized.

## Required developer corrections
1. Define the exact missing-next-bar/order-state rule.
2. Correct the sell-side slippage formula so non-positive fills fail rather than become zero.
3. Re-run the independent tester audit on the corrected exact developer head.
4. Keep the 0/5/10/20/50-bps sensitivity schedule unchanged unless a new methodology change is explicitly proposed.