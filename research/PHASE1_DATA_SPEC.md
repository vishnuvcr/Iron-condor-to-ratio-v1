# Phase 1 — Data Acquisition and Validation Specification

## Objective
Build a reproducible, auditable data layer sufficient to reproduce the frozen one-minute literal-core strategy without look-ahead.

## Canonical Phase 1 gate vocabulary

The repository uses one canonical G1–G14 vocabulary, defined here and in `research/PHASE1_GATE_MATRIX.md`. No other Phase 1 document may assign a different meaning to these IDs.

| Gate | Canonical meaning |
|---|---|
| G1 | Immutable primary dataset / provenance |
| G2 | Structural schema validation |
| G3 | Duplicate handling |
| G4 | Timestamp and session quality |
| G5 | Underlying/option alignment |
| G6 | Production historical Greeks / IV |
| G7 | Target-delta availability |
| G8 | Historical contract metadata |
| G9 | Historical bid/ask / execution quality |
| G10 | Date-specific transaction costs |
| G11 | Market-context datasets |
| G12 | Repaired CI execution |
| G13 | Independent tester approval |
| G14 | Phase 2 authorization |

The detailed validation dimensions below are evidence used by these canonical gates; they are not separate G1–G10 gate IDs.

## Required datasets
1. NIFTY 1-minute underlying index observations.
2. NIFTY option 1-minute observations across the selected monthly expiries and strikes.
3. Historical contract metadata: expiry dates, lot sizes, tick sizes and effective contract rules.
4. Daily India VIX.
5. Daily NIFTY benchmark/index data.
6. Daily FII/FPI and DII activity.
7. Relevant NSE/BSE market-context data, including cross-market and global overnight indicators where available.
8. Corporate-action/event calendars relevant to the NIFTY reference series and option-contract continuity.
9. Date-specific Paytm Money brokerage and statutory/exchange cost schedules.

## Validation dimensions

### Provenance evidence
Record source URL/repository, dataset revision or file hashes, acquisition timestamp, license/terms, and exact file list.

### Schema evidence
Verify timestamps, underlying, expiry, strike, option type, OHLC, volume and OI fields as applicable.

### Time/session evidence
Convert to a canonical timezone representation while retaining original timestamps. Reject future timestamps and malformed timestamps. Characterize duplicates, missing bars, session-length anomalies and exchange-calendar mismatches before production acceptance.

### Market-data integrity evidence
Detect nonpositive prices, invalid OHLC relationships, extreme gaps, stale observations and—if quote fields exist—crossed/locked markets and spread anomalies.

### Contract evidence
Verify that every option observation maps to a valid historical expiry/strike/type and that lot size/tick size are taken from effective-date metadata.

### Underlying-alignment evidence
Verify that option timestamps align with the NIFTY underlying observation grid used for delta reconstruction and direction classification.

### Greek evidence
Prefer vendor-observed Greeks only when methodology and timestamp alignment are documented. Otherwise reconstruct using the frozen Phase 0 Black-Scholes/IV contract and record solver success/failure rates.

### Target-strike evidence
Measure the proportion of one-minute decision timestamps for which the target deltas can be met within the frozen 0.05 maximum error and liquidity filters.

### Execution evidence
Record whether historical bid/ask exists. If absent, do not silently substitute current quotes or close prices. The frozen Phase 0 methodology treats historical midpoint execution as the literal core; any degraded fallback must remain explicitly identified and separately analyzed.

### Reconciliation evidence
Reconcile selected daily aggregates and contract metadata against official NSE sources. Discrepancies are logged rather than silently corrected.

## Sampling policy
The source examples are selective. Phase 1 therefore uses a broad predefined sample of available monthly expiries rather than selecting visually favorable months.

## Context variables
The phase will collect India VIX, NIFTY benchmark returns, FII/FPI and DII activity, GIFT NIFTY/overnight indicators, relevant global volatility/risk indicators, NSE/BSE context, and event/corporate-action markers. These are contextual variables; they do not become strategy signals unless a later phase explicitly pre-registers that use.

## Data retention
Large raw datasets are retained outside ordinary Git history through reproducible cache/artifact mechanisms when licensing permits. Git stores manifests, checksums, schema summaries, validation reports and exact acquisition instructions.

## Historical contract-rule checkpoints
Phase 1 must not apply current NIFTY contract rules retroactively.

- NSE Circular 128/2024 states the NIFTY lot size was revised from 25 to 75 for new index derivatives introduced from 20 November 2024 onward.
- NSE Circular 33/2025 changed NIFTY expiry day from Thursday to Monday effective 4 April 2025 for contracts created under that circular; this was subsequently superseded/modified in June 2025.
- NSE Circular 111/2025 changed NIFTY weekly and monthly/quarterly/half-yearly expiry to Tuesday, with the transition applying to new contracts and specified existing long-dated contracts from the 2025 transition dates.
- Therefore the validator must use the historical contract master/effective contract metadata for every contract rather than infer expiry weekday or lot size from today's specification.

## Primary official references
- NSE Contract Information
- NSE Contract Specifications
- NSE Circular 128/2024
- NSE Circular 103/2025
- NSE Circular 111/2025

## Source-validation additions
- NSE Circular 37/2024 changed NIFTY market lot from 50 to 25 for contracts available from 26-Apr-2024, with the April 25 expiry excluded from the change.
- NSE Circular 128/2024 changed NIFTY market lot from 25 to 75 for new index derivatives introduced from 20-Nov-2024.
- NSE's June 2025 expiry-day transition specified Tuesday for the applicable transition contracts; effective-date contract metadata remains authoritative.
- RBI Weekly Statistical Supplement provides the historical 91-day Treasury-bill primary-yield series used as the risk-free-rate source candidate.
- Paytm Money publications provide date/cohort-specific brokerage and STT chronology; the complete machine-readable statutory/exchange schedule remains a G10 requirement.
