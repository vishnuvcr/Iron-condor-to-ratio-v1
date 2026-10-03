# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
**Tester — Phase 0 independent audit**

## Current phase
**Phase 0 — tester audit: FAILED / corrections required.**

## Gate
**Phase 1 remains blocked pending developer corrections and independent tester re-validation.**

## Source strategy
The uploaded transcript is the primary strategy source. It specifies a monthly Iron Condor using short call/put near 0.30 delta and long call/put near 0.10 delta; transition when either short IC leg reaches approximately 0.10 delta; directional ratio spreads; continuation and reversal delta triggers; and discretionary profit-taking/expiry-day discussion.

## Research files
- [Research plan](RESEARCH_PLAN.md)
- [Research status](RESEARCH_STATUS.md)
- [Source-derived strategy specification](research/STRATEGY_SPEC.md)
- [Literature and data review](research/LITERATURE_AND_DATA_REVIEW.md)
- [Tester handoff](research/TESTER_HANDOFF.md)
- [Independent Phase 0 tester report](research/TESTER_REPORT_PHASE0.md)
- [Error log](ERROR_LOG.md)
- [Conversation log](CONVERSATION_LOG.md)
- [Project instructions](PROJECT_INSTRUCTIONS.md)

## Data policy
The strategy's triggers depend on intraday option deltas. NSE historical reports and contract-wise price/volume data are useful for reference and validation, but production trigger reconstruction requires sufficiently granular intraday option data with documented provenance and execution information.

## Research controls
Each phase will use a separate branch. Every phase will update status and error logs. Backtests will include configurable slippage, brokerage, transaction charges and other applicable costs. Synthetic data is permitted only for engine/unit tests, not for the primary performance conclusion.

## Current tester conclusion
The source-derived core is substantially faithful, but production implementation is not yet deterministic enough for independent reproduction. The unresolved issues are documented in the tester report.

## Branch
Tester audit branch: tester/phase-0-audit
