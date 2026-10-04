#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
import pandas as pd, requests

START=date(2021,1,1); END=date(2026,9,30)
ID_START=24000; ID_END=27900
BASES=["https://www.rbi.org.in/scripts/WSSView.aspx?Id={}","https://rbi.org.in/Scripts/WSSView.aspx?Id={}","https://wss.rbi.org.in/Scripts/WSSView.aspx?Id={}"]
RAW=Path("data/raw/g6_sources/rbi_wss")
OUT=Path("data/processed/g6/risk_free.csv")
REPORT=Path("data/validation/phase1_g6_rbi_acquisition.json")

# Immutable source bytes already independently observed during source bootstrap.
# Unknown retained pages are NOT trusted merely because they exist in the cache.
EXPECTED_SHA256={
    26722:"6cc282aecb2a8d4dae72f05a2c1a1ce8d762def294c1c2ca3fcbd34d036030d9",
    26962:"d3958f5db7784eaac61951643cb3b558c7400412efe81822c108bd626c6f711d",
    27637:"7797f60ced3835d611b713e38207968809296a8d05fd48ddb7580a6fb60c48a4",
    27727:"3cb7786a94c252e9a8525c61b2193cd71f5e166e0c1044789bc0b6dab2edca1b",
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def parse_date(x):
    try:
        return pd.to_datetime(str(x).strip(),dayfirst=True,errors="raise").date()
    except Exception:
        return None

def extract(html,sid):
    rows=[]
    for t in pd.read_html(html):
        s=t.astype(str)
        for _,row in s.iterrows():
            if not row.str.contains("91-Day Treasury Bill",case=False,regex=False).any():
                continue
            dates=[parse_date(c) for c in t.columns]
            for k,d in enumerate(dates):
                if d is None or not (START<=d<=END) or k>=len(row):
                    continue
                m=re.search(r"(?<![A-Za-z])\d+(?:\.\d+)?",str(row.iloc[k]))
                if m:
                    # The WSS observation date is retained as the source's
                    # eligibility date. The production join is strictly prior
                    # to the trading date, so same-day use is prohibited.
                    rows.append({"date":d,"yield_pct":float(m.group()),"source_id":sid})
    return rows

def cached_page(sid):
    p=RAW/f"wss_{sid}.html"
    meta=RAW/f"wss_{sid}.json"
    if not p.exists() or not meta.exists():
        return None
    try:
        b=p.read_bytes()
        m=json.loads(meta.read_text())
        observed=sha(b)
        recorded=m.get("sha256")
        expected=EXPECTED_SHA256.get(sid)
        if not recorded or recorded!=observed:
            raise RuntimeError(f"CACHE_SHA_MISMATCH:{sid}")
        if expected is not None and observed!=expected:
            raise RuntimeError(f"CACHE_EXPECTED_SHA_MISMATCH:{sid}")
        if m.get("source_id")!=sid:
            raise RuntimeError(f"CACHE_SOURCE_ID_MISMATCH:{sid}")
        rows=extract(b.decode("utf-8",errors="replace"),sid)
        if not rows:
            raise RuntimeError(f"CACHE_TARGET_SERIES_MISSING:{sid}")
        return {"id":sid,"status":"CACHE_HIT_VALIDATED","bytes":len(b),"sha256":observed,
                "url":m.get("url"),"rows":len(rows)},rows
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"CACHE_VALIDATION_ERROR:{sid}:{e}")

def fetch_one(sid):
    cached=cached_page(sid)
    if cached is not None:
        return cached
    # A retained file without immutable provenance is never silently trusted.
    if (RAW/f"wss_{sid}.html").exists() or (RAW/f"wss_{sid}.json").exists():
        raise RuntimeError(f"CACHE_PROVENANCE_MISSING:{sid}")
    for base in BASES:
        u=base.format(sid)
        try:
            r=requests.get(u,headers={"User-Agent":"Iron-condor-to-ratio-v1-research/1.0"},timeout=10)
            if r.status_code==200 and b"91-Day Treasury Bill (Primary) Yield" in r.content:
                b=r.content
                rr=extract(r.text,sid)
                if not rr:
                    continue
                RAW.mkdir(parents=True,exist_ok=True)
                (RAW/f"wss_{sid}.html").write_bytes(b)
                (RAW/f"wss_{sid}.json").write_text(json.dumps({
                    "source_id":sid,"url":u,"retrieved_at":"runtime","sha256":sha(b),
                    "observation_date_semantics":"RBI WSS labelled observation date; used conservatively as eligibility date; same-day trading use is prohibited by strict-prior join."
                },indent=2))
                return {"id":sid,"url":u,"status_code":r.status_code,"bytes":len(b),
                        "sha256":sha(b),"rows":len(rr),"status":"NETWORK_ACQUIRED"},rr
        except Exception:
            pass
    return {"id":sid,"status":"NO_TARGET_ALL_BASES"},[]

def main():
    RAW.mkdir(parents=True,exist_ok=True); OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    pages=[]; allrows=[]; errors=[]
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures=[ex.submit(fetch_one,sid) for sid in range(ID_START,ID_END+1)]
        for fut in as_completed(futures):
            try:
                rec,rr=fut.result(); pages.append(rec); allrows.extend(rr)
            except Exception as e:
                errors.append(str(e))
    df=pd.DataFrame(allrows)
    if df.empty:
        status_counts={}
        for x in pages:
            key=x.get("status","UNKNOWN") if x else "UNKNOWN"
            status_counts[key]=status_counts.get(key,0)+1
        REPORT.write_text(json.dumps({"status":"RBI_PRIMARY_ACCESS_FAILED","study_start":str(START),"study_end":str(END),
            "status_counts":status_counts,"errors":errors,"pages":pages,
            "no_lookahead":"source observation date is used only as a conservative eligibility date; strict-prior excludes same-day observations"},indent=2,default=str))
        raise RuntimeError("RBI_NO_91D_TBILL_ROWS")
    df["date"]=pd.to_datetime(df["date"],errors="coerce").dt.date
    df=df[(df.date>=START)&(df.date<=END)].sort_values("date")
    if df.empty:
        raise RuntimeError("RBI_NO_STUDY_WINDOW_ROWS")
    g=df.groupby("date").yield_pct.agg(["min","max"])
    if (g["min"]!=g["max"]).any():
        raise RuntimeError("RBI_CONFLICTING_DUPLICATES")
    df=df.drop_duplicates("date",keep="first")[["date","yield_pct"]]
    df.to_csv(OUT,index=False)
    REPORT.write_text(json.dumps({"status":"ACQUISITION_COMPLETE","study_start":str(START),"study_end":str(END),
      "source_pages_with_target":sum(1 for x in pages if x and x.get("rows",0)>0),"rows":len(df),
      "min_date":str(df.date.min()),"max_date":str(df.date.max()),"output_sha256":sha(OUT.read_bytes()),
      "cache_hits":sum(1 for x in pages if x and x.get("status")=="CACHE_HIT_VALIDATED"),
      "network_acquired":sum(1 for x in pages if x and x.get("status")=="NETWORK_ACQUIRED"),
      "errors":errors,"pages":pages,
      "no_lookahead":"source observation date is used only as a conservative eligibility date; strict-prior excludes same-day observations"},indent=2,default=str))

if __name__=="__main__":
    main()
