# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 0 fourth-gate correction pass — awaiting independent re-test.**

## Gate
**Phase 1 remains blocked.** Historical tester gates remain part of the audit trail, but the active gate is the current independent tester approval for the latest correction pass. The fourth independent tester failed PR #7 on B6 repository-control synchronization; no downstream research has started.

## Source strategy
The uploaded transcript is the primary strategy source. It specifies a monthly Iron Condor using short call/put near 0.30 delta and long call/put near 0.10 delta; transition when either short IC leg reaches approximately 0.10 delta; directional ratio spreads; continuation and reversal delta triggers; and discretionary profit-taking/expiry-day discussion.

## Research files
- [Research plan](RESEARCH_PLAN.md)
- [Research status](RESEARCH_STATUS.md)
- [Source-derived strategy specification](research/STRATEGY_SPEC.md)
- [Operational conventions](research/OPERATIONAL_CONVENTIONS.md)
- [Literature and data review](research/LITERATURE_AND_DATA_REVIEW.md)
- [Tester handoff](research/TESTER_HANDOFF.md)
- [Error log](ERROR_LOG.md)
- [Conversation log](CONVERSATION_LOG.md)
- [Project instructions](PROJECT_INSTRUCTIONS.md)

## First tester finding
The first tester confirmed source fidelity but failed the phase because machine-level semantics were insufficiently defined. The complete tester report is on branch `tester/phase-0-audit` and PR #2.

## Developer correction
The correction branch freezes explicit research implementation conventions for delta arithmetic, one-minute trigger sampling, target-strike selection, entry timing, trigger-to-fill sequencing, bid/ask execution, costs, expiry handling, state transitions and unit-test invariants. These are clearly labelled implementation conventions rather than claims about the video.

## Data policy
The strategy requires intraday option data. Daily NSE reports alone cannot reproduce the delta triggers. Phase 1 will require documented intraday NIFTY option data, coverage, timestamps, contract continuity, Greek methodology, licensing and quote quality.

## Current branch
`phase-0-corrections-v4`

## Current conclusion
No performance conclusion, profitability claim or trading strategy conclusion is justified yet. Phase 1 is prohibited until the current correction pass passes independent tester approval.

## Fourth tester gate
PR #8 / `tester/phase-0-fourth-audit` failed Phase 0 on B6 repository-control synchronization. The v4 correction pass addresses the stale active gate wording, current branch/status visibility, and the literal-core versus sensitivity-only slippage distinction. A new independent tester review is required.

## Automation control
`.github/workflows/phase0-integrity.yml` automatically validates required Phase 0 artifacts on pushes and pull requests and provides a manual `workflow_dispatch` entry. This is a control workflow only; it does not initiate Phase 1.

## Latest correction pass
PR #7 was the v3 developer correction pass reviewed by the fourth tester; PR #8 is the fourth independent tester gate. PR #9 is the current v4 developer correction pass. The current developer branch is `phase-0-corrections-v4`, which must receive another independent tester approval before Phase 1 can begin.

## Slippage control
The literal-core fallback slippage is fixed by `research/OPERATIONAL_CONVENTIONS.md`. Configurable slippage assumptions are reserved for pre-registered sensitivity variants only and cannot change the literal-core result.
