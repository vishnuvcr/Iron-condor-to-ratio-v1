# Tester Report — G6 Production Greek Scaffold Re-audit — 2026-10-04

## Role and determination

Role: Independent tester.

Developer head audited:
- Branch: `phase-1-g6-production-greeks-20261004`
- Commit: `c5f28327c13efd9b93bd4ca5a809dfc39b447c3d`
- Developer PR: #41

**Determination: G6 FAIL / OPEN.**

This re-audit does not authorize G13, G14, Phase 2, or any performance conclusion.

## Scope

The re-audit examined the G6 production specification, production Greek script, regression tests, source-acquisition code, cache-provenance tests, and G6 control-source manifest.

## Findings

### F1 — Production IV/Greek reconstruction is not implemented

`scripts/phase1_g6_production_greeks.py` currently:
- validates presence/schema of r/q CSVs;
- derives an option-date universe from option timestamps;
- reports strictly-prior r/q date coverage;
- validates the first option parquet schema;
- records solver metadata and input checksums.

It does **not** perform the required production valuation scan over the option dataset.

The report fields `iv_converged`, `iv_failures`, `boundary_rejections`, `target_delta_records`, and `target_delta_missing` are initialized to zero but never populated from production observations.

Therefore the acceptance requirements for documented IV success/failure/boundary distributions, signed/absolute delta distributions, target-delta availability, expiry/date coverage and deterministic failure-reason counts are not satisfied.

### F2 — Required contemporaneous NIFTY underlying is not consumed

The frozen G6 specification requires exact contemporaneous NIFTY underlying values at every option valuation timestamp.

The production script does not load the NIFTY index series and does not join it to option timestamps. Thus the required S input is absent from the production evidence path.

This is especially important because G5 is explicitly waived for research use but retains its timestamp-integrity limitation. G6 cannot silently assume that limitation is resolved.

### F3 — r/q observations are not actually applied to option timestamps

The script checks whether at least one r/q observation exists strictly before each option-data trading date, but it does not perform the required per-observation selection of the latest valid source observation strictly earlier than the trading date.

Consequently, no production proof exists for:
- exact r selection,
- exact q selection,
- no same-day use,
- no future use,
- no interpolation,
- no forward-fill,
- no missing-input hard failures at valuation level.

### F4 — Target-delta contract selection is not implemented

The frozen specification requires deterministic target selection for 0.30, 0.10, 0.50, 0.40 and 0.08 absolute deltas, with ±0.05 tolerance and the frozen tie-break.

No production target-delta selection is executed.

### F5 — Study-window constants are not enforced

The script defines `STUDY_START=2021-01-01` and `STUDY_END=2026-09-30`, but the option-date universe is built from all timestamps in all NIFTY option files without filtering to the declared study window.

Therefore the reported coverage universe is not demonstrably the frozen study window.

### F6 — IV solver semantics do not match the frozen description

The G6 specification says to use a deterministic bounded **Brent-style** solver with frozen tolerance/iteration semantics.

The implementation uses deterministic **bisection** over [1e-8, 8.0].

Bisection can be a valid numerical method in isolation, but it is not the frozen Brent-style contract. This must be resolved explicitly before production evidence can be accepted; the implementation cannot silently substitute a different solver algorithm.

### F7 — Production evidence artifact is absent from the audited branch

Neither of the required production inputs nor the generated production evidence artifact is present in the audited branch:
- `data/processed/g6/risk_free.csv`: absent
- `data/processed/g6/dividend_yield.csv`: absent
- `data/validation/phase1_g6_production_greeks_report.json`: absent

The G6 workflow therefore cannot currently produce substantive production evidence from the repository state alone.

### F8 — Source acquisition remains provenance/bootstrap work, not full historical production input

The source-acquisition code correctly fails closed when an expected immutable digest is missing, and the manifest contains candidate SHA-256 values.

However, the acquired HTML source snapshots are not transformed into the required machine-readable, date-aligned r/q production tables in this branch. Source acquisition/provenance is therefore not equivalent to production Greek evidence.

## Positive controls verified

- No-lookahead intent is explicitly specified.
- Cache digest mismatch is rejected.
- Missing expected digest is rejected outside explicit bootstrap mode.
- Black-Scholes call/put parity and delta-sign tests are present.
- IV round-trip and no-arbitrage rejection tests are present.
- Exact checkout SHA is recorded by the production script when it executes.
- The G6 workflow is configured for automated push/PR/manual execution.

These controls are useful but insufficient for G6 PASS.

## Required corrective evidence

Before a G6 PASS can be considered, the developer must provide an immutable exact-tip evidence package that independently demonstrates:

1. Complete machine-readable historical r and q inputs for the declared study universe.
2. Exact contemporaneous NIFTY underlying alignment, with the G5 waiver explicitly carried forward.
3. Strictly-prior r/q selection at every valuation timestamp.
4. Production IV reconstruction for the full eligible option universe, including convergence, residual, iteration, bracket/boundary and failure distributions.
5. Signed delta and absolute-delta distributions.
6. Deterministic target-delta availability for 0.30/0.10/0.50/0.40/0.08 with ±0.05 tolerance and frozen tie-break.
7. Effective expiry/contract metadata and date coverage.
8. Production dataset/evidence checksums and exact checkout SHA.
9. Solver algorithm semantics reconciled with the frozen specification (Brent-style versus an explicitly approved replacement).
10. Sensitivity/robustness handling for the accepted G5 alignment limitation.

## Gate status

| Gate | Tester status |
|---|---|
| G4 | Previously independently PASS |
| G5 | FAIL / WAIVED FOR CONTINUED RESEARCH; not PASS |
| G6 | **FAIL / OPEN** |
| G7 | OPEN |
| G8 | OPEN |
| G9 | PASS under revised proxy methodology |
| G10 | OPEN |
| G11 | OPEN |
| G12 | Previously independently PASS |
| G13 | BLOCKED |
| G14 | BLOCKED |
| Phase 2 | BLOCKED |

No profitability, Sharpe, drawdown, optimization, or trading-strategy conclusion is authorized by this report.
