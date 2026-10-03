# G5 Failure-Isolation External Reconciliation — 2026-10-04

## Scope

This is a non-accepting external reconciliation of the four later full-date G5 underlying gaps identified from the immutable G4/G5 artifacts. It does not alter the G5 acceptance rule.

Frozen G5 evidence:
- checkout: db668dd2b89bf691a6481affb3cb2a9060c5fe98
- run: 37148487963; job: 111277213347; artifact: 11284131045
- artifact SHA-256: 30381036630380820693858817bea51eb98cf09dba61fd95fb
- decision-eligible option rows: 77,727,743
- exact NIFTY matches: 77,206,674
- missing exact matches: 521,069
- exact alignment: 99.3296229%

## Date-level finding

Fourteen affected dates contain option observations but no NIFTY observed date in the independently accepted G4 reconciliation. They account for 487,593 / 521,069 = 93.5755% of missing rows:

- 2021-05-07, 2021-05-10, 2021-05-11, 2021-05-12, 2021-05-14, 2021-05-17, 2021-05-18, 2021-05-19, 2021-05-20, 2021-05-21
- 2025-10-10, 2026-05-25, 2026-05-26, 2026-05-29

The first ten dates precede the independently audited NIFTY source start of 2021-05-24 and are therefore consistent with a source-coverage boundary. They remain source-coverage failures and are not repaired or excluded by G5.

## Independent reconciliation of later dates

### 2025-10-10
NSE's official 2025 F&O holiday circular lists October 2, October 21 (Muhurat), and October 22 as the October 2025 F&O holidays; October 10 is not listed. Therefore 2025-10-10 must not be labelled an NSE F&O holiday. The same date is independently reported as a NIFTY 50 trading day (close 25,285.35). [NSE holiday circular: turn0search40; independent market data: turn3search4, turn3search7]

Classification: unexplained underlying/index-source gap in the primary dataset; not an exchange-holiday exclusion.

### 2026-05-25
NSE's official 2026 F&O holiday circular lists May 28 as the May holiday, not May 25. Independent historical NIFTY data show a 25-May-2026 observation (close 24,031.70). [NSE holiday circular: turn1search2; independent history: turn3search0, turn3search1]

Classification: unexplained underlying/index-source gap; not an exchange-holiday exclusion.

### 2026-05-26
The official 2026 F&O holiday circular lists May 28, not May 26, as the May holiday. Independent historical NIFTY data show a 26-May-2026 observation (close 23,913.70). [NSE holiday circular: turn1search2; independent history: turn3search0, turn3search1]

Classification: unexplained underlying/index-source gap; not an exchange-holiday exclusion.

### 2026-05-29
The official 2026 F&O holiday circular lists May 28 and does not list May 29. Independent historical NIFTY data show a 29-May-2026 observation (close 23,547.75), and NSE pages also display 29-May-2026 NIFTY values. [NSE holiday circular: turn1search2; independent history: turn3search0, turn3search1; NSE page: turn0search8]

Classification: unexplained underlying/index-source gap; not an exchange-holiday exclusion.

## Consequence for G5

The four later dates are not supported as holiday exclusions. The correct interpretation is date-level coverage gaps in the primary NIFTY file relative to independently corroborated market-calendar/index history.

No nearest-minute matching, interpolation, forward-fill, deletion, or relaxation of the 100% exact-timestamp threshold is authorized.

The remaining 33,476 failures across 348 dates with some NIFTY observations still require raw timestamp-level diagnosis.

## Diagnostic terminology correction

The failure-isolation output must distinguish:
- decision_eligible_row_count
- aligned_row_count
- missing_row_count
- unique_decision_timestamps
- unique_aligned_timestamps
- unique_missing_timestamps

Any legacy decision_timestamps/aligned_decision_timestamps fields that contain row counts must be renamed or explicitly documented as row counts. This is a diagnostic semantics correction only.

## Next required CI diagnostic

Reproduce the 521,069 missing rows from the pinned source and classify all affected dates/timestamps by full-date underlying gap, partial intraday gap, option timestamp irregularity, session-rule classification, option partition/range overlap/global-key duplicate risk, and broader source discontinuity.

G5 remains FAIL / OPEN until exact timestamp alignment is 100% under the frozen acceptance rule and the independent tester approves the resulting evidence.

