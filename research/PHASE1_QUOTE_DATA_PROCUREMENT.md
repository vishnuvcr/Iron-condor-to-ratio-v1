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

## Additional official-source technical validation — 2026-10-03

NSE's Historical Order & Trade Data specification (version 1.15, 08-Sep-2025) describes F&O order data at all order ticks and includes transaction time, buy/sell indicator, entry/cancel/modify activity, contract identity, order quantity and limit price. Corresponding F&O trade data include trade time, contract identity, trade price/quantity and buy/sell order numbers. These fields make deterministic order-book reconstruction technically plausible, subject to validating purchased-file coverage, sequencing semantics, and licensing/access terms.

The NSE historical-data service also provides F&O historical order/trade files and technical/sample documentation; access is subscription/procurement controlled.

This does **not** close G9. No licensed historical order/trade files have yet been acquired into the repository and no reconstruction has been validated.

## Current evidence status

**BLOCKED — procurement/access and validation required.**


## 2026-10-03 — broader G9 source screen

Additional public-source screening found several technically interesting but non-qualifying alternatives:
- GitHub NIFTY option pipelines that expose or model bid/ask fields but do not provide a validated complete historical bid/ask archive.
- GitHub projects using 2024 Kaggle/live 2026 data explicitly state bid/ask is unavailable and use close/market-price proxies.
- A public NSE-options analytics pipeline documents bid/ask columns in its input schema, but its raw market-data directory is not tracked in the repository.
- Commercial/subscription-style repositories advertise tick/Level-2 NIFTY option data, but access, licensing, historical coverage and reproducibility are not established for this study.

These sources are retained as search evidence, not as accepted G9 data. The official NSE Historical Order & Trade product remains the preferred acquisition route because its specification exposes all-order-tick F&O data with order price/side/activity and linked trade identifiers. G9 remains BLOCKED until licensed raw data are actually acquired and reconstructed.

## 2026-10-03 — Hugging Face / open-data screening

Hugging Face screening identified additional NIFTY option datasets, including `rissin/nse-options-intraday` and `artist-23/nifty-options-data`. The former combines daily NSE F&O history with 1-minute Upstox candles and does not establish historical bid/ask; the latter exposes OHLC/IV/OI-style fields but does not document bid/ask. The primary `thetrademarkk/india-index-options-1m` schema likewise remains OHLCV(+OI) without historical bid/ask.

These are useful corroborative/data-engineering sources but do not satisfy the frozen G9 execution-price requirement. G9 therefore remains BLOCKED.

## 2026-10-03 — official NSE procurement re-verification
- NSE's current Paid End of the day / Historical Data page explicitly lists **End of the day/Historical Order & Trade data** for CM, F&O, CD and COM, with F&O sample files and a technical specification.
- NSE's data-availability material states that Historical Order & Trade data are available from **January 2008** for F&O, making the product temporally suitable for the 2021-2026 study window.
- NSE's current specification documents effective-date format changes in FAO historical data; the reconstruction implementation must therefore select the correct parser/version by effective date rather than assuming one fixed record width.
- The published tariff confirms that Historical Order & Trade data are subscription-controlled/paid.
- **G9 remains BLOCKED:** no licensed F&O historical files have been acquired into the repository and no reconstruction/quote-quality validation has been executed.
- Close-price substitution remains prohibited under the frozen literal-core midpoint rule.
## 2026-10-03 — new public bid/ask TBT candidate

A new Hugging Face candidate, `antony9952/Nifty_option_TBT`, was identified. Its published preview contains timestamped depth-level `bid_price`, `bid_qty`, `ask_price`, and `ask_qty` fields for `NSE_FO` instrument keys. The dataset's current Hugging Face builder, however, reports incompatible schemas across files: some files contain TBT bid/ask/depth fields while others contain LTP/OHLC/OI/IV fields without those bid/ask columns. The candidate therefore cannot be treated as a homogeneous production archive without raw-file validation. urlHugging Face Nifty_option_TBThttps://huggingface.co/datasets/antony9952/Nifty_option_TBT

The repository now contains `scripts/validate_g9_tbt_candidate.py` and `.github/workflows/phase1-g9-tbt-candidate.yml` to acquire the pinned candidate revision through the HF cache and audit file schemas, bid/ask presence, timestamps and observed coverage. This workflow has a manual dispatch control and an automatic push/PR path.

**G9 remains BLOCKED.** The candidate must first demonstrate adequate study-window coverage, NIFTY contract identity/reconciliation, timestamp quality and quote-quality acceptance. It is not an accepted substitute for the official NSE historical Order & Trade route.


## 2026-10-03 — G9 free-data salvage continuation
The prescribed free-data sequence is now recorded in research/PHASE1_G9_FREE_DATA_SALVAGE.md. Current findings: the Hugging Face TBT candidate has genuine bid/ask/depth preview fields but mixed schemas; ayyararyan/nse-options-pipeline documents bid/ask-bearing raw files but does not track its large raw archive; OptionVault/TickBytes expose public samples while describing full datasets as licensed; BarathGB007/nse-options-data-collector exposes bid/ask-bearing current/sample data but not a complete historical archive. These are leads only. G9 remains BLOCKED and the NSE licensed route remains the fallback.

## 2026-10-03 — methodology change: bid/ask no longer mandatory
The primary research methodology has been formally changed. Historical bid/ask is no longer required for the primary backtest.

The replacement execution convention is defined in `research/PHASE1_EXECUTION_PROXY_SPEC.md`:
- decisions use completed 1-minute bars;
- base fill is the next eligible 1-minute option bar open;
- adverse per-leg slippage is applied at 0/5/10/20/50 bps with an effective-date tick-size floor;
- brokerage/statutory/exchange costs remain date-effective and separate;
- missing next-bar execution is never interpolated or silently filled.

This does **not** convert OHLC/LTP into bid/ask and does not permit historical executable-price claims.

The previous bid/ask procurement path remains useful for future validation, but it is no longer a mandatory blocker for the primary backtest. Independent tester approval of this methodology change is required before Phase 2.

