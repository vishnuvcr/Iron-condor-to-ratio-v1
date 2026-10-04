#!/usr/bin/env python3
"""Production G6 historical IV/Greek reconstruction.

This is a fail-closed, timestamp-level production scan. It consumes:
- exact contemporaneous NIFTY underlying values;
- strictly-prior risk-free and dividend-yield observations;
- deduplicated NIFTY option bars;
- effective expiry timestamps derived from the contract expiry field.

No interpolation, forward-fill, nearest-timestamp matching, same-day r/q,
or synthetic underlying values are permitted.

The IV solver is a deterministic Brent implementation (not bisection).
"""

from __future__ import annotations
import hashlib
import json
import math
import os
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from numba import njit, prange

ROOT=Path("data")
OPT_ROOT=ROOT/"raw/options/NIFTY"
UNDERLYING=ROOT/"raw/index/NIFTY.parquet"
R_PATH=ROOT/"processed/g6/risk_free.csv"
Q_PATH=ROOT/"processed/g6/dividend_yield.csv"
SHARD_INDEX=int(os.environ.get("G6_SHARD_INDEX","0"))
SHARD_COUNT=int(os.environ.get("G6_SHARD_COUNT","1"))
if SHARD_COUNT < 1 or SHARD_INDEX < 0 or SHARD_INDEX >= SHARD_COUNT:
    raise ValueError(f"INVALID_G6_SHARD_CONFIG:{SHARD_INDEX}:{SHARD_COUNT}")
OUT=ROOT/"validation"/f"phase1_g6_production_greeks_shard_{SHARD_INDEX:02d}.json"
STUDY_START=pd.Timestamp("2021-01-01")
STUDY_END=pd.Timestamp("2026-09-30")
EXPIRY_CLOSE_HOUR=15
EXPIRY_CLOSE_MINUTE=30
TARGETS=(0.30,0.10,0.50,0.40,0.08)
DELTA_TOL=0.05
REQUIRED_R={"date","yield_pct"}
REQUIRED_Q={"date","div_yield_pct"}
REQUIRED_OPT={"timestamp","expiry","strike","option_type","close","volume"}

@njit(cache=True)
def _norm_cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))

@njit(cache=True)
def bs_price(s,k,t,r,q,sigma,kind):
    if s<=0 or k<=0 or t<=0 or sigma<=0:
        return math.nan
    rt=math.sqrt(t)
    d1=(math.log(s/k)+(r-q+0.5*sigma*sigma)*t)/(sigma*rt)
    d2=d1-sigma*rt
    if kind==1:
        return s*math.exp(-q*t)*_norm_cdf(d1)-k*math.exp(-r*t)*_norm_cdf(d2)
    return k*math.exp(-r*t)*_norm_cdf(-d2)-s*math.exp(-q*t)*_norm_cdf(-d1)

@njit(cache=True)
def bs_delta(s,k,t,r,q,sigma,kind):
    if s<=0 or k<=0 or t<=0 or sigma<=0:
        return math.nan
    d1=(math.log(s/k)+(r-q+0.5*sigma*sigma)*t)/(sigma*math.sqrt(t))
    if kind==1:
        return math.exp(-q*t)*_norm_cdf(d1)
    return -math.exp(-q*t)*_norm_cdf(-d1)

