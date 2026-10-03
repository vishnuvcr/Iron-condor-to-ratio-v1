# Tester Report — Approval of Bid/Ask Avoidance Methodology

Updated: 2026-10-03

## Audited developer head

PR #31 exact head: `8b99cb3b2b537c5b085c09729c27bb3957285ae8`.

## Determination

**APPROVED: the study may avoid historical bid/ask for the primary backtest under the revised proxy-execution methodology.**

This is approval of the explicit methodology change, not a claim that historical bid/ask exists and not approval of Phase 2.

### E065 re-audit — PASS

The corrected specification now defines deterministic atomic handling:
- every leg must have a valid next eligible bar;
- any missing/invalid/expired leg causes the entire group to fail;
- no partial or synthetic fill is created;
- the pre-adjustment state is retained;
- the triggering event is consumed;
- retry requires trigger exit and re-entry;
- session and expiry boundaries cannot be crossed to manufacture a fill;
- repeated missing bars cannot generate repeated synthetic attempts.

This closes the ambiguity identified in tester PR #30.

### E066 re-audit — PASS

The corrected specification now uses:
- sell fill = base price minus adverse slippage;
- buy fill = base price plus adverse slippage;
- non-positive base or adjusted fills are rejected;
- zero-price clipping is prohibited.

The regression tests encode these rules.

### Methodology controls confirmed

1. Completed 1-minute bar is the latest information point for the decision.
2. Execution uses the first eligible option-bar open strictly after the decision timestamp.
3. Historical tick-size metadata are required; no contemporary rule is projected backward.
4. Slippage scenarios are frozen at 0/5/10/20/50 bps proportional adverse slippage, with the historical one-tick floor active in every scenario.
5. Ten bps remains the primary scenario.
6. Brokerage and statutory/exchange costs remain date-effective and separate from slippage.
7. OHLC/LTP is never relabeled as bid, ask or midpoint.
8. Missing execution observations are fail-closed.
9. The study is explicitly described as proxy-execution research and cannot claim historical live-market fills.
10. A future bid/ask dataset can be used only as separate external validation.

## G9 determination

**G9 = PASS under the revised methodology.**

The original historical-bid/ask requirement is retired for the primary backtest. G9 now means that the pre-registered proxy-execution methodology is the accepted execution-quality model for this research.

This does **not** mean the primary dataset contains bid/ask. It does not.

## Remaining Phase 1 status

G1–G4 and G12 retain their prior accepted status.

G5, G6, G7, G8, G10 and G11 remain open/preliminary as previously documented.

Therefore:
- **G13 = BLOCKED**
- **G14 = BLOCKED**
- **Phase 2 = BLOCKED**

No backtest, optimization, profitability result or trading conclusion is authorized by this approval alone.

## Tester approval statement

The tester explicitly approves **avoidance of historical bid/ask** for the primary backtest, conditional on implementation exactly matching the frozen proxy specification and subsequent Phase 2 validation tests.

