# Phase 1 Gate Matrix

Updated: 2026-10-03 — E053 re-audit / E054

This matrix is the Phase 1 acceptance checklist. A source-validation PASS does not equal production-data acceptance.

| Gate | Requirement | Current state | Evidence / blocker |
|---|---|---|---|
| G1 | Immutable primary dataset / provenance | PASS | HF revision 0f4800e; pinned manifest |
| G2 | Structural schema validation | PASS | 108,625,497 raw rows; 0 hard failures |
| G3 | Duplicate handling | PASS | 30,363,281 exact duplicates; 0 conflicting duplicate groups; deterministic deduplication |
| G4 | Timestamp/session quality | **PASS — independently verified** | Run #55 / exact developer evidence independently verified |
| G5 | Underlying/option alignment | PRELIMINARY / OPEN | Diagnostic alignment is not production acceptance; decision-time coverage remains open |
| G6 | Production historical Greeks / IV | OPEN | Date-aligned r/q and production IV/Greek validation incomplete |
| G7 | Target-delta availability | OPEN | Frozen delta tolerance plus quote/volume/OI availability must be measured |
| G8 | Historical contract metadata | OPEN | Effective-date expiry/lot/tick reconciliation incomplete |
| G9 | Historical bid/ask / execution quality | **BLOCKED** | Historical bid/ask/order-level reconstruction data not acquired/validated |
| G10 | Date-specific transaction costs | OPEN | Complete date-specific brokerage/statutory/exchange schedule incomplete |
| G11 | Market-context datasets | OPEN | Required aligned context package incomplete |
| G12 | Repaired CI execution | **PASS — independently verified** | Run #55 / exact developer evidence independently verified |
| G13 | Independent tester approval | **BLOCKED** | G5–G11 not all production-accepted; E054 remains open |
| G14 | Phase 2 authorization | **BLOCKED** | Cannot begin until G13 PASS |

## Current decision

**Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED.**

## E054 re-audit note

PR #21 substantively synchronized the developer control-plane status. The independent re-audit found one remaining stale current-state identifier in the developer README: its explicit branch field names the superseded E046 branch rather than phase-1-e053-control-sync. E054 remains open until corrected and re-audited.
## Non-negotiable acceptance rules

1. No close-price substitution for the frozen historical bid/ask midpoint rule without an explicit pre-registered methodology change.
2. No contemporary risk-free rate or current cost schedule may be applied retrospectively.
3. Historical lot size, expiry day and tick/contract rules must use effective-date metadata.
4. No Phase 2 engine, optimization, profitability result or strategy conclusion may be accepted before the independent tester PASS.
5. Any future methodology change must update RESEARCH_PLAN.md only if the planned research itself changes; ordinary execution errors belong in ERROR_LOG.md.


## Canonical vocabulary control
This file is the authoritative G1–G14 gate dictionary. No other Phase 1 document may assign a different meaning to these IDs.


## E046 — bidirectional G4 reconciliation blocker

| Gate | Requirement | Current state | Evidence / blocker |
|---|---|---|---|
| G4 | Timestamp/session quality | FAIL / OPEN | E046: prior reconciler iterated only observed dates, so manifest-only special sessions could disappear from the acceptance result. Corrective branch adds bidirectional manifest/data reconciliation, unique canonical mapping validation, fail-closed unknown-date handling, and regression tests. Fresh final-head CI and independent re-audit required. |
| G12 | Repaired CI execution | OPEN for corrective head | Previous final-head run 37125656878 remains valid for the superseded head 09c4c2e4b6bc569d42d4743fac5132ad0672f8d8. This corrective branch requires a new final-head execution. |

Phase 2 remains BLOCKED.


## E046/E047 current gate state — 2026-10-03
| Gate | Current state | Current evidence / blocker |
|---|---|---|
| G4 | PASS — developer evidence | Exact corrective-head run 37129894485 / job 111222750604; artifact 11275819920; 0 unreconciled and 0 missing manifest-session dates. |
| G12 | PASS — developer evidence | Exact corrective head 4099cd1217f072be961f120ab114034578e19197 executed successfully through all Phase 1 CI steps. |
| G13 | BLOCKED | Independent tester must re-audit the exact corrective head and record PASS/FAIL. |
| G14 | BLOCKED | Phase 2 cannot begin until G13 PASS and all Phase 1 gates are accepted. |

E047 is resolved as a control-manifest completion issue. The three newly controlled weekend sessions are 2024-01-20, 2025-02-01 and 2026-02-01. No gate beyond G4/G12 is advanced by this evidence.


## Independent tester Run #55 determination — 2026-10-03
- **G4 PASS — independently verified.** Exact tip `378a130b6d450b288be140655f9b0b75aad840b3`, run `37135122966`, job `111238039571`, artifact `11278418088`.
- **G12 PASS — independently verified.** Artifact digest matches GitHub's recorded digest; all substantive CI steps completed successfully.
- **G13 BLOCKED.** G5–G11 remain incomplete/open/blocked, especially G9 historical bid/ask/execution data.
- **E053 OPEN:** canonical/top-level status text is stale and must be synchronized before final Phase 1 approval.
- G14 / Phase 2 remains BLOCKED.
## E055 re-audit note
- E054 README branch provenance is corrected at developer PR #23.
- E055 remains open because the E054 conversation-log entry contains a malformed exact PR #21 head SHA.
- Canonical gate state remains G4/G12 independently PASS; G5–G8/G10–G11 open; G9 blocked; G13/G14 blocked; Phase 2 blocked.