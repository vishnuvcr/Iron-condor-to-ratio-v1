# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
**Tester — Phase 0 second independent audit**

## Current phase
**Phase 0 second tester gate: FAILED / corrections required.**

## Gate
**Phase 1 remains blocked.** The first tester's blockers were substantially addressed, but the second tester found repository-integrity and reproducibility gaps that must be corrected before approval.

## Source strategy
The uploaded transcript is the primary strategy source. It specifies a monthly Iron Condor using short call/put near 0.30 delta and long call/put near 0.10 delta; transition when either short IC leg reaches approximately 0.10 delta; directional ratio spreads; continuation and reversal delta triggers; and discretionary profit-taking/expiry-day discussion.

## Research files
- [Research plan](RESEARCH_PLAN.md)
- [Research status](RESEARCH_STATUS.md)
- [Source-derived strategy specification](research/STRATEGY_SPEC.md)
- [Second tester report](research/TESTER_REPORT_PHASE0_SECOND.md)
- [First tester report](https://github.com/vishnuvcr/Iron-condor-to-ratio-v1/blob/tester/phase-0-audit/research/TESTER_REPORT_PHASE0.md)
- [Error log](ERROR_LOG.md)
- [Conversation log](CONVERSATION_LOG.md)
- [Project instructions](PROJECT_INSTRUCTIONS.md)

## Second tester finding

The corrected STRATEGY_SPEC now clearly labels machine-level mechanics as research implementation conventions rather than claims about the YouTube source. Most first-tester blockers are explicitly addressed.

However, PR #3 promises `research/OPERATIONAL_CONVENTIONS.md`, links to it, and states it was added, but that artifact is absent from the PR changed-file list and is not retrievable from the correction branch. Exact numerical conventions for Greeks, fallback slippage, tie-breaking, data-quality filters, threshold inequalities, direction classification and historical expiry identification also require further freezing.

## Current conclusion

No performance conclusion is justified. No Phase 1 work should proceed until the second tester blockers are corrected and independently re-tested.
