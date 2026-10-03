import hashlib,json,subprocess
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

RAW=Path("data/raw"); INDEX=RAW/"index"/"NIFTY.parquet"; RULES=Path("data/manifests/phase1_session_rules.json")
OUT=Path("data/validation/phase1_g5_failure_isolation.json")
KEY=["timestamp","expiry","strike","option_type"]

def ts(s): return pd.to_datetime(s,utc=True,errors="coerce")
def minute(v): h,m=map(int,v.split(":")); return 60*h+m
def eligible(t,r):
    x=t.tz_convert(r["timezone"]); d=x.strftime("%Y-%m-%d"); m=x.hour*60+x.minute
    sp={z["date"]:z for z in r["special_sessions"]}; dc={z["date"]:z for z in r["date_controls"]}
    if d in sp: return any(minute(a)<=m<=minute(b) for a,b in sp[d]["execution_intervals"])
    c=dc.get(d)
    if c and c["expected_classification"]=="DATA_GAP_EXCLUDED": return False
    return minute(r["regular_execution_session"]["start"])<=m<=minute(r["regular_execution_session"]["end"])

def file_range(p):
    pf=pq.ParquetFile(p); lo=hi=None
    for i in range(pf.num_row_groups):
        x=ts(pf.read_row_group(i,columns=["timestamp"]).to_pandas()["timestamp"]).dropna()
        if len(x):
            a,b=x.min(),x.max(); lo=a if lo is None or a<lo else lo; hi=b if hi is None or b>hi else hi
    return lo,hi

def main():
    rules=json.loads(RULES.read_text())
    idx=pd.read_parquet(INDEX,columns=["timestamp"]); idx["timestamp"]=ts(idx["timestamp"])
    if idx["timestamp"].isna().any(): raise SystemExit("invalid NIFTY timestamp")
    idxset=set(idx["timestamp"]); byday={}
    for t in idx["timestamp"]:
        d=t.tz_convert(rules["timezone"]).strftime("%Y-%m-%d"); byday.setdefault(d,[]).append(t)
    for d in byday: byday[d].sort()
    files=sorted((RAW/"options"/"NIFTY").glob("*.parquet"))
    ranges=[]; expiry_partition=[]
    for p in files:
        lo,hi=file_range(p)
        ranges.append({"file":str(p.relative_to(RAW)),"min":str(lo),"max":str(hi)})
        vals=pd.read_parquet(p,columns=["expiry"])["expiry"].dropna().astype(str).unique().tolist()
        stem=p.stem
        expiry_partition.append({"file":str(p.relative_to(RAW)),"filename_expiry":stem,"unique_expiry_values":vals,"partition_matches_filename":(len(vals)==1 and vals[0]==stem)})
    ranges.sort(key=lambda z:z["min"]); overlaps=[]
    for a,b in zip(ranges,ranges[1:]):
        if a["max"]>=b["min"]: overlaps.append({"a":a["file"],"b":b["file"],"a_max":a["max"],"b_min":b["min"]})
    total=0; dates={}; freq={}; examples=[]; seconds={}
    for p in files:
        df=pd.read_parquet(p,columns=KEY); df["timestamp"]=ts(df["timestamp"])
        df=df.dropna(subset=["timestamp"]).drop_duplicates(KEY,keep="first")
        mask=df["timestamp"].map(lambda t: eligible(t,rules)) & ~df["timestamp"].isin(idxset)
        miss=df.loc[mask].copy()
        if miss.empty: continue
        total+=len(miss); miss["day"]=miss["timestamp"].dt.tz_convert(rules["timezone"]).dt.strftime("%Y-%m-%d")
        for d,g in miss.groupby("day"):
            q=dates.setdefault(d,{"missing_row_count":0,"unique_missing_timestamps":0,"examples":[]})
            q["missing_row_count"]+=len(g); q["unique_missing_timestamps"]+=g["timestamp"].nunique()
            q["examples"]+=list(map(str,g["timestamp"].drop_duplicates().head(max(0,20-len(q["examples"])))))
        for t,n in miss["timestamp"].value_counts().items(): freq[str(t)]=freq.get(str(t),0)+int(n)
        for t in miss["timestamp"].drop_duplicates().head(200):
            x=t.tz_convert(rules["timezone"]); d=x.strftime("%Y-%m-%d"); arr=byday.get(d,[])
            prev=max((z for z in arr if z<t),default=None); nxt=min((z for z in arr if z>t),default=None)
            k=str(t); seconds[k]={"day":d,"minute":int(x.hour*60+x.minute),"second":int(x.second),"microsecond":int(x.microsecond),"prev_nifty":str(prev),"next_nifty":str(nxt),"nifty_day_rows":len(arr)}
            if len(examples)<100: examples.append({"timestamp":k,"day":d,"prev_nifty":str(prev),"next_nifty":str(nxt)})
    out={"execution_provenance":{"checked_out_commit_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()},
         "frozen_failed_evidence":{"run":37148487963,"job":111277213347,"artifact":11284131045,"artifact_sha256":"30381036630380820693858817bea51be4fae82896e01eb98cf09dba61fd95fb","missing_rows":521069},
         "recomputed_missing_row_count":total,"affected_date_count":len(dates),"affected_dates":dates,
         "diagnostic_field_semantics":{"missing_row_count":"eligible option rows lacking exact NIFTY timestamp","unique_missing_timestamps":"distinct eligible option timestamps lacking exact NIFTY timestamp","decision_timestamps":"not emitted; use unique_decision_timestamps if added by a future diagnostic","aligned_decision_timestamps":"not emitted; use unique_aligned_timestamps if added by a future diagnostic"},
         "missing_timestamp_frequency_top100":sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:100],
         "timestamp_diagnostics":seconds,"examples":examples,
         "option_file_timestamp_ranges":ranges,"overlapping_option_file_ranges":overlaps,"expiry_partition_checks":expiry_partition,"all_files_single_expiry_matching_filename":all(x["partition_matches_filename"] for x in expiry_partition),
         "classification_notes":{"underlying_source_gap":"Requires within-day NIFTY coverage and neighbor-gap evidence; absence alone is not classified as a source gap.","option_source_timestamp_irregularity":"Seconds/microseconds and neighbor distances are reported; no correction is applied.","session_calendar":"Eligibility is recomputed only from phase1_session_rules.json.","cross_file_duplicates":"Non-overlap of timestamp ranges establishes partition separation; overlap requires global key audit.","dataset_discontinuity":"Large clusters are retained, not excluded."},
         "acceptance":{"diagnostic_only":True,"exact_timestamp_requirement":1.0,"no_interpolation":True,"no_forward_fill":True}}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2))
    print(json.dumps({"recomputed_missing_row_count":total,"affected_dates":len(dates),"overlap_pairs":len(overlaps)},indent=2))
    if total==0: raise SystemExit("Frozen failure could not be reproduced")
if __name__=="__main__": main()
