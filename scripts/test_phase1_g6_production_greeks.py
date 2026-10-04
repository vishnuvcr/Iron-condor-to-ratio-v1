import math
import numpy as np
from phase1_g6_production_greeks import (
    bs_price, bs_delta, bs_delta_arrays, solve_iv_arrays, strict_prior, expiry_close
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
    assert out.loc[out["date"]==__import__("pandas").Timestamp("2024-01-02"),"source_date"].iloc[0]==__import__("pandas").Timestamp("2024-01-01")

def test_expiry_close_convention():
    assert expiry_close("2025-10-28")==__import__("pandas").Timestamp("2025-10-28 15:30:00")


def test_strict_prior_is_conservative_against_same_day_observation():
    import pandas as pd
    src=pd.DataFrame({"date":pd.to_datetime(["2024-01-03"]),"r":[0.07]})
    out=strict_prior(pd.to_datetime(["2024-01-03","2024-01-04"]),src)
    assert pd.isna(out.loc[out["date"]==pd.Timestamp("2024-01-03"),"r"].iloc[0])
    assert out.loc[out["date"]==pd.Timestamp("2024-01-04"),"r"].iloc[0]==0.07


def test_target_delta_keys_use_canonical_two_decimal_format():
    targets=[0.30,0.10,0.50,0.40,0.08]
    keys={f"{t:.2f}" for t in targets}
    assert keys == {"0.30","0.10","0.50","0.40","0.08"}


def test_vectorized_delta_matches_scalar():
    s=np.array([18000.0,18000.0]); k=np.array([18000.0,18200.0]); t=np.array([30/365.0,30/365.0])
    r=np.array([0.06,0.06]); q=np.array([0.01,0.01]); iv=np.array([0.20,0.25]); kind=np.array([1,2])
    got=bs_delta_arrays(s,k,t,r,q,iv,kind)
    exp=np.array([bs_delta(float(a),float(b),float(c),float(d),float(e),float(g),int(h)) for a,b,c,d,e,g,h in zip(s,k,t,r,q,iv,kind)])
    assert np.allclose(got,exp,rtol=1e-12,atol=1e-12)


def test_g6_shard_configuration_is_valid():
    from phase1_g6_production_greeks import SHARD_INDEX, SHARD_COUNT
    assert SHARD_COUNT >= 1
    assert 0 <= SHARD_INDEX < SHARD_COUNT


def test_sha256_file_uses_bound_chunk_variable(tmp_path):
    from phase1_g6_production_greeks import sha256_file
    p=tmp_path/"x.bin"
    p.write_bytes(b"abc"*1000)
    import hashlib
    assert sha256_file(p)==hashlib.sha256(b"abc"*1000).hexdigest()


def test_strict_prior_source_date_is_strictly_earlier():
    import pandas as pd
    src=pd.DataFrame({"date":pd.to_datetime(["2024-01-02","2024-01-03"]),"r":[0.06,0.07]})
    out=strict_prior(pd.to_datetime(["2024-01-02","2024-01-03","2024-01-04"]),src)
    assert pd.isna(out.loc[out["date"]==pd.Timestamp("2024-01-02"),"source_date"].iloc[0])
    assert out.loc[out["date"]==pd.Timestamp("2024-01-03"),"source_date"].iloc[0]==pd.Timestamp("2024-01-02")
    assert out.loc[out["date"]==pd.Timestamp("2024-01-04"),"source_date"].iloc[0]==pd.Timestamp("2024-01-03")
