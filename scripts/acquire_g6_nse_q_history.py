#!/usr/bin/env python3
"""Acquire NIFTY 50 daily dividend yield from the official NSE Indices endpoint.

This is acquisition only. It never substitutes a secondary source and records
the exact response bytes plus SHA-256 for each <=365-day request window.
"""
from __future__ import annotations
import hashlib, json, time
from datetime import date, timedelta
from pathlib import Path
from urllib.request import Request, urlopen

START=date(2021,1,1); END=date(2026,9,30)
URL="https://www.niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString"
OUT=Path("data/processed/g6/nse_nifty50_pepb_raw.json")
REPORT=Path("data/validation/phase1_g6_nse_q_acquisition.json")

def fetch(a,b):
    cinfo={"name":"NIFTY 50","startDate":a.strftime("%d %b %Y"),"endDate":b.strftime("%d %b %Y"),"indexName":"NIFTY 50"}
    payload=json.dumps({"cinfo":json.dumps(cinfo,separators=(",",":"))}).encode()
    req=Request(URL,data=payload,headers={
        "Content-Type":"application/json; charset=utf-8",
        "Referer":"https://www.niftyindices.com/reports/historical-data",
        "Origin":"https://www.niftyindices.com",
        "User-Agent":"Iron-condor-to-ratio-v1-research/1.0"})
    with urlopen(req,timeout=120) as r: return r.read()

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    chunks=[]; cur=START
    while cur<=END:
        nxt=min(cur+timedelta(days=364),END)
        try:
            raw=fetch(cur,nxt)
            rec={"start":cur.isoformat(),"end":nxt.isoformat(),"sha256":sha(raw),"bytes":len(raw),
                 "payload":raw.decode("utf-8")}
            chunks.append(rec)
        except Exception as e:
            REPORT.write_text(json.dumps({"status":"ACQUISITION_FAILED","error":str(e),"chunks_completed":len(chunks)},indent=2))
            raise
        cur=nxt+timedelta(days=1); time.sleep(0.75)
    OUT.write_text(json.dumps({"source":"NSE Indices","endpoint":URL,"study_start":START.isoformat(),
                               "study_end":END.isoformat(),"chunks":chunks},indent=2))
    REPORT.write_text(json.dumps({"status":"ACQUISITION_COMPLETE","source":"official_nse_indices",
                                  "chunks":len(chunks),"sha256":sha(OUT.read_bytes()),
                                  "study_start":START.isoformat(),"study_end":END.isoformat()},indent=2))

if __name__=="__main__": main()
