"""Characteristic function of ln(S_T) under Heston."""

import numpy as np

from heston.params import HestonParams


def cf(u, S0: float, r: float, T: float, params: HestonParams, q: float = 0.0):
    """E[exp(i u ln S_T)] under the risk-neutral measure.

    u may be complex and/or a numpy array.
    """
    u = np.asarray(u, dtype=complex)
    v0, kappa, vbar, eta, rho = (params.v0, params.kappa, params.vbar,
                                 params.eta, params.rho)

    # Step 1
    beta = kappa - rho * eta * 1j * u

    # Step 2
    d = np.sqrt(beta**2 + eta**2 * (1j * u + u**2))

    # Step 3
    g = (beta - d) / (beta + d)

    # Step 4: compute exp(-dT) once, reuse it twice
    edT = np.exp(-d * T)

    # Step 5: the v0 coefficient
    D = ((beta - d) / eta**2) * (1 - edT) / (1 - g * edT)

    # Step 6: the time term
    A = (kappa * vbar / eta**2) * ((beta - d) * T - 2 * np.log((1 - g * edT) / (1 - g)))

    # Step 7: assemble
    return np.exp(1j * u * (np.log(S0) + (r - q) * T) + A + D * v0)
