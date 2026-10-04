# Phase 2 Historical NIFTY Contract-Master Provenance

Updated: 2026-10-04

## Reconstruction basis

The production workflow reconstructs the monthly-contract master actually used by this study from the pinned NIFTY 1-minute option partitions and official NSE market-lot chronology.

The reconstruction is intentionally narrower than a full exchange member contract file: weekly and non-monthly contracts are excluded because the literal research strategy selects one monthly expiry per calendar month.

## Official NSE chronology

| Monthly contract interval | Lot size | Basis |
|---|---:|---|
| Jan–Jun 2021 | 75 | NSE FAOP47854 transition from 75 to 50 begins with July 2021 monthly expiry |
| Jul 2021–Apr 2024 | 50 | NSE FAOP47854 |
| May–Nov 2024 | 25 | NSE FAOP61415: revised NIFTY lot begins with May 30, 2024 monthly expiry |
| Dec 2024–Dec 2025 | 75 | NSE FAOP64625: new contracts from Nov 20, 2024; existing Nov monthly remains old lot, subsequent monthly contracts are 75 |
| Jan–Sep 2026 | 65 | NSE FAOP70616: 65 becomes effective for new contracts; existing weekly/monthly retain 75 through Dec 30, 2025 |

## Tick size

NIFTY index-option tick size is 0.05 in the exchange specification. The reconstruction retains this as a source-derived contract parameter and validates it as positive and constant.

## Lifecycle reconstruction

For each monthly option contract:
- contract_start = first observed timestamp in the pinned source;
- contract_end = one minute after the last observed timestamp;
- expiry_close_ts = latest observed timestamp on the contract's expiry date;
- contract_id = expiry + strike + option type;
- lot size = official monthly lot-size chronology above;
- source provenance = official NSE circular references plus immutable raw-source checksums.

The validator fails closed if an expiry has no expiry-day observation, if identifiers duplicate, if lifecycle intervals are invalid, or if provenance is missing.

## Important limitation

This is a deterministic historical-contract reconstruction, not a claim that the original member-level NSE contract file bytes have been recovered for every historical date. The final manuscript must use the precise wording "historical contract-master reconstruction" and disclose the distinction.

If an exact historical NSE contract file becomes available, it should be reconciled against this reconstruction before any final production acceptance.

## Official references

- NSE FAOP47854 — 2021 NIFTY lot revision.
- NSE FAOP61415 — 2024 NIFTY 50 lot revision.
- NSE FAOP64625 — November 2024 NIFTY lot revision.
- NSE FAOP70616 — October 2025 NIFTY lot revision.
- NSE current contract specification — index option price-step specification.

## Public source dataset

The pinned NIFTY option source is the Hugging Face thetrademarkk/india-index-options-1m revision 0f4800e. Its dataset documentation describes the NIFTY option partitions as options/NIFTY/{EXPIRY}.parquet and explicitly warns that option coverage is partial; this is why target-delta availability and contract reconciliation remain measured rather than assumed.
