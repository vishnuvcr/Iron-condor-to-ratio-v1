import math
import numpy as np
from phase1_g6_production_greeks import (
    bs_price, bs_delta, solve_iv_arrays, strict_prior, expiry_close
)

def test_call_put_parity_shapes():
    s,k,t,r,q,sigma=100.0,100.0,30/365,0.06,0.01,0.20
    c=bs_price(s,k,t,r,q,sigma,1); p=bs_price(s,k,t,r,q,sigma,2)
    assert abs((c-p)-(s*math.exp(-q*t)-k*math.exp(-r*t)))<1e-10

def test_delta_signs():
    args=(100.0,100.0,30/365,0.06,0.01,0.20)
    assert 0 < bs_delta(*args,1) < 1
    assert -1 < bs_delta(*args,2) < 0

def test_brent_iv_round_trip():
    s,k,t,r,q,sigma=100.0,105.0,45/365,0.06,0.01,0.25
    premium=bs_price(s,k,t,r,q,sigma,1)
    iv,it,res,code=solve_iv_arrays(
        np.array([s]),np.array([k]),np.array([t]),np.array([r]),
        np.array([q]),np.array([premium]),np.array([1],dtype=np.int64))
    assert code[0]==6
    assert abs(iv[0]-sigma)<1e-7
    assert it[0]>0
    assert res[0]<=1e-8

def test_invalid_premium_fails_closed():
    iv,it,res,code=solve_iv_arrays(
        np.array([100.]),np.array([100.]),np.array([30/365]),np.array([.06]),
        np.array([.01]),np.array([0.]),np.array([1],dtype=np.int64))
    assert np.isnan(iv[0]) and code[0]==2

def test_no_arbitrage_rejection():
    iv,it,res,code=solve_iv_arrays(
        np.array([100.]),np.array([100.]),np.array([30/365]),np.array([.06]),
        np.array([.01]),np.array([200.]),np.array([1],dtype=np.int64))
    assert np.isnan(iv[0]) and code[0]==3

def test_strict_prior_never_uses_same_day():
    left=np.array([np.datetime64("2024-01-02"),np.datetime64("2024-01-03")])
    src=__import__("pandas").DataFrame({
        "date":__import__("pandas").to_datetime(["2024-01-02","2024-01-01"]),
        "r":[.07,.06],
    })
    out=strict_prior(left,src)
    assert out.loc[out["date"]==__import__("pandas").Timestamp("2024-01-02"),"r"].iloc[0]==.06
    assert out.loc[out["date"]==__import__("pandas").Timestamp("2024-01-03"),"r"].iloc[0]==.07

def test_expiry_close_convention():
    assert expiry_close("2025-10-28")==__import__("pandas").Timestamp("2025-10-28 15:30:00")
