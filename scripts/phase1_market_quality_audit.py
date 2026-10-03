import json
import math
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/validation/phase1_market_quality_report.json")
INDEX = RAW / "index" / "NIFTY.parquet"



def norm_ts(s):
    return pd.to_datetime(s, utc=True, errors="coerce")


def session_minute(ts_utc):
    local = ts_utc.dt.tz_convert("Asia/Kolkata")
    return local.dt.hour * 60 + local.dt.minute


def bs_delta(S, K, r, q, T, sigma, is_call):
    if not (S > 0 and K > 0 and T > 0 and sigma > 0):
        return np.nan
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * np.sqrt(T))
    if is_call:
        return float(np.exp(-q * T) * 0.5 * (1.0 + math.erf(d1 / np.sqrt(2.0))))
    return float(-np.exp(-q * T) * 0.5 * (1.0 + math.erf(-d1 / np.sqrt(2.0))))


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_price(S, K, r, q, T, sigma, is_call):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if is_call:
        return S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)


def iv_brent(S, K, premium, r, q, T, is_call):
    if not all(np.isfinite([S, K, premium, r, q, T])) or S <= 0 or K <= 0 or premium <= 0 or T <= 0:
        return np.nan
    def f(sig):
        return bs_price(S, K, r, q, T, sig, is_call) - premium
    lo, hi = 1e-6, 5.0
    flo, fhi = f(lo), f(hi)
    while flo * fhi > 0 and hi < 10.0:
        hi *= 2.0
        fhi = f(hi)
    if flo * fhi > 0:
        return np.nan
    for _ in range(100):
        mid = (lo + hi) / 2.0
        fm = f(mid)
        if abs(fm) <= 1e-8 or (hi - lo) <= max(1e-10, 1e-10 * abs(mid)):
            return mid
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return np.nan


def main():
    if not INDEX.exists():
        raise SystemExit("Missing NIFTY index file")
    idx = pd.read_parquet(INDEX)
    idx["timestamp"] = norm_ts(idx["timestamp"])
    idx = idx.dropna(subset=["timestamp"]).drop_duplicates("timestamp")
    idx_set = set(idx["timestamp"].tolist())
    idx_by_day = idx.assign(local=idx["timestamp"].dt.tz_convert("Asia/Kolkata"))
    idx_by_day["day"] = idx_by_day["local"].dt.date
    session_counts = idx_by_day.groupby("day")["timestamp"].nunique()

    option_files = sorted((RAW / "options" / "NIFTY").glob("*.parquet"))
    if not option_files:
        raise SystemExit("No NIFTY option files found")

    total_rows = 0
    aligned_rows = 0
    stale_or_duplicate_ts = 0
    gaps = []
    daily_counts = []
    target_checks = []

    for path in option_files:
        df = pd.read_parquet(path)
        df["timestamp"] = norm_ts(df["timestamp"])
        df = df.dropna(subset=["timestamp"])
        df = df.drop_duplicates(["timestamp", "expiry", "strike", "option_type"])
        total_rows += len(df)
        aligned_rows += int(df["timestamp"].isin(idx_set).sum())

        ts = pd.Series(df["timestamp"].drop_duplicates().sort_values().tolist())
        if len(ts) > 1:
            diffs = ts.diff().dt.total_seconds().div(60)
            large = diffs[diffs > 1.5]
            for i in large.index[:100]:
                gaps.append({"file": path.name, "gap_minutes": float(diffs.loc[i])})

        local = df["timestamp"].dt.tz_convert("Asia/Kolkata")
        df["day"] = local.dt.date
        for day, g in df.groupby("day"):
            daily_counts.append({
                "file": path.name,
                "day": str(day),
                "timestamps": int(g["timestamp"].nunique()),
                "rows": int(len(g)),
            })

        # Deterministic availability sample: every 15th unique timestamp per file,
        # then retain a bounded number of strikes closest to the underlying.
        sample_ts = ts.iloc[::15].head(40).tolist()
        for t in sample_ts:
            row_idx = idx.loc[idx["timestamp"] == t]
            if row_idx.empty:
                continue
            S = float(row_idx.iloc[0]["close"])
            g = df[df["timestamp"] == t].copy()
            if g.empty:
                continue
            g["moneyness"] = (g["strike"].astype(float) - S).abs() / S
            g = g[g["moneyness"] <= 0.12].sort_values(["moneyness", "strike"]).head(80)
            expiry = pd.to_datetime(g["expiry"], errors="coerce", utc=True)
            for _, x in g.iterrows():
                K = float(x["strike"])
                prem = float(x["close"])
                exp = expiry.loc[_] if _ in expiry.index else pd.NaT
                if pd.isna(exp):
                    continue
                T = max((exp - t).total_seconds(), 1.0) / (365.0 * 86400.0)
                iv = iv_brent(S, K, prem, 0.0, 0.0, T, str(x["option_type"]).upper().startswith("C"))
                if np.isfinite(iv):
                    delta = abs(bs_delta(S, K, 0.0, 0.0, T, iv, str(x["option_type"]).upper().startswith("C")))
                    target_checks.append(delta)

    # Session boundaries are deliberately not hard-coded here; G4 uses the
    # date-specific NSE session calendar specified in research/PHASE1_SESSION_CALENDAR_SPEC.md.
    session_outliers = [
        {"day": str(day), "timestamps": int(n)}
        for day, n in session_counts.items()
        if int(n) < 300 or int(n) > 390
    ]

    result = {
        "status": "phase1_market_quality_audit_complete",
        "option_files": len(option_files),
        "option_rows_after_key_dedup": total_rows,
        "option_timestamp_alignment_to_nifty": {
            "matched_rows": aligned_rows,
            "match_fraction": aligned_rows / total_rows if total_rows else None,
        },
        "nifty_index_rows": int(len(idx)),
        "nifty_trading_days": int(len(session_counts)),
        "session_count_outliers": session_outliers,
        "nifty_session_timestamp_count_summary": {
            "median": float(session_counts.median()) if len(session_counts) else None,
            "min": int(session_counts.min()) if len(session_counts) else None,
            "max": int(session_counts.max()) if len(session_counts) else None,
        },
        "option_gap_observations_sample": gaps[:100],
        "daily_option_coverage_sample": daily_counts[:500],
        "greek_audit": {
            "method": "Deterministic bounded sample using frozen Black-Scholes delta and Brent-style IV contract; r=q=0 only for diagnostic solver smoke testing, not production Greeks.",
            "solver_success_count": len(target_checks),
            "delta_summary": {
                "min": float(min(target_checks)) if target_checks else None,
                "median": float(median(target_checks)) if target_checks else None,
                "max": float(max(target_checks)) if target_checks else None,
            },
            "production_status": "DIAGNOSTIC_ONLY",
        },
        "target_delta_availability": {
            "status": "NOT_YET_ACCEPTED",
            "reason": "Production target-delta availability requires date-specific r/q inputs and the full frozen execution-quality/liquidity filters; this audit only establishes data-path and solver feasibility."
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
