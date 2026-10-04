# Literature Review — Iron Condor to Ratio v1

Updated: 2026-10-04

## Scope
Targeted literature review for (1) condor/iron-condor empirical performance, (2) Indian/NIFTY option risk premia, (3) transaction-cost and execution realism, (4) backtest overfitting and validation, and (5) option-market microstructure.

## Selected evidence

| Topic | Source | Main relevance |
|---|---|---|
| Condor performance | Niblock, *Flight of the Condors* (Applied Finance Letters, 2017), DOI 10.24135/afl.v6i01.69 | Monthly condor results can be materially regime/volatility dependent; risk-adjusted conclusions differ by structure. |
| Iron condor performance | de Saint-Cyr, *A Simple Historical Analysis of the Performance of Iron Condors on the SPX* (2023), SSRN 4643378 | Long historical sample links iron-condor outcomes to market/volatility conditions, supporting regime-conditioned analysis. |
| Indian equity options | Jain, *Indian equity options: Smile, risk premiums, and efficiency* (Journal of Futures Markets, 2019), DOI 10.1002/fut.21971 | Indian option IV contains information about future volatility; supports model-based delta/IV construction and explicit risk-premium analysis. |
| NIFTY variance risk premium | Hora, *Does the variance risk premium (VRP) from NIFTY options drive excess returns in a volatility-selling strategy?* (2025), DOI 10.69889/9035hn40 | Reports positive implied-vs-realized variance premium in NIFTY/India VIX data; relevant to short-volatility context but does not validate this specific strategy. |
| Options trading costs | Chaput, *Volatility trade design* (Journal of Futures Markets, 2005), DOI 10.1002/fut.20142 | Shows volatility-trade design is influenced by delta, transaction costs, gamma and vega considerations. |
| Transaction-cost modeling | Leland, *Option Pricing and Replication with Transactions Costs* (Journal of Finance, 1985), DOI 10.1111/j.1540-6261.1985.tb02383.x | Supports treating trading costs as a first-class component rather than a cosmetic post-adjustment. |
| Option microstructure | Kaeck, van Kervel & Seeger, *Price impact versus bid–ask spreads in the index option market* (Journal of Financial Markets, 2022), DOI 10.1016/j.finmar.2021.100675 | Demonstrates that option execution costs reflect more than quoted spread alone; strengthens conservative proxy-execution treatment. |
| Backtest overfitting | Bailey et al., *The Probability of Backtest Overfitting* (2015) | Supports keeping the literal core frozen, separating sensitivity analysis from optimization, and protecting out-of-sample evaluation. |
| Selection bias / Sharpe | Bailey & López de Prado, *The Deflated Sharpe Ratio* (2014) | Supports adjustment/interpretation of Sharpe-like metrics when many variants are examined. |
| NSE/BSE microstructure | *Market microstructure: a comparative study of Bombay stock exchange and national stock exchange* (2020) | Supports considering Indian-market liquidity, efficiency and volatility regime variables. |

## Research implications
1. A profitable short-volatility option strategy cannot be interpreted independently of volatility regime and transaction-cost drag.
2. Delta-defined strikes must be reconstructed from contemporaneous information; using future IV or same-day risk inputs would introduce look-ahead.
3. Cost sensitivity is a core result, not a side calculation.
4. Parameter sweeps must be pre-registered and limited; the literal source rule-set should be the primary result.
5. Results should be conditioned on regime and expiry-cycle characteristics rather than reported only as an unconditional CAGR/Sharpe.

## Primary references
- https://ojs.aut.ac.nz/applied-finance-letters/1/article/view/69
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4643378
- https://onlinelibrary.wiley.com/doi/full/10.1002/fut.21971
- https://doi.org/10.69889/9035hn40
- https://onlinelibrary.wiley.com/doi/10.1002/fut.20142
- https://onlinelibrary.wiley.com/doi/full/10.1111/j.1540-6261.1985.tb02383.x
- https://doi.org/10.1016/j.finmar.2021.100675
- https://escholarship.org/uc/item/4w1110bb
- https://doi.org/10.2139/ssrn.2460551
- https://www.sciencedirect.com/org/science/article/pii/S0972798120000277

## Review boundary
This is a research-planning literature pass, not a claim that the cited studies validate the YouTube-derived transition strategy. The final manuscript will expand the bibliography, document inclusion/exclusion criteria, and distinguish peer-reviewed work from working papers and web sources.
