# Phase 1 Tester Handoff — Canonical Gate Contract

Effective: 2026-10-03 — E053 synchronized

The canonical Phase 1 gate IDs are authoritative in this document.

| Gate | Meaning |
|---|---|
| G1 | Immutable primary dataset / provenance |
| G2 | Structural schema validation |
| G3 | Duplicate handling |
| G4 | Timestamp and session quality |
| G5 | Underlying/option alignment |
| G6 | Production historical Greeks / IV |
| G7 | Target-delta availability |
| G8 | Historical contract metadata |
| G9 | Historical bid/ask / execution quality |
| G10 | Date-specific transaction costs |
| G11 | Market-context datasets |
| G12 | Repaired CI execution |
| G13 | Independent tester approval |
| G14 | Phase 2 authorization |

## Current tester determination

Independent tester PR #25 independently closed E055 PASS on the developer exact head; the underlying Run #55 G4/G12 evidence remains independently verified. The tester's substantive G13 blocker remains G5–G11 production acceptance.
- exact developer tip `378a130b6d450b288be140655f9b0b75aad840b3`
- Actions run `37135122966`
- job `111238039571`
- artifact `11278418088`
- artifact SHA-256 `de60c50a047357d7f89d5602ea42fd832158855779e34169fec2b9beeb02159`
- G4: PASS
- G12: PASS
- G13: BLOCKED
- G14 / Phase 2: BLOCKED

The tester's G13 blocker remains substantive: G5–G11 are not all production-accepted, particularly G9 historical bid/ask/execution quality.

## Developer control-plane note

This is the developer branch. The README role therefore remains **Developer**. The independent tester's current E055 result is represented by PR #25 and its tester report; it is not converted into a Tester role label on the developer branch.

## Required next checks

1. Resolve the remaining G5–G11 production evidence gates using the frozen research methodology.
2. For G9, acquire licensed historical bid/ask or sufficient NSE F&O order-level data and deterministically reconstruct the required decision-time executable quote state.
3. Re-run validation after any research-code change that affects the production evidence chain.
4. Keep all costs, slippage, brokerage and statutory charges date-specific; do not retrospectively apply current rates.
5. After all production gates are resolved, require an independent tester PASS for G13 before G14/Phase 2.

## Historical handoff/evidence




## G5 developer handoff — 2026-10-03

Developer has opened `phase-1-g5-underlying-option-alignment` for independent review after exact-head CI execution.

Required G5 evidence:
- `research/PHASE1_G5_ALIGNMENT_SPEC.md`
- `scripts/phase1_g5_alignment_audit.py`
- `.github/workflows/phase1-g5-alignment.yml`
- `data/validation/phase1_g5_alignment_report.json`

The acceptance condition is 100% exact timestamp alignment for decision-eligible option observations, with zero invalid option timestamps and zero duplicate NIFTY timestamps. Session eligibility and underlying alignment are intentionally tested as separate predicates. No interpolation or forward-fill is permitted.

Tester must verify the exact developer head, Actions run/checkout SHA, complete G5 report, and that no Phase 2 work was introduced. G13/G14 remain blocked until all G5–G11 gates are independently accepted.

## 2026-10-04 — Tester PR #36 follow-up
- Tester PR #36 determined Phase 1 FAIL / IN PROGRESS.
- G5 exact developer head `3225d29902a20c958bf8c9803479e8fbe7601dbf` had zero workflow runs/statuses. The next G5 evidence must bind the report's recorded checkout SHA to the Actions checkout SHA.
- Developer PR #37 implements that binding and adds an optional exact expected commit SHA for manual dispatch.
- G6 remains OPEN; tester PR #36 also identified missing cache restore/save in the source-acquisition workflow. Developer PR #38 adds this cache control.
- Tester must independently review the corrected exact heads and associated Actions evidence before any gate advancement.


## 2026-10-04 — G6 conditional-acceptance tester handoff
Developer requests an independent determination under `research/G6_CONDITIONAL_ACCEPTANCE_PROPOSAL_20261004.md`.

Tester branch: `tester/phase-1-g6-conditional-acceptance-20261004`
Developer assessment head: `e9d319e7f2e902f77696fc4dbd029fa93cbbce7f`

The tester must review PR #49's findings and the immutable completed G6 artifact, then decide whether the numerical result can be conditionally accepted despite D1-D3 evidence-retention gaps. The tester must not infer missing artifact fields or relabel a normal PASS. Verdict must be PASS, FAIL, or CONDITIONAL PASS WITH CONDITIONS. Until that verdict exists, G6/G13/G14/Phase 2 remain blocked.
