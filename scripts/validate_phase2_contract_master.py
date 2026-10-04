#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

MASTER=Path("data/raw/contracts/nifty_contract_master.parquet")
REQUIRED={
    "contract_id","symbol","option_type","strike","expiry",
    "contract_start","contract_end","lot_size","tick_size",
    "expiry_close_ts","source_reference","source_effective_date",
}

def main():
    if not MASTER.exists():
        raise SystemExit("PHASE2_CONTRACT_MASTER_MISSING")
    df=pd.read_parquet(MASTER)
    missing=REQUIRED-set(df.columns)
    if missing:
        raise SystemExit(f"PHASE2_CONTRACT_MASTER_SCHEMA_FAILURE:{sorted(missing)}")
    for c in ["strike","lot_size","tick_size"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    for c in ["expiry","contract_start","contract_end","expiry_close_ts","source_effective_date"]:
        df[c]=pd.to_datetime(df[c],errors="coerce")
    if df["contract_id"].isna().any() or df["contract_id"].duplicated().any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_CONTRACT_ID_FAILURE")
    if df["option_type"].isin(["CE","PE"]).all() is False:
        raise SystemExit("PHASE2_CONTRACT_MASTER_OPTION_TYPE_FAILURE")
    if (df["lot_size"]<=0).any() or (df["tick_size"]<=0).any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_NONPOSITIVE_RULE_FAILURE")
    if (df["contract_start"]>=df["contract_end"]).any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_INTERVAL_FAILURE")
    if (df["expiry_close_ts"]<df["expiry"]).any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_EXPIRY_CLOSE_FAILURE")
    if df["source_reference"].isna().any() or df["source_effective_date"].isna().any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_PROVENANCE_FAILURE")
    overlap = (
        df.sort_values(["contract_id","contract_start"])
          .assign(prev_end=lambda x:x.groupby("contract_id")["contract_end"].shift())
    )
    if ((overlap["contract_start"] < overlap["prev_end"]) & overlap["prev_end"].notna()).any():
        raise SystemExit("PHASE2_CONTRACT_MASTER_OVERLAP_FAILURE")
    print(json.dumps({
        "status":"PASS",
        "rows":int(len(df)),
        "contracts":int(df["contract_id"].nunique()),
        "lot_sizes":sorted(df["lot_size"].dropna().unique().tolist()),
        "tick_sizes":sorted(df["tick_size"].dropna().unique().tolist())
    },indent=2))

if __name__=="__main__":
    main()
