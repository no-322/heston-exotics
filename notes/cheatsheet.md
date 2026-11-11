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

### Heston Calibration
- We use OTM options for vol calibration: for $K < F$ we use puts and for $K > F$ we use calls. ITM options have time value and intrinsic value, while OTM options have only time value, so they're a better measure. With ITM it's harder to separate the noise in implied vol.

**Q.** Why is VIX greater than ATM implied vol?

**A.** Although both come from implied vol, ATM vol is from one option, while VIX is a combination of all the OTM calls and puts. VIX $-$ ATM implied vol is a measure of skew.

- Parity-implied $r$ is robust and consistent for longer $T$ and sits 25-35 bp above Bloomberg's $r$. This is because the regression is done on $C - P$: we can see this as selling one call-put portfolio to finance the other. The rate we get is the box spread financing rate, which is higher due to margins involved.
- Despite getting the wrong $r$ regardless of maturity, $F$ is accurate and matches Bloomberg data. $r$ can move due to noise, but $F$ is the crossing point of $C - P$ from +ve to -ve, which is not very sensitive to the errors.

- Calibration can be done on prices or implied vol. Prices tend to optimize more on long dated because price there is higher for ATM.
- Vol optimizing puts higher weight on short $\tau$. This is what I am doing.
- Since idk the $F$ used by Bloomberg, I used $F$ (inverted BS with `brentq`) to get implied vol. The fit based on RMSE is better.
- Ran 20 iterations with different starting points and all of them settle at a given value. So we can say that we don't have local minima issues, but we still need to ensure that the parameters are well determined. $\kappa$ and $\eta$ are not observed directly. So I start with fixing $\kappa$ and running the optimization to see how $\eta$ fits.
- $\kappa < 4$ performs worse, but post 4 it fits with RMSE varying by just 0.09. Since $\eta$ rises with $\kappa$, higher $\kappa$ has worse Feller condition.

## Phase 2

## Phase 3

## Phase 4

## Phase 5

## Phase 6
