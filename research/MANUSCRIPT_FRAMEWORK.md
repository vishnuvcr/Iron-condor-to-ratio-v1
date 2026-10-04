# Iron Condor to Ratio v1 — Research Manuscript Framework

**Status:** pre-results framework; no production profitability conclusion  
**Date:** 2026-10-04

## Abstract
To be completed only after independently audited production ledgers exist. The abstract will report the deterministic source-derived rule set, proxy execution assumptions, net-of-cost performance, uncertainty, robustness, limitations and conclusion without overstating historical live execution.

## 1. Introduction
- Motivation: reproducible evaluation of an intraday option strategy described in a public source.
- Research gap: deterministic reconstruction, historical Greeks, realistic costs/slippage, and auditability.
- Primary research question and secondary questions from RESEARCH_PLAN.md.
- Hypotheses:
  - H1: the transition strategy has positive net risk-adjusted performance under the locked 10-bps proxy scenario.
  - H2: performance exceeds the static 30Δ/10Δ monthly Iron Condor benchmark on pre-registered paired metrics.
  - H3: conclusions remain directionally stable across the pre-registered slippage and trigger-sensitivity grid.
  - H4: performance is regime-dependent in explanatory, not predictive, analyses.

## 2. Source and Literature Review
Synthesize the repository literature review, source video/rule provenance, options-market microstructure literature, transaction-cost literature, backtest-overfitting literature, volatility/regime literature, and India-specific market-structure evidence. Every empirical claim will retain source provenance.

## 3. Materials and Data
- NIFTY one-minute options and underlying.
- Production historical Greeks/IV provenance and limitations.
- Contract-master reconstruction and official NSE chronology.
- Session calendar and special-session controls.
- Date-effective Paytm Money/brokerage and statutory cost schedule.
- India VIX, NIFTY, FII/DII, BSE, GIFT NIFTY/NSE IX, USD/INR, gold and event-context datasets where coverage permits.
- Immutable hashes, revisions, acquisition timestamps and missingness controls.

## 4. Strategy Specification
Describe the literal source-derived state machine separately from operational assumptions:
1. monthly 30Δ/10Δ Iron Condor;
2. short-leg 0.10-delta crossing transition;
3. directional ratio construction;
4. continuation reset;
5. reversal;
6. expiry closure;
7. failed atomic adjustment/re-arm behavior.
No discretionary profit-taking rule is silently converted into a deterministic rule.

## 5. Execution and Cost Methodology
- Completed one-minute decision bar.
- Next eligible option bar open.
- Adverse 0/5/10/20/50-bps slippage with historical tick-size floor.
- Atomic multi-leg execution.
- Date-effective brokerage/statutory charges.
- Monthly NSE slab accounting.
- No interpolation or future observations.
- Theoretical expiry-loss capital proxy, clearly separated from historical SPAN.

## 6. Statistical Analysis
Use the pre-registered PHASE3_STATISTICAL_ANALYSIS_PLAN.md:
- mean/geometric returns, drawdown, volatility, Sharpe/Sortino;
- profit factor, win rate, expectancy;
- tail loss and expected shortfall where sample size permits;
- bootstrap/block-bootstrap uncertainty;
- Newey-West inference where serial dependence warrants it;
- paired benchmark comparisons;
- pre-registered sensitivity and regime analyses;
- multiple-comparison disclosure and overfitting diagnostics.

## 7. Results
Populate only from immutable, independently audited production ledgers:
- scenario table;
- benchmark comparison;
- cumulative equity and drawdown figures;
- cost/slippage decomposition;
- trade/adjustment distributions;
- regime tables;
- sensitivity heatmaps;
- uncertainty intervals;
- data-quality/execution exclusions.

## 8. Discussion
Interpret economic significance, execution fragility, cost drag, regime dependence, and comparison with prior literature. Distinguish statistical evidence from practical tradability.

## 9. Strengths
- deterministic rule dictionary;
- explicit source/assumption separation;
- immutable provenance;
- historical cost/slippage treatment;
- atomic execution;
- benchmark and sensitivity controls;
- independent tester gates.

## 10. Limitations
- public-source ambiguity/discretion;
- proxy execution rather than historical bid/ask fills;
- reconstructed rather than original member-file contract metadata where applicable;
- deferred G6 evidence-completeness items;
- potential context-data availability limitations;
- E150 expiry-close correction and its unresolved materiality until consolidated audit;
- theoretical rather than historical SPAN margin.

## 11. Conclusion
Reserved for the final independently audited evidence. No conclusion of profitability or tradability may be inserted before the final gate.

## 12. Future Research
- exact historical order/trade/bid-ask data;
- exact historical exchange contract files;
- historical SPAN/margin;
- broker-specific account statements and charges;
- out-of-sample validation;
- alternative deterministic interpretations of discretionary source rules;
- execution-aware optimization only after locked evaluation.

## Appendices and Supplements
A. Rule dictionary  
B. Data dictionary and provenance  
C. Contract chronology  
D. Cost schedule  
E. Test/gate reports  
F. Statistical code/configuration  
G. Full scenario ledgers and checksums  
H. Context-data provenance  
I. Error log and reproducibility record
