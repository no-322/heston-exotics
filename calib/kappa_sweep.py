"""Kappa profile: fix kappa on a grid, calibrate the other 4 params, record fit.

Run:  python -m calib.kappa_sweep
Writes plots/kappa_profile.png (data CSV stays in data/, which is gitignored).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from calib.calibrate import LB, UB, bs_vega, residuals

ROOT = Path(__file__).resolve().parents[1]
CALIB_SET = ROOT / "data" / "calib_set_20261110.csv"
PLOT_DIR = ROOT / "plots"
KAPPAS = [1.0, 2.0, 4.0, 6.0, 8.0, 12.0, 16.0]
N_STARTS = 5

# free params with kappa removed: v0, vbar, eta, rho
FREE = [0, 2, 3, 4]
LB_FREE = [LB[i] for i in FREE]
UB_FREE = [UB[i] for i in FREE]


def full_x(y, kappa):
    v0, vbar, eta, rho = y
    return np.array([v0, kappa, vbar, eta, rho])


def fit_fixed_kappa(df, kappa, n_starts=N_STARTS, seed=0):
    rng = np.random.default_rng(seed)
    sols = []
    for _ in range(n_starts):
        y0 = rng.uniform(LB_FREE, UB_FREE)
        sol = least_squares(lambda y: residuals(full_x(y, kappa), df), y0,
                            bounds=(LB_FREE, UB_FREE))
        sols.append(sol)
    sols.sort(key=lambda s: s.cost)
    best = sols[0]
    v0, vbar, eta, rho = best.x
    rms = 100 * np.sqrt(np.mean(best.fun ** 2))  # vol pts (residuals are price/vega)
    agree = all(np.allclose(s.x, best.x, rtol=1e-3, atol=1e-4) for s in sols)
    return dict(kappa=kappa, rms=rms, v0=v0, vbar=vbar, eta=eta, rho=rho,
                feller=2 * kappa * vbar - eta ** 2, starts_agree=agree)


def plot_profile(prof, path):
    panels = [("rms", "RMS error (vol pts)"),
              ("eta", r"$\eta$"),
              ("vbar", r"$\bar v$"),
              ("feller", r"$2\kappa\bar v - \eta^2$")]
    best = prof.loc[prof.rms.idxmin()]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)
    for ax, (col, label) in zip(axes.flat, panels):
        ax.plot(prof.kappa, prof[col], color="#2a6fdb", lw=2, marker="o", ms=6)
        ax.axvline(best.kappa, color="0.6", lw=1, ls="--")
        ax.set_title(label, fontsize=11, loc="left")
        ax.grid(alpha=0.25)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[1, 1].axhline(0, color="0.3", lw=1)
    for ax in axes[1]:
        ax.set_xlabel(r"$\kappa$ (fixed)")
    fig.suptitle(rf"Heston $\kappa$ profile  (best $\kappa$ = {best.kappa:g}, "
                 rf"RMS {best.rms:.3f} vol pts)", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    df = pd.read_csv(CALIB_SET, parse_dates=["expiry"])
    df["vega"] = bs_vega(df.F, df.K, df["T"], df.r, df.iv_own)

    rows = []
    for k in KAPPAS:
        row = fit_fixed_kappa(df, k)
        rows.append(row)
        print(f"kappa={k:5.1f}  rms={row['rms']:.3f}  v0={row['v0']:.4f}  "
              f"vbar={row['vbar']:.4f}  eta={row['eta']:.3f}  rho={row['rho']:.3f}  "
              f"agree={row['starts_agree']}")
    prof = pd.DataFrame(rows)
    prof.to_csv(ROOT / "data" / "kappa_profile.csv", index=False)

    PLOT_DIR.mkdir(exist_ok=True)
    plot_profile(prof, PLOT_DIR / "kappa_profile.png")
    print(f"saved {PLOT_DIR / 'kappa_profile.png'}")


if __name__ == "__main__":
    main()
