# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 0 — specification, literature/data review and reproducibility controls: COMPLETE.**

## Gate
**Phase 1 is blocked pending an independent tester report.** No backtest implementation has been advanced past this gate.

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

## Data policy
The strategy's triggers depend on intraday option deltas. NSE public historical-report pages provide authoritative daily derivatives reports, but daily reports alone cannot reproduce intraday trigger timing. Phase 1 therefore requires real historical intraday NIFTY option data with sufficient strike/expiry coverage and documented provenance.

## Research controls
Each phase will use a separate branch. Every phase will update status and error logs. Backtests will include configurable slippage, brokerage, transaction charges and other applicable costs. Synthetic data is permitted only for engine/unit tests, not for the primary performance conclusion.

## Current conclusion
No performance conclusion is justified yet. Phase 0 established a reproducible specification and identified the key data requirement and ambiguity controls.

## Branch
Phase 0 branch: phase-0-specification.
