# Phase 2 Normalized Data Contract

The engine does not silently infer missing production features. A Phase 2 integration run must provide the normalized columns in `research/PHASE2_ENGINE_SPEC.md`, including the date-specific `expiry_close_ts`.

## Required provenance

The normalized file must be accompanied by a manifest containing:
- source raw-file paths and SHA-256 hashes;
- exact upstream Phase 1 commit SHA;
- Greek-model version/spec;
- contract-master version/spec;
- session-calendar version/spec;
- date range;
- row count and duplicate-key audit result.

## Required chronology

For each decision timestamp:
- all selection inputs come from bars at that timestamp or earlier;
- execution may use only the first eligible bar strictly after the decision timestamp for the selected contract;
- the engine must never search backward or forward beyond the first eligible bar;
- contracts must remain unexpired at execution.

## Required delta semantics

`abs_delta` means absolute Black-Scholes delta from the frozen Phase 1 Greek model. The sign is retained upstream for diagnostics, but strike selection uses absolute delta because the source rule is stated in platform-style delta magnitudes.

## Required option data quality

No duplicate `(timestamp, contract_id)` rows.
No negative/zero execution opens.
Historical `tick_size` and `lot_size` must be effective-date values.
No future-dated Greek or cost input.
Missing bars remain missing.

