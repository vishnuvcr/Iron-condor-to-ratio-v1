# Phase 2 — Production Run Specification

Updated: 2026-10-04

## Required inputs

1. Pinned NIFTY option 1-minute OHLCV(+OI) files.
2. Pinned NIFTY underlying 1-minute file.
3. Phase 1 strict-prior risk-free and dividend-yield series.
4. Authoritative historical NIFTY contract master.
5. Phase 1 session rules.
6. Date-effective Phase 2 cost schedule.

## Production sequence

1. Restore cached source data.
2. Validate exact source hashes.
3. Validate the historical contract master.
4. Recompute production IV/absolute delta using the same frozen G6 solver contract.
5. Build session-aware normalized bars with exact underlying timestamp alignment.
6. Run the deterministic strategy separately for the locked primary slippage scenario and pre-registered sensitivities.
7. Emit trade/fill/charge/event ledgers and a complete provenance manifest.
8. Run baseline static Iron Condor comparator.
9. Run pre-registered sensitivity and regime analyses.
10. Generate manuscript tables/figures from the immutable result ledger.

## Fail-closed conditions

The production workflow must stop without a result when:
- input data are missing;
- contract metadata do not reconcile;
- solver or delta reconstruction fails beyond configured acceptance;
- a cost rule is missing/ambiguous;
- source hashes do not match;
- look-ahead controls fail;
- exact Git SHA cannot be recorded.

## Primary output scenarios

- 10 bps proportional adverse slippage per leg;
- 0, 5, 20 and 50 bps sensitivity/stress;
- historical tick-size floor in every scenario.

## Benchmark

Static monthly 30Δ/10Δ Iron Condor using the same expiry, strike-selection, execution and cost conventions.

## Interpretation

The production result is a proxy-execution result. It is not a claim of historical live fills or realized broker P&L.
