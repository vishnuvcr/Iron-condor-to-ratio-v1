#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import requests

OUT = Path("data/raw/index/NIFTY.parquet")
META = Path("data/raw/index/NIFTY.provenance.json")
URL = "https://huggingface.co/datasets/thetrademarkk/india-index-options-1m/resolve/92e0288/index/NIFTY.parquet?download=true"
EXPECTED_SHA256 = "613864738250107807354c17c7092986960220ac3062b830c65cc5f9ec16fcf7"
REVISION = "92e0288"

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    cache_hit=False
    if OUT.exists() and META.exists():
        m=json.loads(META.read_text())
        if m.get("revision")!=REVISION or m.get("expected_sha256")!=EXPECTED_SHA256:
            raise RuntimeError("NIFTY_CACHE_PROVENANCE_MISMATCH")
        actual=sha256_file(OUT)
        if actual!=EXPECTED_SHA256 or m.get("sha256")!=actual:
            raise RuntimeError("NIFTY_CACHE_SHA256_MISMATCH")
        cache_hit=True
    else:
        headers={"User-Agent":"Iron-condor-to-ratio-v1-research/1.0"}
        token=os.getenv("HF_TOKEN","")
        if token:
            headers["Authorization"]=f"Bearer {token}"
        r=requests.get(URL,headers=headers,timeout=120)
        r.raise_for_status()
        OUT.write_bytes(r.content)
        actual=sha256_file(OUT)
        if actual!=EXPECTED_SHA256:
            OUT.unlink(missing_ok=True)
            raise RuntimeError(f"NIFTY_IMMUTABLE_SHA256_MISMATCH:{actual}")
        META.write_text(json.dumps({
            "source":"Hugging Face dataset thetrademarkk/india-index-options-1m",
            "revision":REVISION,
            "url":URL,
            "expected_sha256":EXPECTED_SHA256,
            "sha256":actual,
            "retrieved_at":"runtime",
        },indent=2))
    print(json.dumps({"status":"CACHE_HIT_VALIDATED" if cache_hit else "NETWORK_ACQUIRED",
                      "path":str(OUT),"revision":REVISION,"sha256":sha256_file(OUT)},indent=2))

if __name__=="__main__":
    main()
