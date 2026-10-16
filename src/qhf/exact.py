"""Exact reference: score every equal-weight K-of-N selection. This is the answer key, not a competitor."""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

from qhf.config import Config, Profile
from qhf.portfolio import (
    allowed_breaches,
    breach_count,
    cap_excess,
    label,
    objective,
    passes_loss_rule,
    turnover,
    weights,
)

TIE_TOLERANCE = 1e-12
SORT_DECIMALS = 12  # objective is rounded before sorting so float noise cannot reorder near-ties


class NoAdmissiblePortfolio(ValueError):
    """The binding loss rule excludes every selection."""


def free_indices(config: Config) -> list[int]:
    excluded = {config.index(name) for name in config.excluded}
    return [i for i in range(len(config.industries)) if i not in excluded]


def enumerate_portfolios(config: Config) -> list[np.ndarray]:
    """All selections with exactly K holdings among the non-excluded industries, in lexicographic order."""
    n = len(config.industries)
    result = []
    for chosen in combinations(free_indices(config), config.cardinality):
        x = np.zeros(n, dtype=int)
        x[list(chosen)] = 1
        result.append(x)
    return result


def rank_portfolios(
    mu: np.ndarray, sigma: np.ndarray, outcomes: np.ndarray, profile: Profile, config: Config
) -> pd.DataFrame:
    """One row per portfolio; ``rank`` 1 = admissible optimum. Ties are broken by label and flagged."""
    allowed = allowed_breaches(len(outcomes), profile.loss_tolerance)
    rows = []
    for x in enumerate_portfolios(config):
        w = weights(x, config)
        breaches = breach_count(x, outcomes, profile.loss_threshold, config)
        rows.append(
            {
                "holdings": label(x, config),
                "x": "".join(map(str, x)),
                "objective": objective(x, mu, sigma, profile, config),
                "mean": float(mu @ w),
                "volatility": float(np.sqrt(w @ sigma @ w)),
                "turnover": turnover(x, config),
                "cap_excess": cap_excess(x, profile, config),
                "breaches": breaches,
                "allowed_breaches": allowed,
                "passes_loss_rule": bool(passes_loss_rule(x, outcomes, profile, config)),
                "passes_loss_rule_strict": bool(passes_loss_rule(x, outcomes, profile, config, strict=True)),
            }
        )
    table = pd.DataFrame(rows)
    table["_key"] = table.objective.round(SORT_DECIMALS)
    table = table.sort_values(["_key", "holdings"], kind="mergesort").drop(columns="_key").reset_index(drop=True)
    admissible = table[table.passes_loss_rule]
    table["rank"] = pd.Series(range(1, len(admissible) + 1), index=admissible.index)
    table["rank"] = table["rank"].astype("Int64")
    best = admissible.objective.min() if len(admissible) else np.nan
    table["tied_with_optimum"] = table.passes_loss_rule & (np.abs(table.objective - best) <= TIE_TOLERANCE)
    return table


def optimum(table: pd.DataFrame) -> pd.Series:
    admissible = table[table.passes_loss_rule]
    if admissible.empty:
        raise NoAdmissiblePortfolio("no admissible portfolio: the loss rule excludes every selection")
    return admissible.iloc[0]

