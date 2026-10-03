import json
from pathlib import Path

def test_nse_q_artifact_schema():
    p=Path("data/processed/g6/nse_nifty50_pepb_raw.json")
    if not p.exists(): return
    x=json.loads(p.read_text())
    assert x["source"]=="NSE Indices"
    assert len(x["chunks"])>=6
    for c in x["chunks"]:
        assert c["bytes"]>0 and len(c["sha256"])==64
        assert c["start"]<=c["end"]
