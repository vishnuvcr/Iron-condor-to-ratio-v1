# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 1 — data acquisition and validation: G6 production historical Greeks/IV audit is OPEN and running on the frozen developer head. Phase 0 is complete.**

## Gate
**G6 remains OPEN. Phase 2 remains BLOCKED.** The current exact-head CI run must finish all exhaustive shards and produce the aggregate artifact before an isolated tester handoff is permitted.

### Current exact-head evidence
- Developer head: `1a9eab7389b972c05362271ee9fb23092aa7354d`
- GitHub Actions run: `37191768801`
- Preparation job: PASS
- Shards: **6 completed PASS, 16 in progress, 8 queued; 0 completed failures** at latest observation
- Exact-head shard artifacts: **5**
- Aggregate artifact: not yet available
- Prior aggregate failure E126 was a missing NumPy dependency and has been corrected; prior-run artifacts are not eligible as current-head evidence.

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
No trading or performance conclusion is justified yet. The current work is confined to production historical Greek/IV evidence required for Phase 1.

## Branch
Phase 0 branch: phase-0-specification.


## Latest developer continuation — 2026-10-04
- Paired G5 exact-tip Run 37148487963 remains **in progress** at the substantive alignment audit; G5 is not marked PASS.
- G6 production work continues on `phase-1-g6-production-greeks-20261004`; developer PR #41 is open as a draft for independent review.
- E084 was corrected: G6 reference-data coverage is now measured against actual NIFTY option-data trading dates, not the q reference table.
- G6 remains **OPEN**. G13/G14 and Phase 2 remain **BLOCKED**.
