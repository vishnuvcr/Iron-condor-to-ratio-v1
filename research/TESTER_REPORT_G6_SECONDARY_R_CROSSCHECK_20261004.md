# Tester Report — G6 Secondary RBI Cross-Check — 2026-10-04

## Scope
Independent gate check of the developer's newly recorded secondary RBI cross-check. No production source code was modified on this tester branch.

## Findings
1. The developer correctly keeps G6 FAIL / OPEN.
2. The Dataful dataset is clearly labelled as a weekly RBI-derived dataset and explicitly contains 91-Day Treasury Bill (Primary) Yield.
3. The developer does not silently substitute the third-party dataset into production.
4. The current evidence does not establish immutable full-file provenance, complete study-window coverage at the required observation granularity, duplicate/conflict behavior, or exact value reconciliation to primary RBI observations.
5. Therefore the secondary source cannot be accepted as a G6 PASS input on the evidence currently available.

## Determination
**G6: FAIL / OPEN.**

## Required developer action before any G6 advancement
- Acquire the complete secondary file only in a separately labelled provisional cache.
- Hash and preserve the exact source bytes and retrieval metadata.
- Filter only the specified 91-Day Treasury Bill (Primary) Yield series.
- Audit date coverage, duplicates, conflicts and strict-prior eligibility.
- Reconcile a representative sample against primary RBI WSS observations.
- Run the production evidence workflow at an immutable exact head.
- Do not alter G5 status and do not authorize Phase 2.