@njit(cache=True)
def _brent_one(s,k,t,r,q,premium,kind,lo,hi,xtol,maxiter):
    a=lo; b=hi
    fa=bs_price(s,k,t,r,q,a,kind)-premium
    fb=bs_price(s,k,t,r,q,b,kind)-premium
    if not (math.isfinite(fa) and math.isfinite(fb)):
        return math.nan,0,math.nan
    if fa==0.0: return a,0,0.0
    if fb==0.0: return b,0,0.0
    if fa*fb>0.0:
        return math.nan,-2,math.nan
    c=b; fc=fb; d=b-a; e=d
    for it in range(1,maxiter+1):
        if (fb>0 and fc>0) or (fb<0 and fc<0):
            c=a; fc=fa; d=b-a; e=d
        if abs(fc)<abs(fb):
            a,b,c=b,c,b
            fa,fb,fc=fb,fc,fb
        tol=2.0*1e-15*abs(b)+xtol
        m=0.5*(c-b)
        if abs(m)<=tol or fb==0.0:
            return b,it,abs(fb)
        if abs(e)>=tol and abs(fa)>abs(fb):
            s1=fb/fa
            if a==c:
                p=2.0*m*s1
                q1=1.0-s1
            else:
                q1=fa/fc; r1=fb/fc
                p=s1*(2.0*m*q1*(q1-r1)-(b-a)*(r1-1.0))
                q1=(q1-1.0)*(r1-1.0)*(s1-1.0)
            if p>0: q1=-q1
            else: p=-p
            if 2.0*p<min(3.0*m*q1-abs(tol*q1),abs(e*q1)):
                e=d; d=p/q1
            else:
                d=m; e=m
        else:
            d=m; e=m
        a=b; fa=fb
        if abs(d)>tol: b += d
        else: b += tol if m>0 else -tol
        fb=bs_price(s,k,t,r,q,b,kind)-premium
    return math.nan,maxiter,abs(fb)

@njit(cache=True,parallel=False)
def bs_delta_arrays(s,k,t,r,q,sigma,kind):
    n=len(s)
    out=np.empty(n,dtype=np.float64)
    inv_sqrt_2pi=1.0/math.sqrt(2.0)
    for i in range(n):
        if s[i]<=0 or k[i]<=0 or t[i]<=0 or sigma[i]<=0:
            out[i]=math.nan
            continue
        d1=(math.log(s[i]/k[i])+(r[i]-q[i]+0.5*sigma[i]*sigma[i])*t[i])/(sigma[i]*math.sqrt(t[i]))
        cdf=0.5*(1.0+math.erf(d1*inv_sqrt_2pi))
        disc=math.exp(-q[i]*t[i])
        out[i]=disc*cdf if kind[i]==1 else -disc*(1.0-cdf)
    return out

@njit(cache=True,parallel=True)
def solve_iv_arrays(s,k,t,r,q,premium,kind):
    n=len(s)
    iv=np.full(n,np.nan); iters=np.zeros(n,np.int32); residual=np.full(n,np.nan); code=np.zeros(n,np.int8)
    for i in prange(n):
        if not (math.isfinite(s[i]) and math.isfinite(k[i]) and math.isfinite(t[i]) and math.isfinite(r[i]) and math.isfinite(q[i]) and math.isfinite(premium[i])):
            code[i]=1; continue
        if s[i]<=0 or k[i]<=0 or t[i]<=0 or premium[i]<=0:
            code[i]=2; continue
        ds=s[i]*math.exp(-q[i]*t[i]); dk=k[i]*math.exp(-r[i]*t[i])
        lower=max(0.0,ds-dk) if kind[i]==1 else max(0.0,dk-ds)
        upper=ds if kind[i]==1 else dk
        if premium[i] < lower-1e-8 or premium[i] > upper+1e-8:
            code[i]=3; continue
        root,its,res=_brent_one(s[i],k[i],t[i],r[i],q[i],premium[i],kind[i],1e-8,8.0,1e-8,100)
        if its<0:
            code[i]=4; continue
        if not math.isfinite(root):
            code[i]=5; iters[i]=its; residual[i]=res; continue
        iv[i]=root; iters[i]=its; residual[i]=res; code[i]=6
    return iv,iters,residual,code


def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b): h.update(b)
    return h.hexdigest()

def norm_ts(s):
    x=pd.to_datetime(s,errors="coerce")
    if getattr(x.dt,"tz",None) is not None:
        x=x.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    return x

def expiry_close(exp):
    x=pd.to_datetime(exp,errors="coerce")
    if pd.isna(x): return pd.NaT
    if isinstance(x,pd.Timestamp) and x.tzinfo is not None:
        x=x.tz_convert("Asia/Kolkata").tz_localize(None)
    return pd.Timestamp(x).normalize()+pd.Timedelta(hours=EXPIRY_CLOSE_HOUR,minutes=EXPIRY_CLOSE_MINUTE)

