# Phase 1 CI Evidence — 2026-10-03

## Successful execution

- Workflow: Phase 1 Data Acquisition and Validation
- Run ID: 37122686454
- Job/check ID: 111201763817
- Head commit: 68b39d91035bcb79c192cac80f20fd29ed6e709d
- Branch: phase-1-data-acquisition-validation
- Artifact: phase1-validation-report
- Artifact ID: 11274027306
- Artifact SHA-256: 329eb437e42745f5613e7c41bdf33313977b09d49492513a190d3c1216f01980
- All workflow steps completed successfully.

## Fresh-run evidence

### Structural/provenance
- Immutable Hugging Face revision: 0f4800e
- Files: 268 (267 option + 1 NIFTY index)
- Raw rows: 108,625,497
- Hard-failure files: 0
- Conflicting duplicate-key groups: 0
- Exact duplicate rows removed deterministically: 30,363,281
- Post-dedup rows: 78,262,216
- Historical bid/ask fields: absent

### Market-quality diagnostic
- Option rows after key dedup: 77,776,166
- Option/NIFTY timestamp alignment: 77,228,081 / 77,776,166 = 99.2953047%
- NIFTY index rows: 486,050
- Observed NIFTY dates: 1,262
- Session-count diagnostic outliers: 286 dates
- NIFTY daily timestamp count median/min/max: 378 / 6 / 420
- Greek/IV solver smoke observations: 596,005
- Greek solver status: DIAGNOSTIC_ONLY; r=q=0
- Production target-delta availability: NOT_YET_ACCEPTED

## Gate interpretation

- G1 PASS
- G2 PASS
- G3 PASS
- G4 OPEN
- G5 PRELIMINARY PASS
- G6 OPEN
- G7 OPEN
- G8 OPEN
- G9 BLOCKED
- G10 OPEN
- G11 OPEN
- G12 PASS
- G13 BLOCKED pending independent tester
- G14 BLOCKED

This file is execution evidence, not Phase 1 approval and not a profitability result.
