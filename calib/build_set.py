"""Build the OTM calibration set for 2026-11-10 and save it to data/calib_set_20261110.csv.

Per expiry: F from parity (±10% window); r from parity (±10%), except 2026-12-18 which
uses the ±2% window; q = r - ln(F/S0)/T. Keep OTM options with 0.8 <= K/F <= 1.2, bid > 0.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

from calib.parity import parity_r_F
from data.load_bbg import S0, load_spx

EXPIRIES = pd.to_datetime(["2026-12-18", "2027-03-19", "2027-05-21", "2027-12-17", "2028-12-15"])
R_WINDOW_2PCT = {pd.Timestamp("2026-12-18")}       # expiries whose r uses the ±2% window
MONEYNESS = (0.8, 1.2)
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "calib_set_20261110.csv"
COLUMNS = ["expiry", "T", "K", "cp", "bid", "ask", "mid", "spread", "ivm", "iv_own", "r", "q", "F"]
IV_BRACKET = (1e-4, 5.0)


def black76(F, K, T, r, sigma, cp):
    """Black-76 price of a European call ('C') or put ('P') on forward F."""
    sd = sigma * np.sqrt(T)
    d1 = (np.log(F / K) + 0.5 * sd**2) / sd
    d2 = d1 - sd
    df = np.exp(-r * T)
    if cp == "C":
        return df * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def black76_iv(price, F, K, T, r, cp, bracket=IV_BRACKET):
    """Black-76 implied vol via brentq. nan if price is outside no-arbitrage bounds or not bracketed."""
    df = np.exp(-r * T)
    intrinsic = df * max(F - K, 0.0) if cp == "C" else df * max(K - F, 0.0)
    upper = df * F if cp == "C" else df * K
    if not (intrinsic < price < upper):
        return np.nan
    f = lambda s: black76(F, K, T, r, s, cp) - price
    lo, hi = bracket
    if f(lo) > 0 or f(hi) < 0:
        return np.nan
    return brentq(f, lo, hi, xtol=1e-12, maxiter=200)


def within(g, S0, w):
    """Rows with (1-w)*S0 < K < (1+w)*S0. parity_r_F applies its own ±10% filter on top,
    so pre-filtering to w < 10% gives a ±w window."""
    return g[(g.K > (1 - w) * S0) & (g.K < (1 + w) * S0)]


def build_set(df=None, S0=S0):
    if df is None:
        df = load_spx()

    parts = []
    for expiry in EXPIRIES:
        g = df[df.expiry == expiry]
        T = g["T"].iloc[0]

        r, F, _ = parity_r_F(g, S0)                       # ±10%
        if expiry in R_WINDOW_2PCT:
            r, _, _ = parity_r_F(within(g, S0, 0.02), S0)  # ±2% for r only
        q = r - np.log(F / S0) / T

        otm = ((g.cp == "P") & (g.K < F)) | ((g.cp == "C") & (g.K > F))
        m = g.K / F
        keep = otm & (m >= MONEYNESS[0]) & (m <= MONEYNESS[1]) & (g.bid > 0)

        out = g[keep].copy()
        out["spread"] = out["ask"] - out["bid"]
        out["r"], out["q"], out["F"] = r, q, F
        out["iv_own"] = [black76_iv(row.mid, F, row.K, T, r, row.cp) for row in out.itertuples()]
        parts.append(out[COLUMNS])

    return pd.concat(parts, ignore_index=True).sort_values(["expiry", "K"]).reset_index(drop=True)


if __name__ == "__main__":
    cs = build_set()
    cs.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(cs)} options to {OUT_PATH}\n")
    summary = cs.groupby("expiry").agg(
        T=("T", "first"), n=("K", "size"),
        puts=("cp", lambda s: (s == "P").sum()), calls=("cp", lambda s: (s == "C").sum()),
        r=("r", "first"), q=("q", "first"), F=("F", "first"),
    )
    print(summary.to_string(float_format=lambda x: f"{x:.4f}"))

    diff = 100 * (cs["iv_own"] - cs["ivm"])          # vol points
    print("\niv_own - ivm (vol points):")
    print(diff.groupby(cs["expiry"]).agg(mean="mean", max="max", n_nan=lambda s: s.isna().sum())
          .to_string(float_format=lambda x: f"{x:+.3f}"))
