"""Extract the six challenge industries (VW monthly, 2015-01..2024-12) from Ken French's 10 Industry file
and print first-look statistics for the estimation window (2015-01..2019-12).

Note: the organisers supply a frozen challenge file. French revises data with each CRSP vintage,
so numbers here may differ slightly. Use the supplied file for final results.
"""
from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd

INDUSTRIES = ["NoDur", "Manuf", "Enrgy", "HiTec", "Hlth", "Utils"]
CURRENT = ("NoDur", "Hlth", "Utils")
PROPOSAL = ("HiTec", "Hlth", "Utils")


def load_vw_monthly(csv_path: Path) -> pd.DataFrame:
    lines = csv_path.read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if "Average Value Weighted Returns -- Monthly" in l) + 1
    end = next(i for i in range(start + 1, len(lines)) if not lines[i].strip())
    rows = [l.split(",") for l in lines[start:end]]
    header = [h.strip() for h in rows[0]]
    df = pd.DataFrame([[c.strip() for c in r] for r in rows[1:]], columns=["date"] + header[1:])
    df["date"] = pd.PeriodIndex(df["date"], freq="M")
    return df.set_index("date").astype(float) / 100.0  # percent -> decimal


def portfolio_stats(mu: pd.Series, cov: pd.DataFrame, names: tuple[str, ...]) -> tuple[float, float]:
    w = np.full(len(names), 1 / len(names))
    m = float(w @ mu[list(names)])
    v = float(w @ cov.loc[list(names), list(names)].values @ w)
    return m, np.sqrt(v)


def main(csv_path: Path, out_path: Path) -> None:
    returns = load_vw_monthly(csv_path)[INDUSTRIES].loc["2015-01":"2024-12"]
    assert len(returns) == 120, len(returns)
    returns.to_csv(out_path)

    est = returns.loc["2015-01":"2019-12"]
    assert len(est) == 60
    mu, cov = est.mean(), est.cov()
    print("Estimation window 2015-01..2019-12 (monthly, decimal)")
    print(pd.DataFrame({"mean": mu, "vol": np.sqrt(np.diag(cov)), "min": est.min()}).round(4))
    print("\nCorrelation\n", est.corr().round(2))

    print("\nAll 20 equal-weight 3-of-6 portfolios (monthly mean, vol, worst month in window)")
    table = []
    for combo in combinations(INDUSTRIES, 3):
        m, s = portfolio_stats(mu, cov, combo)
        worst = est[list(combo)].mean(axis=1).min()
        tag = "CURRENT" if set(combo) == set(CURRENT) else "PROPOSAL" if set(combo) == set(PROPOSAL) else ""
        table.append(("+".join(combo), m, s, worst, tag))
    df = pd.DataFrame(table, columns=["portfolio", "mean", "vol", "worst", "tag"]).sort_values("mean", ascending=False)
    print(df.round(4).to_string(index=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
