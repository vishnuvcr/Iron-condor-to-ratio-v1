# Phase 1 Acceptance Report — Interim

Updated: 2026-10-03

## Scope
This is an interim evidence report, not production-data acceptance or a profitability result.

## Canonical gate mapping
All Phase 1 acceptance references use the canonical G1–G14 vocabulary below.

| Gate | Meaning | Current status |
|---|---|---|
| G1 | Immutable primary dataset / provenance | PASS |
| G2 | Structural schema validation | PASS on prior pinned acquisition |
| G3 | Duplicate handling | PASS on prior pinned acquisition |
| G4 | Timestamp and session quality | **FAIL / OPEN — E046** |
| G5 | Underlying/option alignment | PRELIMINARY |
| G6 | Production historical Greeks / IV | OPEN |
| G7 | Target-delta availability | OPEN |
| G8 | Historical contract metadata | OPEN |
| G9 | Historical bid/ask / execution quality | BLOCKED |
| G10 | Date-specific transaction costs | OPEN |
| G11 | Market-context datasets | OPEN |
| G12 | Repaired CI execution | **PASS — independently verified** | Final-head run 37125656878 / job 111210327724; artifact 11275311823; artifact SHA-256 754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c |
| G13 | Independent tester approval | FAIL / BLOCKED |
| G14 | Phase 2 authorization | BLOCKED |

**Important:** Older evidence below may contain historical run-specific gate language. Those historical labels are retained as evidence, but the canonical interpretation is the table above.

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


## Independent tester final-head re-audit — E046
- Exact final-head CI execution is independently verified and closes the prior E045 evidence mismatch for G12.
- The G4 artifact itself reports 1,254 normal eligible dates, 7 special sessions, 1 data-gap exclusion, and 0 unreconciled observed rows. These output counts are internally consistent with the tested dataset.
- However, the implementation remains fail-open for missing special-session dates because `phase1_session_reconciliation.py` only iterates dates present in the observed dataset. A special date declared in the manifest but absent from the data is never processed. The implementation also does not enforce the session-calendar specification's requirement that every observed date map to exactly one canonical session row.
- Therefore G4 is not accepted despite the successful final-head CI run. G13 and G14 remain blocked.