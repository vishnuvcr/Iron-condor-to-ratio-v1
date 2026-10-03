# Phase 1 G9 — Free/Public Data Salvage and Common Validation

Updated: 2026-10-03

## Status
G9 remains **BLOCKED**. This phase-1 work is limited to historical execution-quality data discovery, raw-file salvage, provenance, and validation. No Phase 2 backtest or performance analysis is authorized.

## Tester-prescribed acquisition order
1. **Hugging Face `antony9952/Nifty_option_TBT`** — salvage raw CSV files at immutable revision `643b48383839947b5fe3ed9483c9f7c0f167e865`; classify every file independently; hash retained files; measure bid/ask coverage, timestamps, instrument identity and date coverage.
2. **GitHub `ayyararyan/nse-options-pipeline`** — investigate the actual `NSEI-Data` archive behind the documented schema, including branches, releases, linked storage and author-published mirrors. The repository states that the raw directory is not tracked because it is too large.
3. **OptionVault / TickBytes public samples and archives** — inspect samples for field semantics and determine whether any historical archive is publicly downloadable. Current public documentation distinguishes samples from licensed full datasets.
4. **Other NSE option-data collectors** — inspect retained historical files/releases and distinguish acquisition pipelines from historical evidence. `BarathGB007/nse-options-data-collector` currently exposes bid/ask/Greeks in sample/current collection schemas but does not establish the complete 2021–2026 historical archive required here.
5. Apply **one common G9 validator** to every candidate.
6. If no candidate supplies complete, reproducible, legally usable historical bid/ask or deterministic order-level reconstruction coverage, use the **NSE Historical F&O Order & Trade** acquisition route.

## Common G9 acceptance contract
Every candidate must provide, or permit deterministic reconstruction of:
- timestamp and timezone;
- NIFTY option contract identity (expiry, strike, CE/PE, instrument identifier);
- observed bid and ask, including quantities where available;
- quote age/staleness control;
- non-crossed/non-invalid quote checks;
- complete study-window coverage or explicit missing-period accounting;
- deterministic mapping to the historical contract master;
- raw-file checksums and immutable acquisition provenance;
- licensing/permission evidence suitable for the research;
- deterministic execution reconstruction without future leakage.

**Forbidden:** candle close, OHLC midpoint, LTP, or any other proxy may not be relabeled as historical bid/ask or midpoint merely to unblock G9.

## Findings to date
### A. `antony9952/Nifty_option_TBT`
The public Hugging Face preview at the pinned revision shows genuine depth-shaped fields (`bid_price`, `bid_qty`, `ask_price`, `ask_qty`, `depth_level`, `instrument_key`, `timestamp`). The Hugging Face builder simultaneously reports incompatible schemas across files, including files where the TBT bid/ask fields are absent. The raw files therefore require independent salvage and per-file classification before any acceptance decision. The dataset page reports a total size of about 378 MB.
The local runtime could not directly resolve `huggingface.co`, so local raw acquisition was not claimed. The repository CI workflow remains the intended reproducible acquisition path using `HF_TOKEN` and cache retention.

### B. `ayyararyan/nse-options-pipeline`
The repository documents raw files under `NSEI-Data/date=YYYY-MM-DD/{SYMBOL}.csv` with `captured_at`, `symbol`, `expiry`, `strike_price`, `option_type`, `bid_price`, `ask_price`, `bid_qty`, `ask_qty`, OI, volume and underlying fields. The repository explicitly says the raw `NSEI-Data` files are not tracked because they are too large. This is a high-priority archive lead, not production evidence.

### C. OptionVault / TickBytes
Public repositories expose representative NIFTY option/depth samples. Their documentation states that complete historical datasets are licensed/subscription-controlled. Samples can establish semantics but cannot establish complete study-window coverage.

### D. `BarathGB007/nse-options-data-collector`
The public collector stores 15-minute option-chain snapshots containing CE/PE bid, ask, IV, Greeks, OI and volume and includes NIFTY samples. It is a reproducible collection pipeline, not yet evidence of a retained complete historical 2021–2026 quote archive.

## Required machine-readable evidence
For each candidate the common validator must emit:
- candidate identifier and immutable revision/commit;
- acquisition timestamp and source URL;
- file count, byte size and SHA-256 per retained raw file;
- schema class per file;
- row counts and bid/ask-bearing row counts;
- minimum/maximum timestamp and observed trading dates;
- instrument-key and contract-identity diagnostics;
- duplicate/out-of-order diagnostics;
- invalid/crossed quote counts;
- quote-age diagnostics at the frozen decision timestamps where applicable;
- study-window coverage by date/contract/option side;
- licensing/provenance status;
- explicit ACCEPT / REJECT / INSUFFICIENT_COVERAGE result with reasons.

No candidate is accepted from a marketing description, sample file alone, or dataset schema declaration alone.

## Exit criteria
G9 can move from BLOCKED only after a retained raw dataset or deterministic order-level archive demonstrates sufficient complete study-window coverage and passes the common validator plus independent tester review. Otherwise the research moves to the NSE licensed historical F&O Order & Trade route.