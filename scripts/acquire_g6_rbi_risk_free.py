#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,time
from datetime import date
from pathlib import Path
import pandas as pd, requests

START=date(2021,1,1); END=date(2026,9,30)
ID_START=25000; ID_END=27900
BASE="https://www.rbi.org.in/scripts/WSSView.aspx?Id={}"
RAW=Path("data/raw/g6_sources/rbi_wss")
OUT=Path("data/processed/g6/risk_free.csv")
REPORT=Path("data/validation/phase1_g6_rbi_acquisition.json")

def sha(b): return hashlib.sha256(b).hexdigest()

def parse_date(x):
    try: return pd.to_datetime(str(x).strip(),dayfirst=True,errors="raise").date()
    except Exception: return None

def extract(html,sid):
    rows=[]
    for t in pd.read_html(html):
        s=t.astype(str)
        for i,row in s.iterrows():
            if not row.str.contains("91-Day Treasury Bill",case=False,regex=False).any(): continue
            # WSS tables normally have the observation dates in column headers.
            dates=[parse_date(c) for c in t.columns]
            for k,d in enumerate(dates):
                if d is None or not (START<=d<=END) or k>=len(row): continue
                m=re.search(r"(?<![A-Za-z])\d+(?:\.\d+)?",str(row.iloc[k]))
                if m: rows.append({"date":d,"yield_pct":float(m.group()),"source_id":sid})
    return rows

def main():
    RAW.mkdir(parents=True,exist_ok=True); OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    s=requests.Session(); s.headers.update({"User-Agent":"Iron-condor-to-ratio-v1-research/1.0"})
    pages=[]; allrows=[]; hits=0
    for sid in range(ID_START,ID_END+1):
        u=BASE.format(sid)
        try:
            r=s.get(u,timeout=20)
            if r.status_code!=200 or b"91-Day Treasury Bill (Primary) Yield" not in r.content: continue
            b=r.content; hits+=1
            (RAW/f"wss_{sid}.html").write_bytes(b)
            rr=extract(r.text,sid)
            pages.append({"id":sid,"url":u,"bytes":len(b),"sha256":sha(b),"rows":len(rr)})
            allrows.extend(rr)
        except Exception as e:
            pages.append({"id":sid,"url":u,"error":str(e)})
        if sid%50==0: time.sleep(.25)
    df=pd.DataFrame(allrows)
    if df.empty: raise RuntimeError("RBI_NO_91D_TBILL_ROWS")
    df["date"]=pd.to_datetime(df["date"],errors="coerce").dt.date
    df=df[(df.date>=START)&(df.date<=END)].sort_values("date")
    if df.empty: raise RuntimeError("RBI_NO_STUDY_WINDOW_ROWS")
    g=df.groupby("date").yield_pct.agg(["min","max"])
    if (g["min"]!=g["max"]).any(): raise RuntimeError("RBI_CONFLICTING_DUPLICATES")
    df=df.drop_duplicates("date",keep="first")[["date","yield_pct"]]
    df.to_csv(OUT,index=False)
    REPORT.write_text(json.dumps({"status":"ACQUISITION_COMPLETE","study_start":str(START),"study_end":str(END),
      "source_pages_with_target":hits,"rows":len(df),"min_date":str(df.date.min()),"max_date":str(df.date.max()),
      "output_sha256":sha(OUT.read_bytes()),"pages":pages},indent=2,default=str))
if __name__=="__main__": main()
