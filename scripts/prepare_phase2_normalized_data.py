#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from phase1_g6_production_greeks import (
    bs_delta_arrays,
    expiry_close,
    load_rates,
    norm_ts,
    sha256_file,
    solve_iv_arrays,
    strict_prior,
)

OPT_ROOT = Path("data/raw/options/NIFTY")
INDEX = Path("data/raw/index/NIFTY.parquet")
CONTRACT_MASTER = Path("data/raw/contracts/nifty_contract_master.parquet")
RULES = Path("data/manifests/phase1_session_rules.json")
R_PATH = Path("data/processed/g6/risk_free.csv")
Q_PATH = Path("data/processed/g6/dividend_yield.csv")
OUT_ROOT = Path("data/processed/phase2/options")
STUDY_START = pd.Timestamp("2021-01-01")
STUDY_END = pd.Timestamp("2026-09-30 23:59:59")


def build_contract_ids(df: pd.DataFrame) -> pd.Series:
    return (
        df["expiry"].dt.strftime("%Y-%m-%d")
        + "|"
        + df["strike"].map(lambda x: f"{float(x):.4f}")
        + "|"
        + df["option_type"].astype(str).str.upper().str.strip()
    )


def load_contract_master() -> pd.DataFrame:
    if not CONTRACT_MASTER.exists():
        raise RuntimeError("PHASE2_CONTRACT_MASTER_MISSING")
    master = pd.read_parquet(CONTRACT_MASTER)
    required = {
        "contract_id", "option_type", "strike", "expiry",
        "contract_start", "contract_end", "lot_size", "tick_size",
        "expiry_close_ts", "source_reference", "source_effective_date",
    }
    missing = required - set(master.columns)
    if missing:
        raise RuntimeError(f"PHASE2_CONTRACT_MASTER_SCHEMA_FAILURE:{sorted(missing)}")
    for c in ["strike", "lot_size", "tick_size"]:
        master[c] = pd.to_numeric(master[c], errors="coerce")
    for c in ["expiry", "contract_start", "contract_end", "expiry_close_ts", "source_effective_date"]:
        master[c] = pd.to_datetime(master[c], errors="coerce")
    if master["contract_id"].duplicated().any():
        raise RuntimeError("PHASE2_CONTRACT_MASTER_DUPLICATE")
    return master


def load_underlying() -> pd.DataFrame:
    if not INDEX.exists():
        raise RuntimeError("PHASE2_UNDERLYING_MISSING")
    df = pd.read_parquet(INDEX)
    ts_col = next((c for c in df.columns if c.lower() in {"timestamp", "datetime", "date"}), None)
    px_col = next((c for c in df.columns if c.lower() in {"close", "value", "price", "index_value"}), None)
    if ts_col is None or px_col is None:
        raise RuntimeError("PHASE2_UNDERLYING_SCHEMA_FAILURE")
    out = df[[ts_col, px_col]].rename(columns={ts_col: "timestamp", px_col: "underlying"})
    out["timestamp"] = norm_ts(out["timestamp"])
    out["underlying"] = pd.to_numeric(out["underlying"], errors="coerce")
    out = out[(out["timestamp"] >= STUDY_START) & (out["timestamp"] <= STUDY_END)]
    if out["timestamp"].duplicated().any():
        raise RuntimeError("PHASE2_UNDERLYING_DUPLICATE_TIMESTAMP")
    return out


