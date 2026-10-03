# Research Status

Updated: 2026-10-03

| Phase | Status | Gate |
|---|---|---|
| 0 Specification/audit | **COMPLETE** | Tester handoff ready |
| 1 Data | **IN PROGRESS** | Phase 0 approved; Phase 1 validation gates apply |
| 2 Engine | BLOCKED | Phase 1 |
| 3 Experiments | BLOCKED | Phase 2 |
| 4 Statistics | BLOCKED | Phase 3 |
| 5 Interpretation | BLOCKED | Phase 4 |
| 6 Manuscript/release | BLOCKED | Phase 5 |

## Phase 0 completed
- Developer role confirmed.
- Target repository audited; it was empty.
- Uploaded YouTube transcript converted into a source-derived deterministic rule specification.
- Research questions, aims, objectives, methodology and statistical analysis plan established.
- Literature and data-source review completed at scoping level.
- Intraday option-chain/Greek data requirement identified as essential.
- Tester handoff created.
- Errors and repository controls established.
- Phase 0 merged to main.

## Phase 0 gate passed
The seventh independent tester approved Phase 0 via tester report `research/TESTER_REPORT_PHASE0_SEVENTH.md` and tester PR #12. Phase 1 is now unblocked.

## Phase 1 current work
- Created `phase-1-data-acquisition-validation`.
- Registered primary and secondary intraday NIFTY option candidates.
- Added reproducible acquisition and validation manifests.
- Added automated GitHub Actions acquisition/validation using the repository `HF_TOKEN` secret and cache.
- Added market-context and date-specific cost-source registers.
- No backtest engine, optimization or performance claim has started.

## Important source limitation
The video demonstrates selected months and explicitly says the examples are selective rather than representative of every month. The future backtest must therefore use a broad, predefined sample rather than selected examples.

## Phase 0 evidence
- research/STRATEGY_SPEC.md
- research/LITERATURE_AND_DATA_REVIEW.md
- research/TESTER_HANDOFF.md

## Phase 1 initial findings
The current source sweep identified thetrademarkk/india-index-options-1m as the primary open candidate because its documented NIFTY data contain 1-minute OHLCV, OI, strike, option type and expiry across a multi-year span. Its documented schema does not include historical bid/ask, so quote execution remains a validation gap. A secondary rissin/nse-options-intraday dataset covers 2024 onward but documents unavailable intraday OI and no bid/ask. Official NSE sources will provide contract metadata, daily reference data, India VIX, FII/DII, corporate actions and reconciliation inputs.
