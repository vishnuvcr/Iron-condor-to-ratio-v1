# Research Plan

## Research question
Can the YouTube-described transition strategy—monthly 30Δ/10Δ Iron Condor transitioning to a directional ratio spread when the IC short leg reaches about 10Δ—produce reproducible risk-adjusted returns after realistic execution costs, slippage and brokerage assumptions?

## Secondary questions
1. What exact deterministic rules can be extracted from the video without adding unsupported assumptions?
2. How sensitive are results to delta thresholds, rebalance frequency, profit-taking and expiry handling?
3. How does the strategy behave across range-bound, trending, high-volatility and sharp-reversal regimes?
4. What are the distributions of returns, drawdowns, tail losses, turnover, margin use and cost drag?
5. Which parts of the video are fully specified versus discretionary or ambiguous?

## Aims
- Reproduce the strategy as faithfully and deterministically as the source permits.
- Quantify net performance after realistic Indian derivatives trading costs.
- Test robustness across market regimes and out-of-sample periods.
- Produce a reproducible research manuscript and complete audit trail.

## Objectives
- Build a source-derived rule dictionary.
- Acquire and validate intraday NIFTY option data.
- Implement the strategy as a state machine.
- Model fills, slippage, brokerage, taxes and margin/capital usage.
- Run baseline, sensitivity and robustness experiments.
- Report statistical uncertainty and limitations.

## Phase 0 — Specification and audit
Status: IN PROGRESS
- Capture source transcript and citation.
- Separate explicit rules from ambiguous/discretionary statements.
- Define research questions, aims, objectives, methodology and statistical plan.
- Audit repository controls.
- Identify historical data sources and coverage.
- Define tester gate.

Exit criterion: reproducible specification, data-source decision framework and tester handoff.

## Phase 1 — Data acquisition and validation
Status: BLOCKED BY TESTER GATE
- Obtain historical NIFTY index and option-chain intraday data.
- Cache source-derived data in repository-compatible storage or documented artifact storage.
- Validate timestamps, expiries, strikes, OHLC, OI and Greeks.
- Detect missing bars, stale quotes, crossed markets and contract errors.
- Reconstruct Greeks only when necessary using a documented model and market inputs.
- Prevent look-ahead in strike selection and execution.

## Phase 2 — Backtest engine
Status: BLOCKED
- Implement a deterministic Python state machine.
- Use minute/event data where available.
- Model bid/ask execution when available; otherwise configurable conservative slippage.
- Include brokerage and applicable exchange/transaction charges, GST, SEBI charges and stamp duty as configurable assumptions.
- Model lot size and capital/margin use.
- Log every trade, adjustment, trigger, fill and reason.

## Phase 3 — Baseline and robustness experiments
Status: BLOCKED
- Run the literal core rule-set.
- Run explicitly documented sensitivity variants.
- Compare with static Iron Condor baseline and appropriate index benchmark.
- Do not optimize on the evaluation period.

## Phase 4 — Statistical analysis
Status: BLOCKED
Primary metrics: cumulative P&L, annualized return where appropriate, maximum drawdown, volatility, Sharpe, Sortino, profit factor, win rate, expectancy, tail-loss metrics, turnover, cost drag and capital utilization.

Robustness: bootstrap confidence intervals, monthly return distributions, regime-conditioned results, parameter sensitivity, and walk-forward/out-of-sample analysis where the data length permits. Multiple-comparison risk will be reported for parameter sweeps.

## Phase 5 — Interpretation
Status: BLOCKED
Results; inferences; discussion; strengths; limitations; conclusion; future research; reproducibility appendix; full trade ledger and data dictionary.

## Phase 6 — Manuscript and release
Status: BLOCKED
Deliver a complete manuscript containing abstract, introduction, literature/data review, research questions, aims/objectives, methods, results, statistical analysis, discussion, limitations, conclusion, future directions, tables, graphs, appendices, supplements and exact reproduction instructions.

## Source-derived rule dictionary
The transcript states that the initial monthly Iron Condor sells calls and puts around 0.30 delta and buys calls and puts around 0.10 delta. See uploaded transcript lines 292–307.

Transition occurs when either short IC leg reaches approximately 0.10 delta; the IC is exited and replaced with a directional ratio spread. See lines 328–370.

For a downward move, the video creates a call-side ratio; for an upward move, a put-side ratio. Initial ratio: long 0.50 delta, short 2 lots at 0.40 delta, hedge at 0.10 delta. See lines 375–415.

For continuation, the combined short-leg delta is described as falling from about 0.80 to 0.20; the reset is long 0.40 delta, short 2 lots at 0.30 delta, hedge at 0.08 delta. See lines 427–501.

For reversal, the combined short-leg delta is described as rising to about 1.20–1.30, after which the ratio is exited and the opposite-side ratio is created. See lines 505–543.

The video also discusses profit-taking and expiry-day decisions in a discretionary manner. Those will be isolated from the deterministic core backtest rather than silently hard-coded.
