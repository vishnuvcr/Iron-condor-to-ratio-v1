# Phase 2 Context Data Specification

Updated: 2026-10-04

## Purpose

Market-context variables are used to explain regime dependence and cross-market exposure. They are not strategy signals in the literal core.

## Required context

| Dataset | Frequency | Preferred source | Role |
|---|---|---|---|
| India VIX | daily | NSE | volatility regime |
| NIFTY 50 benchmark | daily | NSE/NSE Indices | market trend/return regime |
| FII/FPI net activity | daily | NSE | institutional-flow context |
| DII net activity | daily | NSE | institutional-flow context |
| BSE Sensex | daily | BSE | cross-exchange confirmation |
| GIFT NIFTY / NSE IX activity | daily/overnight where obtainable | NSE IX | global-crossing / overnight context |
| Global equity volatility | daily | official/index or reproducible public source | global risk regime |
| USD/INR | daily | RBI/FBIL/reproducible market source | currency regime |
| Gold | daily | MCX/official or reproducible benchmark | defensive/risk-off context |
| Corporate/index events | event dates | NSE/BSE/NIFTY Indices | event-marker controls |

## Required fields

Each context dataset must carry:
- observation timestamp/date;
- timezone semantics;
- source and immutable revision/file hash;
- value and units;
- publication/availability timestamp where relevant;
- missingness flag;
- corporate-action/event adjustment flag where relevant.

## Look-ahead rule

A context value may be used as a descriptive regime label only when its observation/publication was available before the strategy decision period. Post-close daily data must not be used to label an intraday decision as though it were known intraday.

## Regime definitions

Pre-defined, non-optimized labels:
- India VIX quintiles over the development window;
- NIFTY rolling 20-day realized volatility quintiles;
- positive/negative 20-day trend;
- large-gap / normal-gap days;
- major event-window flag.

These labels are explanatory only.

## Cross-market analysis

The manuscript will separately report:
- strategy performance on high/low volatility days;
- strategy performance after large overnight NIFTY/GIFT moves;
- strategy performance around large FII/DII flow days;
- strategy behavior during major global risk-off events;
- BSE/NSE divergence days where measurable.

No context variable becomes a trigger unless explicitly pre-registered as a later variant.

## Data integrity

Missing context data do not cause the primary strategy backtest to fail. They produce an UNKNOWN_CONTEXT label and are excluded only from the corresponding conditional-regime analysis.
