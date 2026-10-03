# Tester Report — Phase 0 Fifth Independent Gate (PR #9)

**Date:** 2026-10-03  
**Role:** Independent Tester  
**Repository:** \`vishnuvcr/Iron-condor-to-ratio-v1\`  
**Developer PR under test:** #9  
**Developer branch:** \`phase-0-corrections-v4\`  
**Tester branch:** \`tester/phase-0-fifth-audit\`

## Verdict

**FAIL — Phase 0 approval is not granted. Phase 1 remains BLOCKED.**

PR #9 materially addresses the fourth tester's B6 repository-record defects. The source/operational separation is clear, the frozen numerical conventions are substantially reproducible, the active gate wording is synchronized, and the literal-core slippage rule is explicitly separated from sensitivity variants.

However, the current Phase 0 integrity control still contains a concrete ineffective assertion, and the repository does not expose a verifiable CI status for the v4 commit through the available GitHub status interface. Because this project treats repository controls and auditability as gate requirements, these defects must be corrected before approval.

## Scope checked

- PR #9 metadata and changed files.
- \`RESEARCH_PLAN.md\`, \`RESEARCH_STATUS.md\`, \`README.md\`.
- \`ERROR_LOG.md\`, \`CONVERSATION_LOG.md\`.
- \`research/OPERATIONAL_CONVENTIONS.md\`.
- \`research/STRATEGY_SPEC.md\`.
- \`research/TESTER_HANDOFF.md\`.
- \`.github/workflows/phase0-integrity.yml\`.
- Historical tester reports from the first through fourth gates.
- Current v4 commit status exposed by the GitHub integration.

No Phase 1 dataset, production backtest engine, optimization result, profitability result or trading conclusion was found in the v4 correction material reviewed.

## Passed checks

### A. Active gate synchronization — PASS

The active gate now consistently uses the current independent tester approval model rather than a historical tester count. Phase 1 is explicitly blocked pending approval of the current correction pass.

### B. Literal-core versus sensitivity slippage — PASS

The v4 specification fixes the literal-core fallback at:

\`max(2 * tick_size, 0.005 * reference_price)\`

and explicitly limits alternative slippage assumptions to pre-registered sensitivity variants. \`RESEARCH_PLAN.md\`, \`STRATEGY_SPEC.md\`, \`README.md\`, and the operational contract are mutually aligned on this point.

### C. Numerical B1–B5 controls — PASS on document inspection

The previously reported controls remain present:

- Brent-Dekker/Brent-style solver contract, binary64 arithmetic, tolerances, pricing error and iteration limit.
- Explicit discounted Black-Scholes bounds and one-tick tolerance semantics.
- Explicit integer tick ceil/floor fill rounding and on-grid handling.
- Explicit rejection of future-dated quotes.
- Strategy specification aligned with the fixed fallback slippage rule.

### D. Source/convention separation — PASS

The repository clearly distinguishes source-derived rules from researcher-selected implementation conventions. This distinction is necessary because the video does not uniquely determine sampling, strike-selection, execution, Greek reconstruction or expiry semantics.

### E. Phase gating — PASS

No evidence was found that Phase 1 has been started. The status, plan and handoff continue to prohibit data acquisition/backtesting before the current tester gate passes.

## Blocker B7 — Ineffective stale-branch workflow assertion

The workflow contains:

\`\`\`sh
! grep -q "## Current branch\n\`phase-0-corrections-v2\`" README.md
\`\`\`

Standard \`grep\` does not interpret \`\n\` in a basic quoted search pattern as a cross-line match. A two-line README containing exactly:

\`\`\`text
## Current branch
\`phase-0-corrections-v2\`
\`\`\`

returns **no match**, so the negated test succeeds. I independently reproduced this shell behavior.

Therefore the workflow does **not** actually enforce the stale-v2 current-branch condition it claims to enforce. This matters because the fourth tester's B6 defect was specifically about stale active branch/status records.

### Required correction

Replace the multiline grep with a line-aware assertion, for example by checking the heading and following line separately, using \`grep -A1\`, \`awk\`, Python, or another deterministic parser. The workflow should fail when the README still identifies v2 as the current branch.

The same principle should be applied to any other multi-line stale-record assertions added later.

## Blocker B8 — Claimed workflow pass is not independently auditable from the current commit status

The developer records state that the Phase 0 integrity workflow passed on \`phase-0-corrections-v4\` and PR #9 is ready for retest. I checked the v4 head commit (\`1ba06188ff5adc48ab0055087d813ca617b5b873\`) through the available GitHub workflow-run/status interfaces.

The available workflow-run query returned no workflow runs for that commit, and the combined commit-status query returned no statuses/checks. This does **not** prove that GitHub Actions did not execute; it means the claimed successful run is not independently verifiable from the repository status evidence available to this tester.

### Required correction

Persist an auditable CI reference for the exact v4 head commit: workflow run ID/URL or an equivalent GitHub check/status record tied to the tested SHA. The README/status record should identify the exact SHA and successful workflow run rather than relying only on prose stating that the workflow passed.

If the workflow genuinely passed on another SHA, the active PR/branch record must identify that SHA and explain the relationship to the current head.

## Non-blocking observations for Phase 1 preparation

1. **Risk-free-rate convention:** the operational file states \`r = ln(1+y)\` but should explicitly define what the RBI T-bill \`y\` represents for this conversion (annual effective equivalent versus another quoted convention), and record the publication/effective-date selection rule. RBI identifies Indian T-bills as money-market instruments using actual/365 conventions and publishes auction yields/YTMs. This should be frozen before production Greek reconstruction.
2. **CI scope:** the current workflow is an integrity-control workflow, not a research execution workflow. That is appropriate while Phase 1 is blocked. Downstream phase workflows should not be introduced or enabled until their respective gates pass.
3. **Historical cost schedules:** the operational contract correctly requires date-specific Paytm Money and statutory schedules, but no historical cost schedule has yet been validated. This remains a Phase 1 prerequisite, not a reason to start Phase 1 early.

## Required retest conditions

1. Correct B7 in \`.github/workflows/phase0-integrity.yml\`.
2. Re-run the integrity workflow on the resulting exact commit.
3. Make the successful run/check auditable by exact commit SHA and run/check identifier.
4. Update README/status/error/conversation records to identify the new correction and retest state.
5. Submit the resulting correction pass to a fresh independent tester review.
6. Keep Phase 1 blocked until that fresh review records PASS.

## Gate decision

**PHASE 0: FAIL.**

**PHASE 1: BLOCKED.**

No historical data acquisition, backtesting, optimization, profitability assessment, or trading conclusion should begin from this gate.

## External reference used for the non-blocking rate-convention observation

- RBI Government Securities / Treasury Bills FAQ: https://m.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=711
- RBI Treasury Bill auction results: https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60674
