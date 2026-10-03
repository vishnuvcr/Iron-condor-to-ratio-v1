# G5 Failure Isolation Specification

Purpose: diagnose the independently confirmed 521,069 decision-eligible option rows lacking an exact NIFTY timestamp without weakening the 100% exact-timestamp rule.

Frozen evidence: developer checkout db668dd2b89bf691a6481affb3cb2a9060c5fe98; Run 37148487963; Job 111277213347; Artifact 11284131045; artifact SHA-256 30381036630380820693858817bea51be4fae82896e01eb98cf09dba61fd95fb; raw option rows 108,139,447; decision-eligible rows 77,727,743; exact-aligned 77,206,674; missing 521,069; alignment 99.3296229%; affected expiry/day groups 362.

Required diagnostic classes:
1. underlying-source gaps;
2. option-source timestamp irregularity;
3. session-calendar classification;
4. cross-file partition/duplicate effects;
5. broader primary-dataset discontinuities.

No class may be inferred solely from missing exact timestamps. Report raw counts and examples.

Required tests:
- recompute missing rows from pinned source and exact session manifest;
- per-date and per-timestamp missing counts;
- compare missing timestamps with surrounding NIFTY timestamps and within-day NIFTY coverage;
- report seconds/microseconds/minute-grid characteristics;
- compare date-level option/NIFTY observed ranges;
- identify timestamps outside observed NIFTY intraday span;
- validate special-session and DATA_GAP_EXCLUDED classification independently;
- inspect all option parquet timestamp ranges for overlap;
- if ranges overlap, perform global contract-key duplicate audit; otherwise record non-overlap evidence as the partition guarantee.

This branch is diagnostic only. It cannot change G5 acceptance. No interpolation, forward-fill, nearest-minute matching, blanket deletion, or relaxed threshold is permitted.
