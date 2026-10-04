# G6 Secondary RBI Risk-Free Cross-Check — 2026-10-04

Purpose: record a secondary-source investigation after the bounded primary RBI WSS acquisition failed closed with zero parseable 91-Day Treasury Bill (Primary) Yield observations in GitHub Actions.

Secondary source located: Dataful dataset 17860, Week wise Ratios ... Rates ... Treasury Bill (Primary) Yield.

Observed metadata:
- Time period: 2011–2026
- Update frequency: weekly
- Granularity: date/category
- 23,784 rows / 6 columns
- Source attribution: Reserve Bank of India / DBIE
- 91-Day Treasury Bill (Primary) Yield is explicitly present.

Scientific treatment: PROVISIONAL CROSS-CHECK ONLY.

This source is not accepted as production G6 r input because it is a third-party redistribution; the current evidence is metadata/sample-level rather than an immutable cached full-file acquisition; its weekly frequency requires a separate no-lookahead/coverage audit; and substituting it without tester review would incorrectly convert an access limitation into data acceptance.

No interpolation, nearest-date matching, silent forward-fill, or secondary-source substitution has been performed.

Gate consequence: G6 remains FAIL / OPEN. G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH. G9 remains PASS. G13/G14 and Phase 2 remain BLOCKED.

Candidate controlled action: if independently approved, acquire the complete Dataful dataset bytes into a separate provisional-source cache, hash the file, filter exactly to the 91-Day Treasury Bill (Primary) Yield, audit date coverage and duplicate/conflict behavior, and compare values against independently accessible RBI WSS observations.

External evidence: Dataful publicly identifies the dataset as weekly RBI-derived data and explicitly lists the 91-Day Treasury Bill (Primary) Yield field.