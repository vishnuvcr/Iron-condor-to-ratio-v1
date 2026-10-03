# Tester Report — G9 Free/Public Historical Bid/Ask Data Search

Date: 2026-10-03  
Role: Tester  
Phase: Phase 1  
Gate: G9 — Historical bid/ask / execution quality  
Decision: **BLOCKED — no free source is currently production-accepted**

## 1. Executive decision

An additional broad public-data screening was performed after rejection of `antony9952/Nifty_option_TBT` as a production G9 source.

The search covered public Hugging Face datasets, GitHub repositories/projects, exchange documentation, and publicly described market-data sources. Several sources contain bid/ask-shaped or depth-shaped records, but none has yet demonstrated all of the following across the complete Phase 1 study window:

- historical NIFTY option bid and ask;
- bid/ask quantities where required;
- deterministic timestamps and timezone;
- complete contract identity;
- complete study-period coverage;
- quote-age/staleness controls;
- reproducible raw-data acquisition;
- a license/permission basis suitable for this research;
- deterministic execution/fill reconstruction.

**Therefore G9 must remain BLOCKED. No Phase 2 authorization is implied.**

## 2. High-priority free/public candidates

### A. Hugging Face: `antony9952/Nifty_option_TBT`

Public dataset:
https://huggingface.co/datasets/antony9952/Nifty_option_TBT

The public preview demonstrates genuine TBT/depth-shaped records containing fields including:

- `instrument_key`
- `timestamp`
- `depth_level`
- `bid_price`
- `bid_qty`
- `ask_price`
- `ask_qty`

This makes it the most direct free-data candidate found.

However, the dataset viewer reports a `DatasetGenerationCastError`: files do not share one schema. The reported conflicting schemas include 18 newly appearing fields such as `request_mode`, `volume`, `oi`, `ltp`, `feed_timestamp`, `iv`, etc., and seven missing TBT fields including `depth_level`, `ask_qty`, `ask_price`, `timestamp`, `tick_id`, `bid_qty`, and `bid_price`.

**Tester recommendation:** do not discard the underlying raw files solely because the viewer fails. Inspect each raw CSV independently, classify schemas, and determine whether a coherent bid/ask/depth subset can be isolated. This is the highest-priority free-data salvage task.

**Current G9 status:** rejected pending raw-file salvage and full-sample validation.

### B. GitHub: `ayyararyan/nse-options-pipeline`

Repository:
https://github.com/ayyararyan/nse-options-pipeline

Its documented NSE option-data schema includes fields such as:

- `captured_at`
- `symbol`
- `expiry`
- `strike_price`
- `option_type`
- `bid_price`
- `ask_price`
- `bid_qty`
- `ask_qty`
- `open_interest`
- `total_traded_volume`
- `underlying_value`

This schema is unusually close to the frozen G9 requirement.

The repository states that its large `NSEI-Data` files are not tracked in Git because of size. Therefore the repository itself is not yet evidence of complete historical coverage.

**Tester recommendation:** investigate repository releases, branches, Git LFS references, linked archives and author-published mirrors. Do not accept until raw historical files and coverage are independently verified.

**Current G9 status:** high-priority lead, not accepted.

### C. GitHub: QuantDev-stack OptionVault

Repository:
https://github.com/QuantDev-stack/OptionVault

The project describes NSE options data including tick data and Level-2 market-depth samples, with NIFTY examples.

The repository provides samples, but the complete historical dataset is described as much larger and not established as freely available for this study.

**Tester recommendation:** use the free samples for schema/semantic validation and search for any freely released historical archive. Do not infer full-sample availability from samples.

**Current G9 status:** free sample only; not accepted.

### D. GitHub: QuantDev-stack TickBytes

Repository:
https://github.com/QuantDev-stack/TickBytes

The project describes tick-by-tick execution data and Level-2/top-5 bid/ask information for NSE options, including NIFTY examples.

The public repository provides representative samples; complete historical daily data are not established as freely available.

**Tester recommendation:** inspect sample semantics and search for public historical releases/mirrors, but retain the distinction between free samples and complete historical coverage.

**Current G9 status:** free sample only; not accepted.

### E. GitHub: BarathGB007/nse-options-data-collector

Repository:
https://github.com/BarathGB007/nse-options-data-collector

The project documents collection of NIFTY option-chain fields including bid, ask, IV, Greeks, OI and volume.

The repository is principally a collection pipeline rather than a demonstrated complete historical archive.

**Tester recommendation:** inspect committed data, releases and historical archives. If no complete archive exists, treat it as a reproducible acquisition method rather than historical evidence.

**Current G9 status:** lead, not accepted.

### F. Hugging Face OHLC/IV/OI datasets

Examples identified include:

- https://huggingface.co/datasets/rissin/nse-options-intraday
- https://huggingface.co/datasets/artist-23/nifty-options-data

These are useful supplementary option datasets, but their documented fields are primarily OHLC/volume/OI/IV-type data and do not establish historical bid/ask.

**Tester recommendation:** use them for G5/G6/G7 cross-validation where appropriate, but never substitute candle close for historical bid/ask in G9.

