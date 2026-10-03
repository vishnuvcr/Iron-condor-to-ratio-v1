"""Conservative raw-file-level audit for the G9 TBT candidate."""
from __future__ import annotations
import csv, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from huggingface_hub import snapshot_download

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/".cache"/"huggingface_g9_tbt"
HF_CACHE=ROOT/".cache"/"huggingface"
OUT=ROOT/"data"/"validation"/"g9_tbt_candidate_report.json"
REPO_ID="antony9952/Nifty_option_TBT"
REVISION="643b48383839947b5fe3ed9483c9f7c0f167e865"
TS=("timestamp","received_timestamp","feed_timestamp","datetime","date")
INST=("instrument_key","instrument_token","symbol","tradingsymbol","contract")
BID=("bid_price","best_bid","bid")
ASK=("ask_price","best_ask","ask")
BQ=("bid_qty","best_bid_qty","bid_quantity")
AQ=("ask_qty","best_ask_qty","ask_quantity")

def first(row, fields):
    for f in fields:
        if row.get(f) not in (None,""): return str(row[f])
    return None

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1048576),b""): h.update(c)
    return h.hexdigest()

def dtparse(v):
    if not v: return None
    try:
        x=datetime.fromisoformat(v.strip().replace("Z","+00:00"))
        return x
    except ValueError: return None

def inspect(path):
    out={"file":str(path.relative_to(ROOT)),"bytes":path.stat().st_size,
         "sha256":sha256(path),"schema_class":"UNKNOWN","columns":[],"rows":0,
         "rows_with_bid_and_ask":0,"rows_with_bid_ask_qty":0,
         "rows_without_bid_or_ask":0,"invalid_or_crossed_quotes":0,
         "negative_quote_values":0,"parseable_timestamps":0,
         "unparseable_timestamps":0,"naive_timestamps":0,
         "min_timestamp":None,"max_timestamp":None,"observed_dates":[],
         "unique_instrument_count":0,"contract_identity_fields_present":[],
         "missing_contract_identity_rows":0,"out_of_order_rows":0,
         "duplicate_row_count":0,"error":None}
    dates=set(); inst=set(); seen=set(); prev=None
    try:
        with path.open("r",encoding="utf-8",errors="replace",newline="") as fh:
            reader=csv.DictReader(fh); cols=tuple(reader.fieldnames or ())
            out["columns"]=list(cols); low={c.lower() for c in cols}
            hb=any(x in low for x in BID); ha=any(x in low for x in ASK)
            depth=any(x in low for x in ("depth_level","bid_qty","ask_qty"))
            ohlc=any(x in low for x in ("open","high","low","close","ltp"))
            out["schema_class"]="TBT_BID_ASK_DEPTH" if hb and ha and depth else ("BID_ASK" if hb and ha else ("OHLC_LTP_NO_BID_ASK" if ohlc else "OTHER"))
            out["contract_identity_fields_present"]=[x for x in ("expiry","expiry_date","strike","strike_price","option_type","instrument_key","symbol","tradingsymbol") if x in cols]
            for row in reader:
                out["rows"]+=1
                raw=json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(",",":"))
                if raw in seen: out["duplicate_row_count"]+=1
                else: seen.add(raw)
                d=dtparse(first(row,TS))
                if d is None: out["unparseable_timestamps"]+=1
                else:
                    out["parseable_timestamps"]+=1
                    if d.tzinfo is None: out["naive_timestamps"]+=1
                    dates.add(d.date().isoformat())
                    iso=d.isoformat()
                    if out["min_timestamp"] is None or iso<out["min_timestamp"]: out["min_timestamp"]=iso
                    if out["max_timestamp"] is None or iso>out["max_timestamp"]: out["max_timestamp"]=iso
                    if prev is not None and d<prev: out["out_of_order_rows"]+=1
                    prev=d
                iv=first(row,INST)
                if iv: inst.add(iv)
                if any(first(row,(f,)) is None for f in ("expiry","expiry_date")) or any(first(row,(f,)) is None for f in ("strike","strike_price")) or first(row,("option_type",)) is None:
                    out["missing_contract_identity_rows"]+=1
                b,a=first(row,BID),first(row,ASK)
                if b is None or a is None: out["rows_without_bid_or_ask"]+=1
                else:
                    try:
                        bf,af=float(b),float(a); out["rows_with_bid_and_ask"]+=1
                        if bf<0 or af<0: out["negative_quote_values"]+=1
                        if bf>af: out["invalid_or_crossed_quotes"]+=1
                    except ValueError: out["invalid_or_crossed_quotes"]+=1
                if first(row,BQ) is not None and first(row,AQ) is not None: out["rows_with_bid_ask_qty"]+=1
    except Exception as e: out["error"]=f"{type(e).__name__}: {e}"
    out["unique_instrument_count"]=len(inst); out["instrument_keys"]=sorted(inst)[:1000]; out["observed_dates"]=sorted(dates)
    return out

def write(x):
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(x,indent=2,sort_keys=True),encoding="utf-8")

def main():
    result={"status":"UNEXECUTED_ACQUISITION","production_acceptance":"BLOCKED","repository":REPO_ID,"revision":REVISION,
            "acquisition_started_at_utc":datetime.now(timezone.utc).isoformat(),
            "raw_file_reports":[],"blockers":["Every retained raw file must be independently classified.","Full study-window coverage, NIFTY identity, contract reconciliation and licensing remain unproven.","Quote age, validity and deterministic no-leakage execution reconstruction remain unproven."]}
    try:
        local=snapshot_download(repo_id=REPO_ID,repo_type="dataset",revision=REVISION,local_dir=CACHE,cache_dir=HF_CACHE,token=os.environ.get("HF_TOKEN"),allow_patterns=["*.csv"])
        files=sorted(Path(local).rglob("*.csv"))
        if not files:
            result["status"]="ACQUISITION_COMPLETED_NO_RAW_CSV"; result["acquisition_error"]="No CSV files acquired"; write(result); raise SystemExit(result["acquisition_error"])
        reports=[inspect(p) for p in files]
        result.update(status="RAW_FILE_AUDIT_COMPLETE",file_count=len(reports),total_bytes=sum(x["bytes"] for x in reports),
                      total_rows=sum(x["rows"] for x in reports),files_with_bid_ask=sum(x["rows_with_bid_and_ask"]>0 for x in reports),
                      files_with_depth_bid_ask=sum(x["schema_class"]=="TBT_BID_ASK_DEPTH" for x in reports),
                      observed_dates=sorted({d for x in reports for d in x["observed_dates"]}),raw_file_reports=reports)
        write(result)
        print(json.dumps({k:result[k] for k in ("status","file_count","total_rows","files_with_bid_ask","files_with_depth_bid_ask","production_acceptance")},indent=2))
    except SystemExit: raise
    except Exception as e:
        result.update(status="UNEXECUTED_ACQUISITION",acquisition_error=f"{type(e).__name__}: {e}",network_or_environment_limitation=True)
        write(result); raise SystemExit(f"G9 acquisition unexecuted: {type(e).__name__}: {e}")

if __name__=="__main__": main()
