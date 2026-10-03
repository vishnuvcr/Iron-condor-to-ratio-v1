# Independent Tester Report — Phase 1 Data-Gathering Audit

Updated: 2026-10-03

## Role and scope

Independent **Tester** audit of developer branch `phase-1-data-acquisition-validation`, head `833d8a0b7195418bdc98d04976841963b6bacfc2`.

Scope: verify the new data inventory, acquisition provenance, current CI execution evidence, and canonical G1–G14 Phase 1 gates. No Phase 2/backtest/profitability work is performed or accepted.

## Verdict

**PHASE 1: FAIL / IN PROGRESS**

**PHASE 2: BLOCKED**

The new inventory is appropriately conservative and E036 is confirmed. However, there is no fresh Actions run for the repaired acquisition/audit path, several production gates remain unresolved, and the current workflow has a CI syntax-check command defect (E037).

## Independently verified evidence

### Primary immutable source

`data/manifests/phase1_data_inventory.json` records:

- Hugging Face dataset `thetrademarkk/india-index-options-1m`
- immutable revision `0f4800e`
- NIFTY-only scope: `options/NIFTY/*.parquet` and `index/NIFTY.parquet`
- documented 1-minute OHLCV(+OI), IST timestamps, strike/type/expiry
- prior evidenced inventory: 268 files, 108,625,497 rows
- 30,363,281 exact duplicate rows
- 0 conflicting duplicate-key groups
- no bid/ask fields
- NIFTY index SHA-256 recorded

The manifest explicitly distinguishes historical acquisition evidence from datasets not yet materialized. It does not overclaim a fresh acquisition.

### GitHub Actions evidence

PR #13 head is `833d8a0b7195418bdc98d04976841963b6bacfc2`. The workflow-run query for that exact commit returns **zero workflow runs**.

Therefore the current evidence does not establish fresh execution of the repaired Phase 1 workflow.

### Historical data evidence

Earlier successful runs remain historical evidence only. They support prior structural/dedup observations but do not validate the repaired current workflow or newly gathered production datasets.

## New blocker: E037

The current `.github/workflows/phase1-data-validation.yml` contains:

```
- name: Syntax-check Phase 1 scripts
  run: python -m py_compile scripts/validate_phase1_data.py scripts/deduplicate_phase1_data.py scripts/phase1_market_quality_audit.py scripts/phase1_session_outlier_characterization.py scripts/validate_phase1_control_manifests.py
    python scripts/validate_phase1_control_manifests.py
```

Because `run:` is not a block scalar (`|`), the indented continuation is folded into the same shell command. The intended second Python invocation is therefore not a separate command; the resulting command attempts to pass `python` and the second script path as arguments to `py_compile`.

This is a CI correctness defect independent of the absent workflow run. It must be corrected before G12 can be accepted.

**E037 severity: blocking.**

Recommended form:

```
run: |
  python -m py_compile scripts/validate_phase1_data.py scripts/deduplicate_phase1_data.py scripts/phase1_market_quality_audit.py scripts/phase1_session_outlier_characterization.py scripts/validate_phase1_control_manifests.py
  python scripts/validate_phase1_control_manifests.py
```

## Canonical gate assessment

| Gate | Tester state | Reason |
|---|---|---|
| G1 | PASS as provenance control; fresh production acquisition still required | Immutable revision and manifest are consistent |
| G2 | Historical PASS only | Prior pinned acquisition passed; no fresh current run |
| G3 | Historical PASS only | Prior deterministic dedup evidence exists; no fresh current execution |
| G4 | OPEN | Session anomalies remain unreconciled to effective-date exchange sessions |
| G5 | PRELIMINARY / OPEN | Prior 99.2953% alignment is diagnostic, not final decision-time acceptance |
| G6 | OPEN | Production date-aligned r/q and IV/Greeks not materialized |
| G7 | OPEN | Target-delta availability under frozen tolerance and liquidity filters not quantified |
| G8 | OPEN | Effective-date expiry/lot/tick reconciliation not materialized |
| G9 | BLOCKED | Historical bid/ask/order-level data not acquired |
| G10 | OPEN | Complete date-specific brokerage/statutory/exchange/IPFT/SEBI/GST/stamp/clearing schedule not materialized |
| G11 | OPEN | Context datasets not fully acquired/aligned |
| G12 | FAIL / OPEN | Zero workflow runs for current repaired head; E037 workflow defect |
| G13 | BLOCKED | Independent Phase 1 PASS cannot be issued |
| G14 | BLOCKED | Phase 2 authorization requires G1–G13 and explicit tester PASS |

## E036 assessment

**E036: CONFIRMED.**

Reopening PR #13 did not produce a new Actions run. The inventory correctly separates historical acquisition evidence from current execution evidence. No fresh download or fresh validation result is inferred.

## Required corrections before the next tester gate

1. Correct E037 and retain a deterministic CI syntax/control check.
2. Obtain an independently verifiable Actions run on the corrected commit.
3. Execute and archive pinned NIFTY-only acquisition/validation/dedup/audit outputs.
4. Reconcile G4 session anomalies to effective-date exchange calendars and pre-register the rule.
5. Complete production G5 decision-time alignment.
6. Produce date-aligned production r/q and IV/Greeks under the frozen Phase 0 numerical contract.
7. Quantify G7 target-delta availability after the frozen delta tolerance and liquidity/volume/OI filters.
8. Materialize G8 effective-date expiry/lot/tick metadata.
9. Resolve G9 through historical bid/ask or validated order-level reconstruction; do not substitute close prices.
10. Materialize G10 complete date-specific costs, including brokerage and applicable statutory/exchange/IPFT/SEBI/GST/stamp/clearing components.
11. Materialize and align G11 contextual variables.
12. Repeat independent tester review after the evidence is present.

## Phase discipline

No Phase 2 engine, optimization, backtest result, profitability claim, or trading conclusion was accepted.

## Final decision

**FAIL. Phase 1 remains IN PROGRESS. Phase 2 remains BLOCKED.**

This report is a tester artifact and does not authorize phase advancement.
