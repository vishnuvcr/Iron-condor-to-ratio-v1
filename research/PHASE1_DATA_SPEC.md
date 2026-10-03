# Phase 1 — Data Acquisition and Validation Specification

## Objective
Build a reproducible, auditable data layer sufficient to reproduce the frozen one-minute literal-core strategy without look-ahead.

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

## Validation gates
A dataset is not accepted merely because it downloads.

### G1 Provenance
Record source URL/repository, dataset revision or file hashes, acquisition timestamp, license/terms, and exact file list.

### G2 Schema
Verify timestamps, underlying, expiry, strike, option type, OHLC, volume and OI fields as applicable.

### G3 Time integrity
Convert to a canonical timezone representation while retaining original timestamps. Reject future timestamps, duplicate observations and malformed timestamps.

### G4 Market-data integrity
Detect nonpositive prices, invalid OHLC relationships, missing bars, extreme gaps, stale observations and—if quote fields exist—crossed/locked markets and spread anomalies.

### G5 Contract integrity
Verify that every option observation maps to a valid historical expiry/strike/type and that lot size/tick size are taken from effective-date metadata.

### G6 Underlying alignment
Verify that option timestamps align with the NIFTY underlying observation grid used for delta reconstruction and direction classification.

### G7 Greek provenance
Prefer vendor-observed Greeks only when methodology and timestamp alignment are documented. Otherwise reconstruct using the frozen Phase 0 Black-Scholes/IV contract and record solver success/failure rates.

### G8 Target-strike availability
Measure the proportion of one-minute decision timestamps for which the target deltas can be met within the frozen 0.05 maximum error and liquidity filters.

### G9 Execution fields
Record whether bid/ask exists. If absent, explicitly route execution to the frozen fallback-slippage convention and mark the observation as degraded execution data.

### G10 Reconciliation
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
- NSE Contract Information: https://www.nseindia.com/static/products-services/equity-derivatives-contract-information
- NSE Contract Specifications: https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications
- NSE Circular 128/2024: https://nsearchives.nseindia.com/content/circulars/FAOP64625.pdf
- NSE Circular 103/2025: https://nsearchives.nseindia.com/content/circulars/FAOP68589.pdf
- NSE Circular 111/2025: https://nsearchives.nseindia.com/content/circulars/FAOP68747.pdf


## Additional official contract metadata evidence
- NSE Circular 37/2024 changed NIFTY market lot from 50 to 25 for contracts available from 26-Apr-2024, with the April 25 expiry excluded from the change. citeturn3search16
- NSE Circular 128/2024 changed NIFTY market lot from 25 to 75 for new index derivatives introduced from 20-Nov-2024. citeturn3search13
- NSE's June 2025 expiry-day transition first specified Tuesday for contracts expiring on/after Sep-2025, with detailed transition treatment for existing contracts. citeturn2search29turn2search28
- NSE's current contract specification records the current Tuesday expiry and index-option tick-step framework; historical contract files/circular effective dates remain authoritative for historical reconstruction. citeturn2search0turn2search9
