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
