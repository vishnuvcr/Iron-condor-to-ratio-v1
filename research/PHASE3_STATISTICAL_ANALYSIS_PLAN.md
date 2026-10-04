# Phase 3 — Statistical Analysis and Robustness Plan

Updated: 2026-10-04

## Pre-registration boundary

This document defines the analysis before looking at production strategy results. Parameter sweeps are sensitivity experiments, not optimization. The literal source-derived rule set remains the primary analysis.

## Primary estimands

1. Net cumulative P&L after slippage, Paytm Money brokerage, NSE/IPFT, SEBI, STT, stamp duty and GST.
2. Annualized geometric return where the backtest horizon supports it.
3. Maximum peak-to-trough drawdown.
4. Annualized volatility of monthly strategy returns.
5. Sharpe ratio using monthly returns and a contemporaneous risk-free benchmark; the exact annualization convention will be frozen before release.
6. Sortino ratio using downside deviation.
7. Profit factor and trade/event win rate.
8. Expectancy per initiated monthly cycle and per adjustment.
9. Tail loss measures: worst trade, 95%/99% empirical loss quantiles, expected shortfall where sample size permits.
10. Cost drag in rupees and as a percentage of gross strategy P&L.
11. Turnover, number of adjustments, failed execution groups, and capital/margin utilization.

## Statistical tests

- One-sample bootstrap confidence intervals for strategy mean monthly return and geometric growth metrics.
- Stationary/block bootstrap for path-dependent drawdown and serial dependence.
- Newey–West adjusted inference for mean monthly return when autocorrelation is material.
- Paired comparisons versus a static monthly 30Δ/10Δ iron-condor benchmark using the same execution/cost layer.
- Regime-conditioned descriptive statistics by pre-defined India VIX quintiles and trend/return states. Regime labels are descriptive, not trading signals.
- Multiple-comparison disclosure for sensitivity grids; no best-parameter selection from the evaluation sample.
- Deflated-Sharpe / probability-of-backtest-overfitting style diagnostics when the number of tested variants is sufficient to justify them.

## Robustness matrix

### Slippage
0, 5, 10, 20, 50 bps with historical tick-size floor.

### Trigger sensitivity
Only pre-registered neighboring variants:
- IC trigger 0.08 / 0.10 / 0.12;
- continuation trigger 0.15 / 0.20 / 0.25;
- reversal trigger 1.20 / 1.25 / 1.30.

### Delta-target tolerance
0.03 / 0.05 / 0.07.

### Expiry convention
Primary monthly latest-listed-expiry rule; a documented alternate nearest-month rule may be used only as a robustness comparison.

### Profit taking
Literal core excludes discretionary profit-taking. A separately labelled discretionary variant may be evaluated after the literal core, with no parameter selection based on final-period performance.

## Out-of-sample protocol

Use chronological evaluation:
- development/training period only for implementation debugging;
- locked primary evaluation period not used for rule selection;
- optional walk-forward windows if the sample is long enough.

No random train/test shuffling is permitted for path-dependent trading rules.

## Reporting

Every sensitivity run must retain:
- exact configuration;
- exact data manifest and input hashes;
- exact Git SHA;
- number of cycles and adjustments;
- net P&L and all primary metrics;
- cost/slippage breakdown;
- drawdown and tail-loss statistics;
- reason for exclusion or missing execution.

## Interpretation rule

A positive result at 0 bps but negative result at the 10 bps primary scenario will be interpreted as execution-fragile. A positive result only after omitting realistic fees/costs will not be considered a viable strategy conclusion.

No single Sharpe ratio or CAGR is sufficient for acceptance. Tail behavior, cost drag, regime dependence and reproducibility are co-equal decision criteria.
