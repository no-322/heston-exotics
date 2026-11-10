"""Fourier pricer for European calls under Heston."""

import numpy as np
from scipy.integrate import quad
from heston.cf import cf

def call(S0, K, r, T, params, q=0.0, u_max=200.0):
    lnK = np.log(K)
    phi_mi = cf(-1j, S0, r, T, params, q)                    # phi(-i)

    def integrand_P2(u):
        P2 = ((np.exp(-1j * lnK * u) * cf(u, S0, r, T, params, q))/ (1j * u)).real                           # Re[ e^{-iu lnK} phi(u) / (iu) ]
        return P2

    def integrand_P1(u):
        P1 = ((np.exp(-1j * u * lnK ) * cf(u - 1j, S0, r, T, params, q))/ (1j * u * phi_mi)).real                          # Re[ e^{-iu lnK} phi(u - i) / (iu phi(-i)) ]
        return P1
    P1 = 0.5 + quad(integrand_P1, 1e-8, u_max, limit=200)[0] / np.pi
    P2 = 0.5 + quad(integrand_P2, 1e-8, u_max, limit=200)[0] / np.pi
    return S0 * np.exp(-q * T) * P1 - K * np.exp(-r * T) * P2                        # S0 e^{-qT} P1 - K e^{-rT} P2