def session_mask(ts: pd.Series, rules: dict) -> pd.Series:
    local = ts
    day = local.dt.strftime("%Y-%m-%d")
    minute = local.dt.hour * 60 + local.dt.minute
    regular = rules["regular_execution_session"]
    start_h, start_m = map(int, regular["start"].split(":"))
    end_h, end_m = map(int, regular["end"].split(":"))
    regular_mask = (
        local.dt.weekday < 5
        & (minute >= start_h * 60 + start_m)
        & (minute <= end_h * 60 + end_m)
    )
    out = regular_mask.copy()

    special = {x["date"]: x for x in rules["special_sessions"]}
    controls = {x["date"]: x for x in rules["date_controls"]}

    for special_day, rule in special.items():
        idx = day.eq(special_day)
        if not idx.any():
            continue
        allowed = pd.Series(False, index=ts.index)
        for start, end in rule["execution_intervals"]:
            sh, sm = map(int, start.split(":"))
            eh, em = map(int, end.split(":"))
            allowed |= (minute >= sh * 60 + sm) & (minute <= eh * 60 + em)
        out.loc[idx] = allowed.loc[idx]

    for control_day, control in controls.items():
        if control.get("expected_classification") == "DATA_GAP_EXCLUDED":
            out.loc[day.eq(control_day)] = False

    return out.astype(bool)