def strict_prior(left_dates, source):
    s=source.sort_values("date").copy()
    s["date"]=pd.to_datetime(s["date"],errors="coerce").astype("datetime64[ns]")
    l=pd.DataFrame({"date":pd.to_datetime(left_dates,errors="coerce").astype("datetime64[ns]").sort_values().unique()})
    out=pd.merge_asof(l,s,on="date",direction="backward",allow_exact_matches=False)
    return out

def detect_underlying_columns(df):
    ts=next((c for c in df.columns if c.lower() in {"timestamp","datetime","date"}),None)
    px=next((c for c in df.columns if c.lower() in {"close","value","price","index_value"}),None)
    if ts is None or px is None: raise RuntimeError("UNDERLYING_SCHEMA_FAILURE")
    return ts,px

def load_rates():
    if not R_PATH.exists() or not Q_PATH.exists():
        missing=[str(p) for p in (R_PATH,Q_PATH) if not p.exists()]
        raise RuntimeError("MISSING_PRODUCTION_RQ:"+",".join(missing))
    r=pd.read_csv(R_PATH); q=pd.read_csv(Q_PATH)
    if not REQUIRED_R.issubset(r.columns): raise RuntimeError("R_SCHEMA_FAILURE")
    if not REQUIRED_Q.issubset(q.columns): raise RuntimeError("Q_SCHEMA_FAILURE")
    r["date"]=pd.to_datetime(r["date"],errors="coerce").dt.normalize()
    q["date"]=pd.to_datetime(q["date"],errors="coerce").dt.normalize()
    if r["date"].isna().any() or q["date"].isna().any(): raise RuntimeError("RQ_INVALID_DATE")
    if r["date"].duplicated().any() or q["date"].duplicated().any(): raise RuntimeError("RQ_DUPLICATE_DATE")
    r["r"]=pd.to_numeric(r["yield_pct"],errors="coerce")/100.0
    q["q"]=pd.to_numeric(q["div_yield_pct"],errors="coerce")/100.0
    if (~np.isfinite(r["r"])).any() or (~np.isfinite(q["q"])).any(): raise RuntimeError("RQ_NONFINITE")
    return r[["date","r"]],q[["date","q"]]

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    report={"gate":"G6","status":"FAIL","execution_provenance":{"checked_out_commit_sha":head},
            "study_window":{"start":str(STUDY_START.date()),"end":str(STUDY_END.date()),
                            "expiry_time_convention":"15:30 Asia/Kolkata on effective expiry date"},
            "solver":{"algorithm":"Brent","vol_lower":1e-8,"vol_upper":8.0,"xtol":1e-8,"max_iterations":100},
            "target_delta_tolerance":DELTA_TOL,"targets":list(TARGETS)}
    try:
        r,q=load_rates()
        if not UNDERLYING.exists(): raise RuntimeError("UNDERLYING_INPUT_MISSING")
        udf=pd.read_parquet(UNDERLYING)
        uts,upx=detect_underlying_columns(udf)
        udf=udf[[uts,upx]].rename(columns={uts:"timestamp",upx:"underlying"})
        udf["timestamp"]=norm_ts(udf["timestamp"])
        udf["underlying"]=pd.to_numeric(udf["underlying"],errors="coerce")
        udf=udf[(udf["timestamp"]>=STUDY_START)&(udf["timestamp"]<STUDY_END+pd.Timedelta(days=1))]
        if udf["timestamp"].duplicated().any(): raise RuntimeError("UNDERLYING_DUPLICATE_TIMESTAMP")
        report["underlying_rows"]=int(len(udf))
        rate_dates=strict_prior(udf["timestamp"].dt.normalize(),r)
        div_dates=strict_prior(udf["timestamp"].dt.normalize(),q)
        report["rate_coverage"]={"underlying_days":int(udf["timestamp"].dt.normalize().nunique()),
                                 "strict_prior_r_days":int(rate_dates["r"].notna().sum()),
                                 "strict_prior_q_days":int(div_dates["q"].notna().sum()),
                                 "r_full":bool(rate_dates["r"].notna().all()),
                                 "q_full":bool(div_dates["q"].notna().all())}
        if not report["rate_coverage"]["r_full"] or not report["rate_coverage"]["q_full"]:
            raise RuntimeError("STRICT_PRIOR_RQ_COVERAGE_FAILURE")
        day_to_r=dict(zip(rate_dates["date"].astype(str),rate_dates["r"]))
        day_to_q=dict(zip(div_dates["date"].astype(str),div_dates["q"]))
        counters={k:0 for k in ["option_rows_scanned","option_rows_study_window","underlying_exact_match","underlying_missing",
                                 "r_missing","q_missing","invalid_model_input","nonpositive_premium","no_arbitrage_rejection",
                                 "bracket_failure","non_convergence","iv_converged","target_timestamp_groups","target_selected_records",
                                 "target_available_0.30","target_available_0.10","target_available_0.50","target_available_0.40","target_available_0.08"]}
        target_errors={f"{t:.2f}":[] for t in TARGETS}
        delta_bins=np.linspace(-1.0,1.0,101); delta_hist=np.zeros(100,dtype=np.int64)
        abs_bins=np.linspace(0.0,1.0,101); abs_hist=np.zeros(100,dtype=np.int64)
        iv_bins=np.linspace(0.0,3.0,121); iv_hist=np.zeros(120,dtype=np.int64)
        files=sorted(OPT_ROOT.glob("*.parquet"))
        if not files: raise RuntimeError("OPTION_INPUTS_MISSING")
        all_files=files
        files=[fp for i,fp in enumerate(all_files) if i % SHARD_COUNT == SHARD_INDEX]
        counters["option_files_total"]=len(all_files)
        counters["option_files"]=len(files)
        counters["shard_index"]=SHARD_INDEX
        counters["shard_count"]=SHARD_COUNT
        counters["option_files_processed"]=len(files)
        for fp in files:
            pf=pq.ParquetFile(fp)
            cols=pf.schema.names
            miss=REQUIRED_OPT-set(cols)
            if miss: raise RuntimeError("OPTION_SCHEMA_FAILURE:"+",".join(sorted(miss)))
            for batch in pf.iter_batches(batch_size=250000,columns=list(REQUIRED_OPT)):
                df=batch.to_pandas()
                counters["option_rows_scanned"]+=len(df)
                df["timestamp"]=norm_ts(df["timestamp"])
                df["expiry_close"]=df["expiry"].map(expiry_close)
                df["strike"]=pd.to_numeric(df["strike"],errors="coerce")
                df["close"]=pd.to_numeric(df["close"],errors="coerce")
                df["volume"]=pd.to_numeric(df["volume"],errors="coerce").fillna(0.0)
                df=df[(df["timestamp"]>=STUDY_START)&(df["timestamp"]<STUDY_END+pd.Timedelta(days=1))]
                counters["option_rows_study_window"]+=len(df)
                if df.empty: continue
                df=df.merge(udf,on="timestamp",how="left",validate="many_to_one")
                counters["underlying_exact_match"]+=int(df["underlying"].notna().sum())
                counters["underlying_missing"]+=int(df["underlying"].isna().sum())
                dates=df["timestamp"].dt.normalize().astype(str)
                df["r"]=dates.map(day_to_r); df["q"]=dates.map(day_to_q)
                counters["r_missing"]+=int(df["r"].isna().sum()); counters["q_missing"]+=int(df["q"].isna().sum())
                df["t"]=(df["expiry_close"]-df["timestamp"]).dt.total_seconds()/31557600.0
                kind=np.where(df["option_type"].astype(str).str.upper().isin(["CE","CALL","C"]),1,2)
                valid=(df["underlying"].notna()&df["r"].notna()&df["q"].notna()&df["t"].notna()&
                       (df["t"]>0)&df["strike"].gt(0)&df["underlying"].gt(0)&df["close"].gt(0))
                counters["invalid_model_input"]+=int((~valid).sum())
                arr=df.loc[valid,["underlying","strike","t","r","q","close"]].astype(float)
                if len(arr):
                    iv,it,res,code=solve_iv_arrays(arr["underlying"].to_numpy(),arr["strike"].to_numpy(),arr["t"].to_numpy(),
                                                   arr["r"].to_numpy(),arr["q"].to_numpy(),arr["close"].to_numpy(),
                                                   kind[valid.to_numpy()])
                    counters["nonpositive_premium"]+=int((code==2).sum())
                    counters["no_arbitrage_rejection"]+=int((code==3).sum())
                    counters["bracket_failure"]+=int((code==4).sum())
                    counters["non_convergence"]+=int((code==5).sum())
                    counters["iv_converged"]+=int((code==6).sum())
                    good=code==6
                    if good.any():
                        gd=df.loc[valid].iloc[np.flatnonzero(good)].copy()
                        gd["iv"]=iv[good]
                        gd["signed_delta"]=bs_delta_arrays(gd["underlying"].to_numpy(dtype=float),gd["strike"].to_numpy(dtype=float),
                                                              gd["t"].to_numpy(dtype=float),gd["r"].to_numpy(dtype=float),
                                                              gd["q"].to_numpy(dtype=float),gd["iv"].to_numpy(dtype=float),
                                                              kind[valid.to_numpy()][good])
                        gd["abs_delta"]=gd["signed_delta"].abs()
                        delta_hist += np.histogram(gd["signed_delta"].clip(-0.999999,0.999999),bins=delta_bins)[0]
                        abs_hist += np.histogram(gd["abs_delta"].clip(0,0.999999),bins=abs_bins)[0]
                        iv_hist += np.histogram(gd["iv"].clip(0,2.999999),bins=iv_bins)[0]
                        for (ts,ex,ot),g in gd.groupby(["timestamp","expiry","option_type"],sort=False):
                            counters["target_timestamp_groups"]+=1
                            for target in TARGETS:
                                g=g.assign(delta_error=(g["abs_delta"]-target).abs(), strike_distance=(g["strike"]-g["underlying"]).abs())
                                eligible=g[g["delta_error"]<=DELTA_TOL]
                                if eligible.empty: continue
                                selected=eligible.sort_values(["delta_error","volume","strike_distance"],ascending=[True,False,True],kind="mergesort").iloc[0]
                                key=f"target_available_{target:.2f}"
                                counters[key]+=1
                                counters["target_selected_records"]+=1
                                target_errors[f"{target:.2f}"].append(float(selected["delta_error"]))
        report["diagnostics"]=counters
        report["target_error_summary"]={k:({"count":len(v),"max_error":max(v),"mean_error":float(np.mean(v))} if v else {"count":0})
                                        for k,v in target_errors.items()}
        report["greek_distributions"]={
            "signed_delta_histogram":{"bin_edges":delta_bins.tolist(),"counts":delta_hist.tolist()},
            "absolute_delta_histogram":{"bin_edges":abs_bins.tolist(),"counts":abs_hist.tolist()},
            "iv_histogram":{"bin_edges":iv_bins.tolist(),"counts":iv_hist.tolist()}
        }
        report["checksums"]={"risk_free_csv":sha256_file(R_PATH),"dividend_yield_csv":sha256_file(Q_PATH),
                             "underlying_parquet":sha256_file(UNDERLYING)}
        report["status"]="PRODUCTION_SCAN_COMPLETE"
        report["acceptance_decision"]="G6 remains OPEN until independent tester verifies complete r/q coverage, production counts, solver distributions, target evidence and exact-checkout artifact."
    except Exception as exc:
        report["status"]="PRODUCTION_SCAN_FAILED"
        report["failure_reason"]=str(exc)
    OUT.write_text(json.dumps(report,indent=2,default=str))
    if report["status"]!="PRODUCTION_SCAN_COMPLETE":
        raise SystemExit(2)

if __name__=="__main__":
    main()

# E121 exact-head revalidation trigger: corrected G6 shard environment and evidence output.
