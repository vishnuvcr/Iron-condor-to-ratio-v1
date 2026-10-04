# Phase 2 — Historical NIFTY Contract-Master Specification

Updated: 2026-10-04

## Purpose

Provide the authoritative, date-effective contract metadata required by the proxy-execution engine. The engine must not infer historical lot size, expiry convention, or contract lifecycle from current specifications.

## Required file

Path:

data/raw/contracts/nifty_contract_master.parquet

Required columns:

- contract_id
- symbol
- option_type
- strike
- expiry
- contract_start
- contract_end
- lot_size
- tick_size
- expiry_close_ts
- source_reference
- source_effective_date

## Identity rule

contract_id must equal:

expiry YYYY-MM-DD + "|" + strike formatted to four decimals + "|" + CE/PE

The normalized option bars and contract master must reconcile one-to-one on contract_id.

## Chronology

A contract row is valid for an option-bar timestamp only when:

contract_start <= timestamp < contract_end

and timestamp <= expiry_close_ts.

No future contract metadata may be applied to an earlier bar.

## Historical rules that must be represented

The repository already records the following official transitions as evidence inputs:

- 2024 NIFTY lot-size reduction from 50 to 25 for the applicable new contracts.
- 2024-11-20 NIFTY lot-size increase from 25 to 75 for new contracts.
- 2025 expiry-day transition(s), including explicit treatment of existing/long-dated contracts.
- 2025-10-28 EOD NIFTY lot-size revision from 75 to 65 with contract-specific transition treatment.

These references are not sufficient by themselves to populate every contract. The actual historical contract master or a deterministic exchange-file reconstruction must be acquired and retained before production acceptance.

## Tick size

NIFTY index-option tick size must be taken from the effective historical contract metadata. A current specification must not be projected backward.

## Acceptance

The validator fails when:
- a required column is missing;
- contract_id duplicates exist;
- contract intervals overlap;
- lot_size or tick_size are nonpositive;
- expiry_close_ts is missing/inconsistent;
- an option bar cannot be matched exactly;
- more than one metadata row is active for the same bar;
- source_reference or source_effective_date is missing.

## Provenance

The master-file manifest must contain:
- source URL or repository;
- source file/date;
- acquisition timestamp;
- source checksum;
- exact parser version;
- exact Git SHA.

Until this file is present and passes validation, no production backtest result may be labelled historical-contract-correct.

## Reconstruction clarification

The primary study now uses a deterministic **monthly historical contract-master reconstruction** generated from the pinned NIFTY option partitions and official NSE lot-size chronology. It is not represented as recovered original NSE member-file bytes.

The reconstruction is accepted as the production candidate only after:
1. all source option partitions are acquired and hash-validated;
2. official monthly lot-size chronology is regression-tested;
3. every monthly contract has an expiry-day observation;
4. lifecycle, identifier and provenance validation passes;
5. the independent tester audits the exact resulting manifest.

An exact historical NSE contract file, if later obtained, supersedes the reconstruction after reconciliation.


## E150 — expiry-close boundary control

The reconstructed expiry_close_ts is not the latest raw timestamp observed on the expiry date. It is the latest observed option timestamp on that date that is at or before the date-specific F&O execution-session close in phase1_session_rules.json. Post-session observations remain source data for audit but cannot extend the execution boundary. A regression test explicitly proves that a 15:31 observation cannot extend a normal 15:30 expiry close.


## E151 — disjoint special-session interval membership and horizon control

For expiry-day observations, eligibility is determined by interval membership, not by comparison with the maximum special-session endpoint. This prevents observations in a non-trading gap between disjoint execution intervals from becoming expiry_close_ts.

The contract-master study horizon is now derived from the session-control manifest's study_data_end rather than a separate later hard-coded date. The current session-control evidence horizon is 2026-07-02; dates beyond that horizon are not claimed by this contract-master build until the session manifest is extended and independently validated.

The production workflow includes an E150/E151 impact scan. Any affected expiry/contract groups require affected scenario reruns before final profitability inference.
