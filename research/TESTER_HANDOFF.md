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


## 2026-10-04 — Pragmatic progression policy

The independent tester branch records the project-owner waiver that the historical G6 aggregate is accepted for research progression with deferred audit. Developer work may continue through later phases without waiting for another intermediate formal gate, provided material failures remain blocking and all assumptions, costs, slippage, limitations, provenance and reproducibility risks remain explicit.

The tester will consolidate independent audits at milestone/final acceptance. The deferred checklist remains: data provenance/coverage, mathematical and sign correctness, look-ahead/execution chronology, transaction costs/brokerage/slippage, backtest correctness, regime/statistical methodology, robustness, reproducibility, and manuscript/code/status consistency.

Phase 2 developer work is now authorized under this progression policy. This does not retroactively change the historical G6 gate wording.


## 2026-10-04 — Phase 2 milestone handoff

Phase 2 is active under the owner progression waiver. The dedicated developer milestone handoff is `research/PHASE2_TESTER_HANDOFF_20261004.md`. The tester should independently audit the state machine, chronology/no-lookahead, atomic execution, slippage, date-specific cost resolution and reproducibility before final acceptance. Intermediate audit timing does not authorize omission of material defects.


## E152 fresh-gate handoff — 2026-10-04

Developer remediation head will be frozen after this handoff update.

Blocking tester findings at prior head:
1. expiry dates were timezone-naive while option timestamps were Asia/Kolkata-aware in expiry interval predicates;
2. the E150 impact scan did not classify old-only or corrected-only close states as affected.

Required independent checks at the next gate:
- verify all expiry/timestamp comparisons are timezone-consistent or explicitly calendar-date based;
- execute aware and naive regression tests and inspect the source for any remaining direct aware/naive comparisons;
- verify impact classification for changed, old-only, and corrected-only groups;
- run the impact scan over the pinned source and independently verify source-file count, source hashes, study horizon, contract-group count, and output hash;
- if affected groups > 0, verify affected production scenarios are rerun from the corrected exact head;
- if zero, preserve and independently verify the immutable zero-impact artifact;
- verify exact developer SHA in any CI artifact; do not reuse pre-remediation artifacts;
- re-audit E146–E151 and confirm no regression in fail-closed workflow behavior.

Production acceptance remains BLOCKED until this gate passes. No profitability, tradability, or strategy conclusion is authorized.


## E152 exact-head freeze — 2026-10-04

Exact developer head for this fresh gate: 75cc4b3f9f43bb09a68c47eda400ca13197e4cda.

Fresh isolated tester branch: tester/phase-2-e152-final-audit-v2-20261004.

The remediation PR is #54. The workflow now triggers on the remediation branch, includes the new regression tests in path filters, and executes the E150/E151 impact scan once before fail-closed production validation.

Tester must treat only this exact developer SHA and artifacts generated from it as authoritative.


## E153–E156 fresh exact-head handoff — 2026-10-04

Prior exact-head freeze is superseded. The next tester must use the exact developer SHA produced by this handoff commit.

PR #55 remediates E153–E156:
- impact scan syntax repaired;
- regression tests call the public execution predicate;
- original E150 latest-raw expiry-day close is restored;
- intermediate pre-E151 endpoint-bounded close and corrected interval-member close are both retained;
- study-horizon comparison is local-calendar-date safe;
- source SHA-256 inventory and report-content hash are recorded.

Fresh tester branch must be created from the final handoff SHA and must independently verify source semantics, syntax/tests, the three-way chronology, pinned-data scan, provenance, and exact-head CI. Any original-vs-corrected affected group requires affected production scenario reruns. No E150 closure or profitability inference is permitted from earlier artifacts.


## E157 fresh remediation handoff — 2026-10-04
Prior developer head `7f9f9209c77416986ba0827028067ab5b911160f` is rejected for the impact scan because its vectorized expiry-day filter mixed timezone-aware timestamps with timezone-naive expiry dates. Developer remediation branch: `phase-2-e157-remediation-20261004`.

Required fresh tester checks: (1) verify the vectorized predicate explicitly compares Asia/Kolkata local calendar dates; (2) execute the new naive/aware/mismatch regression tests; (3) inspect the three chronology states for preservation; (4) independently run/verify the pinned-source impact scan, source hashes, coverage/group counts, classification counts and deterministic report hash; (5) verify exact developer SHA in CI artifacts, without reusing prior artifacts; (6) if affected groups are nonzero, require affected production scenario reruns. E150 and Phase 2 production remain blocked until PASS.


## E157 execution handoff / E158 limitation — 2026-10-04
E157 remediation baseline: `636ebdfdf89a97461709c7d4097f89a04e7228a3`.
Execution descendant: `32d9421a449fd12933e88dcf37c78f3f16b93a7b`.
PR: #57.

The execution workflow explicitly runs `scripts/test_phase2_contract_master.py` and `scripts/test_phase2_e150_impact_scan.py`, then reconstructs the contract master and runs the pinned-source E150/E151 impact scan. The exact execution SHA currently has zero GitHub Actions runs/statuses exposed by the available connector, and local repository execution is unavailable because external network/DNS access is disabled.

Tester must independently verify the exact SHA, workflow contents, regression coverage, and absence of any stale artifact reuse. If an externally observable exact-head CI artifact becomes available, audit its checkout SHA, tests, source-file count/SHA-256 inventory, contracts scanned, chronology classifications/timestamps, gap/post-session counts and deterministic report hash. Any affected groups require corrected production scenario reruns. Until such evidence exists, E150 and Phase 2 remain blocked.


## Exact-head CI bootstrap trigger — 2026-10-04
Execution branch remains derived from immutable E157 baseline `636ebdfdf89a97461709c7d4097f89a04e7228a3`. Main now contains infrastructure-only bootstrap workflow `phase2-exact-head-bootstrap.yml`, which checks out the PR head SHA exactly and runs the contract-master plus E150/E151/E157 regression suites. This commit is an execution trigger only; no research logic or data rules are changed.
