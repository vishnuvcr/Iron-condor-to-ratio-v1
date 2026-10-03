# Phase 0 — Seventh Independent Tester Report

**Date:** 2026-10-03  
**Role:** Tester  
**Correction pass audited:** `phase-0-corrections-v6` / PR #11  
**Exact CI commit audited:** `fd1ed356bdc12d18e3b3dbfb507c8d5be2510237`

## Verdict

**PASS — Phase 0 approval granted. Phase 1 may be started by the Developer, subject to the existing Phase 1 plan and controls.**

This is an independent repository audit of the v6 correction pass. No Phase 1 data acquisition, backtesting, optimization, profitability analysis, or trading conclusion was performed as part of this tester gate.

## Gate checks

| Check | Result | Evidence |
|---|---|---|
| B9 current tester handoff | PASS | `research/TESTER_HANDOFF.md` names `phase-0-corrections-v6` / PR #11 and keeps Phase 1 blocked pending this approval. |
| B10 active-branch CI assertion | PASS | `.github/workflows/phase0-integrity.yml` uses a line-aware positive assertion requiring the README `## Current branch` value to be exactly `phase-0-corrections-v6`. |
| Exact CI provenance | PASS | Workflow run #37114577283, integrity job/check #111178768606; job completed successfully and the tested SHA is `fd1ed356bdc12d18e3b3dbfb507c8d5be2510237`. |
| Required Phase 0 artifacts | PASS | Integrity workflow checks required files and key frozen semantics. |
| Numerical conventions | PASS | IV/Black-Scholes, no-arbitrage bounds, tick rounding, timestamp rejection, threshold inequalities and fallback slippage are explicitly frozen. |
| Execution semantics | PASS | Trigger-to-fill ordering, bid/ask fills, fallback slippage, expiry handling and no-look-ahead rules are specified. |
| Strategy/source separation | PASS | Source-derived rules are separated from research implementation conventions and discretionary variants. |
| Cost policy | PASS | Paytm Money and applicable statutory/exchange costs are required to be date-specific and not double-counted. |
| State/unit-test contract | PASS | State transitions and minimum unit-test invariants are enumerated. |
| Phase discipline | PASS | Phase 1 remains blocked in the audited v6 records until this independent tester approval. |
| Project instructions | PASS | `PROJECT_INSTRUCTIONS.md` records phase gating, status/error logging, reproducibility, cost controls and manuscript requirements. |

## Mathematical/logical audit

No remaining Phase 0 blocker was identified in the frozen operational contract.

Important controls independently checked:

- Delta is signed internally but absolute for target matching; combined short delta is explicitly defined as the sum of absolute short-leg deltas.
- Equality counts at thresholds, eliminating boundary ambiguity.
- The literal-core thresholds are explicitly frozen at 0.10 for IC transition, 0.20 for continuation reset, and 1.20 for reversal.
- The IV reconstruction specifies model equations, inputs, bracket, Brent-Dekker semantics, absolute/relative tolerances, iteration limit and rejection behavior.
- No-arbitrage bounds and one-tick tolerance are explicit.
- Future-dated quotes are rejected and quote freshness is bounded.
- Tick rounding is specified through integer tick arithmetic with directional ceil/floor behavior.
- Strike selection has an explicit maximum delta error and deterministic tie-break sequence.
- Direction classification at simultaneous IC triggers is deterministic and rejects a zero-return ambiguity.
- New structures cannot recursively trigger at the same timestamp.
- Primary fills use contemporaneous ask/bid rather than portfolio midpoint.
- Fallback slippage is fixed for the literal core and alternative slippage is restricted to pre-registered sensitivity variants.
- Expiry handling does not silently substitute settlement prices for the primary execution-adjusted result.
- Historical expiry, lot size and tick size are required to come from historical contract metadata rather than current assumptions.
- Cost records are explicitly one-per-executed-cash-flow leg.
- Invalid IV observations cannot be forward-filled.

These are Phase 0 reproducibility controls, not evidence of strategy profitability.

## Remaining Phase 1 prerequisites

Approval of Phase 0 does **not** establish that the strategy is profitable or that suitable data are already available. Before performance claims are made, Phase 1 must still verify:

1. Real intraday NIFTY option data sufficient for the one-minute trigger grid.
2. Bid/ask quality and timestamp provenance, or documented application of the literal-core fallback.
3. Historical contract metadata, expiry calendars, lot sizes and tick sizes.
4. Date-specific Paytm Money and applicable statutory/regulatory charges.
5. Greek provenance or deterministic Black-Scholes reconstruction inputs.
6. Data licensing/redistribution constraints and reproducible caching.
7. The planned global/NSE/BSE market-regime, volatility, FII/DII, corporate-action and news context where applicable.
8. Unit tests against the frozen contract before baseline backtesting.
9. Pre-registration of all sensitivity variants before examining their performance.
10. Out-of-sample/robustness analysis as specified in later phases.

## Tester conclusion

The sixth-gate B9/B10 defects are resolved. The v6 correction pass is internally synchronized, its exact CI run is successful, and the Phase 0 operational contract is sufficiently deterministic to permit the next research phase.

**Phase 0: APPROVED.**  
**Phase 1: MAY START — Developer gate opened by this tester approval.**

No profitability or trading recommendation is implied by this approval.
