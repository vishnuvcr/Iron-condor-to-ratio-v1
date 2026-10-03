# Phase 1 Acceptance Report — Interim

Updated: 2026-10-03

## Scope

This report records the Phase 1 data-acquisition evidence accumulated so far. It is an interim acceptance record, not a production-data acceptance or profitability result.

## Primary source

- Dataset: `thetrademarkk/india-index-options-1m`
- License documented by the dataset card: CC-BY-NC-4.0.
- Dataset documentation describes 1-minute OHLCV(+OI) bars for NIFTY/BANKNIFTY/SENSEX index spot and option chains, with IST timestamps and option strike/type/expiry fields.
- The dataset documentation explicitly warns that option coverage is partial and illiquid/far strikes may be sparse.
- Immutable acquisition revision now pinned to `0f4800e` in `data/manifests/phase1_sources.json`.
- Historical bid/ask is not documented in the source schema; execution therefore cannot be represented as historical bid/ask unless an independent quote source is validated.

## Acquisition evidence

The earlier structural acquisition downloaded 269 parquet files and passed the corrected schema/duplicate validation workflow.

Evidence:
- workflow run: 37116084761
- job: 111183065244
- validation artifact: 11271990517
- artifact SHA-256: 67fd3898800131d736a5652d1ece3c112c4b5b0489ffe07468f5865fb850d789

That run used mutable `main`, so it is retained as historical evidence only. Production validation must use the pinned revision.

## Official exchange cross-checks

NSE's current option-chain documentation exposes LTP, OI, volume, IV and best bid/ask fields, but the displayed IV is described as reference-only and the site terms restrict copying/aggregation. It therefore serves as an authoritative reference/reconciliation source, not as an assumed historical intraday archive.

NSE Circular 128/2024 revised NIFTY's lot size from 25 to 75 for new index derivatives introduced from 20 November 2024 onward.

NSE Circular 103/2025 and Circular 111/2025 establish the 2025 expiry-day transition and the Tuesday expiry regime for newly introduced NIFTY contracts, with explicit transition treatment for already introduced contracts. Historical contract masters must therefore be applied by effective date.

## Paytm Money cost evidence

Paytm Money's published materials document date/cohort-dependent brokerage. Its 25 August 2023 notice states ₹20 per executed order for new users from that date while earlier cohorts retained older schedules. Its January 2025 update states flat ₹20 brokerage across segments from 15 January 2025. Paytm Money also documents the option-sale STT change to 0.1% effective 1 October 2024.

The production cost engine must therefore use a date-specific schedule and must not apply one current brokerage rate retrospectively.

## Acceptance matrix

| Gate | Current status | Evidence / next action |
|---|---|---|
| G1 Provenance | PARTIAL/PASS | Source, license and pinned revision recorded; final file-level hashes still required. |
| G2 Schema | PASS (structural) | Corrected validator passed on prior acquisition. Re-run required on pinned revision. |
| G3 Time integrity | PARTIAL | Structural checks exist; full production report on pinned revision required. |
| G4 Market-data integrity | PARTIAL | Structural checks exist; stale/missing coverage statistics and execution-quality assessment remain. |
| G5 Contract integrity | OPEN | Historical effective-date contract master reconciliation required. |
| G6 Underlying alignment | OPEN | Pinned-revision option/index timestamp alignment must be quantified. |
| G7 Greek provenance | OPEN | No vendor Greeks are documented. Reconstruct Greeks under the frozen Phase 0 model and report solver success/failure. |
| G8 Target-strike availability | OPEN | Quantify target-delta availability at one-minute decision timestamps under the frozen ±0.05 tolerance and liquidity filters. |
| G9 Execution fields | ASSESSED / DEGRADED | Primary source does not document bid/ask. Independent historical quote source remains unvalidated; fallback slippage must remain explicitly flagged. |
| G10 NSE reconciliation | OPEN | Reconcile selected daily aggregates and historical contract metadata against official NSE references. |
| Costs | OPEN | Build and validate date-specific Paytm Money + statutory/exchange schedule. |
| Context data | OPEN | Collect NIFTY, India VIX, FII/FPI, DII, GIFT NIFTY/overnight, global risk/volatility, NSE/BSE and event context where applicable. |