**Current G9 status:** non-qualifying for execution-quality acceptance.

## 3. Exchange-origin route

NSE's historical F&O Order & Trade specification is technically important because order/trade records can potentially support deterministic quote/order-book reconstruction.

NSE historical-data documentation:
https://www.nseindia.com/market-data/historical-equity-market-data

NSE historical order/trade technical specification:
https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Hist_Order_Trade_Data_1.15.pdf

The documented F&O order data include transaction time, buy/sell indicator, order activity, contract identity, quantity and price; trade data include transaction time, contract identity, trade price/quantity and linked order identifiers.

This is technically compatible with a reconstruction route, but the full historical product is not established as freely downloadable.

**Tester recommendation:** exhaust the free raw-file routes first, while simultaneously obtaining an NSE historical Order & Trade sample/specification. If no free full-period quote/depth archive survives validation, use the NSE licensed route rather than relaxing G9.

## 4. Required validation pipeline for any free candidate

The developer should implement/extend a common validator so every candidate is tested identically:

1. **Raw acquisition**
   - pin repository/dataset revision;
   - preserve raw files;
   - record SHA-256 hashes;
   - record license and acquisition timestamp.

2. **Schema classification**
   - validate every file independently;
   - detect schema drift across files;
   - reject silent column reinterpretation;
   - classify TBT/L1/L2/trade/OHLC files separately.

3. **Contract mapping**
   - map instrument identifiers to symbol, expiry, strike and CE/PE;
   - validate against historical contract metadata.

4. **Timestamp**
   - establish timezone;
   - normalize to IST;
   - establish timestamp resolution;
   - detect duplicate/out-of-order events.

5. **Quote reconstruction**
   - construct the best valid bid/ask at each decision timestamp;
   - never use future observations;
   - define maximum quote age \\(\\Delta_{max}\\) before using a quote;
   - reject crossed/negative-spread/zero-invalid quotes according to pre-registered rules.

6. **Coverage**
   - calculate coverage by date, expiry, strike, option type and trading session;
   - report missing periods rather than silently filling them.

7. **Execution**
   - use observed bid for sell executions and observed ask for buy executions when applicable;
   - define partial-fill and unavailable-quote behavior;
   - preserve deterministic rules.

8. **Cost model**
   - combine fill price with date-specific brokerage, STT, exchange charges, GST, stamp duty, SEBI/IPFT and applicable Paytm Money schedule.

9. **Independent audit**
   - produce machine-readable audit output;
   - retain rejected records and rejection reasons;
   - run the same validator on every candidate.

## 5. Critical prohibition

Do **not** convert:

`close -> assumed bid/ask`

or

`close -> midpoint`

and call the result historical execution quality.

If historical bid/ask cannot be observed or deterministically reconstructed, G9 remains blocked.

## 6. Recommended acquisition order

### Priority 1 — salvage `antony9952/Nifty_option_TBT`

Inspect the raw repository files independently of the Hugging Face viewer.

Deliverables:

- file inventory;
- schema classes;
- per-file date ranges;
- per-file bid/ask row counts;
- NIFTY option contract counts;
- coverage heatmap;
- raw-file hashes;
- license/provenance;
- incompatibility report.

### Priority 2 — investigate `ayyararyan/nse-options-pipeline`

Search:

- releases;
- Git LFS;
- branches;
- linked storage;
- archived files;
- author references.

If data can be obtained, subject it to the common G9 validator.

### Priority 3 — inspect OptionVault/TickBytes public samples

Use these to establish:

- field semantics;
- depth conventions;
- timestamp semantics;
- contract identifiers;
- whether historical archive links exist.

### Priority 4 — inspect other GitHub/Hugging Face public mirrors

Search for:

- NIFTY option bid/ask;
- NSE option TBT;
- NSE option L1;
- NSE option L2;
- option-chain snapshots with bid/ask;
- historical market-depth archives.

Every candidate must be pinned and independently validated.

### Priority 5 — NSE licensed Order & Trade

If the free-data routes fail full-period coverage or licensing/reproducibility requirements, proceed to the licensed NSE route.

Do not weaken the G9 acceptance standard merely to avoid acquisition cost.

## 7. Current gate state

- G1: PASS
- G2: PASS
- G3: PASS
- G4: independently PASS
- G5: OPEN/PRELIMINARY
- G6: OPEN
- G7: OPEN
- G8: OPEN
- **G9: BLOCKED**
- G10: OPEN
- G11: OPEN
- G12: independently PASS
- G13: BLOCKED
- G14: BLOCKED
- Phase 2: BLOCKED

## 8. Tester conclusion

The free-data search has **not produced a production-acceptable G9 dataset yet**, but it has produced several concrete leads worth exhausting before purchasing/licensing data.

The most important next technical action is **raw-file salvage and independent validation of `antony9952/Nifty_option_TBT`**, followed by investigation of the underlying archive associated with `ayyararyan/nse-options-pipeline`.

If neither provides complete, reproducible, legally usable historical quote coverage for the Phase 1 sample, the developer should proceed to the NSE historical F&O Order & Trade acquisition route.

**No Phase 2 work is authorized by this report.**
