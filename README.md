# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 0 third-gate correction pass — awaiting independent re-test.**

## Gate
**Phase 1 remains blocked.** The first independent tester failed Phase 0 and required corrections. The second independent tester failed PR #3. The developer has addressed the reported repository-integrity and numerical-reproducibility defects on `phase-0-corrections-v3`; no downstream research has started.

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
`phase-0-corrections-v2`

## Current conclusion
No performance conclusion, profitability claim or trading strategy conclusion is justified yet. Phase 1 is prohibited until the corrected specification passes independent tester approval.

## Third tester gate
PR #6 / `tester/phase-0-third-audit` failed Phase 0. The reported B1–B5 defects are addressed on `phase-0-corrections-v3` and a new independent tester review is required.

## Automation control
`.github/workflows/phase0-integrity.yml` automatically validates required Phase 0 artifacts on pushes and pull requests and provides a manual `workflow_dispatch` entry. This is a control workflow only; it does not initiate Phase 1.

## Fourth tester gate
PR #7 / phase-0-corrections-v3 passed the numerical B1–B5 re-check, but the fourth tester failed the repository-control gate because current status/plan/README records remain stale or inconsistent. Phase 1 remains blocked.
