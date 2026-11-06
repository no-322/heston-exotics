"""Characteristic function of ln(S_T) under Heston."""

import numpy as np

from heston.params import HestonParams


def cf(u, S0: float, r: float, T: float, params: HestonParams):
    """E[exp(i u ln S_T)] under the risk-neutral measure.

    u may be complex and/or a numpy array.
    """
    # TODO: implement
    raise NotImplementedError
