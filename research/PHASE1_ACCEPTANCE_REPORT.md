# Phase 1 Acceptance Report — Interim

Updated: 2026-10-03 — E053 re-audit / E054

## Scope

This is an interim evidence report, not production-data acceptance or a profitability result.

## Current canonical gate state

| Gate | Meaning | Current status |
|---|---|---|
| G1 | Immutable primary dataset / provenance | PASS |
| G2 | Structural schema validation | PASS |
| G3 | Duplicate handling | PASS |
| G4 | Timestamp and session quality | **PASS — independently verified** |
| G5 | Underlying/option alignment | PRELIMINARY / OPEN |
| G6 | Production historical Greeks / IV | OPEN |
| G7 | Target-delta availability | OPEN |
| G8 | Historical contract metadata | OPEN |
| G9 | Historical bid/ask / execution quality | **BLOCKED** |
| G10 | Date-specific transaction costs | OPEN |
| G11 | Market-context datasets | OPEN |
| G12 | Repaired CI execution | **PASS — independently verified** |
| G13 | Independent tester approval | **BLOCKED** |
| G14 | Phase 2 authorization | **BLOCKED** |

## Current decision

**Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED.**

## E054 re-audit note

Developer PR #21 corrected the stale G4/G12 top-level gate-state problem. Independent re-audit found one remaining current-state defect: the developer README explicit branch field still names phase-1-e046-bidirectional-reconciliation instead of the actual developer branch phase-1-e053-control-sync. This does not invalidate Run #55 G4/G12 evidence, but E054 must be corrected before control-plane synchronization is fully closed.
## Primary source
- Dataset: `thetrademarkk/india-index-options-1m`
- License documented by the dataset card: CC-BY-NC-4.0.
- Immutable acquisition revision: `0f4800e`.
- Historical bid/ask is not documented in the source schema.

## Acquisition evidence
Earlier structural and pinned-source runs are retained as historical evidence. They do not constitute final Phase 1 approval because the repaired audit has not yet had independently verifiable Actions execution.

## Official exchange cross-checks
NSE current option-chain documentation exposes LTP, OI, volume, IV and best bid/ask, but it is not treated as a historical intraday quote archive.

NSE Circular 128/2024 revised NIFTY's lot size from 25 to 75 for new index derivatives introduced from 20 November 2024 onward. The 2025 expiry-day transition likewise requires effective-date contract metadata.

## Paytm Money cost evidence
Paytm Money publications document cohort/date-dependent brokerage and the 1 October 2024 option-sale STT change. The production cost engine must use a date-specific schedule and must not apply one current brokerage rate retrospectively.

## Historical evidence
- Prior pinned structural audit: 37116400642; 109,112,358 rows; 0 hard structural failures; 30,363,281 exact duplicates; 0 conflicting duplicate groups.
- NIFTY-only scoped audit: 37116565802; 108,625,497 rows; 0 hard failures; 30,363,281 exact duplicates; no bid/ask fields.
- Run 21: 37117424573; structural validation and deterministic deduplication passed, with diagnostic market-quality output. NIFTY daily timestamp counts ranged from 6 to 420 across 1,262 dates. Its r=q=0 Greek sample is diagnostic-only.
- Run 22: 37118147417; structural validation and deterministic deduplication passed, but E029 caused the market-quality audit to fail before completion.
- Repaired audit commit: 336c8e8ddf5de93f31ef6b114e621747ae956620.
- Tester audit of PR #13: Phase 1 FAIL. The repaired commit has no independently verifiable successful Actions execution.

## Current decision
**Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED.**

The next acceptance run must independently execute the repaired audit, characterize the 1,262 session-length observations, and then resolve the remaining G5–G12 production gates. An independent tester must subsequently record PASS for G13 before G14 can be opened.


The repaired audit now has a successful, independently inspectable Actions execution. This closes G12 only; it does not close G4–G11 or authorize Phase 2.


## G4 reconciliation result — developer evidence
- Run `37124047220`, job `111205697146`, completed successfully.
- Artifact `11274239403`, SHA-256 `141abc86ec20be5d34c8c4fcb6735fd04a8da10e4c5e9d7dc15158a5ec7eb48b`.
- Session reconciliation: 1,254 normal eligible dates; 7 documented special-session dates; 1 pre-registered incomplete-session exclusion (2026-06-03); 0 unreconciled dates.
- The regular execution window is 09:15–15:30 Asia/Kolkata. Out-of-window source observations are retained and quantified but are not eligible for strategy decisions.
- G4 is **PASS on developer evidence**, pending independent tester verification.


## E046 corrective re-audit status — 2026-10-03

Independent tester PR #18 identified E046: the G4 reconciler only iterated dates present in the observed NIFTY dataset, so a special-session date declared by the authoritative manifest but absent from the data could never become UNRECONCILED. The tester also required the one-to-one observed-date/session mapping specified by PHASE1_SESSION_CALENDAR_SPEC.md.

The developer accepted E046 without advancing any gate. Corrective branch: phase-1-e046-bidirectional-reconciliation. The implementation now performs manifest/data and data/manifest reconciliation, validates duplicate/overlapping mappings, and includes four regression tests.

Current state: G4 FAIL/OPEN; G12 OPEN for the corrective head; G13 BLOCKED; Phase 2 BLOCKED.


## E046/E047 exact-head evidence — 2026-10-03
- Corrective head: 4099cd1217f072be961f120ab114034578e19197.
- Actions run: 37129894485; job: 111222750604; all job steps completed successfully.
- Artifact: 11275819920; SHA-256: 57cdcc53ec350fea1ce398f1130d5dd66beb63cdc0b481485e2b0e4fe3d54178.
- Reconciliation artifact: 1,262 observed dates; 13 manifest control dates; 1,251 normal eligible; 10 special-session reconciled; 1 data-gap excluded; 0 unreconciled; 0 missing manifest-session dates.
- E047 arose when the fail-closed exact-head run identified three genuine documented weekend live-trading dates absent from the control manifest. Those dates were added with dated exchange-source references and the exact-head rerun then passed.
- Developer evidence: G4 PASS and G12 PASS for the exact corrective head. Independent approval is not yet granted; G13 remains BLOCKED. Phase 2 remains BLOCKED.


## Independent tester Run #55 determination — 2026-10-03
- Exact developer tip `378a130b6d450b288be140655f9b0b75aad840b3` was independently verified against Actions run `37135122966`, job `111238039571`, artifact `11278418088`.
- G4 is independently PASS: the artifact reports 1,262 observed dates, 13 manifest controls, 10 special-session reconciliations, 1 data-gap exclusion, 0 unreconciled dates, and 0 missing manifest-session dates; the four E046 regression tests passed.
- G12 is independently PASS.
- G13 remains BLOCKED because G5–G11 are not all production-accepted. Phase 2 remains blocked.
- E053: stale canonical/top-level control-plane status remains to be synchronized.