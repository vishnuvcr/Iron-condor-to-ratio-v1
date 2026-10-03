# Phase 1 — Market Context Registry

These datasets are contextual and are not strategy signals unless explicitly pre-registered later.

| Context | Source | Frequency | Intended use |
|---|---|---|---|
| NIFTY 50 | NSE historical index data | Daily + intraday from primary dataset | Underlying return/regime classification |
| India VIX | NSE historical India VIX | Daily; methodology uses NIFTY option bid/ask | Volatility-regime stratification |
| FII/FPI and DII | NSE report | Daily | Institutional-flow regime context |
| GIFT NIFTY | NSE IX | Intraday/daily where historical access permits | Overnight/global crossing context |
| BSE/Sensex | BSE historical data | Daily/intraday where licensed | Cross-exchange context |
| Global equity risk | S&P 500/Nasdaq or licensed source | Daily/intraday where licensed | Overnight/global regime context |
| Global volatility | CBOE VIX or licensed source | Daily/intraday where licensed | Global volatility regime |
| Corporate actions/events | NSE corporate-action and announcement sources | Event-based | Event/regime flags and data-quality checks |
| News | Timestamped licensed/public source | Event-based | Event-study/contextual flags; no post-event look-ahead |

## Important constraints
- Historical availability and licensing will be verified before inclusion.
- Context variables are aligned strictly using information available by the decision timestamp.
- News/event timestamps must use publication/announcement time rather than later summaries.
- No contextual variable will be used to alter trades unless its use is pre-registered in a later phase.

## Source-level validation additions
- **India VIX:** NSE publishes historical India VIX and documents that the index is calculated from best bid/ask NIFTY option quotes for the near-term volatility estimate. This makes India VIX useful as an exogenous regime variable, but it cannot substitute for contract-level historical quotes required by the strategy. citeturn4search0turn4search1
- **NIFTY dividend yield:** NSE historical reports expose NIFTY P/E, P/B and dividend-yield values, providing a candidate date-aligned source for the frozen Black-Scholes q input. citeturn4search3
- **Risk-free rate:** RBI publishes 91-day Treasury-bill auction yields and weekly statistical series; the Phase 0 convention will use the latest available 91-day T-bill yield on or before each decision date, then convert the quoted annual yield as pre-registered. citeturn4search2turn4search12
- **Quote dependency:** India VIX methodology itself uses best bid/ask inputs, reinforcing the distinction between contextual volatility data and the missing historical contract-level quote data.


## Date-specific risk-free source validation
RBI Weekly Statistical Supplements provide 91-day Treasury-bill primary yields across historical reporting dates. Examples covering the study period show explicit 91-day primary yields, confirming that the required r input can be sourced from an official historical series rather than a contemporary rate. The production pipeline must still acquire the complete date-aligned series and apply the Phase 0 latest-on-or-before rule. citeturn4search6turn4search10turn4search0turn4search1turn4search2
