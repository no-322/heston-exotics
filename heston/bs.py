"""Black-Scholes call price and implied volatility."""

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


def bs_call(S0: float, K: float, r: float, T: float, sigma: float, q: float = 0.0) -> float:
    """Black-Scholes price of a European call (continuous dividend yield q)."""
    if T <= 0 or sigma <= 0:
        return max(S0 * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
    sqrtT = np.sqrt(T)
    d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    return S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def implied_vol(price: float, S0: float, K: float, r: float, T: float, q: float = 0.0) -> float:
    """Black-Scholes implied vol of a European call via brentq on [1e-4, 5.0].

    Returns nan if the price is outside no-arbitrage bounds or the root isn't bracketed.
    """
    lo, hi = 1e-4, 5.0
    lower = max(S0 * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
    upper = S0 * np.exp(-q * T)
    if not (lower < price < upper):
        return float("nan")
    f = lambda s: bs_call(S0, K, r, T, s, q) - price
    if f(lo) > 0 or f(hi) < 0:
        return float("nan")
    return brentq(f, lo, hi, xtol=1e-12, maxiter=200)
