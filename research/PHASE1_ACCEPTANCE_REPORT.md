# Phase 1 Acceptance Report — Interim

Updated: 2026-10-03

## Scope
This is an interim evidence report, not production-data acceptance or a profitability result.

## Canonical gate mapping
All Phase 1 acceptance references use the canonical G1–G14 vocabulary below.

| Gate | Meaning | Current status |
|---|---|---|
| G1 | Immutable primary dataset / provenance | PARTIAL |
| G2 | Structural schema validation | PASS on prior pinned acquisition |
| G3 | Duplicate handling | PASS on prior pinned acquisition |
| G4 | Timestamp and session quality | OPEN |
| G5 | Underlying/option alignment | PRELIMINARY |
| G6 | Production historical Greeks / IV | OPEN |
| G7 | Target-delta availability | OPEN |
| G8 | Historical contract metadata | OPEN |
| G9 | Historical bid/ask / execution quality | BLOCKED |
| G10 | Date-specific transaction costs | OPEN |
| G11 | Market-context datasets | OPEN |
| G12 | Repaired CI execution | FAIL / unverified |
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
