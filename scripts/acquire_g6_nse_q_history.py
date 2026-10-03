#!/usr/bin/env python3
"""Acquire NIFTY 50 daily dividend yield from the official NSE Indices endpoint.

This is acquisition only. It never substitutes a secondary source and records
the exact response bytes plus SHA-256 for each <=365-day request window.
"""
from __future__ import annotations
import hashlib, json, time
from datetime import date, timedelta
from pathlib import Path
import requests

START=date(2021,1,1); END=date(2026,9,30)
URL="https://www.niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString"
OUT=Path("data/processed/g6/nse_nifty50_pepb_raw.json")
REPORT=Path("data/validation/phase1_g6_nse_q_acquisition.json")

def fetch(a,b):
    cinfo={"name":"NIFTY 50","startDate":a.strftime("%d %b %Y"),"endDate":b.strftime("%d %b %Y"),"indexName":"NIFTY 50"}
    cinfo_text=str(cinfo).replace(chr(34),chr(39))
    payload={"cinfo":cinfo_text}
    headers={"Content-Type":"application/json; charset=utf-8","Accept":"application/json, text/javascript, */*; q=0.01","Referer":"https://www.niftyindices.com/reports/historical-data","Origin":"https://www.niftyindices.com","User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"}
    session=requests.Session(); session.headers.update(headers)
    session.get("https://www.niftyindices.com/reports/historical-data",timeout=60)
    endpoints=["https://www.niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString","https://www.niftyindices.com/BackPage/getpepbHistoricaldataDBtoString"]
    last=None
    for endpoint in endpoints:
        try:
            r=session.post(endpoint,json=payload,timeout=120)
            body=r.content
            if r.status_code==200 and not body.lstrip().startswith(b"<!DOCTYPE") and b"<html" not in body[:1000].lower():
                json.loads(body.decode("utf-8")); return body
            last=f"{endpoint}: status={r.status_code} html={body[:40]!r}"
        except Exception as e: last=f"{endpoint}: {e}"
    raise RuntimeError("NSE_Q_ENDPOINT_ACCESS_FAILURE:"+str(last))
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
