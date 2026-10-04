#!/usr/bin/env python3
from datetime import date
import pandas as pd

from phase2_backtest_engine import (
    BacktestEngine, ChargeRule, CostSchedule, EngineConfig, adverse_fill, normalize_bars
)

def cost_schedule():
    rules=[]
    for ct in ["BROKERAGE","NSE_TRANSACTION","IPFT","SEBI","STT","STAMP_DUTY"]:
        rules.append(ChargeRule(ct,date(2020,1,1),None,rate=0.0,taxable=(ct in {"BROKERAGE","NSE_TRANSACTION","IPFT","SEBI"})))
    rules[0]=ChargeRule("BROKERAGE",date(2020,1,1),None,fixed_per_order=20.0,taxable=True)
    return CostSchedule(rules,gst_rate=0.18)

def make_row(ts, expiry, strike, ot, d, op, cp, session=True):
    return {
        "timestamp":ts,"expiry":expiry,"strike":strike,"option_type":ot,
        "open":op,"close":cp,"volume":1000,"underlying":20000.0,
        "abs_delta":d,"tick_size":0.05,"lot_size":75,
        "session_eligible":session,"execution_eligible":session,
        "expiry_close_ts":pd.Timestamp(expiry, tz="Asia/Kolkata").replace(hour=15, minute=30)
    }

def fixture():
    rows=[]
    expiry=pd.Timestamp("2025-10-30")
    t0=pd.Timestamp("2025-10-01 09:15:00",tz="Asia/Kolkata")
    t1=t0+pd.Timedelta(minutes=1)
    t2=t0+pd.Timedelta(minutes=2)
    # IC targets
    contracts=[
        ("CE",19000,0.30,100.0),("CE",21000,0.10,50.0),
        ("PE",19000,0.10,50.0),("PE",21000,0.30,100.0),
        # Down ratio
        ("CE",20000,0.50,120.0),("CE",20500,0.40,90.0),("CE",22000,0.10,25.0),
    ]
    for ts in [t0,t1,t2]:
        for ot,k,d,p in contracts:
            cur_d=d
            if ts==t1 and (ot,k)==("CE",19000): cur_d=0.09
            rows.append(make_row(ts,expiry,k,ot,cur_d,p,p-1))
    return pd.DataFrame(rows)

def test_slippage_floor_and_rejection():
    assert adverse_fill(100.0,"BUY",0.05,10)==100.05
    assert adverse_fill(100.0,"SELL",0.05,10)==99.95
    assert adverse_fill(0.05,"SELL",0.05,20000) is None

def test_engine_enters_ic_and_transitions():
    engine=BacktestEngine(fixture(),cost_schedule(),EngineConfig(entry_min_dte_days=1,slippage_bps=0))
    result=engine.run()
    assert (result["events"]["event_type"]=="ENTER_IRON_CONDOR").any()
    assert (result["events"]["event_type"]=="TRANSITION_TO_RATIO").any()
    ev=result["events"]
    tr=ev[ev["event_type"]=="TRANSITION_TO_RATIO"].iloc[0]
    assert tr["execution_status"]=="FILLED"
    assert tr["post_state"]=="RATIO"

def test_missing_next_bar_fails_group_without_partial_fill():
    df=fixture()
    # Remove one contract's next bar so the initial entry is incomplete.
    t1=pd.Timestamp("2025-10-01 09:16:00",tz="Asia/Kolkata")
    mask=~((df["timestamp"]==t1)&(df["option_type"]=="PE")&(df["strike"]==21000))
    df=df[mask]
    engine=BacktestEngine(df,cost_schedule(),EngineConfig(entry_min_dte_days=1,slippage_bps=0))
    result=engine.run()
    assert (result["events"]["execution_status"]=="FAILED_INCOMPLETE_EXECUTION").any()
    assert result["fills"].empty

def test_costs_are_required():
    df=fixture()
    incomplete=CostSchedule([],gst_rate=0.18)
    engine=BacktestEngine(df,incomplete,EngineConfig(entry_min_dte_days=1,slippage_bps=0))
    try:
        engine.run()
    except RuntimeError as exc:
        assert "COST_RULE_RESOLUTION_FAILURE" in str(exc)
    else:
        raise AssertionError("missing cost schedule did not fail closed")

def test_transition_missing_target_is_consumed():
    df=fixture()
    t1=pd.Timestamp("2025-10-01 09:16:00",tz="Asia/Kolkata")
    bad=(df["timestamp"]==t1) & (df["option_type"]=="CE") & df["strike"].isin([20000,20500,22000])
    df=df[~bad]
    engine=BacktestEngine(df,cost_schedule(),EngineConfig(entry_min_dte_days=1,slippage_bps=0))
    result=engine.run()
    tr=result["events"][result["events"]["event_type"]=="TRANSITION_TO_RATIO"].iloc[0]
    assert tr["execution_status"]=="FAILED_INCOMPLETE_EXECUTION"
    assert tr["trigger_consumed"]
    assert tr["post_state"]=="IRON_CONDOR"
def test_transition_missing_target_is_consumed():
    df=fixture()
    t1=pd.Timestamp("2025-10-01 09:16:00",tz="Asia/Kolkata")
    bad=(df["timestamp"]==t1) & (df["option_type"]=="CE") & df["strike"].isin([20000,20500,22000])
    df=df[~bad]
    engine=BacktestEngine(df,cost_schedule(),EngineConfig(entry_min_dte_days=1,slippage_bps=0))
    result=engine.run()
    tr=result["events"][result["events"]["event_type"]=="TRANSITION_TO_RATIO"].iloc[0]
    assert tr["execution_status"]=="FAILED_INCOMPLETE_EXECUTION"
    assert tr["trigger_consumed"]
    assert tr["post_state"]=="IRON_CONDOR"

if __name__=="__main__":
    for fn in [test_slippage_floor_and_rejection,test_engine_enters_ic_and_transitions,
               test_missing_next_bar_fails_group_without_partial_fill,test_costs_are_required,test_transition_missing_target_is_consumed]:
        fn()
    print("phase2 engine tests passed")


def test_naive_timestamps_are_interpreted_as_ist():
    df = fixture()
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df["expiry_close_ts"] = df["expiry_close_ts"].dt.tz_localize(None)
    out = normalize_bars(df)
    assert str(out.loc[0, "timestamp"]) == "2025-10-01 09:15:00+05:30"
    assert str(out.loc[0, "expiry_close_ts"].utcoffset()) == "5:30:00"
