from scripts.phase1_g6_production_greeks import bs_price, bs_delta, implied_vol

def test_call_put_parity_shapes():
    s,k,t,r,q,sigma=100.0,100.0,30/365,0.06,0.01,0.20
    c=bs_price(s,k,t,r,q,sigma,"CE")
    p=bs_price(s,k,t,r,q,sigma,"PE")
    assert abs((c-p)-(s*__import__("math").exp(-q*t)-k*__import__("math").exp(-r*t)))<1e-10

def test_delta_signs():
    args=(100.0,100.0,30/365,0.06,0.01,0.20)
    assert 0 < bs_delta(*args,"CE") < 1
    assert -1 < bs_delta(*args,"PE") < 0

def test_iv_round_trip():
    args=(100.0,105.0,45/365,0.06,0.01,0.25)
    premium=bs_price(*args,"CE")
    iv,status,it,res=implied_vol(*args,premium,"CE")
    assert status=="CONVERGED"
    assert abs(iv-0.25)<1e-7
    assert it>0
    assert res<=1e-8

def test_invalid_premium_fails_closed():
    iv,status,_,_=implied_vol(100,100,30/365,0.06,0.01,0,"CE")
    assert iv is None and status=="NONPOSITIVE_PREMIUM"

def test_no_arbitrage_rejection():
    iv,status,_,_=implied_vol(100,100,30/365,0.06,0.01,200,"CE")
    assert iv is None and status=="NO_ARBITRAGE_BOUND_REJECTION"
