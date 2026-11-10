# heston/fft_pricer.py
import numpy as np
from heston.cf import cf

from scipy.interpolate import CubicSpline

def fft_price_at(K_market, S0, r, T, params, q=0.0, **kw):
    K_grid, C_grid = fft_calls(S0, r, T, params, q, **kw)
    F = S0 * np.exp((r - q) * T)
    mask = (K_grid > 0.2 * F) & (K_grid < 5 * F)    # well beyond your 70%-130% data
    spline = CubicSpline(np.log(K_grid[mask]), C_grid[mask])
    return spline(np.log(K_market))

def fft_calls(S0, r, T, params, q=0.0, alpha=1.5, N=4096, dnu=0.25):
    # 1. Grids
    j = np.arange(N)
    nu = j * dnu                                  # nu_j = j * dnu
    dk = 2 * np.pi / (N * dnu)                                 # from dnu * dk = 2*pi / N
    lnF = np.log(S0) + (r - q) * T
    beta = lnF - dk * N / 2                                # centre: lnF - N*dk/2
    k = beta + j * dk                                   # k_m = beta + m*dk  (m = j)

    # 2. psi(nu): the damped call's Fourier transform
    phi = cf(nu - (alpha + 1) * 1j, S0, r, T, params, q)
    denom = alpha**2 + alpha - nu**2 + 1j * (2 * alpha + 1) * nu                               # alpha^2 + alpha - nu^2 + i(2 alpha + 1) nu
    psi = np.exp( -r * T) * phi / denom                                 # e^{-rT} phi / denom

    # 3. Simpson weights: 1/3, 4/3, 2/3, 4/3, ...
    w = (3 + (-1) ** (j + 1)) / 3
    w[0] = 1 / 3                                # delta_{j0} correction

    # 4. FFT
    x = np.exp(-1j * nu * beta) * psi * w * dnu                                   # e^{-i nu beta} psi w dnu
    C = (np.exp(-alpha * k) / np.pi) * np.fft.fft(x).real                                  # e^{-alpha k} / pi * Re(fft(x))

    return np.exp(k), C