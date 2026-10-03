# Paytm Money / Statutory Cost Source Register

Phase 1 records source documents first. Numerical cost application is deferred to the exact backtest date and account-cohort mapping.

## Paytm Money brokerage
- Paytm Money's August 2023 announcement states that new users from 25 August 2023 were charged ₹20 per executed order for F&O, while earlier user cohorts retained older brokerage schedules.
- Paytm Money's January 2025 update states a flat ₹20 brokerage across segments effective 15 January 2025.
- Paytm Money's October 2024 update records the statutory STT change on option sales from 0.0625% to 0.1% effective 1 October 2024.

## Exchange / regulatory charges
- NSE transaction charges changed effective 1 April 2023 and again effective 1 October 2024; the cost engine must map the trade date to the applicable schedule.
- NSE announced another transaction-charge revision effective 1 March 2026.
- SEBI turnover/regulatory charges are also date-dependent and must be sourced from the applicable rule/circular.

## Cost-engine rule
Every executed option leg receives a dated cost record for brokerage, STT where applicable, NSE transaction/IPFT charges, SEBI turnover fee, GST, stamp duty and any other applicable documented charge. Do not double-count exchange/IPFT components when a "true to label" schedule already combines them.

## Source URLs
- https://www.paytmmoney.com/blog/brokerage-charges-increase-from-25th-aug-23-existing-users-will-continue-on-old-brokerage-charges/
- https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/
- https://www.paytmmoney.com/blog/paytm-money-pricing-update-revised-charges-effective-1st-october/
- https://archives.nseindia.com/content/circulars/FA56129.pdf
- https://nsearchives.nseindia.com/content/circulars/FA64232.pdf
- https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
- https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
