# Literature and Data Review — Phase 0

## Purpose
This is a scoping review for the strategy backtest. It does not treat prior studies as evidence that this specific strategy works.

## Literature findings
1. **Iron-condor risk structure.** Dziawgo describes the iron condor as a combination of two option spreads and studies the effects of the underlying price on delta, gamma, vega and theta. The paper emphasizes the strategy's range-oriented payoff and risk characteristics. Source: Wroclaw University of Economics and Business, 2020. DOI 10.15611/pn.2020.2.03. citeturn1search3turn1search15
2. **Condor empirical performance.** Niblock studies condor spreads using monthly Australian equity options and evaluates nominal and risk-adjusted performance. This supports using risk-adjusted metrics rather than raw P&L alone. It is not evidence for NIFTY or this transition strategy. citeturn1search0
3. **Volatility-trade design.** Chaput reports that observed volatility-trade designs are related to delta, transaction costs, gamma and vega. This reinforces the need to model transaction costs and Greeks when evaluating a delta-selected condor. citeturn1search4
4. **Indian option-market characteristics.** Jain's study of Indian equity options finds that a smile-adjusted Black model fits option prices well and that IV contains information about future volatility. This supports careful treatment of the implied-volatility surface when reconstructing deltas. citeturn1search16
5. **NIFTY option-return asymmetry.** Bhat and co-author research reports a day/night asymmetry in NIFTY option returns and notes the relevance of volatility risk premia to option-selling strategies. This supports intraday timing controls and regime analysis. citeturn1search17
6. **NIFTY variance risk premium.** A 2025 study reports positive variance risk premium using daily NIFTY and India VIX data over five years. This is relevant background for short-volatility strategies but does not establish profitability of this strategy. citeturn1search2
7. **Recent 0DTE iron-condor evidence.** Perz reports one-minute SPX 0DTE iron-condor experiments over a 12-month sample. The market, maturity and strategy rules differ materially from this project, so it is background rather than direct evidence. citeturn1search11
8. **Iron-condor optimization literature.** Recent work frames iron-condor portfolio management as a risk/optimal-stopping problem, highlighting the importance of path dependence and stopping rules. This supports treating adjustment timing as a first-class research variable. citeturn1academia42

## Data-source findings
### NSE
NSE's derivatives report portal exposes historical daily reports including F&O bhavcopy, settlement prices, volatility, participant-wise open interest and other derivatives reports. NSE also documents paid end-of-day/historical trade-data products. These are authoritative sources for daily contract/reference data, but the public report pages do not by themselves provide the minute-by-minute option chain required by the video's delta triggers. citeturn0search0turn0search1

### Public/open-source candidates
- A GitHub pipeline documents a method for collecting NIFTY option 1-minute OHLCV/OI through the ICICI Direct Breeze API, subject to account/API access. citeturn0search2
- A GitHub collector documents 1-minute NIFTY option OHLCV/OI using Zerodha data, also requiring account access. citeturn0search3
- An open GitHub repository provides a synthetic NIFTY option dataset for validating engine mechanics, but explicitly says it is synthetic; it must not be used as the primary performance dataset. citeturn0search4
- Other public repositories advertise historical 1-minute option/Greek datasets, but access/licensing must be independently verified before using them as research data. citeturn0search6turn0search9

## Data decision rule
The primary performance backtest must use real historical NIFTY option prices with intraday resolution sufficient to reproduce delta triggers. Synthetic data may be used only for unit tests. If observed Greeks are absent, the engine will reconstruct deltas from contemporaneous option prices and a documented IV model, with sensitivity analysis.

## Key unresolved data questions
- Exact historical bid/ask availability.
- Exact intraday timestamps and timezone conventions.
- Historical lot-size changes.
- Expiry-calendar changes, especially after exchange rule changes.
- Corporate/action relevance to index data.
- Whether the selected data source includes reliable Greeks or only prices/OI.
- Licensing/redistribution constraints for cached data.
