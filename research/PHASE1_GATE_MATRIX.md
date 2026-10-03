# Phase 1 Gate Matrix

Updated: 2026-10-03

This matrix is the Phase 1 acceptance checklist. A source-validation PASS does not equal production-data acceptance.

| Gate | Requirement | Current state | Evidence / blocker |
|---|---|---|---|
| G1 | Immutable primary dataset | PASS | HF revision 0f4800e; pinned manifest |
| G2 | Structural schema validation | PASS | 108,625,497 raw rows; 0 hard failures |
| G3 | Duplicate handling | PASS | 30,363,281 exact duplicates; 0 conflicting duplicate groups; deterministic dedup implemented |
| G4 | Timestamp/session quality | OPEN | Prior audit found 1,262 NIFTY dates with 6–420 timestamps/day; repaired diagnostic must execute and anomalies reconciled to historical sessions |
| G5 | Underlying/option alignment | PRELIMINARY PASS | Prior diagnostic alignment 99.2953%; production decision-time quality still open |
| G6 | Historical Greeks | OPEN | RBI r source and NSE q source identified; complete date-aligned series and production IV/Greek calculation still required |
| G7 | Target-delta availability | OPEN | Must apply frozen ±0.05 delta tolerance, quote quality and volume/OI filters |
| G8 | Contract metadata | OPEN | Official NSE lot/expiry changes identified; effective-date contract files still need machine-readable reconciliation |
| G9 | Historical bid/ask | BLOCKED | Primary and reviewed alternatives lack historical bid/ask; NSE historical order/trade data is preferred procurement candidate |
| G10 | Transaction costs | OPEN | Paytm Money brokerage/STT chronology validated; complete date-specific exchange/IPFT/SEBI/GST/stamp/clearing schedule not yet assembled |
| G11 | Context variables | OPEN | NIFTY/India VIX/FII/DII/GIFT NIFTY/global/BSE/events registered; complete aligned datasets not yet assembled |
| G12 | Repaired CI execution | OPEN | E029 repaired; API-created commits did not emit a new Actions status in this environment |
| G13 | Independent tester approval | BLOCKED | Required before Phase 2 |
| G14 | Phase 2 | BLOCKED | Cannot begin until G1–G13 are accepted and tester explicitly PASSes |

## Non-negotiable acceptance rules

1. No close-price substitution for the frozen historical bid/ask midpoint rule without an explicit pre-registered methodology change.
2. No contemporary risk-free rate or current cost schedule may be applied retrospectively.
3. Historical lot size, expiry day and tick/contract rules must use effective-date metadata.
4. No Phase 2 engine, optimization, profitability result or strategy conclusion may be accepted before the independent tester PASS.
5. Any future methodology change must update RESEARCH_PLAN.md only if the planned research itself changes; ordinary execution errors belong in ERROR_LOG.md.


## Canonical vocabulary control
This file is the authoritative G1–G14 gate dictionary. No other Phase 1 document may assign a different meaning to these IDs.
