"""Heston model parameters.

dS_t = r S_t dt + sqrt(v_t) S_t dW^S_t
dv_t = kappa (vbar - v_t) dt + eta sqrt(v_t) dW^v_t
d<W^S, W^v>_t = rho dt
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HestonParams:
    v0: float     # initial variance
    kappa: float  # mean-reversion speed
    vbar: float   # long-run variance
    eta: float    # vol-of-vol
    rho: float    # spot/variance correlation

    def feller_ok(self) -> bool:
        """True if the Feller condition 2*kappa*vbar > eta**2 holds."""
        return 2.0 * self.kappa * self.vbar > self.eta ** 2
