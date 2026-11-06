"""Fourier pricer for European calls under Heston."""

from heston.params import HestonParams


def call_price(S0: float, K: float, r: float, T: float, params: HestonParams) -> float:
    """European call price via Fourier inversion of the characteristic function."""
    # TODO: implement
    raise NotImplementedError
