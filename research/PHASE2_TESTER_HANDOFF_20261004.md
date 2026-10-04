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

## 2026-10-04 — E146/E147 remediation handoff
Developer corrected E146 malformed GitHub Actions expressions and E147 scenario-artifact naming mismatch. The analysis job now asserts all five scenario artifacts (0/5/10/20/50 bps) before statistical processing.

Fresh tester audit is required on the exact post-remediation head. Production execution must still wait for authoritative historical NIFTY contract-master validation.


## E150 fresh independent audit — developer head 4adbd3fb7d3de5c5bb9328400b3f6ac359768104

Independently verify, without relying on developer assertions:
1. expiry_close_ts is bounded by the date-specific F&O execution-session close;
2. post-session observations cannot extend the expiry boundary;
3. the regression test exercises the corrected helper/path;
4. special-session handling cannot introduce an ineligible close;
5. contract_end/expiry chronology remains coherent;
6. E150 cannot introduce look-ahead or alter non-expiry execution timing;
7. re-audit E146–E149 and the complete state-machine/math/cost/slippage controls at this exact head;
8. assess whether E150 can materially change tested P&L or trade timing; do not require a full rerun unless impact is material;
9. do not issue final profitability/trading-strategy acceptance from source inspection alone.

Owner policy: continue under the lenient gate. No existing P&L is final. If E150 is materially outcome-changing, affected production scenarios become mandatory before final conclusion.


## E151 remediation audit — developer head 1501165689bf6f879628f34fab1fe787e1759697

Independently verify:
1. special-session timestamps must belong to an explicit execution interval;
2. timestamps in disjoint-session gaps are rejected;
3. dates beyond session_data_end fail closed;
4. contract-master and E150 impact scan exclude expiries beyond the documented session horizon;
5. the old-vs-corrected impact scan faithfully reproduces pre-E151 semantics and corrected semantics;
6. workflow uploads the impact scan and blocks production inference when affected groups exist;
7. exact SHA/reproducibility and E146–E150 controls remain intact;
8. if an independently executed impact scan reports affected groups, require affected production scenario reruns before final inference.

No final profitability conclusion is permitted until E150 materiality is quantitatively closed.


## Final E151 gate v2 — developer head 66e2a06850eb75f4b9eebca4bf994ba592a59ff7

Audit the exact head independently. Verify interval membership, horizon filtering, old-vs-corrected impact scan semantics, workflow fail-closed gating, exact SHA/reproducibility, and all prior E146-E150 controls. If affected contract groups are found, do not permit final inference without affected production reruns. If zero are found, quantify that result and assess whether E150 can be classified non-material for the tested study horizon.
