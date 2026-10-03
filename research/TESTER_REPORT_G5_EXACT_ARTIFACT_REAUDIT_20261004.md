# Independent Tester Report — G5 Exact-Tip Artifact Re-audit

**Date:** 2026-10-04  
**Role:** Independent Tester  
**Scope:** G5 exact-tip artifact verification and assessment of the proposed date/session characterization correction.

## Determination

**G5: FAIL / OPEN.**

The independently inspectable G5 exact-tip CI evidence is substantive and reproducible. The reported **521,069** decision-eligible option rows without an exact NIFTY timestamp and the **99.3296229%** exact alignment fraction are confirmed from the retained artifact and its expiry/day decomposition.

The proposed next correction — characterize the unmatched observations by **trading date and session before changing any acceptance rule** — is appropriate and required.

**No G5 acceptance-rule relaxation is approved.** The frozen requirement remains 100% exact timestamp alignment for decision-eligible option observations.

**G6: OPEN. G13/G14: BLOCKED. Phase 2: BLOCKED.**

## Exact evidence independently verified

| Item | Verified value |
|---|---|
| Repository | `vishnuvcr/Iron-condor-to-ratio-v1` |
| Checkout commit | `db668dd2b89bf691a6481affb3cb2a9060c5fe98` |
| Workflow run | `37148487963` |
| Job | `111277213347` |
| Job result | failure at substantive G5 alignment audit |
| Artifact | `11284131045` |
| Artifact name | `phase1-g5-alignment-report` |
| Artifact SHA-256 | `30381036630380820693858817bea51eb98cf09dba61fd95fb` |
| Raw option rows | 108,139,447 |
| Decision-eligible option rows | 77,727,743 |
| Decision-eligible rows with exact NIFTY timestamp | 77,206,674 |
| Missing exact alignments | **521,069** |
| Exact alignment | **99.3296229%** |
| Invalid option timestamps | 0 |
| Duplicate NIFTY timestamps | 0 |
| NIFTY index rows | 486,050 |
| Eligible NIFTY timestamps | 471,541 |

The artifact ZIP digest was independently recomputed from the downloaded workflow artifact and matched the GitHub-reported SHA-256.

The arithmetic is internally exact:

`77,727,743 - 77,206,674 = 521,069`.

The expiry/day coverage table also reconciles exactly to the top-level totals:

- decision-eligible rows: 77,727,743
- exact-aligned rows: 77,206,674
- missing rows: 521,069

Therefore the failure is not a reporting-rounding artifact.

## Missing-row concentration by date

The key diagnostic finding is that the missing rows are highly concentrated in a small number of complete date failures.

There are **14 dates** with decision-eligible option observations but **zero** exact NIFTY alignment. Those dates account for:

- **487,593 of 521,069 missing rows = 93.5755% of all missing rows**
- 487,593 rows are **0.6273% of all decision-eligible option rows**

The 14 complete-miss dates are:

| Date | Missing decision-eligible rows |
|---|---:|
| 2021-05-07 | 21,421 |
| 2021-05-10 | 22,272 |
| 2021-05-11 | 22,429 |
| 2021-05-12 | 23,554 |
| 2021-05-14 | 92 |
| 2021-05-17 | 25,814 |
| 2021-05-18 | 28,042 |
| 2021-05-19 | 25,530 |
| 2021-05-20 | 27,310 |
| 2021-05-21 | 28,971 |
| 2025-10-10 | 39,273 |
| 2026-05-25 | 88,111 |
| 2026-05-26 | 91,085 |
| 2026-05-29 | 43,689 |

The remaining **33,476** missing rows occur across 348 partial-miss dates.

This pattern is not consistent with treating the whole failure as ordinary sparse/far-strike option coverage. Most of the missing rows are entire trading-date gaps in the underlying timestamp grid.

## Cross-check against the independently audited G4 evidence

The earlier independently verified G4 artifact reports the NIFTY index file as:

- 486,050 rows
- SHA-256 `613864738250107807354c17c7092986960220ac3062b830c65cc5f9ec16fcf7`
- minimum timestamp `2021-05-24 03:37:00+00:00`
- maximum timestamp `2026-07-02 10:00:00+00:00`

Comparing the option-observed dates with the independently audited NIFTY observed-date set shows that the same 14 dates above are **option-observed but NIFTY-unobserved** dates.

This establishes two different classes that must not be conflated:

### 1. 2021-05-07 through 2021-05-21

These occur before the NIFTY index file's observed start on 2021-05-24. They are therefore consistent with an underlying-source coverage boundary in the current pinned NIFTY file.

### 2. 2025-10-10, 2026-05-25, 2026-05-26, 2026-05-29

These are later study-window dates that are absent from the NIFTY file but are not listed in the current Phase 1 session manifest as controlled data-gap dates or special-session exclusions. They therefore remain **unexplained underlying/index coverage gaps or source-extraction defects** until directly reconciled against an independent historical NIFTY source.

