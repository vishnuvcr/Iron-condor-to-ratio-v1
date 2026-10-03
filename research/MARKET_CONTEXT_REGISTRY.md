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
