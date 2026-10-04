#!/usr/bin/env python3
from __future__ import annotations
import concurrent.futures, hashlib, json, os
from pathlib import Path
import requests

ROOT=Path("data/raw/options/NIFTY")
MANIFEST=ROOT/"hf_manifest.json"
API="https://huggingface.co/api/datasets/thetrademarkk/india-index-options-1m/tree/0f4800e/options/NIFTY?recursive=true&expand=true&limit=1000"
BASE="https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/resolve/0f4800e/"
REVISION="0f4800e"

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def get_headers():
    h={"User-Agent":"Iron-condor-to-ratio-v1-research/1.0"}
    tok=os.getenv("HF_TOKEN","")
    if tok: h["Authorization"]=f"Bearer {tok}"
    return h

def list_files():
    r=requests.get(API,headers=get_headers(),timeout=60)
    r.raise_for_status()
    rows=r.json()
    files=[]
    for x in rows:
        p=x.get("path","")
        if p.endswith(".parquet") and p.startswith("options/NIFTY/"):
            lfs=x.get("lfs") or {}
            files.append({"path":p,"sha256":lfs.get("sha256"),"size":x.get("size")})
    if not files: raise RuntimeError("HF_NIFTY_OPTIONS_FILE_LIST_EMPTY")
    return sorted(files,key=lambda x:x["path"])

def fetch_one(meta):
    rel=meta["path"].split("options/NIFTY/",1)[1]
    out=ROOT/rel
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and meta.get("sha256"):
        if sha256(out)==meta["sha256"]:
            return {"path":meta["path"],"status":"CACHE_HIT_VALIDATED","sha256":meta["sha256"],"size":out.stat().st_size}
        out.unlink()
    url=BASE+meta["path"]
    r=requests.get(url,headers=get_headers(),timeout=120)
    r.raise_for_status()
    out.write_bytes(r.content)
    actual=sha256(out)
    expected=meta.get("sha256")
    if expected and actual!=expected:
        out.unlink(missing_ok=True)
        raise RuntimeError(f"HF_OPTION_SHA256_MISMATCH:{meta['path']}:{actual}:{expected}")
    return {"path":meta["path"],"status":"NETWORK_ACQUIRED","sha256":actual,"size":out.stat().st_size}

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    files=list_files()
    results=[]; errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(fetch_one,m):m for m in files}
        for fut in concurrent.futures.as_completed(futs):
            try: results.append(fut.result())
            except Exception as e: errors.append(str(e))
    if errors: raise RuntimeError("HF_NIFTY_OPTIONS_ACQUISITION_FAILED:"+json.dumps(errors[:20]))
    results.sort(key=lambda x:x["path"])
    MANIFEST.write_text(json.dumps({"revision":REVISION,"api":API,"files":files,"results":results},indent=2))
    print(json.dumps({"revision":REVISION,"files":len(results),
                      "cache_hits":sum(r["status"]=="CACHE_HIT_VALIDATED" for r in results),
                      "network_acquired":sum(r["status"]=="NETWORK_ACQUIRED" for r in results),
                      "bytes":sum(r["size"] for r in results)},indent=2))

if __name__=="__main__":
    main()