They must not be silently reclassified as holidays, deleted, interpolated, nearest-matched, or forward-filled.

## Session classification assessment

The current G5 validator correctly separates:

1. date/session eligibility of the option timestamp; and
2. exact timestamp membership in the NIFTY timestamp grid.

That separation is necessary and should be retained.

The current manifest already contains explicit special sessions and a pre-registered 2026-06-03 data-gap exclusion. None of the 14 complete-miss dates is one of those controls.

Therefore the next diagnostic should classify each missing date/timestamp into an explicit evidence-backed category:

- `INDEX_SOURCE_BOUNDARY`
- `INDEX_SOURCE_FULL_DATE_GAP`
- `INDEX_INTRADAY_GAP`
- `SESSION_CONTROLLED`
- `OPTION_TIMESTAMP_IRREGULARITY`
- `CROSS_FILE_DUPLICATE_OR_PARTITION_EFFECT`
- `UNRECONCILED`

No category should be assigned solely from absence of an exact NIFTY match.

## Validator/code assessment

The existing G5 acceptance logic is correctly fail-closed at 100% exact alignment.

One reporting semantics issue should be corrected during the diagnostic hardening: the expiry/day report fields named `decision_timestamps` and `aligned_decision_timestamps` are actually **row counts**, not unique timestamp counts. The arithmetic itself is correct, but the field names can mislead an auditor. The diagnostic output should explicitly expose:

- decision-eligible option rows
- aligned decision-eligible option rows
- missing decision-eligible option rows
- unique missing timestamps
- whether a NIFTY observed date exists
- NIFTY eligible timestamp count for that date
- option observed min/max timestamp
- NIFTY observed min/max timestamp for that date
- previous/next NIFTY timestamp around representative missing timestamps

This is a control-quality correction, not a justification to relax the G5 rule.

## Assessment of the proposed failure-isolation correction

The developer's failure-isolation direction is appropriate.

In particular, the diagnostic should:

- reproduce the frozen 521,069-row failure from the pinned source;
- report missing counts by date and timestamp;
- compare option and NIFTY within-day coverage;
- identify complete-date versus partial-intraday gaps;
- examine seconds/microseconds and minute-grid behavior;
- inspect all option parquet timestamp ranges for overlap;
- verify expiry/file partition consistency;
- check whether missing timestamps occur outside the NIFTY observed intraday span;
- independently verify session classification;
- preserve the 100% exact-timestamp acceptance rule.

The diagnostic branch must remain **non-accepting**. It should produce evidence for classification, not a new pass rule.

## External session-calendar cross-check

Official NSE F&O holiday materials do not support treating the four later unexplained dates as scheduled F&O holidays. The 2025 NSE F&O holiday list contains October holidays on 2 October, 21 October and 22 October, while the NSE settlement schedule contains a trade-date entry for 10 October 2025. The 2026 F&O holiday list includes 28 May but not 25 May, 26 May or 29 May.

Accordingly, those four dates require source-level reconciliation rather than automatic holiday exclusion.

## Gate decision

| Gate | Tester determination |
|---|---|
| G5 | **FAIL / OPEN** |
| G6 | **OPEN** |
| G7 | OPEN |
| G8 | OPEN |
| G9 | PASS under previously independently approved proxy methodology |
| G10 | OPEN |
| G11 | OPEN |
| G13 | **BLOCKED** |
| G14 | **BLOCKED** |
| Phase 2 | **BLOCKED** |

No performance result, backtest result, profitability claim, optimization, or trading-strategy conclusion is authorized by this report.

## Required next evidence

Before any G5 acceptance-rule change is considered, the next exact-tip diagnostic must provide:

1. the complete set of affected dates;
2. a date/session classification with independent evidence;
3. explicit separation of full-date and partial-intraday gaps;
4. exact option/NIFTY neighbor timestamps for representative failures;
5. confirmation that all 14 complete-miss dates are option-observed/NIFTY-unobserved;
6. reconciliation of the four later unexplained dates against an independent NIFTY/index source;
7. confirmation that no interpolation, nearest matching, forward filling, or silent deletion is used;
8. an updated machine-readable artifact tied to the exact checkout SHA.

Only after that evidence exists should the tester reassess whether the current 100% rule can be satisfied by correcting the data/source or whether a **pre-registered research-methodology change** is scientifically justified. Any such methodology change would require an explicit plan/specification update and independent tester re-review; it must not be introduced merely to make the current dataset pass.

## Conclusion

The reported G5 failure is genuine. The 521,069 missing exact alignments and 99.3296229% alignment rate are independently verified, and the expiry/day decomposition reconciles exactly.

The proposed date/session characterization is therefore the correct next diagnostic step. The current evidence does **not** justify relaxing the 100% exact-timestamp criterion.

G5 remains FAIL/OPEN, G6 remains OPEN, and G13/G14/Phase 2 remain BLOCKED.
