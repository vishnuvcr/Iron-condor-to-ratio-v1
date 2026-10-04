# Phase 2 Milestone Engineering Report — 2026-10-04

## Scope

Deterministic implementation and production-run orchestration for the source-derived Iron Condor → directional ratio strategy.

## Frozen scientific choices

- Decision bar: completed 1-minute option observation.
- Execution bar: first eligible option bar strictly after decision timestamp.
- Primary proportional slippage: 10 bps per leg.
- Sensitivities: 0 / 5 / 20 / 50 bps.
- Historical tick-size floor active in every scenario.
- Entry: first eligible monthly opportunity.
- Expiry: latest listed expiry in each calendar month, subject to at least 20 calendar days after entry.
- Target tolerance: absolute-delta error <= 0.05.
- Transition: 0.10 absolute-delta crossing of the IC short.
- Continuation: combined short delta crosses downward to <= 0.20.
- Reversal: combined short delta crosses upward to >= 1.20.
- Literal core excludes discretionary profit-taking.
- Failed multi-leg execution is atomic, consumes the trigger, and requires re-arm.
- Forced close uses date-specific expiry-close metadata.
- Static 30Δ/10Δ IC benchmark uses the same execution/cost layer.

## Engineering components

- `scripts/phase2_backtest_engine.py`
- `scripts/prepare_phase2_normalized_data.py`
- `scripts/phase2_run_cycles.py`
- `scripts/phase2_run_backtest.py`
- `scripts/analyze_phase2_results.py`
- `scripts/validate_phase2_contract_master.py`
- `scripts/test_phase2_backtest_engine.py`
- `scripts/test_phase2_cost_schedule.py`
- `scripts/validate_phase2_cost_schedule.py`
- `.github/workflows/phase2-engine-tests.yml`
- `.github/workflows/phase2-production-backtest.yml`

## Error-correction record

### E141
NSE/IPFT decimal unit conversion error in the first cost schedule draft. Corrected before production use and regression-tested.

### E142
Timezone defect: G6 timestamps are timezone-naive Asia/Kolkata, while the first Phase 2 parser treated naive timestamps as UTC. Corrected with IST localization and regression test.

### E143
Model-side direct public-data download unavailable because the runtime has no external network/DNS. Repository acquisition remains pinned/cache-first; no substitute data were fabricated.

### E144
Inclusive 20-day expiry boundary used as strict greater-than. Corrected to >=20 days in both engine and cycle scheduler.

### E145
Pandas DataFrame truth-value bug in cycle-runner manifest count. Corrected before production.

## Cost-model controls

The cost schedule contains date-effective:
- Paytm Money legacy-cohort brokerage;
- NSE option transaction slabs through 2024-09-30;
- uniform NSE option charges from 2024-10-01;
- IPFT;
- SEBI turnover fees;
- STT;
- stamp duty;
- GST.

The pre-October-2024 exchange slab is calculated from the strategy's own monthly premium turnover, explicitly treated as an isolated-strategy-account assumption.

## Production data controls

The production workflow requires:
- pinned NIFTY option 1-minute data;
- pinned NIFTY underlying;
- strict-prior risk-free and dividend yield;
- G4 reconciled sessions;
- authoritative historical NIFTY contract master;
- exact provenance and hashes.

The contract master is deliberately fail-closed because historical NIFTY lot-size and expiry transitions cannot be safely reconstructed from current rules alone.

## Current scientific status

No production P&L, Sharpe, drawdown or trading-strategy acceptance has been claimed from Phase 2 yet.

The exact implementation and workflow are ready for the independent milestone audit. Production performance remains conditional on the authoritative historical contract master and successful reproducible workflow execution.

## Reproducibility boundary

The Git SHA, input hashes, configuration, source revisions, cost schedule and output artifacts must accompany every final result. A CI workflow status that is not observable is not treated as a pass.
