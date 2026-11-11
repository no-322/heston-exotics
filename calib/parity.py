"""Put-call parity tools for calibration.


"""

import numpy as np
import pandas as pd

from data.load_bbg import load_spx, S0, VALUATION


def parity_r_F(df_expiry, S0):
    # 1. keep strikes that have BOTH a call and a put, within ~10% of S0
    df_expiry = df_expiry[(df_expiry.K > 0.9 * S0) & (df_expiry.K < 1.1 * S0)]
    calls = df_expiry[df_expiry.cp == "C"]
    puts = df_expiry[df_expiry.cp == "P" ]
    combined = pd.merge(calls, puts, on = "K", suffixes= ("_c", "_p"))
    # 2. y = call mid - put mid at each strike
    y = combined["mid_c"] - combined["mid_p"]
    # 3. b, a = np.polyfit(K, y, 1)      # slope first, then intercept
    b , a = np.polyfit(combined.K, y, 1)
    # 4. r, F, q from the formulas above
    r = -np.log(-b) / df_expiry["T"].mean()
    F = -a / b
    q = r - np.log(F / S0) / df_expiry["T"].mean()
    return r, F, q

if __name__ == "__main__":
    df = load_spx()
    print(f"S0 = {S0}, valuation = {VALUATION}, {len(df)} quotes\n")

    for expiry, g in df.groupby("expiry"):
        calls = g[g.cp == "C"]
        puts = g[g.cp == "P"]
        T, r_bbg, q_bbg = g["T"].iloc[0], g["r"].iloc[0], g["idiv"].iloc[0]
        print(f"{expiry.date()}  T={T:.4f}  r_bbg={r_bbg:.4f}  q_bbg={q_bbg:.4f}  "
              f"calls={len(calls)}  puts={len(puts)}")
        r, F, q = parity_r_F(g, S0 )
        print(expiry, g["T"].iloc[0], r, F, q)
        

