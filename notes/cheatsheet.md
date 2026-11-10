# What Breaks

## Phase 1
- In `cf.py` when $u = -i$ and $\rho\eta \ge \kappa$ we get $0/0$ in $g$ ($\beta + d = 0$). Stocks have -ve $\rho$ but on the off chance we get +ve $\rho$ this may cause an issue.
- Since the characteristic function is $\mathbb{E}^*[e^{iu \ln S_T}]$, $u = 0$ just verifies that probability adds up to 1. $u = -i$ gives us the forward price.
- Heston pricer with $\eta = 10^{-4}$ and $v_0 = \bar v$ gives a price lower than BS because $\eta$ isn't exactly 0 (the gap scales like $\eta^2$). The `quad` lower limit adds a little, the upper limit doesn't matter.
- $\rho = 0$ makes the curve symmetric (in $\ln(K/F)$). Adding $\rho$ not only causes tilt (skew) but also changes which point is the lowest vol. Negative $\rho$ pushes the lowest vol to $K > K_{ATM}$.
- Even though Heston prices each maturity at a single point in time, it is still affected by the SDE of the time-varying vol, because the vol impacts how likely the price is to get into the ITM region between today and maturity.
- For shorter maturities ($T \lesssim 1/\kappa$, about 6 months here) ATM vol hovers at $\sqrt{v_0}$, while for longer maturities it hovers at $\sqrt{\bar v}$. The reason is similar to the last point: longer time pushes vol towards the mean vol.
- Shorter maturity also has a very steep vol curve.
- $\eta$ adds curvature.
- Important!! Pts to be added on why I switched to cubic interpolation and the cleanup because of cubic interpolation.

## Phase 2

## Phase 3

## Phase 4

## Phase 5

## Phase 6
