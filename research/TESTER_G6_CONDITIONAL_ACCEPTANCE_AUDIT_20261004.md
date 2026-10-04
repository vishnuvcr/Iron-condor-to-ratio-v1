# Independent Tester Audit — G6 Conditional Acceptance — 2026-10-04

## Verdict

**CONDITIONAL PASS WITH CONDITIONS**

This verdict is limited to **retention of the completed historical numerical G6 result as provisional research evidence**. It is **not** a formal G6 PASS, does not waive the canonical G6 evidence requirements, and does not authorize G13, G14, Phase 2, or any profitability/strategy conclusion.

## Scope

Audited independently against:
- `research/TESTER_HANDOFF.md`
- `research/PHASE1_G6_PRODUCTION_GREEKS_SPEC.md`
- `research/G6_CONDITIONAL_ACCEPTANCE_PROPOSAL_20261004.md`
- `research/PHASE1_GATE_MATRIX.md`
- `ERROR_LOG.md`
- `RESEARCH_STATUS.md`

Submitted remediation reference: `e9d319e7f2e902f77696fc4dbd029fa93cbbce7f`.

Prior completed numerical G6 evidence:
- Actions run: `37191768801`
- Exact checkout: `1a9eab7389b972c05362271ee9fb23092aa7354d`
- Aggregate artifact: `11299929192`
- Aggregate SHA-256: `80512999956437e2acfdbcea2d4a6a6ebfb659267691ef033dcf7b19f55c3ae6`

## Independent findings

### Numerical evidence that may be retained

The prior exact-head aggregate established a completed exhaustive numerical computation with:
- 32 shards and complete file partition;
- 267/267 option files;
- strict-prior r coverage 1262/1262;
- strict-prior q coverage 1262/1262;
- 102,759,697 IV-converged observations and zero non-convergence;
- reconciled signed/absolute delta histograms;
- reconciled target-selection counts of 8,016,434;
- maximum target-delta selection error <= 0.05;
- exact checkout/provenance and production checksums.

The prior tester audit found no mathematical contradiction in these aggregate results. This is sufficient to preserve the result as **provisional numerical research evidence**, provided it is never represented as a complete G6 gate pass.

### D1 — IV iteration/residual evidence

The old aggregate did not preserve the mandatory IV iteration/residual evidence. The remediation code now adds iteration and residual histograms and aggregate consistency checks, but no fresh exact-head CI artifact was independently observed in this audit.

**Condition:** the old result remains provisional only; a future exact-head run must independently verify the new evidence fields.

### D2 — expiry/date coverage

The old aggregate did not expose sufficiently specific expiry/date coverage. The remediation code now emits option-trading-date and expiry-date coverage plus missing/non-positive time-to-expiry counters.

**Condition:** no claim may be made that the old artifact contained this evidence. Fresh CI and tester verification remain required.

### D3 — future-input/no-lookahead evidence

The implementation uses strict-prior joins and the old code review found no same-day/future selection path, but the old aggregate did not emit explicit machine-readable counters. The remediation code now emits same-day/future counters and boolean strict-prior audit results.

**Condition:** the old numerical result is retained only under the conservative documented methodology; the corrected evidence implementation must be rerun and independently checked before formal G6 closure.

## Canonical gate interpretation

The G6 specification states that any missing mandatory evidence leaves G6 OPEN. Therefore this conditional verdict **does not change the formal gate state**:

- G6: **OPEN / not formally approved**
- G13: **BLOCKED**
- G14: **BLOCKED**
- Phase 2: **BLOCKED**

The conditional classification means only that the completed numerical result need not be discarded or recomputed solely to preserve its historical research value while the evidence-completeness remediation is completed.

## Conditions of acceptance

