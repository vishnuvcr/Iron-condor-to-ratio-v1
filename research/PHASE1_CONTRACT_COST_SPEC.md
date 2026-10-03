# Phase 1 — Historical Contract and Cost Specification

Updated: 2026-10-03

## Purpose

Define the machine-readable effective-date controls required for G8 and G10. Source identification alone does not close either gate.

## G8 — NIFTY contract metadata

Each contract-master record must include:

- `instrument`
- `symbol`
- `option_type`
- `strike`
- `expiry`
- `contract_start`
- `contract_end`
- `lot_size`
- `tick_size`
- `expiry_rule`
- `source_reference`
- `source_effective_date`

### Known effective-date changes

1. NSE Circular 128/2024 changed NIFTY lot size from 25 to 75 for **new index derivatives introduced from 20 November 2024**. Existing contracts are not retroactively rewritten by this statement. [NSE Circular 128/2024](https://nsearchives.nseindia.com/content/circulars/FAOP64625.pdf).
2. NSE Circular 33/2025 revised NIFTY expiry to Monday effective 4 April 2025, with existing-contract treatment specified in the circular. [NSE Circular 33/2025](https://nsearchives.nseindia.com/content/circulars/FAOP66938.pdf).
3. NSE Circular 111/2025 subsequently revised NIFTY weekly/monthly/quarterly/half-yearly expiry to Tuesday, with explicit transition treatment for existing and long-dated contracts. [NSE Circular 111/2025](https://nsearchives.nseindia.com/content/circulars/FAOP68747.pdf).
4. NSE Circular 176/2025 revised NIFTY lot size from 75 to 65, effective 28 October 2025 EOD, with weekly/monthly and quarterly/half-yearly transition treatment. [NSE Circular 176/2025](https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf).

Therefore, the backtest must use the actual historical contract file/expiry for each contract rather than deriving expiry from today's weekday rule.

## G10 — Paytm Money and statutory transaction costs

Each charge schedule must be date-indexed and contain:

- `effective_from`
- `effective_to`
- `charge_type`
- `rate_or_amount`
- `base`
- `per_order_or_per_contract`
- `brokerage_cohort_rule`
- `source_reference`
- `source_hash`

### Paytm Money source facts already verified

- From 25 August 2023, new Paytm Money users were charged ₹20 per executed Stock Delivery/Intraday/F&O order; existing cohorts retained their applicable historical rates. [Paytm Money, 25 Aug 2023](https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/).
- From 15 January 2025, Paytm Money stated that brokerage would be flat ₹20 across segments. [Paytm Money, 18 Dec 2024](https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/).
- From 1 October 2024, option-sale STT increased from 0.0625% to 0.1%, according to Paytm Money's pricing update citing the exchange mandate. [Paytm Money, Oct 2024](https://www.paytmmoney.com/blog/paytm-money-pricing-update-revised-charges-effective-1st-october/).

These facts are not the complete cost schedule.

## Required charge components

The production ledger must model, as applicable to each dated trade:

- Paytm Money brokerage;
- STT;
- NSE transaction charges;
- IPFT;
- SEBI charges;
- GST;
- stamp duty;
- applicable clearing/regulatory charges.

No charge may be applied retrospectively using today's rate.

## Cost acceptance tests

- Every executed leg maps to exactly one brokerage rule.
- Brokerage cohort is an explicit input; the study must state the selected cohort assumption.
- Every sale/purchase maps to the correct STT base and dated rate.
- GST is applied only to the taxable service components defined by the contemporaneous schedule.
- No component is double counted.
- Zero-cost and boundary cases have deterministic unit tests.
- All schedules have provenance and effective dates.

## 2026-10-03 evidence update

The historical contract rule map now includes the 2024 lot-size increase, the April 2025 Monday-expiry transition, the June/July 2025 Tuesday-expiry transition, and the October 2025 lot-size revision. Production acceptance still requires the actual effective-date contract master and one-to-one reconciliation of every acquired option contract.

## Current evidence status

**OPEN.** The major historical brokerage/STT transition points are sourced, but the complete date-aligned statutory/exchange/Paytm Money schedule is not yet assembled and executed.