def prepare_one(raw_path: Path, master: pd.DataFrame, underlying: pd.DataFrame, r: pd.DataFrame, q: pd.DataFrame, rules: dict, output: Path) -> dict:
    pf = pq.ParquetFile(raw_path)
    required = {"timestamp", "expiry", "strike", "option_type", "close", "volume"}
    missing = required - set(pf.schema.names)
    if missing:
        raise RuntimeError(f"PHASE2_OPTION_SCHEMA_FAILURE:{raw_path.name}:{sorted(missing)}")

    chunks = []
    for batch in pf.iter_batches(batch_size=200_000, columns=list(required)):
        df = batch.to_pandas()
        df["timestamp"] = norm_ts(df["timestamp"])
        df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.normalize()
        df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
        df["option_type"] = df["option_type"].astype(str).str.upper().str.strip().replace({"CALL":"CE","C":"CE","PUT":"PE","P":"PE"})
        df = df[(df["timestamp"] >= STUDY_START) & (df["timestamp"] <= STUDY_END)]
        if df.empty:
            continue
        df["contract_id"] = build_contract_ids(df)
        df = df.merge(master, on=["contract_id"], how="left", suffixes=("", "_master"), validate="many_to_one")
        for c in ["lot_size", "tick_size", "expiry_close_ts", "contract_start", "contract_end", "source_reference"]:
            if df[c].isna().any():
                raise RuntimeError(f"PHASE2_CONTRACT_MASTER_MISSING_MATCH:{raw_path.name}:{c}")
        active = (
            (df["timestamp"] >= df["contract_start"])
            & (df["timestamp"] < df["contract_end"])
            & (df["timestamp"] <= df["expiry_close_ts"])
        )
        if not active.all():
            df = df.loc[active].copy()
        if df.empty:
            continue

        df = df.merge(underlying, on="timestamp", how="left", validate="many_to_one")
        if df["underlying"].isna().any():
            raise RuntimeError(f"PHASE2_UNDERLYING_EXACT_MATCH_FAILURE:{raw_path.name}")

        rate_dates = strict_prior(df["timestamp"].dt.normalize(), r)
        div_dates = strict_prior(df["timestamp"].dt.normalize(), q)
        df["r"] = df["timestamp"].dt.normalize().map(dict(zip(rate_dates["date"], rate_dates["r"])))
        df["q"] = df["timestamp"].dt.normalize().map(dict(zip(div_dates["date"], div_dates["q"])))
        if df["r"].isna().any() or df["q"].isna().any():
            raise RuntimeError(f"PHASE2_RQ_STRICT_PRIOR_FAILURE:{raw_path.name}")

        df["t"] = (df["expiry_close_ts"] - df["timestamp"]).dt.total_seconds() / 31557600.0
        valid = (
            np.isfinite(df["underlying"]) & np.isfinite(df["strike"]) & np.isfinite(df["close"])
            & np.isfinite(df["t"]) & np.isfinite(df["r"]) & np.isfinite(df["q"])
            & df["underlying"].gt(0) & df["strike"].gt(0) & df["close"].gt(0) & df["t"].gt(0)
        )

        df["iv"] = np.nan
        df["signed_delta"] = np.nan
        if valid.any():
            arr = df.loc[valid, ["underlying","strike","t","r","q","close"]].astype(float)
            kind = np.where(df.loc[valid, "option_type"].isin(["CE"]), 1, 2).astype(np.int64)
            iv, _, _, code = solve_iv_arrays(
                arr["underlying"].to_numpy(),
                arr["strike"].to_numpy(),
                arr["t"].to_numpy(),
                arr["r"].to_numpy(),
                arr["q"].to_numpy(),
                arr["close"].to_numpy(),
                kind,
            )
            converged = code == 6
            if converged.any():
                sub = df.loc[valid].iloc[np.flatnonzero(converged)].copy()
                sub["iv"] = iv[converged]
                sub["signed_delta"] = bs_delta_arrays(
                    sub["underlying"].to_numpy(dtype=float),
                    sub["strike"].to_numpy(dtype=float),
                    sub["t"].to_numpy(dtype=float),
                    sub["r"].to_numpy(dtype=float),
                    sub["q"].to_numpy(dtype=float),
                    sub["iv"].to_numpy(dtype=float),
                    kind[converged],
                )
                df.loc[sub.index, "iv"] = sub["iv"]
                df.loc[sub.index, "signed_delta"] = sub["signed_delta"]

        df["abs_delta"] = df["signed_delta"].abs()
        df["session_eligible"] = session_mask(df["timestamp"], rules)
        df["execution_eligible"] = df["session_eligible"] & df["open"].notna() if "open" in df else df["session_eligible"]
        if "open" not in df:
            df["open"] = np.nan
            raise RuntimeError(f"PHASE2_OPTION_OPEN_MISSING:{raw_path.name}")

        keep = [
            "timestamp","expiry","strike","option_type","open","close","volume",
            "underlying","abs_delta","tick_size","lot_size",
            "session_eligible","execution_eligible","expiry_close_ts","contract_id",
        ]
        chunks.append(df[keep])

    if not chunks:
        raise RuntimeError(f"PHASE2_NORMALIZATION_EMPTY:{raw_path.name}")

    out = pd.concat(chunks, ignore_index=True)
    if out.duplicated(["timestamp","contract_id"]).any():
        raise RuntimeError(f"PHASE2_NORMALIZED_DUPLICATE:{raw_path.name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)
    return {
        "source": str(raw_path),
        "output": str(output),
        "rows": int(len(out)),
        "sha256": sha256_file(output),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-files", type=int, default=0)
    ap.add_argument("--output", default=str(OUT_ROOT))
    args = ap.parse_args()

    rules = json.loads(RULES.read_text())
    master = load_contract_master()
    underlying = load_underlying()
    r, q = load_rates()

    if not OPT_ROOT.exists():
        raise SystemExit("PHASE2_OPTION_SOURCE_MISSING")
    files = sorted(OPT_ROOT.glob("*.parquet"))
    if args.limit_files:
        files = files[:args.limit_files]
    if not files:
        raise SystemExit("PHASE2_OPTION_SOURCE_EMPTY")

    outputs = []
    for raw in files:
        out = Path(args.output) / raw.name
        outputs.append(prepare_one(raw, master, underlying, r, q, rules, out))

    manifest = {
        "status": "PHASE2_NORMALIZATION_COMPLETE",
        "study_start": str(STUDY_START.date()),
        "study_end": str(STUDY_END.date()),
        "raw_files": len(files),
        "outputs": outputs,
        "contract_master_sha256": sha256_file(CONTRACT_MASTER),
        "underlying_sha256": sha256_file(INDEX),
        "risk_free_sha256": sha256_file(R_PATH),
        "dividend_yield_sha256": sha256_file(Q_PATH),
    }
    out_manifest = Path(args.output) / "manifest.json"
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
