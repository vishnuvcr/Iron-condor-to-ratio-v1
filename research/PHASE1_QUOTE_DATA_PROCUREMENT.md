# Phase 1 — Historical Quote Data Procurement Decision

Updated: 2026-10-03

## G9 decision

The frozen Phase 0 literal-core execution rule requires historical bid/ask midpoint pricing. The primary Hugging Face source provides 1-minute OHLCV/OI but does not document historical bid/ask fields. Public alternatives reviewed to date likewise do not establish the required historical bid/ask series.

Therefore **close-price execution is not accepted as a substitute**.

## Preferred procurement route

NSE's paid historical order and trade data product explicitly covers the F&O segment and provides a technical specification plus sample files. The NSE product page states that historical order/trade data is provided through an online platform and that F&O historical order/trade files are available. [NSE historical order/trade data](https://betanseapi.nseindia.com/static/market-data/eod-historical-data-subscription).

The repository must obtain, subject to licensing and access authorization, the F&O historical order/trade dataset covering the complete study period or document the exact obtainable interval.

## Required reconstruction evidence

If order-level data are acquired, the reconstruction package must document:

1. raw file checksum and source date;
2. exchange transaction timestamp;
3. instrument/contract identifier;
4. order side and order activity type;
5. order price and quantity where present;
6. trade linkage where present;
7. reconstruction rule for best bid and best ask at every decision timestamp;
8. treatment of cancellations/modifications;
9. quote age and timestamp ordering;
10. crossed/locked-market handling;
11. missing-side handling;
12. spread and liquidity diagnostics;
13. exact midpoint used for IV/delta calculations and any execution fallback.

The reconstruction must be deterministic and replayable from retained raw files.

## Acceptance rule

G9 remains **BLOCKED** until either:

- historical bid/ask snapshots sufficient for the frozen midpoint rule are acquired and validated, or
- order-level data sufficient to reconstruct the same rule are acquired and validated.

A commercial description or live NSE option-chain page is not sufficient evidence of historical intraday quotes.

## Why this matters

The strategy repeatedly changes multiple option legs near delta thresholds. Using close prices in place of contemporaneous executable bid/ask can alter:

- trigger timing;
- target-delta strike selection;
- entry/exit fills;
- transaction costs;
- ratio reset/reversal timing;
- reported P&L and drawdown.

The quote-data decision is therefore a validity condition, not merely a performance refinement.

## Current evidence status

**BLOCKED — procurement/access required.**
