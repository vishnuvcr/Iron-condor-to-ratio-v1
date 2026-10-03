# Independent Tester Report — Phase 1 G4 Final-Head Re-audit

Date: 2026-10-03  
Role: Tester  
Developer head audited: `09c4c2e4b6bc569d42d4743fac5132ad0672f8d8`  
Workflow run: `37125656878`  
Job/check: `111210327724`  
Artifact: `11275311823`  
Artifact SHA-256: `754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c`

## Independent outcome

**PHASE 1: FAIL / IN PROGRESS**  
**G4: FAIL / OPEN — E046**  
**G12: PASS — independently verified for the exact final developer head**  
**G13: BLOCKED**  
**G14 / Phase 2: BLOCKED**

No Phase 2 engine, optimization, profitability analysis, or trading-strategy conclusion is authorized.

## 1. What was independently verified

The final developer branch `phase-1-data-acquisition-validation` currently points to `09c4c2e4b6bc569d42d4743fac5132ad0672f8d8`.

GitHub Actions run `37125656878` independently reports:

- head branch: `phase-1-data-acquisition-validation`
- head SHA: `09c4c2e4b6bc569d42d4743fac5132ad0672f8d8`
- status: completed
- conclusion: success
- job `111210327724`: completed / success
- the G4 reconciliation step executed successfully
- the validation artifact `11275311823` exists and is unexpired

The downloaded artifact SHA-256 independently recomputes to:

`754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c`

Therefore E045 is resolved and **G12 is independently PASS**.

The artifact reconciliation output independently reports:

- normal eligible dates: 1,254
- special sessions reconciled: 7
- data-gap exclusions: 1
- unreconciled rows: 0
- controlled anomaly classifications all matched their declared expectations

The seven special-session dates are present in the artifact, and their declared interval coverage checks passed for the observed rows.

The independent review also cross-checked key exchange timings against NSE primary material. For example, NSE documents 2024-03-02 F&O execution as 09:15–10:00 and 11:30–12:30, while the capital-market schedule includes adjacent observation windows. citeturn448733view0turn448733view1 NSE documents the 2025-10-21 F&O Muhurat session as 13:45–14:45. citeturn448733view1 The cited 2025 capital-market schedule independently shows surrounding windows such as block-deal, pre-open, closing, and trade-modification periods. citeturn890817search24

## 2. E046 — missing-session blind spot in the reconciler

### Finding

The corrected `scripts/phase1_session_reconciliation.py` still iterates only over dates observed in the NIFTY dataset:

`for day, g in df.groupby("day", sort=True):`

A special-session rule is only evaluated inside:

`if day in special:`

This means a special-session date declared in `phase1_session_rules.json` but completely absent from the observed dataset produces **no reconciliation row at all**.

The script then defines:

`"unreconciled_dates": uncontrolled`

where `uncontrolled` is built only from the already-created observed-date rows. Therefore a completely missing special session cannot increase `unreconciled_dates` and cannot fail CI.

### Why this violates the declared methodology

`research/PHASE1_SESSION_CALENDAR_SPEC.md` requires:

- every observed date to join to exactly one canonical session row;
- a date with no canonical session row to be classified `UNRECONCILED`;
- G4 cannot PASS with any `UNRECONCILED` trading date;
- every documented special session must be reconciled against its expected session window.

The implementation does not perform the required calendar-level join. It performs an observed-date-only pass plus a generic normal-session fallback.

The result is therefore not fail-closed for missing special-session data.

### Concrete failure mode

Suppose one of the seven manifest special dates had zero NIFTY observations because the source acquisition silently missed that entire date. Under the current code:

1. the date is absent from `df.groupby("day")`;
2. `reconcile_special()` is never called for that date;
3. no row is emitted for the date;
4. `uncontrolled` remains unaffected;
5. the artifact can still report `unreconciled: 0`;
6. CI can still succeed.

That is a substantive timestamp/session-quality defect, not a documentation defect.

### Related coverage defect

The same structure means an observed date that is not explicitly recognised as a special session or date-control is still passed through the generic normal-session rule. The current validator therefore does not implement the specification's required one-to-one canonical session join for all observed dates.

A new/unregistered exchange exception could consequently be treated as a generic regular day or a generic data-gap exclusion instead of becoming `UNRECONCILED`.

## 3. Required correction

The reconciler should be fail-closed against both directions of coverage:

1. **Manifest-to-data coverage:** every date declared in the canonical session calendar and every special session in the control manifest must have an observed-date record when the study data scope says the date is in-sample; otherwise it must be explicitly classified as a data gap / unreconciled condition according to a pre-registered rule.
2. **Data-to-calendar coverage:** every observed date must resolve to exactly one canonical session record (normal, special, holiday/closed, or another explicitly documented category). Generic fallback must not silently replace a missing calendar mapping.
3. A zero-observation special session must generate a failure or explicit pre-registered data-gap record rather than disappearing from the reconciliation table.
4. Add regression tests for:
   - missing special date;
   - unknown observed date;
   - duplicate calendar mapping;
   - special interval with no observations;
   - observation outside both execution and source-observation windows.

## 4. Gate state after this audit

| Gate | Tester state |
|---|---|
| G1 | PASS — existing evidence retained |
| G2 | PASS — existing evidence retained |
| G3 | PASS — existing evidence retained |
| G4 | **FAIL / OPEN — E046** |
| G5 | PRELIMINARY / OPEN |
| G6 | OPEN |
| G7 | OPEN |
| G8 | OPEN |
| G9 | BLOCKED |
| G10 | OPEN |
| G11 | OPEN |
| G12 | **PASS — final-head CI independently verified** |
| G13 | BLOCKED |
| G14 | BLOCKED |

## 5. Phase boundary

The final-head CI result is valid and reproducible for the code that was tested. It is not sufficient for G4 acceptance because the current reconciliation implementation does not satisfy the repository's own session-calendar specification in a fail-closed manner.

No backtest engine, optimization, profitability result, or strategy conclusion has been introduced by the tester.

## 6. Tester recommendation

Correct E046 on the developer branch, add the regression coverage above, then run the complete Phase 1 workflow again on the resulting exact head. The tester gate should be re-opened only after the new run demonstrates that missing or unrecognised session dates cannot be silently omitted from the reconciliation result.
