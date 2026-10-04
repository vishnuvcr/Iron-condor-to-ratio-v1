# Phase 2 Tester Handoff — Deterministic Engine Milestone

Effective: 2026-10-04

## Developer branch
- Branch: `phase-2-backtest-engine-20261004`
- Current work: deterministic backtest engine under the owner progression waiver.
- No optimization or profitability claim.

## Independent checks requested

Verify independently:

1. State-machine correctness
   - 30Δ/10Δ IC construction.
   - Crossing semantics for 10Δ IC short trigger.
   - Downward → call ratio; upward → put ratio.
   - 0.50 / 0.40×2 / 0.10 initial ratio.
   - 0.80→0.20 continuation trigger and 0.40 / 0.30×2 / 0.08 reset.
   - >=1.20 reversal trigger and opposite ratio construction.
   - Trigger consumption and re-arm after failed adjustments.

2. Chronology / look-ahead
   - decisions use current completed bar;
   - target strike selection cannot use later bars;
   - fills use strictly the first eligible option bar after the decision;
   - no expiry crossing or later-bar fallback;
   - date-specific expiry close metadata are used.

3. Atomic execution
   - any missing/invalid leg causes the entire group to fail;
   - no partial fill leakage into fill/cash/charge ledgers;
   - failed transitions preserve pre-state;
   - persistent triggers cannot repeatedly fire without re-arm.

4. Slippage and costs
   - adverse buy/sell formulas;
   - historical tick-size floor;
   - 0/5/10/20/50-bps configuration;
   - dated cost-rule resolution;
   - missing cost rules fail closed;
   - brokerage is per executed leg/order in the current implementation;
   - no double counting within the cost layer.

5. Reproducibility
   - normalized input contract;
   - source hashes;
   - exact Git SHA manifest;
   - deterministic tie-breaking;
   - regression test coverage.

## Known research limitations

The current Phase 2 engine intentionally requires upstream normalized `abs_delta`, effective tick/lot sizes, date-specific `expiry_close_ts`, session flags and complete dated costs. It does not claim to have generated these inputs yet.

The historical G6 D1–D3 evidence gaps remain deferred under the owner progression waiver and must be audited at milestone/final acceptance. Material mathematical, data, look-ahead, cost/slippage, logic or reproducibility failures remain blocking.

## Suggested milestone verdict categories

- PASS / no material findings
- PASS WITH CONDITIONS / non-material deferred findings
- FAIL / material correctness or reproducibility defect

No tester report should be inferred from this handoff alone.

## 2026-10-04 — Fresh exact-head milestone scope

Current developer head after chronology, contract-master, normalization and production-workflow hardening: 2939f05e5b604e6a7694c594b20749d6b2cafaf3.

Additional mandatory checks:
- E142 timezone correction: naive G6 IST timestamps must remain IST in Phase 2.
- Historical contract-master validator must fail closed when absent or inconsistent.
- G4 reconciliation must gate normalized trading days.
- Normalization must require raw option open prices, exact underlying timestamp matches, strict-prior r/q, contract lifecycle validity, and production Greeks.
- Cycle runner must process the selected monthly-expiry schedule without overlapping positions and must fail on terminal unclosed cycles.
- Static IC benchmark mode must use the same execution/cost layer.
- Production workflow must cache normalized data across matrix jobs and produce deterministic scenario artifacts.
- No CI success may be inferred where the connector exposes no exact-head run.
