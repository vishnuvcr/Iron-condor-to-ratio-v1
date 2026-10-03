# Independent Tester Report — G5 Failure-Isolation Exact-Tip Re-audit

**Date:** 2026-10-04  
**Role:** Independent Tester  
**Scope:** Exact-tip failure-isolation run 37154986733 and the newly identified cross-file timestamp-range overlap.

## Determination

**G5: FAIL / OPEN.**

The exact-tip failure-isolation execution is independently verified and successful as a diagnostic execution, not as G5 acceptance evidence.

The artifact independently confirms:
- 521,069 reproduced missing exact NIFTY matches;
- 362 affected dates;
- 14 full-date underlying/index gaps accounting for 487,593 missing rows;
- 33,476 remaining failures across 348 dates;
- 238 option-file timestamp-range overlap pairs;
- 267 option parquet files;
- every file individually contains a single expiry matching its filename.

The new **238 range-overlap finding is substantive**. Timestamp-range separation cannot be used as a global partition/uniqueness guarantee.

The current diagnostic performs per-file contract-key deduplication only. Because multiple option files have overlapping timestamp ranges, that does **not** prove that the combined option population is globally unique by the frozen contract key.

Therefore a **global cross-file key-level audit is mandatory before the 521,069-row failure population can be interpreted as final row-level evidence**.

The 100% exact-timestamp requirement remains frozen. No interpolation, nearest matching, forward filling, silent deletion, holiday reclassification, or threshold relaxation is approved.

## Exact evidence

| Item | Verified value |
|---|---|
| Workflow run | `37154986733` |
| Job | `111296435573` |
| Job result | successful |
| Checkout | `ee3ab7f2b08f79faa0f15d756aab2379136cefa9` |
| Artifact | `11285517033` |
| Artifact SHA-256 | `292c823060e87e5cf8ff72e5b08fc9662b8adc4c0ef10eacb87207f3ac8cc498` |
| Recomputed missing rows | **521,069** |
| Affected dates | **362** |
| Full-date gaps | **14** |
| Full-date missing rows | **487,593** |
| Remaining partial-date failures | **33,476** |
| Remaining partial dates | **348** |
| Option parquet files | **267** |
| Timestamp-range overlap pairs | **238** |
| Filename/expiry partition mismatches | **0** |

I downloaded the artifact and independently recomputed its SHA-256. The digest exactly matches the GitHub artifact digest.

The artifact's `execution_provenance.checked_out_commit_sha` also records the same immutable checkout `ee3ab7f2b08f79faa0f15d756aab2379136cefa9`.

## Reproduction result

The diagnostic recomputed **521,069** missing decision-eligible option rows, exactly matching the frozen G5 failure.

This establishes that the failure-isolation branch did not accidentally eliminate or materially change the original failure population.

The diagnostic also reports the explicit semantic distinction between row counts and unique missing timestamps. This corrects the earlier ambiguity around `decision_timestamps` / `aligned_decision_timestamps`.

## Full-date gap result

The independently accepted date-level reconciliation identifies 14 option-observed/NIFTY-unobserved dates containing 487,593 missing rows.

The exact fraction is:

`487,593 / 521,069 = 0.9357551495 = 93.5755%`

Thus the correct rounded value is **93.5755%**.

The repository's earlier E087 prose contains **93.5762%** for the same numerator and denominator. That is a documentation arithmetic/rounding error and is recorded as **E082** by this tester. It does not alter the underlying counts or gate result.

The four later dates — 2025-10-10, 2026-05-25, 2026-05-26 and 2026-05-29 — remain appropriately classified as unresolved primary NIFTY-source coverage gaps rather than exchange-holiday exclusions.

## Critical new finding: 238 timestamp-range overlaps

The artifact reports **238 adjacent range-overlap pairs** among the 267 option files.

Examples include:
- `2021-05-27.parquet` overlapping `2021-06-03.parquet`;
- `2021-06-03.parquet` overlapping `2021-06-24.parquet`;
- `2021-06-24.parquet` overlapping `2021-06-17.parquet`.

The artifact also reports:
- all 267 files have a single unique expiry value;
- each unique expiry value matches the filename;
- zero filename/expiry partition mismatches.

These are useful controls, but they do **not** establish row-level uniqueness.

