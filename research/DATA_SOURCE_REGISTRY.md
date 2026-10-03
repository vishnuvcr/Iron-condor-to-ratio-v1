# Phase 1 — Data Source Registry

## Acquisition decision framework
The primary backtest requires real intraday NIFTY option observations. A source is accepted only if it passes provenance, licensing, timestamp integrity, expiry/strike continuity, sufficient target-strike coverage, underlying alignment, data-quality checks, and reproducibility.

## Candidate sources

| Source | Coverage / resolution | Useful fields | Main gap | Phase 1 disposition |
|---|---|---|---|---|
| Hugging Face thetrademarkk/india-index-options-1m | NIFTY 1-minute, approximately 2021–2026 | OHLCV, OI, strike, type, expiry, timestamp | No documented bid/ask; partial illiquid/far-strike coverage | Primary candidate pending validation and immutable revision pin |
| Hugging Face rissin/nse-options-intraday | NIFTY 1-minute from 2024 onward | OHLCV, strike, expiry, volume | No bid/ask; Upstox intraday OI unavailable | Secondary cross-check / extension candidate |
| ICICI Direct Breeze pipeline | 1-minute NIFTY option OHLCV/OI; account/API dependent | OHLCV, OI | Requires account/API access; no documented historical bid/ask | Acquisition fallback / reconciliation source |
| Zerodha collector | 1-minute NIFTY option OHLCV/OI; account dependent | OHLCV, OI | Requires account/API access; no documented historical bid/ask | Acquisition fallback / reconciliation source |
| NSE official reports | Daily/EOD reference and contract data | bhavcopy, settlement, contract metadata, corporate actions | Not sufficient alone for intraday triggers | Mandatory reference/reconciliation source |
| OptionVault | Advertises 1-minute options with Greeks and richer market data | OHLCV, OI, Greeks, possibly tick/depth | Access/licensing not established | Commercial/reference candidate; not accepted yet |

## Important source findings
The Hugging Face thetrademarkk dataset is the strongest open candidate identified so far because its documented schema contains 1-minute option OHLCV, open interest, strike, type and expiry, and it includes NIFTY files across a multi-year span. The dataset card states CC-BY-NC-4.0 and warns that illiquid/far strikes can be sparse. This makes it suitable for Phase 1 validation but not automatically suitable for a production conclusion.

The rissin dataset combines NSE daily EOD data with Upstox 1-minute intraday candles. Its documented intraday rows do not provide OI, and neither candidate documents historical bid/ask. Therefore the execution-adjusted primary backtest must either obtain an independent quote source or use the already-frozen literal-core conservative fallback with a degraded-quality flag.

## Official exchange context
NSE's option-chain interface exposes OI, volume, IV, LTP, bid/ask and strike fields for the current chain, but its terms state that the displayed IV is reference-only and the site restricts aggregation/copying. Current option-chain data therefore cannot be silently treated as a redistributable historical dataset.

NSE's contract specification and contract-information pages provide expiry, strike/price-step and permitted-lot-size references. Historical contract metadata must be captured by effective date rather than using today's settings for older observations.

NSE's FII/FPI and DII report provides daily buy/sell/net activity and explicitly notes that the data are provisional and may change. These fields will be used only as contextual regime variables, not as causal inputs to the strategy unless pre-registered later.

NSE's corporate-action/reporting infrastructure will be used to identify relevant index/constituent events and contract/reference-data discontinuities.

## External research/data context
The GitHub nifty-options-greeks project demonstrates reconstruction of NIFTY IV/Greeks from official NSE bhavcopy data, which is useful for validation of numerical plumbing but is daily data and cannot reproduce intraday trigger timing. The Breeze and Zerodha pipelines demonstrate practical 1-minute acquisition paths but require broker/API access.

## Acceptance rule
No production performance dataset is accepted until the validation report records:
1. immutable source revision or source file hashes;
2. exact coverage period;
3. timezone/timestamp semantics;
4. option/expiry/strike continuity;
5. underlying alignment;
6. missing/stale/duplicate/crossed quote statistics where quote fields exist;
7. target-delta strike availability;
8. Greek provenance/reconstruction success rate;
9. historical lot/tick/expiry metadata;
10. licensing/redistribution constraints;
11. independent reconciliation against official NSE reference data.


## Independent quote-source escalation
- **NSE Historical Order & Trade Data (F&O):** official historical order/trade product. NSE documents F&O order data at all order ticks and provides a technical specification; current NSE market-data documentation also distinguishes Level 1 best bid/ask, Level 2 depth, Level 3 depth and tick-by-tick full order book. This is the strongest identified official route for reconstructing historical execution-quality quotes, but it is a paid product and requires procurement/access credentials. See the official NSE historical-data and real-time-data product pages for scope and subscription requirements.
- **Acceptance status:** candidate/procurement required; not yet acquired, therefore not yet part of the production backtest dataset.


## Additional open-source search results
- GitHub repository darshkale/nse-options-data-pipeline explicitly notes that public NSE bhavcopy lacks bid/ask and advertises a private full dataset with execution modeling; its public repository does not supply the required historical quote data. citeturn1search0
- GitHub repository SauMStats/nifty-options-data-engine exposes a historical NIFTY OHLCV/OI interface and explicitly assumes bid/ask unavailable and market_price=close_price. It therefore cannot satisfy the frozen literal-core midpoint requirement without a separately supplied quote source. citeturn1search6
- Commercial 1-minute NIFTY chain archives reviewed also explicitly state no bid/ask fields. citeturn1search5turn1search10
- NSE's live option-chain schema confirms that bid/ask are distinct fields in current snapshots, but this does not establish historical intraday snapshots. citeturn1search8turn1search12
