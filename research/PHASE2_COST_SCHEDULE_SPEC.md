# Phase 2 — Date-Effective Cost Schedule Specification

Updated: 2026-10-04

## Purpose

The engine must model the actual dated cost regime without projecting current rates backward. Historical exchange-option transaction charges were slab-based before October 2024, so they are calculated from monthly premium turnover after the complete fill ledger is known. The monthly total is then allocated pro-rata across fills by premium turnover for reporting.

## Primary brokerage cohort

The first full-sample schedule uses the Paytm Money cohort that opened before 5 August 2022:

- ₹10 per executed F&O order before 5 August 2022.
- ₹15 per executed F&O order from 5 August 2022 until 15 January 2025 for legacy users in this cohort.
- ₹20 per executed order from 15 January 2025 onward.

This is a scenario assumption, not a claim about the user's account history. Alternative cohort schedules are required for sensitivity.

## Exchange transaction charges — NIFTY/NSE equity options

The schedule uses premium turnover:

| Effective period | Monthly premium slab | Transaction charge |
|---|---|---:|
| 2021-01-01 to 2023-03-31 | up to ₹3 crore | ₹2,500/month |
| 2021-01-01 to 2023-03-31 | ₹3–100 crore incremental | ₹53/lakh |
| 2021-01-01 to 2023-03-31 | ₹100–750 crore incremental | ₹50.50/lakh |
| 2021-01-01 to 2023-03-31 | ₹750–1,500 crore incremental | ₹45.50/lakh |
| 2021-01-01 to 2023-03-31 | ₹1,500–2,000 crore incremental | ₹40.50/lakh |
| 2021-01-01 to 2023-03-31 | above ₹2,000 crore incremental | ₹33/lakh |
| 2023-04-01 to 2024-03-31 | up to ₹3 crore | ₹2,500/month |
| 2023-04-01 to 2024-03-31 | ₹3–100 crore incremental | ₹50/lakh |
| 2023-04-01 to 2024-03-31 | ₹100–750 crore incremental | ₹47.50/lakh |
| 2023-04-01 to 2024-03-31 | ₹750–1,500 crore incremental | ₹42.50/lakh |
| 2023-04-01 to 2024-03-31 | ₹1,500–2,000 crore incremental | ₹37.50/lakh |
| 2023-04-01 to 2024-03-31 | above ₹2,000 crore incremental | ₹30/lakh |
| 2024-04-01 to 2024-09-30 | monthly slab | ₹2,500 + 49.50/47/42/37/29.50 per lakh increments |
| 2024-10-01 to 2026-02-28 | all turnover | ₹3,503/crore each side of premium turnover |
| 2026-03-01 onward | all turnover | ₹3,552.99/crore |

The 2024-10-01 regime is a true-to-label uniform MII charge. From 2026-03-01, NSE set transaction charges at ₹3,552.99/crore and IPFT at ₹0.01/crore, total ₹3,553/crore, each side.

Primary sources:
- NSE FA56129, 24-Mar-2023: https://nsearchives.nseindia.com/content/circulars/FA56129.pdf
- NSE FA61137, 24-Mar-2024: https://nsearchives.nseindia.com/content/circulars/FA61137.pdf
- NSE FA64232, 27-Sep-2024: https://nsearchives.nseindia.com/content/circulars/FA64232.pdf
- NSE FA73061, 27-Feb-2026: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf

## NSE IPFT contribution

| Effective period | Equity options IPFT |
|---|---:|
| 2021-01-01 to 2023-03-31 | ₹0.01/crore |
| 2023-04-01 to 2026-02-28 | ₹50/crore |
| 2026-03-01 onward | ₹0.01/crore |

IPFT is kept as a separate ledger component and is not folded into NSE transaction charges.

## STT

For options sold by the seller on premium:
- through 2023-03-31: 0.0625%;
- 2023-04-01 through 2026-03-31: 0.10%;
- from 2026-04-01: 0.15%.

Source register:
- NSE FATAX56235 / Finance Act 2023: https://nsearchives.nseindia.com/content/circulars/FATAX56235.pdf
- NSE FATAX63809 / Finance Act 2024: https://nsearchives.nseindia.com/content/circulars/FATAX63809.pdf
- NSE FATAX73524 / Finance Act 2026: https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf

The literal-core backtest closes before expiry and does not exercise options, so exercise-specific STT is not modeled.

## SEBI turnover fee

- 2021 through 2025-12-31: 0.00015% of option premium turnover.
- 2026 schedule: 0.00010% of equity-derivatives turnover, with the exact effective date of the amended fee schedule recorded in the source registry before final statistical release.

Sources:
- SEBI Payment of Fees schedule: https://www.sebi.gov.in/sebi_data/attachdocs/aug-2021/1628678904669.pdf
- SEBI 2026 fee schedule: https://www.sebi.gov.in/sebi_data/attachdocs/jan-2026/1767852346757.pdf

## Stamp duty

Equity options: 0.003% on the buyer.

Source:
https://www.nseindia.com/static/invest/first-time-investor-stamp-duty-charges-taxes

## GST

GST is currently configured at 18% on taxable broker/exchange service components. STT and stamp duty are not treated as taxable services. The exact taxable-component mapping is retained as a configurable input and must be reconciled with the contemporaneous Paytm Money invoice/pricing rules before final release.

## Paytm Money source registry

- 25-Aug-2023 cohort notice: https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/
- Flat ₹20 from 15-Jan-2025: https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/
- 01-Oct-2024 STT update: https://www.paytmmoney.com/blog/paytm-money-pricing-update-revised-charges-effective-1st-october/

## Cost-engine acceptance rules

1. No overlapping effective-date rules.
2. Every executed fill must resolve exactly one brokerage, IPFT, SEBI, STT, stamp-duty and exchange-transaction rule.
3. Monthly slab calculations must use only completed fill turnover, not future decision inputs.
4. Slab totals are exact; pro-rata per-fill allocation is reporting-only.
5. GST is computed after all taxable service components are known.
6. No current rate may be back-projected.
7. Missing/ambiguous rates fail closed.
8. All assumptions and source hashes are stored in the cost manifest.

## Status

The schedule is a production-ready research control candidate. Exact effective-date validation of the 2026 SEBI change and final Paytm Money taxable-component mapping remain mandatory before final manuscript acceptance.


## Modeling boundary — exchange slab scope

Historical NSE equity-option transaction charges before October 2024 are member-level monthly slab charges. The strategy-only backtest does not have the user's other account turnover, so the primary research model treats the strategy's own monthly option premium turnover as the billable turnover base.

This is an explicit **isolated-strategy account assumption**, not a claim about the user's full Paytm Money account. Sensitivity around this assumption will be reported in the final cost-robustness discussion. The monthly slab total is calculated from the complete strategy fill ledger for that month and allocated to individual fills pro-rata for audit reporting; the allocation does not change the total charge.

## Brokerage cohort boundary

The pinned primary schedule uses the Paytm Money pre-5-Aug-2022 legacy cohort. This is a scenario assumption because the user's actual account opening date is not part of the research dataset. The final manuscript must state that the brokerage result is cohort-specific.

## 2026 SEBI fee boundary

The 2026 SEBI fee schedule in the repository is a provisional effective-date control pending exact notification-effective-date reconciliation. The final production release must verify the effective date before treating the 2026-01-01 boundary as definitive.
