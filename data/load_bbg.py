"""Load the Bloomberg SPX option chain export (SPX_all.xlsx) into a tidy DataFrame.

Sheet layout (one sheet per expiry):
    row 1: "Calls"
    row 2: Strike, Ticker, Bid, Ask, Last, IVM, Volm  (calls)  | same 7 columns (puts)
    row 3: expiry header, e.g. "20-Nov-26 (10d); CSize 100; ; IDiv 2.15; R 4.43; FF 0"
    row 4+: data
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

S0 = 7528.5                                        # SPX spot
VALUATION = pd.Timestamp("2026-11-10 10:30", tz="America/New_York")
DEFAULT_PATH = Path(__file__).with_name("SPX_all.xlsx")

COLS = ["Strike", "Ticker", "Bid", "Ask", "Last", "IVM", "Volm"]
HEADER_RE = re.compile(
    r"^\s*(?P<date>\d{1,2}-[A-Za-z]{3}-\d{2})\s*\((?P<days>\d+)d\)"
    r".*?IDiv\s+(?P<idiv>-?[\d.]+)"
    r".*?\bR\s+(?P<r>-?[\d.]+)"
)


def parse_header(header: str) -> dict:
    """Parse the row-3 expiry header. IDiv and R are converted from % to decimals."""
    m = HEADER_RE.search(header)
    if m is None:
        raise ValueError(f"Can't parse expiry header: {header!r}")
    return {
        "expiry": pd.to_datetime(m["date"], format="%d-%b-%y"),
        "days": int(m["days"]),
        "idiv": float(m["idiv"]) / 100.0,
        "r": float(m["r"]) / 100.0,
    }


def _parse_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    meta = parse_header(str(raw.iat[2, 0]))
    data = raw.iloc[3:]

    legs = []
    for cp, offset in (("C", 0), ("P", len(COLS))):
        leg = data.iloc[:, offset:offset + len(COLS)].copy()
        leg.columns = COLS
        leg["cp"] = cp
        legs.append(leg)
    df = pd.concat(legs, ignore_index=True)

    for c in ("Strike", "Bid", "Ask", "IVM"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Strike", "Bid", "Ask"])

    out = pd.DataFrame({
        "expiry": meta["expiry"],
        "days": meta["days"],
        "T": meta["days"] / 365.0,
        "K": df["Strike"].astype(float),
        "cp": df["cp"],
        "bid": df["Bid"].astype(float),
        "ask": df["Ask"].astype(float),
        "ivm": df["IVM"].astype(float) / 100.0,
        "idiv": meta["idiv"],
        "r": meta["r"],
    })
    out.insert(out.columns.get_loc("ask") + 1, "mid", 0.5 * (out["bid"] + out["ask"]))
    return out


def load_spx(path=DEFAULT_PATH) -> pd.DataFrame:
    """All expiries, calls and puts, in one tidy DataFrame.

    Columns: expiry, days, T (days/365), K, cp ('C'/'P'), bid, ask, mid,
             ivm (decimal), idiv (decimal), r (decimal).
    Rows with bid <= 0 are dropped.
    """
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    df = pd.concat([_parse_sheet(raw) for raw in sheets.values()], ignore_index=True)
    df = df[df["bid"] > 0]
    return df.sort_values(["expiry", "cp", "K"]).reset_index(drop=True)


if __name__ == "__main__":
    df = load_spx()
    print(df.head(), "\n")
    print(df.groupby("expiry").agg(days=("days", "first"), r=("r", "first"),
                                   idiv=("idiv", "first"), n=("K", "size"),
                                   K_min=("K", "min"), K_max=("K", "max")))
