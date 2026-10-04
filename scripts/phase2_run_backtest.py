#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import json
import pandas as pd

from phase2_backtest_engine import BacktestEngine, CostSchedule, EngineConfig, save_outputs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="Normalized option parquet")
    ap.add_argument("--costs",required=True,help="Complete dated cost schedule JSON")
    ap.add_argument("--output",required=True)
    ap.add_argument("--slippage-bps",type=float,default=10.0)
    args=ap.parse_args()

    inp=Path(args.input); out=Path(args.output); costs_path=Path(args.costs)
    bars=pd.read_parquet(inp)
    costs=CostSchedule.from_json(costs_path)
    cfg=EngineConfig(slippage_bps=args.slippage_bps)
    result=BacktestEngine(bars,costs,cfg).run()
    save_outputs(out,result,cfg,[inp,costs_path])
    print(json.dumps({k:int(len(v)) for k,v in result.items()}))

if __name__=="__main__":
    main()
