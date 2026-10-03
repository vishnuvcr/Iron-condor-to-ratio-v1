# Phase 1 Data Cache

Phase 1 stores source manifests, hashes, validation summaries and reproducibility metadata in Git. Large raw datasets are not copied into normal Git history; the acquisition workflow caches/downloads them using immutable source manifests and GitHub Actions cache/artifacts where licensing permits.

## Primary candidate
- Hugging Face dataset: thetrademarkk/india-index-options-1m
- NIFTY option files provide 1-minute OHLCV plus open interest; the dataset card reports coverage approximately 2021–2026 and warns that option coverage is partial for illiquid/far strikes.
- License: CC-BY-NC-4.0 according to the dataset card.
- Historical bid/ask is not in the documented schema. Therefore it cannot be represented as true historical bid/ask without another source; the literal-core fallback-slippage path remains necessary unless a separate quote source is validated.

## Secondary candidate
- Hugging Face dataset: rissin/nse-options-intraday
- Combines NSE daily EOD data with Upstox 1-minute intraday candles from 2024 onward.
- Intraday schema includes OHLCV but not bid/ask and reports OI as unavailable for Upstox intraday rows.
- License is listed as "other"; redistribution must be checked before use.

## Research rule
No dataset becomes the primary performance dataset until the Phase 1 validation workflow records schema, coverage, timestamp, strike/expiry continuity, missing-bar/stale/crossed-quote findings, provenance, licensing and reconciliation results.
