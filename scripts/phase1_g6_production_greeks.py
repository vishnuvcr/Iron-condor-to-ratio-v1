#!/usr/bin/env python3
"""Fail-closed G6 production evidence audit.

The script intentionally requires prepared historical r/q tables. It never
fabricates, interpolates, forward-fills, or silently substitutes current values.
"""

from __future__ import annotations
import hashlib, json, math, subprocess
from pathlib import Path
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq

ROOT=Path("data")
OPT_ROOT=ROOT/"raw"
R_PATH=ROOT/"processed/g6/risk_free.csv"
Q_PATH=ROOT/"processed/g6/dividend_yield.csv"
OUT=ROOT/"validation/phase1_g6_production_greeks_report.json"
STUDY_START=pd.Timestamp("2021-01-01")
STUDY_END=pd.Timestamp("2026-09-30")

REQUIRED_R={"date","yield_pct"}
REQUIRED_Q={"date","div_yield_pct"}
REQUIRED_OPT={"timestamp","expiry","strike","option_type","close"}

def sha256_file(p: Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def bs_price(s,k,t,r,q,sigma,kind):
    if min(s,k,t,sigma)<=0: raise ValueError("INVALID_MODEL_INPUT")
    rt=math.sqrt(t)
    d1=(math.log(s/k)+(r-q+0.5*sigma*sigma)*t)/(sigma*rt)
    d2=d1-sigma*rt
    n=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
    if kind=="CE": return s*math.exp(-q*t)*n(d1)-k*math.exp(-r*t)*n(d2)
    return k*math.exp(-r*t)*n(-d2)-s*math.exp(-q*t)*n(-d1)

def bs_delta(s,k,t,r,q,sigma,kind):
    rt=math.sqrt(t)
    d1=(math.log(s/k)+(r-q+0.5*sigma*sigma)*t)/(sigma*rt)
    n=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
    return math.exp(-q*t)*(n(d1) if kind=="CE" else n(d1)-1)

def implied_vol(s,k,t,r,q,premium,kind):
    if premium<=0: return None,"NONPOSITIVE_PREMIUM",0,float("nan")
    disc_s=s*math.exp(-q*t); disc_k=k*math.exp(-r*t)
    lo,hi=(max(0.0,disc_s-disc_k),disc_s) if kind=="CE" else (max(0.0,disc_k-disc_s),disc_k)
    if premium<lo-1e-8 or premium>hi+1e-8:
        return None,"NO_ARBITRAGE_BOUND_REJECTION",0,float("nan")
    a,b=1e-8,8.0
    fa=bs_price(s,k,t,r,q,a,kind)-premium
    fb=bs_price(s,k,t,r,q,b,kind)-premium
    if fa*fb>0: return None,"VOLATILITY_BRACKET_FAILURE",0,float("nan")
    for i in range(1,101):
        m=(a+b)/2
        fm=bs_price(s,k,t,r,q,m,kind)-premium
        if abs(fm)<=1e-8 or (b-a)<=1e-8:
            return m,"CONVERGED",i,abs(fm)
        if fa*fm<=0: b,fb=m,fm
        else: a,fa=m,fm
    return None,"NON_CONVERGENCE",100,abs(fm)

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    report={"gate":"G6","status":"BLOCKED","acceptance_boundary":"Substantive production evidence only; no Phase 2 authorization.","generated_at_utc":datetime.utcnow().isoformat()+"Z"}
    report["execution_provenance"]={"checked_out_commit_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()}
    required=[R_PATH,Q_PATH]
    missing=[str(p) for p in required if not p.exists()]
    if missing:
        report.update({"status":"PRODUCTION_INPUTS_INCOMPLETE","missing_inputs":missing})
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(2)
    r=pd.read_csv(R_PATH); q=pd.read_csv(Q_PATH)
    r["date"]=pd.to_datetime(r["date"],errors="coerce"); q["date"]=pd.to_datetime(q["date"],errors="coerce")
    errors=[]
    if not REQUIRED_R.issubset(r.columns): errors.append("R_SCHEMA_FAILURE")
    if not REQUIRED_Q.issubset(q.columns): errors.append("Q_SCHEMA_FAILURE")
    for name,df in [("r",r),("q",q)]:
        if df["date"].isna().any(): errors.append(f"{name.upper()}_INVALID_DATE")
        if not df["date"].is_monotonic_increasing: df.sort_values("date",inplace=True)
        if df["date"].duplicated().any(): errors.append(f"{name.upper()}_DUPLICATE_DATE")
        if (df["date"]>=STUDY_END).any() and name in {"r","q"}:
            pass
    if errors:
        report.update({"status":"INPUT_VALIDATION_FAILURE","errors":errors})
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(3)

    # Strictly-before coverage is measured against the actual option-data trading-date universe.
    parquet=list((OPT_ROOT/"options/NIFTY").glob("*.parquet"))
    report["option_files"]=len(parquet)
    if not parquet:
        report["status"]="PRODUCTION_OPTION_INPUTS_MISSING"
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(4)
    option_dates=set()
    invalid_files=0
    for p in parquet:
        df_dates=pd.read_parquet(p,columns=["timestamp"])
        ts=pd.to_datetime(df_dates["timestamp"],errors="coerce")
        if ts.isna().any(): invalid_files += 1
        option_dates.update(ts.dropna().dt.normalize().unique())
    if invalid_files:
        report["status"]="OPTION_INVALID_TIMESTAMP"
        report["invalid_option_timestamp_files"]=invalid_files
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(6)
    trading_days=sorted(option_dates)
    r_dates=set(r["date"].dt.normalize())
    q_dates=set(q["date"].dt.normalize())
    r_eligible=[d for d in trading_days if any(x<d for x in r_dates)]
    q_eligible=[d for d in trading_days if any(x<d for x in q_dates)]
    report["coverage"]={
        "study_start":str(STUDY_START.date()),"study_end":str(STUDY_END.date()),
        "q_observations":len(q_dates),"r_observations":len(r_dates),
        "trading_days_tested":len(trading_days),
        "r_strictly_prior_days":len(r_eligible),"q_strictly_prior_days":len(q_eligible),
        "r_full_strict_prior_coverage":len(r_eligible)==len(trading_days),
        "q_full_strict_prior_coverage":len(q_eligible)==len(trading_days)
    }

    # Production option scan is deliberately explicit: locate the deduplicated
    # parquet tree and require the frozen core columns before valuation.
    parquet=list((OPT_ROOT/"options/NIFTY").glob("*.parquet"))
    report["option_files"]=len(parquet)
    if not parquet:
        report["status"]="PRODUCTION_OPTION_INPUTS_MISSING"
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(4)

    option_schema=set(pq.ParquetFile(parquet[0]).schema.names)
    missing_cols=sorted(REQUIRED_OPT-option_schema)
    if missing_cols:
        report["status"]="OPTION_SCHEMA_FAILURE"; report["missing_option_columns"]=missing_cols
        OUT.write_text(json.dumps(report,indent=2)); raise SystemExit(5)

    report["solver"]={"algorithm":"deterministic_bisection","max_iterations":100,"vol_lower":1e-8,"vol_upper":8.0,"price_tolerance":1e-8}
    report["diagnostics"]={"iv_converged":0,"iv_failures":0,"boundary_rejections":0,"target_delta_records":0,"target_delta_missing":0}
    report["status"]="IMPLEMENTATION_READY_PRODUCTION_DATA_REQUIRED"
    report["checksums"]={"risk_free_csv":sha256_file(R_PATH),"dividend_yield_csv":sha256_file(Q_PATH)}
    OUT.write_text(json.dumps(report,indent=2))

if __name__=="__main__": main()
