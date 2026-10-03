# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current gate
Phase 0 — research specification and reproducibility setup. Tester gate required before Phase 1.

## Source strategy
The uploaded transcript is the primary strategy source. It specifies a monthly Iron Condor using short call/put near 0.30 delta and long call/put near 0.10 delta; transition when either short IC leg reaches approximately 0.10 delta; a directional ratio spread after transition; continuation and reversal delta triggers; and additional discretionary profit-taking/expiry-day discussion.

See RESEARCH_PLAN.md and RESEARCH_STATUS.md.

## Data policy
The research requires intraday option prices and a defensible method for calculating or observing Greeks. NSE public archives provide historical derivatives reports, but daily reports alone do not establish the intraday option-chain history required for these delta-trigger rules. Candidate datasets will be evaluated and provenance/licensing documented before use.

## Research controls
- RESEARCH_PLAN.md
- RESEARCH_STATUS.md
- ERROR_LOG.md
- CONVERSATION_LOG.md
- PROJECT_INSTRUCTIONS.md

## Phase gate
No Phase 1 implementation/backtest will be treated as validated until an independent tester report is available, as required by the project instructions.
