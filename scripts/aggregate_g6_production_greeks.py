#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT=Path("data/validation")
N=int(__import__("os").getenv("G6_SHARD_COUNT","8"))
OUT=ROOT/"phase1_g6_production_greeks_report.json"

def main():
    paths=[ROOT/f"phase1_g6_production_greeks_shard_{i:02d}.json" for i in range(N)]
    if not all(p.exists() for p in paths):
        missing=[str(p) for p in paths if not p.exists()]
        raise RuntimeError("G6_SHARD_ARTIFACT_MISSING:"+",".join(missing))
    rs=[json.loads(p.read_text()) for p in paths]
    if any(r.get("status")!="PRODUCTION_SCAN_COMPLETE" for r in rs):
        raise RuntimeError("G6_SHARD_NOT_COMPLETE")
    idx=[r["diagnostics"]["shard_index"] for r in rs]
    if sorted(idx)!=list(range(N)): raise RuntimeError("G6_SHARD_INDEX_INCOMPLETE")
    totals=[r["diagnostics"]["option_files_total"] for r in rs]
    if len(set(totals))!=1: raise RuntimeError("G6_SHARD_FILE_TOTAL_MISMATCH")
    processed=sum(r["diagnostics"]["option_files_processed"] for r in rs)
    if processed!=totals[0]: raise RuntimeError(f"G6_SHARD_FILE_COVERAGE_MISMATCH:{processed}:{totals[0]}")
    keys=list(rs[0]["diagnostics"].keys())
    counters={}
    for k in keys:
        if k in {"option_files_total","shard_index","shard_count","option_files_processed"}: continue
        vals=[r["diagnostics"].get(k,0) for r in rs]
        counters[k]=sum(vals) if all(isinstance(v,(int,float)) for v in vals) else vals
    counters["option_files_total"]=totals[0]
    counters["option_files"]=totals[0]
    counters["option_files_processed"]=processed
    counters["shard_count"]=N
    counters["shard_index"]="ALL"
    base=rs[0]
    for r in rs[1:]:
        for k in ["underlying_rows","rate_coverage","dividend_coverage","checksums"]:
            if r.get(k)!=base.get(k): raise RuntimeError("G6_SHARD_SHARED_EVIDENCE_MISMATCH:"+k)
    for r in rs:
        nla=r.get("no_lookahead_audit")
        if not nla or not nla.get("r_strict_prior_only") or not nla.get("q_strict_prior_only"):
            raise RuntimeError("G6_NO_LOOKAHEAD_AUDIT_FAILURE")
    def merge_hist(key):
        edges=base["greek_distributions"][key]["bin_edges"]
        counts=np.zeros(len(edges)-1,dtype=np.int64)
        for r in rs:
            rr=r["greek_distributions"][key]
            if rr["bin_edges"]!=edges: raise RuntimeError("G6_SHARD_HISTOGRAM_EDGE_MISMATCH:"+key)
            counts+=np.asarray(rr["counts"],dtype=np.int64)
        return {"bin_edges":edges,"counts":counts.tolist()}
    dist={k:merge_hist(k) for k in ["signed_delta_histogram","absolute_delta_histogram","iv_histogram","iv_iteration_histogram","iv_residual_log10_histogram"]}
    if sum(dist["iv_iteration_histogram"]["counts"])!=counters["iv_converged"]:
        raise RuntimeError("G6_IV_ITERATION_EVIDENCE_MISMATCH")
    if sum(dist["iv_residual_log10_histogram"]["counts"])!=counters["iv_converged"]:
        raise RuntimeError("G6_IV_RESIDUAL_EVIDENCE_MISMATCH")
    tes={}
    for k in base["target_error_summary"]:
        vals=[r["target_error_summary"].get(k,{"count":0,"max_error":0,"mean_error":0}) for r in rs]
        count=sum(v["count"] for v in vals)
        tes[k]={"count":count,
                "max_error":max(v["max_error"] for v in vals) if count else 0,
                "mean_error":sum(v["mean_error"]*v["count"] for v in vals)/count if count else 0}
    expiry_dates=sorted({d for r in rs for d in r.get("expiry_coverage",{}).get("expiry_dates",[])})
    option_dates=sorted({d for r in rs for d in r.get("expiry_coverage",{}).get("option_trading_dates",[])})
    expiry_missing=sum(r.get("expiry_coverage",{}).get("expiry_missing",0) for r in rs)
    expiry_nonpositive=sum(r.get("expiry_coverage",{}).get("expiry_nonpositive_t",0) for r in rs)
    expiry_valid=sum(r.get("expiry_coverage",{}).get("expiry_valid",0) for r in rs)
    lookahead={k:sum(r.get("no_lookahead_audit",{}).get(k,0) for r in rs) for k in ["r_same_day","r_future","q_same_day","q_future"]}
    out=dict(base)
    out["diagnostics"]=counters
    out["target_error_summary"]=tes
    out["greek_distributions"]=dist
    out["expiry_coverage"]={
        "option_trading_date_count":len(option_dates),
        "option_trading_dates":option_dates,
        "expiry_date_count":len(expiry_dates),
        "expiry_dates":expiry_dates,
        "expiry_missing":expiry_missing,
        "expiry_nonpositive_t":expiry_nonpositive,
        "expiry_valid":expiry_valid
    }
    out["no_lookahead_audit"]={
        **lookahead,
        "r_strict_prior_only":lookahead["r_same_day"]==0 and lookahead["r_future"]==0,
        "q_strict_prior_only":lookahead["q_same_day"]==0 and lookahead["q_future"]==0
    }
    out["status"]="PRODUCTION_SCAN_COMPLETE"
    out["aggregation"]={"shards":N,"complete_file_partition":True}
    out["acceptance_decision"]="G6 remains OPEN until independent tester verifies the complete aggregated evidence package, expiry/date coverage, explicit no-lookahead audit and exact-checkout artifact."
    OUT.write_text(json.dumps(out,indent=2))
    print(json.dumps({"status":out["status"],"files":totals[0],"shards":N,"rows":counters["option_rows_scanned"]},indent=2))

if __name__=="__main__":
    main()
