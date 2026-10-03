# Phase 1 — G5–G11 Source Audit and Production-Gate Progress

Updated: 2026-10-03

## Scope

This is a substantive Phase 1 evidence step after E055 closure. It does not authorize Phase 2 and does not by itself close any production gate. Source identification is separated from production-data acceptance.

## G5 — Underlying/option alignment

Existing independently verified Run #55 evidence provides the current diagnostic alignment baseline:

- 77,776,166 option rows after deterministic key deduplication.
- 77,228,081 option rows matched to NIFTY timestamps.
- Diagnostic match fraction: 0.9929530468241389.
- NIFTY index rows: 486,050.
- 1,262 observed trading dates.

This remains **PRELIMINARY / OPEN** because production acceptance additionally requires decision-time coverage, explicit missing-index handling, duplicate-key controls, and leg/expiry/date coverage on the production dataset.

## G6 — Production historical Greeks / IV

Official RBI evidence confirms that the 91-day Treasury Bill Primary Yield is published in the Weekly Statistical Supplement. RBI WSS pages expose the series directly, while RBI Treasury-bill auction/bulletin material provides primary-market yield observations. Examples reviewed include WSS observations and 2025 auction results. [RBI WSS](https://www.rbi.org.in/scripts/WSSView.aspx?Id=26962), [RBI WSS](https://www.rbi.org.in/scripts/WSSView.aspx?Id=27637), [RBI WSS](https://www.rbi.org.in/Scripts/WSSView.aspx?Id=27727), [RBI Bulletin](https://www.rbi.org.in/Scripts/BS_ViewBulletin.aspx?Id=23288).

NSE's NIFTY underlying-information page identifies daily NIFTY P/E and annual dividend-yield information, and the project already identifies NSE historical index/context data as the candidate source for the dividend-yield side. [NSE NIFTY underlying information](https://www.nseindia.com/static/products-services/equity-derivatives-underlying-information-nifty-50).

**Gate status: OPEN.** The complete date-aligned machine-readable r/q series has not yet been assembled, and production IV/Greek solver validation against the frozen Phase 0 tolerances remains outstanding. No diagnostic Black-Scholes output is promoted to production Greek evidence.

## G7 — Target-delta availability

NSE states that India VIX itself is calculated from best bid/ask NIFTY option prices, demonstrating the exchange's quote-based volatility framework. [NSE India VIX](https://www.nseindia.com/static/products-services/indices-indiavix-index).

However, the study's target-delta availability requires every strategy decision timestamp to have an eligible contract satisfying the frozen delta tolerance plus liquidity/quote-quality rules. That cannot be established from the current OHLCV/OI-only primary archive.

**Gate status: OPEN.** G7 remains dependent on G6 and G9-quality execution/quote data.

## G8 — Historical contract metadata

Verified NSE effective-date controls now include:

1. NIFTY lot size 25 → 75 for new index derivatives introduced from 20-Nov-2024 under Circular 128/2024. [NSE Circular 128/2024](https://nsearchives.nseindia.com/content/circulars/FAOP64625.pdf).
2. NIFTY weekly/monthly/quarterly/half-yearly expiries moved to Monday under Circular 33/2025, effective 04-Apr-2025, with explicit treatment of already introduced contracts. [NSE Circular 33/2025](https://nsearchives.nseindia.com/content/circulars/FAOP66938.pdf).
3. NSE subsequently revised NIFTY expiry to Tuesday under Circular 111/2025, with newly generated contracts from 26-Jun-2025 EOD and explicit long-dated transition rules. [NSE Circular 111/2025](https://nsearchives.nseindia.com/content/circulars/FAOP68747.pdf).
4. Circular 176/2025 revised NIFTY lot size 75 → 65, effective 28-Oct-2025 EOD, with different transition dates for weekly/monthly versus quarterly/half-yearly contracts. [NSE Circular 176/2025](https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf).

NSE's contract-information page also exposes a current permitted-lot-size CSV, but current files cannot be projected backward. [NSE Contract Information](https://www.nseindia.com/static/products-services/equity-derivatives-contract-information).

**Gate status: OPEN.** These source facts materially advance the historical rule map, but the production gate still requires a machine-readable effective-date contract master and one-to-one reconciliation of every source contract to its historical rule set.

## G9 — Historical bid/ask / execution quality

The official NSE historical-data service confirms that Historical Order & Trade data are available for F&O and that the service is subscription-controlled. NSE states that historical Order & Trade data are available from January 2008 for F&O and describes separate F&O sample/specification downloads. [NSE Paid EOD/Historical Data](https://betanseapi.nseindia.com/static/market-data/eod-historical-data-subscription).

NSE's current historical Order & Trade specification documents chronological FAO data-format changes, including the F&O trade-number change effective 07-Sep-2020 and the order-file limit-price-indicator change effective 16-Dec-2021 in the published specification version reviewed. [NSE Historical Order & Trade Specification](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Hist_Order_Trade_Data_1.15.pdf).

NSE's published data-availability material states that historical Order & Trade data cover CM, F&O and CD from January 2008 onward, and NSE Data & Analytics documents Level 1 best bid/ask availability for F&O. [NSE FPI data-availability FAQ](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FPI%20FAQs_Brochure.pdf).

The published tariff confirms that the F&O historical Order & Trade product is a paid data product. [NSE Historical Order & Trade tariff](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Download%20Other%20Products%20Tariff%20%28Effective%20April%2001%202024%29_8.pdf).

**Gate status: BLOCKED.** The route is now better specified and technically validated at the source/specification level, but the licensed F&O files have not been acquired into the repository and no deterministic reconstruction has been executed. Close-price substitution remains prohibited.

## G10 — Date-specific transaction costs

Paytm Money's historical brokerage chronology confirms user-cohort-dependent pricing from 25-Aug-2023, while its October 2024 update documents the option-sale STT increase from 0.0625% to 0.1% effective 01-Oct-2024. [Paytm Money Aug-2023](https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/), [Paytm Money Oct-2024](https://www.paytmmoney.com/blog/paytm-money-pricing-update-revised-charges-effective-1st-october/).

Paytm Money also states that brokerage for F&O is charged per unique executed order on its F&O FAQ, and its brokerage calculator warns that platform fees, depository charges, auto-square-off charges and other fees are outside the calculator. [Paytm Money F&O FAQ](https://www.paytmmoney.com/stocks/customer/fno-faq/onboarding-and-kyc/account-segment-activation/how-to-activate-fo-from-mobile-app-web), [Paytm Money Brokerage Calculator](https://www.paytmmoney.com/stocks/brokerage-calculator).

**Gate status: OPEN.** A complete date-indexed schedule still needs exchange transaction charges, IPFT, SEBI fees, GST bases, stamp duty, applicable clearing/regulatory charges, and explicit brokerage-cohort assumptions. No current rate will be back-applied to historical trades.

## G11 — Market-context datasets

The minimum context package is now source-verified at the provider level:

- NIFTY historical index data: [NSE Historical Index Data](https://www.nseindia.com/reports-indices-historical-index-data).
- India VIX historical data and methodology: [NSE India VIX](https://www.nseindia.com/static/products-services/indices-indiavix-index) and [Historical India VIX](https://www.nseindia.com/reports-indices-historical-vix).
- FII/FPI and DII daily activity: [NSE FII/FPI & DII](https://www.nseindia.com/reports/fii-dii).
- GIFT NIFTY / overnight global-crossing context: [NSE IX](https://www.nseix.com/) and its historical NLT/Block Trade interface [NSE IX Historical NLT](https://www.nseix.com/markets/historical-nlt).
- BSE historical market/corporate context remains a registered source in the project control manifest and requires procurement/access validation before use.
- Corporate actions/events remain sourced from NSE corporate filings/actions and must be aligned by event date rather than used as look-ahead variables.

**Gate status: OPEN.** Provider/source coverage is now materially documented, but the full date-aligned context package has not yet been assembled and leakage controls have not yet been executed.

## Current Phase 1 decision

| Gate | Status | This step accomplished |
|---|---|---|
| G5 | PRELIMINARY / OPEN | Existing exact-run alignment evidence retained; production decision-time coverage specification sharpened |
| G6 | OPEN | RBI 91-day primary-yield source and NIFTY dividend-yield candidate re-verified |
| G7 | OPEN | Quote-based target-delta requirement explicitly tied to production quote quality |
| G8 | OPEN | Effective-date lot-size/expiry transitions expanded and sourced through 2025 |
| G9 | BLOCKED | Official F&O Historical Order & Trade procurement route and schema/tariff evidence strengthened |
| G10 | OPEN | Paytm cohort/STT evidence and missing charge components explicitly documented |
| G11 | OPEN | NIFTY/VIX/FII-DII/GIFT NIFTY/BSE/event source package documented |

**No Phase 2 work is authorized by this evidence step.**

## G9 candidate update — public TBT bid/ask dataset

A new Hugging Face candidate, `antony9952/Nifty_option_TBT`, exposes bid/ask/depth fields in its published preview. The dataset builder currently reports incompatible schemas across files, so the candidate is **not accepted**. The repository now contains an automated cached CI audit workflow to inspect raw CSV schemas, bid/ask presence and observed coverage. G9 remains BLOCKED pending successful validation and contract reconciliation.


## G5 dedicated acceptance implementation — 2026-10-03

A dedicated G5 production-evidence path is now implemented. `research/PHASE1_G5_ALIGNMENT_SPEC.md` freezes the acceptance rule, `scripts/phase1_g5_alignment_audit.py` performs the full-source audit, and `.github/workflows/phase1-g5-alignment.yml` provides automatic push/PR execution plus manual dispatch and cache reuse.

The validator deliberately separates two predicates:
1. whether an option timestamp is inside the date-specific strategy execution interval; and
2. whether that exact timestamp exists in the NIFTY underlying grid.

This separation prevents a tautological alignment test. G5 remains OPEN until exact-head CI produces the machine-readable report and an independent tester reviews it.
