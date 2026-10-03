# Tester Report — G9 TBT Candidate Audit

Date: 2026-10-03
Role: Independent Tester
Candidate: `antony9952/Nifty_option_TBT`
Pinned revision in repository workflow: `643b48383839947b5fe3ed9483c9f7c0f167e865`

## Determination

**Candidate: REJECTED for production G9.**

The candidate cannot be accepted as the production historical execution/quote dataset because its own Hugging Face dataset viewer reports a dataset-generation schema cast failure. At the pinned revision, the dataset contains files with the expected TBT schema (including `depth_level`, `bid_price`, `bid_qty`, `ask_price`, `ask_qty`, `timestamp`, `tick_id`) and other files with a different 18-column OHLC/market-stat schema (including `request_mode`, `volume`, `oi`, `ltq`, `atp`, `vtt`, `feed_timestamp`, `close`, `cp`, `tbq`, `tsq`, `ltt`, `ltp`, `low`, `open`, `received_timestamp`, `high`, `iv`). Hugging Face explicitly reports that the files do not have matching columns.

The public dataset preview also shows TBT rows with `instrument_key` values such as `NSE_FO|58973` and five depth levels, demonstrating that bid/ask/depth-shaped data exist, but this does not overcome the mixed-schema failure or establish NIFTY contract identity, complete study-window coverage, quote age, spread quality, or deterministic execution validity.

## Workflow execution control

The repository contains `.github/workflows/phase1-g9-tbt-candidate.yml`, with `workflow_dispatch` and a pinned dataset revision. The connected GitHub Actions interface available to this tester exposes workflow-run/artifact reads and reruns but does not expose a manual workflow-dispatch operation. Therefore **no claim is made that a fresh manual G9 workflow execution occurred**.

This is an execution-observability limitation, not evidence of candidate quality. The candidate rejection above is independently supported by the public dataset metadata/schema failure.

## Additional validator-control finding

The repository validator `scripts/validate_g9_tbt_candidate.py` records per-file schemas but does not fail on incompatible schemas across files. Its `schema_changes_detected` check is ineffective for CSV files because `csv.DictReader.fieldnames` is fixed for the file after header parsing. The validator therefore cannot, by itself, establish schema consistency across the candidate. This should be corrected before any candidate is ever considered production-qualifying.

The validator also does not yet establish:
- complete 2021–2026 study-window coverage;
- contract-master reconciliation;
- quote-age/staleness statistics;
- crossed/locked/negative spread checks;
- tick-size conformity;
- depth continuity/availability statistics;
- decision-time executable quote coverage;
- deterministic midpoint/execution reconstruction.

## G9 impact

G9 remains **BLOCKED**, but this candidate is now recorded as **rejected evidence**, not as an unresolved alternative.

The production G9 route should proceed to the licensed NSE Historical F&O Order & Trade data path. G9 must not be marked PASS until raw execution/quote data complete the chain:

raw data → schema validation → contract mapping → timestamp validation → quote-age filter → bid/ask sanity → midpoint reconstruction → execution/fill model → deterministic audit.

No G5–G11 gate is promoted by this report and Phase 2 remains blocked.