1. The old aggregate SHA-256 remains immutable and must be cited whenever this provisional result is used.
2. D1-D3 must remain explicitly disclosed in all downstream research outputs.
3. The old artifact must never be relabelled as satisfying D1-D3.
4. No G7/G8/G10/G11 or other gate requirement is waived by this decision.
5. The corrected G6 evidence implementation must receive a fresh exact-head CI run.
6. The fresh run must prove 32/32 shard completion, complete partition, aggregate reconciliation, D1-D3 evidence fields, strict-prior/no-lookahead checks, expiry/date coverage, target evidence, checksums, and exact checkout binding.
7. A fresh independent tester audit is mandatory after that run.
8. No Phase 2 engine, optimization, profitability result, or trading-strategy conclusion may rely on this conditional status as if G6 were formally PASS.
9. Slippage, brokerage, statutory charges and other execution costs remain mandatory for any later trading analysis.

## Tester conclusion

**CONDITIONAL PASS WITH CONDITIONS** is scientifically preferable to either (a) falsely promoting the old artifact to PASS or (b) discarding a numerically reconciled historical result solely because its evidence retention was incomplete.

The conditional decision is deliberately narrow: **retain the numerical result as provisional evidence; keep the formal G6 gate OPEN until the corrected evidence path is executed and independently verified.**

Tester branch: `tester/phase-1-g6-conditional-acceptance-20261004`.


## Follow-up control-plane verification — 2026-10-04

Developer reports exact head `94ea4b12de8ab9be2c404534db501ec30d53fd81` and PR #52. Independent tester verification confirms:
- PR #52 head SHA is exactly `94ea4b12de8ab9be2c404534db501ec30d53fd81`.
- GitHub's commit workflow-run query returns **zero workflow runs** for that exact SHA.
- Commit status is `pending` with zero published statuses.
- Therefore no fresh exact-head CI artifact is presently available to audit.
- The prior numerical artifact is not reused as fresh evidence.

**Tester control-plane state: WAITING FOR FRESH EXACT-HEAD ARTIFACT.**

No new G6 verdict is issued. The existing **CONDITIONAL PASS WITH CONDITIONS** remains the latest tester verdict, while the formal G6 gate remains OPEN.

**Next tester gate:** once a fresh exact-head aggregate artifact exists, independently verify exact checkout binding, all 32 shards, complete file partition, D1-D3 evidence, expiry/date coverage, strict-prior/no-lookahead controls, mathematical reconciliation, checksums, and fail-closed aggregation before issuing a new verdict.


## Principal-investigator progression waiver — 2026-10-04

The project owner has explicitly directed that the historical G6 aggregate be **accepted for research progression** and that gate strictness be reduced from this point forward, with substantive audits consolidated before final acceptance.

This changes the **research progression policy**, not the underlying numerical facts:

- The prior G6 aggregate remains the accepted working evidence for Phase 1 progression.
- D1-D3 evidence-completeness gaps are retained as documented limitations and must not be hidden.
- Fresh CI evidence for D1-D3 is no longer a prerequisite for opening later research phases.
- Later phases may proceed using the accepted G6 evidence, provided all material assumptions, costs, slippage, data limitations, and reproducibility risks remain disclosed.
- Independent tester audits will be performed at milestone/final acceptance checkpoints rather than blocking every intermediate implementation step.
- A final independent audit remains mandatory before any result is presented as a validated trading conclusion.

### Revised tester verdict for progression

**G6: ACCEPTED FOR RESEARCH PROGRESSION WITH DEFERRED AUDIT.**

This is a user-authorized pragmatic research-control decision. It is not a claim that the historical artifact contains D1-D3 evidence that it does not contain.

### Deferred final audit checklist

Before final research acceptance, the tester will audit at minimum:
1. data provenance and coverage;
2. mathematical/sign/formula correctness;
3. no-lookahead and execution chronology;
4. transaction costs, brokerage and slippage;
5. backtest implementation correctness;
6. regime/statistical methodology;
7. robustness and sensitivity claims;
8. reproducibility and cached-data integrity;
9. manuscript tables, figures, appendices and conclusions;
10. consistency between code, evidence artifacts, README, status and error logs.

**Research may continue past G6 under this waiver.**