# G5 Failure-Isolation External Reconciliation — 2026-10-04

## Scope

This is a non-accepting external reconciliation of the G5 underlying/index timestamp failures. It does not alter the G5 acceptance rule.

## Frozen failing evidence

- Developer/tester frozen checkout: `db668dd2b89bf691a6481affb3cb2a9060c5fe98`
- Run: `37148487963`; job: `111277213347`; artifact: `11284131045`
- Frozen artifact SHA-256: `30381036630380820693858817bea51eb98cf09dba61fd95fb`
- Decision-eligible option rows: **77,727,743**
- Exact NIFTY matches: **77,206,674**
- Missing exact matches: **521,069**
- Exact alignment: **99.3296229%**

## Immutable-tip reproduction

Corrected failure-isolation CI run:

- Run: `37154986733`
- Job: `111296435573`
- Checkout/head: `ee3ab7f2b08f79faa0f15d756aab2379136cefa9`
- Job conclusion: **success**
- Diagnostic artifact: `11285517033`
- Artifact SHA-256: `292c823060e87e5cf8ff72e5b08fc9662b8adc4c0ef10eacb87207f3ac8cc498`

The artifact records its runtime checkout as exactly `ee3ab7f2b08f79faa0f15d756aab2379136cefa9`. It independently recomputes **521,069** missing rows, exactly matching the frozen failed evidence. Thus the substantive failure is reproducible at the immutable developer diagnostic tip.

## Date-level concentration

The diagnostic reports **362 affected dates**. The previously identified 14 full-date underlying gaps remain present and account for **487,593 / 521,069 = 93.5755%** of missing rows:

- 2021-05-07, 2021-05-10, 2021-05-11, 2021-05-12, 2021-05-14, 2021-05-17, 2021-05-18, 2021-05-19, 2021-05-20, 2021-05-21
- 2025-10-10, 2026-05-25, 2026-05-26, 2026-05-29

The first ten dates precede the independently audited NIFTY source start of 2021-05-24 and remain source-coverage failures; they are not silently excluded.

The four later dates are not supported as exchange holidays by the previously reconciled NSE calendars and independent NIFTY observations. They therefore remain unexplained primary-source coverage gaps rather than holiday exclusions.

## Timestamp-level findings

The immutable diagnostic reports row-level and unique-timestamp counts separately. For the four later dates:

- 2025-10-10: 39,273 missing rows / 376 unique missing timestamps
- 2026-05-25: 88,111 / 752
- 2026-05-26: 91,085 / 752
- 2026-05-29: 43,689 / 375

The largest missing-timestamp frequencies cluster on the two 2026 full-date gaps, consistent with broad underlying absence rather than a single isolated option timestamp.

The diagnostic does **not** interpolate, nearest-match, forward-fill, delete, or relax the exact timestamp rule.

## Option partition/range finding

All inspected option files have a single expiry value matching their filename. However, the diagnostic reports **238 overlapping option-file timestamp ranges**. Therefore timestamp-range separation alone cannot establish global cross-file duplicate absence.

This is a diagnostic finding, not a duplicate conclusion. A global key-level audit across all NIFTY option files is required before using partition boundaries as evidence of unique observations.

## Diagnostic terminology

The diagnostic explicitly distinguishes:

- missing row count
- unique missing timestamp count
- row-level evidence from timestamp-level evidence

Legacy `decision_timestamps` / `aligned_decision_timestamps` fields are not emitted by this diagnostic and must not be interpreted as unique-timestamp counts.

## Remaining unresolved population

After the 14 full-date gaps, **33,476 missing rows across 348 dates** remain for timestamp-level characterization. These dates have at least some NIFTY observations, so their mechanism cannot be inferred from date absence alone.

Required next diagnostic work:

1. classify each remaining timestamp by NIFTY previous/next observation distance;
2. quantify session-position and timestamp-second/microsecond irregularities;
3. perform a global option-key duplicate audit across overlapping files;
4. separate underlying intraday gaps from option-side timestamp irregularity;
5. preserve all raw failures rather than excluding them.

## Gate consequence

**G5 remains FAIL / OPEN.**

The 100% exact timestamp-alignment acceptance rule remains frozen. No Phase 2/backtest/optimization/profitability/trading-strategy conclusion is authorized until the remaining Phase 1 gates are independently approved.
