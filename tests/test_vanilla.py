"""Sanity checks for the Heston characteristic function and vanilla pricer.

Tests skip automatically while cf / call still raise NotImplementedError.
"""

import numpy as np
import pytest

from heston.bs import bs_call
from heston.cf import cf
from heston.params import HestonParams
from heston.pricer import call
from heston.fft_pricer import fft_price_at

S0, r, T = 100.0, 0.03, 1.0
PARAMS = HestonParams(v0=0.04, kappa=1.5, vbar=0.04, eta=0.5, rho=-0.7)


def _call_or_skip(fn, *args):
    try:
        return fn(*args)
    except NotImplementedError:
        pytest.skip(f"{fn.__name__} not implemented yet")


def test_cf_at_zero_is_one():
    # TODO: phi(0) = E[1] = 1
    val = _call_or_skip(cf, 0.0, S0, r, T, PARAMS)
    assert np.isclose(val, 1.0)


def test_cf_at_minus_i_is_forward():
    # TODO: phi(-i) = E[S_T] = S0 * exp(rT)  (martingale check)
    val = _call_or_skip(cf, -1j, S0, r, T, PARAMS)
    assert np.isclose(val, S0 * np.exp(r * T))


@pytest.mark.parametrize("K", [80.0, 100.0, 120.0])
def test_degenerate_heston_matches_bs(K):
    # TODO: eta -> 0 and v0 = vbar  =>  constant variance vbar  =>  BS with sigma^2 = vbar
    vbar = 0.04
    p = HestonParams(v0=vbar, kappa=1.5, vbar=vbar, eta=1e-4, rho=0.0)
    heston = _call_or_skip(call, S0, K, r, T, p)
    bs = bs_call(S0, K, r, T, np.sqrt(vbar))
    assert np.isclose(heston, bs, atol=1e-4)


def test_fft_matches_quad_pricer():
    # Carr-Madan FFT + cubic spline in log-strike vs the quad pricer
    p = PARAMS
    Ks = [80, 90, 100, 110, 120]
    C_fft = fft_price_at(np.array(Ks, dtype=float), 100, 0.03, 1.0, p)
    for K, c in zip(Ks, C_fft):
        assert abs(c - call(100, K, 0.03, 1.0, p)) < 1e-3
