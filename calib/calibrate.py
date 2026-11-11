import numpy as np
from scipy.optimize import least_squares
from scipy.stats import norm
from heston.params import HestonParams
from heston.fft_pricer import fft_price_at
from calib.parity import parity_r_F

S0 = 7528.5
# parameter order: v0, kappa, vbar, eta, rho
LB = [1e-4, 0.01, 1e-4, 0.01, -0.999]
UB = [1.0,  20.0, 1.0,  5.0,   0.999]

def bs_vega(F, K, T, r, sigma):
    # Black-76 vega: e^{-rT} F n(d1) sqrt(T)
    discountFactor = np.exp(-r * T)
    d1 = (np.log(F / K) +  (sigma**2) * T / 2) * (1 / (sigma * np.sqrt(T)))
    return discountFactor * F * norm.pdf(d1) * np.sqrt(T)

def residuals(x, df):
    p = HestonParams(*x)
    res = []
    for expiry, g in df.groupby("expiry"):
        T, r, q, F = g["T"].iloc[0], g.r.iloc[0], g.q.iloc[0], g.F.iloc[0]  # one value each from g
        C = fft_price_at(g.K.values, S0, r, T, p, q)
        model = np.where(g.cp == "C", C, C - np.exp(-r * T) * (F - g.K)) # put via parity: C - e^{-rT}(F - K)
        res.append((model - g["mid"].values) / g["vega"].values)
    return np.concatenate(res)

def calibrate(df, n_starts=20, seed=0):
    rng = np.random.default_rng(seed)
    df = df.copy()
    df["vega"] = bs_vega(df.F, df.K, df["T"], df.r, df.iv_own)                          # bs_vega with each row's ivm
    results = []
    for _ in range(n_starts):
        x0 = rng.uniform(LB, UB)
        sol = least_squares(residuals, x0, bounds=(LB, UB), args=(df,))
        results.append((sol.cost, sol.x))
    return sorted(results, key=lambda t: t[0])