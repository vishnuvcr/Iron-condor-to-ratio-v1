# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 1 — data acquisition and validation: IN PROGRESS. Phase 0 is APPROVED.**

## Gate
**Phase 1 is UNBLOCKED by the seventh independent tester PASS.** No backtest engine or performance analysis has begun; this phase is limited to data acquisition, validation and provenance.

## Source strategy
The uploaded transcript is the primary strategy source. It specifies a monthly Iron Condor using short call/put near 0.30 delta and long call/put near 0.10 delta; transition when either short IC leg reaches approximately 0.10 delta; directional ratio spreads; continuation and reversal delta triggers; and discretionary profit-taking/expiry-day discussion.

## Research files
- [Research plan](RESEARCH_PLAN.md)
- [Research status](RESEARCH_STATUS.md)
- [Source-derived strategy specification](research/STRATEGY_SPEC.md)
- [Literature and data review](research/LITERATURE_AND_DATA_REVIEW.md)
- [Tester handoff](research/TESTER_HANDOFF.md)
- [Error log](ERROR_LOG.md)
- [Conversation log](CONVERSATION_LOG.md)
- [Project instructions](PROJECT_INSTRUCTIONS.md)

## Phase 0 approval
Seventh independent tester report: `research/TESTER_REPORT_PHASE0_SEVENTH.md` on `tester/phase-0-seventh-audit`; tester PR #12. The tester approved Phase 0 after independently verifying B9/B10, exact CI provenance, numerical conventions, execution semantics, cost policy and phase discipline.

## Phase 1 controls
- [Phase 1 data specification](research/PHASE1_DATA_SPEC.md)
- [Data source registry](research/DATA_SOURCE_REGISTRY.md)
- [Market context registry](research/MARKET_CONTEXT_REGISTRY.md)
- [Data cache policy](data/README.md)
- [Source manifest](data/manifests/phase1_sources.json)
- [Acquisition manifest](data/manifests/phase1_acquisition.json)
- [Automated acquisition/validation workflow](.github/workflows/phase1-data-validation.yml)

## Data policy
The strategy's triggers depend on intraday option deltas. NSE public historical-report pages provide authoritative daily derivatives reports, but daily reports alone cannot reproduce intraday trigger timing. Phase 1 therefore requires real historical intraday NIFTY option data with sufficient strike/expiry coverage and documented provenance.

## Research controls
Each phase will use a separate branch. Every phase will update status and error logs. Backtests will include configurable slippage, brokerage, transaction charges and other applicable costs. Synthetic data is permitted only for engine/unit tests, not for the primary performance conclusion.

## Current conclusion
No performance conclusion is justified yet. Phase 0 established a reproducible specification and identified the key data requirement and ambiguity controls.

## Branch
`phase-1-data-acquisition-validation`.

## Current conclusion
No performance conclusion is justified yet. Phase 1 has only established the acquisition/validation framework and candidate sources; no strategy P&L has been computed.


## Latest Phase 1 evidence
Structural acquisition/validation is green on commit 5f701e329c7888e5ccd5cfe70cea0f5c14e452ac (GitHub Actions run 37116084761, job 111183065244). The run acquired 269 parquet files and produced validation artifact 11271990517. This is a structural data-quality pass only; it is not a trading-result or profitability claim.

**Open Phase 1 gates:** historical quote/bid-ask availability, target-delta strike coverage, Greek reconstruction success and provenance, historical contract metadata reconciliation, and date-specific Paytm Money/statutory costs.