### Why the overlap matters

The current diagnostic executes:

`df.drop_duplicates(KEY, keep="first")`

**inside each file separately**.

The frozen key is:

`timestamp, expiry, strike, option_type`

If the same key occurs in two different files, each file-level deduplication retains one copy. The combined dataset therefore still contains two observations for the same contract-time key.

Consequences include:
1. inflated decision-eligible row counts;
2. potentially inflated missing-alignment counts;
3. possible double representation of the same observation;
4. ambiguity about which file's value should be retained if non-key fields differ;
5. inability to assert that the 521,069 count is a globally unique-row count until the cross-file audit is completed.

Importantly, this does **not** prove that cross-file duplicates exist. It proves that the current evidence does not establish that they do not exist.

## Required global key-level audit

The next diagnostic must perform a global audit over all 267 option files using the frozen key:

`(timestamp, expiry, strike, option_type)`

It must report at minimum:

### A. Global key multiplicity
- total rows before global deduplication;
- total unique frozen keys;
- number of keys occurring exactly once;
- number occurring 2, 3, 4, ... times;
- maximum key multiplicity;
- total excess rows beyond one per key.

### B. Cross-file duplication
For every key with multiplicity >1:
- number of distinct files containing the key;
- list of files;
- expiry;
- timestamp;
- strike;
- option type;
- whether all non-key fields are byte/value identical.

### C. Conflict classification
For duplicate frozen keys, classify:
- **EXACT_CROSS_FILE_DUPLICATE** — all non-key observations identical;
- **CONFLICTING_CROSS_FILE_DUPLICATE** — one or more non-key fields differ;
- **MULTI_FILE_PARTITION_RECORD** — duplicate key appears because the source legitimately stores overlapping partitions;
- **UNCLASSIFIED** — requires manual/source investigation.

No conflicting key may be silently resolved by `keep="first"`.

### D. Impact on G5
Recompute the G5 alignment failure after a deterministic **global** key audit.

Report:
- pre-global-dedup decision-eligible rows;
- globally unique decision-eligible rows;
- globally duplicated decision-eligible rows;
- exact-aligned unique rows;
- missing unique rows;
- exact alignment fraction;
- how many of the original 521,069 missing rows disappear solely because of duplicate-key removal.

This comparison must be performed without changing the 100% acceptance threshold.

### E. Deterministic resolution rule
If exact duplicate keys are confirmed, the research specification should state whether they are removed deterministically before G5.

If conflicting duplicate keys exist, G5 must remain fail-closed until the source conflict is independently resolved.

A global `drop_duplicates(KEY, keep="first")` without first classifying duplicate conflicts is **not acceptable**.

## Additional implementation observation

The current diagnostic's overlap algorithm compares adjacent ranges after sorting by minimum timestamp:

`for a,b in zip(ranges,ranges[1:])`

This is sufficient to identify many overlapping intervals but should be reviewed for interval-sweep completeness. For a robust global audit, an interval-overlap calculation should not rely solely on adjacent sorted ranges if one broad interval can overlap multiple later intervals.

The definitive control, however, is the global key audit itself; interval overlap is only a diagnostic trigger for that audit.

## Gate decision

| Gate | Tester determination |
|---|---|
| G5 | **FAIL / OPEN** |
| G6 | OPEN |
| G7 | OPEN |
| G8 | OPEN |
| G9 | PASS under approved proxy methodology |
| G10 | OPEN |
| G11 | OPEN |
| G12 | PASS |
| G13 | **BLOCKED** |
| G14 | **BLOCKED** |
| Phase 2 | **BLOCKED** |

No backtest, optimization, profitability analysis, or trading-strategy conclusion is authorized.

## Required next step

The developer should implement a **non-accepting global cross-file frozen-key audit** and execute it at an immutable exact tip.

The resulting artifact must be independently inspectable and must preserve:
- the original 521,069 failure count;
- global duplicate/conflict counts;
- exact duplicate versus conflicting duplicate classifications;
- impact of global deduplication on G5;
- exact checkout SHA;
- artifact SHA-256.

Only after that evidence is independently re-audited can the tester determine whether the current 521,069-row failure population is itself globally deduplicated and whether subsequent timestamp-level diagnosis is valid.

**No G5 acceptance-rule change is warranted at this stage.**