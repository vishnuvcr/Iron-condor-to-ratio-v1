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