## Gate decision

**Phase 1 remains IN PROGRESS and is not approved for Phase 2.**

The next technical step is to validate the pinned revision and generate the full Phase 1 audit report. Only after all acceptance gates are evidenced and an independent tester approves the final Phase 1 branch may the backtest engine phase begin.

## External source notes

The public source review supports the source schema, license, historical revision history, NSE contract changes, and Paytm Money pricing changes. These external findings are documented as source evidence, not as strategy-performance evidence.

## Pinned-source structural audit result — 2026-10-03

The pinned-revision workflow completed successfully on commit 8f094253c2a925b2727c2ffef0a39fa72e23d609.

- Workflow run: 37116400642
- Job: 111183955555
- Artifact: 11271442031
- Artifact SHA-256: 137396eab20370bbbf2285cbc684f7db1e1693d0b3a88f7c64f77a2e8ea967d0
- Files audited: 269 (267 option files + 2 index files under the earlier broad acquisition pattern)
- Total rows audited: 109,112,358
- Hard-failure files: 0
- Files with quality flags: 138
- Exact duplicate rows: 30,363,281
- Conflicting duplicate-key groups: 0
- Nonpositive closes: 0
- Historical bid/ask columns observed: none
- Source timestamps: IST documented by the dataset; validator converted them to UTC for structural checks
- Observed span in the audited files: 2021-05-07 through 2026-07-02 UTC representation

The exact duplicates are conflict-free, but their scale is material (about 27.8% of all audited rows). They will be deterministically removed before production backtesting, with pre/post counts retained in the audit trail. This is a data-quality issue, not evidence of strategy performance.

The acquisition scope has since been narrowed to the exact NIFTY underlying file rather than the earlier wildcard that also captured BANKNIFTY. A fresh validation run is required after that scope correction.

## Deterministic deduplication control — 2026-10-03

A deterministic transformation `scripts/deduplicate_phase1_data.py` has been added. It removes exact duplicate rows only, retains the first occurrence deterministically, rejects conflicting duplicate keys, and records source/output SHA-256 hashes and row counts. The CI workflow now runs this transformation after structural validation. This is a reproducibility control, not an assumption that duplicates are economically meaningful observations.

The workflow was also given a concurrency group and conditional cache-save logic after a cache-reservation race was observed during rapid successive commits (E025).


## Run 21 market-quality evidence — 2026-10-03

Workflow run 37117424573 completed successfully with structural validation, deterministic deduplication, and the diagnostic market-quality/Greek-feasibility audit.

- 268 files: 267 NIFTY option files + 1 NIFTY index file.
- Structural input rows: 108,625,497; hard failures: 0; conflicting duplicate-key groups: 0.
- Exact duplicate rows removed deterministically: 30,363,281.
- Post-dedup rows: 78,262,216.
- Market-quality option rows after key-level deduplication: 77,776,166.
- Option rows aligned to a NIFTY timestamp: 77,228,081 (99.2953%).
- NIFTY dates: 1,262; daily timestamp count median 378, minimum 6, maximum 420.
- The session-count range is not accepted as uniform market-session coverage. Dates below 300 or above 390 timestamps are now explicitly reported for characterization before production use.
- Diagnostic IV/Greek solver sample: 596,005 successful solver observations. This used r=q=0 solely as a computational smoke test and is **not** production Greek evidence.
- Target-delta availability remains OPEN because the production calculation requires date-specific r/q, frozen liquidity rules, and full decision-timestamp evaluation.
- Historical bid/ask remains absent from the primary source schema; execution remains degraded unless an independent historical quote source is validated.

**Current decision: Phase 1 remains IN PROGRESS.** The session-coverage anomalies and production Greek/target-delta gates must be resolved before independent tester handoff.


## Updated quote-data finding
The primary Hugging Face 1-minute source remains structurally useful but does not contain historical bid/ask. Public/commercial 1-minute archives reviewed also describe OHLCV/OI rather than bid/ask. NSE's official historical order-and-trade product is now registered as the preferred independent quote-source escalation because its F&O order data is documented at order-tick level; however, access is paid and has not yet been procured. The frozen Phase 0 literal core therefore remains blocked on quote-quality data rather than silently substituting close prices. citeturn3search0turn3search19
