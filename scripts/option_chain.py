#!/usr/bin/env python3
"""
option_chain.py — Pull a delta-targeted option chain summary for a ticker.

Outputs spot price, risk-free rate, dividend yield, next earnings date,
realized volatility (30d / 90d), and for each of the next N expiries a
table of calls and puts at user-specified delta targets.

Requires:
    pip install -r scripts/requirements.txt

Usage:
    python3 scripts/option_chain.py NVDA
    python3 scripts/option_chain.py NVDA --expiries 3 --targets 0.15,0.25,0.35,0.50
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime

try:
    import pandas as pd
    import yfinance as yf
except ImportError as e:
    print(
        f"Missing dependency: {e.name}. Install with:\n"
        f"    pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------- Black-Scholes delta (no scipy) ----------

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_delta(side: str, S: float, K: float, T: float, r: float, q: float, sigma: float) -> float:
    """Black-Scholes delta. side='C' or 'P'. T in years, rates as decimals."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return float("nan")
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    if side == "C":
        return math.exp(-q * T) * _norm_cdf(d1)
    return math.exp(-q * T) * (_norm_cdf(d1) - 1.0)


# ---------- Data helpers ----------

def get_risk_free_rate() -> float:
    """13-week T-bill yield as a proxy for short-term risk-free rate."""
    try:
        irx = yf.Ticker("^IRX").history(period="5d")
        if not irx.empty:
            return float(irx["Close"].iloc[-1]) / 100.0
    except Exception:
        pass
    return 0.043  # fallback ~4.3%


def realized_vol(history: pd.DataFrame, window: int) -> float | None:
    """Annualized realized vol from a rolling window of daily returns."""
    if history is None or history.empty or len(history) < window + 1:
        return None
    returns = history["Close"].pct_change().dropna()
    if len(returns) < window:
        return None
    rolling = returns.rolling(window=window).std().dropna()
    if rolling.empty:
        return None
    return float(rolling.iloc[-1] * math.sqrt(252))


def find_strike_at_delta(
    df: pd.DataFrame,
    target: float,
    side: str,
    S: float,
    T: float,
    r: float,
    q: float,
) -> dict | None:
    """Return the chain row whose computed delta is closest to `target`."""
    if df is None or df.empty:
        return None
    best, best_dist = None, float("inf")
    for _, row in df.iterrows():
        sigma = row.get("impliedVolatility")
        if sigma is None or pd.isna(sigma) or sigma <= 0:
            continue
        delta = bs_delta(side, S, float(row["strike"]), T, r, q, float(sigma))
        if math.isnan(delta):
            continue
        dist = abs(abs(delta) - abs(target))
        if dist < best_dist:
            best_dist = dist
            best = {
                "strike": float(row["strike"]),
                "bid": None if pd.isna(row.get("bid")) else float(row["bid"]),
                "ask": None if pd.isna(row.get("ask")) else float(row["ask"]),
                "last": None if pd.isna(row.get("lastPrice")) else float(row["lastPrice"]),
                "iv": float(sigma),
                "volume": 0 if pd.isna(row.get("volume")) else int(row["volume"]),
                "oi": 0 if pd.isna(row.get("openInterest")) else int(row["openInterest"]),
                "delta": float(delta),
            }
    return best


def fmt_money(x: float | None) -> str:
    return f"{x:.2f}" if x is not None else "  —  "


# ---------- Main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Option chain summary with delta-targeted strikes.")
    ap.add_argument("ticker", help="Ticker symbol (e.g. NVDA)")
    ap.add_argument("--expiries", type=int, default=3, help="How many expiries to summarize (default 3)")
    ap.add_argument("--targets", type=str, default="0.15,0.25,0.35,0.50",
                    help="Comma-separated absolute delta targets (default 0.15,0.25,0.35,0.50)")
    args = ap.parse_args()

    ticker = args.ticker.upper()
    targets = [float(x.strip()) for x in args.targets.split(",")]

    tk = yf.Ticker(ticker)
    info = {}
    try:
        info = tk.info or {}
    except Exception:
        pass

    spot = info.get("currentPrice") or info.get("regularMarketPrice")
    if spot is None:
        hist_short = tk.history(period="2d")
        if hist_short.empty:
            print(f"ERROR: could not fetch price for {ticker}", file=sys.stderr)
            return 2
        spot = float(hist_short["Close"].iloc[-1])
    spot = float(spot)

    div_yield = info.get("dividendYield") or 0.0
    if div_yield > 1:  # yfinance occasionally returns as percent
        div_yield /= 100.0

    r = get_risk_free_rate()
    hist_year = tk.history(period="1y")
    rv30 = realized_vol(hist_year, 30)
    rv90 = realized_vol(hist_year, 90)

    expiries = list(tk.options or [])
    if not expiries:
        print(f"No options listed for {ticker}.", file=sys.stderr)
        return 2
    expiries = expiries[: args.expiries]

    print(f"=== {ticker} option chain summary ===")
    print(f"Spot:                ${spot:,.2f}")
    print(f"Risk-free (13w):     {r * 100:.2f}%")
    print(f"Dividend yield:      {div_yield * 100:.2f}%")
    if rv30 is not None:
        print(f"Realized vol 30d:    {rv30 * 100:.1f}%")
    if rv90 is not None:
        print(f"Realized vol 90d:    {rv90 * 100:.1f}%")
    earn_ts = info.get("earningsTimestamp")
    if earn_ts:
        try:
            edt = datetime.fromtimestamp(earn_ts).date()
            print(f"Next earnings (est): {edt.isoformat()}")
        except Exception:
            pass
    print()

    today = date.today()
    for exp_str in expiries:
        try:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        days = max((exp_date - today).days, 0)
        T = max(days, 1) / 365.0

        try:
            chain = tk.option_chain(exp_str)
        except Exception as e:
            print(f"  ! could not fetch chain for {exp_str}: {e}", file=sys.stderr)
            continue

        print(f"--- Expiry {exp_str} ({days} days, T={T:.3f}y) ---")
        for side, df, label in (("C", chain.calls, "Calls"), ("P", chain.puts, "Puts")):
            print(f"  {label}:")
            print(f"    {'Δtgt':>6}  {'Strike':>8}  {'Bid':>6}  {'Ask':>6}  {'Mid':>6}  {'IV':>6}  {'Δ':>6}  {'OI':>8}  {'Vol':>7}")
            for t in targets:
                signed = t if side == "C" else -t
                row = find_strike_at_delta(df, signed, side, spot, T, r, div_yield)
                if row is None:
                    print(f"    {signed:>+6.2f}  {'—':>8}")
                    continue
                bid = row["bid"]
                ask = row["ask"]
                mid = (bid + ask) / 2 if bid is not None and ask is not None else (row["last"] or 0.0)
                print(
                    f"    {signed:>+6.2f}  "
                    f"{row['strike']:>8.2f}  "
                    f"{fmt_money(bid):>6}  "
                    f"{fmt_money(ask):>6}  "
                    f"{mid:>6.2f}  "
                    f"{row['iv'] * 100:>5.1f}%  "
                    f"{row['delta']:>+6.2f}  "
                    f"{row['oi']:>8,}  "
                    f"{row['volume']:>7,}"
                )
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
