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