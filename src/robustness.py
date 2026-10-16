from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import AllocationConfig, MANDATES, Mandate
from .data import CURRENT_PORTFOLIO, INDUSTRIES
from .enumerate import all_portfolios, best_portfolios_by_mandate, build_reference_table
from .evaluate import evaluate_selection, portfolio_moments


def holdout_table(
    evaluation: pd.DataFrame, selections: dict[str, str]
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for mandate, portfolio in selections.items():
        selection = tuple(portfolio.split("+"))
        metrics = portfolio_moments(evaluation, selection)
        rows.append(
            {
                "mandate": mandate,
                "portfolio": portfolio,
                "mean": metrics.mean,
                "volatility": metrics.volatility,
                "worst_month": metrics.worst_month,
            }
        )
    return pd.DataFrame(rows)


def sensitivity_table(
    returns: pd.DataFrame,
    scenarios: pd.DataFrame,
    *,
    mandate_name: str,
    shifts: tuple[float, ...] = (-0.01, -0.005, 0.0, 0.005),
    risk_weights: tuple[float, ...] = (0.5, 1.0, 5.0, 20.0, 50.0),
    change_penalties: tuple[float, ...] = (0.0, 0.002, 0.005, 0.01),
) -> pd.DataFrame:
    base = MANDATES[mandate_name]
    rows: list[dict[str, Any]] = []
    for shift in shifts:
        shifted = returns.copy()
        shifted["HiTec"] += shift
        scenario_shifted = scenarios.copy()
        scenario_shifted["HiTec"] += shift
        table = build_reference_table(shifted, scenario_shifted, AllocationConfig())
        winner = best_portfolios_by_mandate(table)[mandate_name]
        rows.append({"parameter": "HiTec shift", "value": shift, "winner": winner})
    for value in risk_weights:
        mandate = Mandate(
            base.name, value, base.loss_threshold, base.tolerance, base.hitec_cap
        )
        candidates = []
        for selection in all_portfolios():
            metrics = evaluate_selection(
                returns, selection, mandate, scenarios, AllocationConfig()
            )
            if metrics.feasible:
                candidates.append((metrics.score or float("-inf"), "+".join(selection)))
        winner = max(candidates)[1] if candidates else "review"
        rows.append({"parameter": "risk weight", "value": value, "winner": winner})
    for value in change_penalties:
        table = build_reference_table(
            returns, scenarios, AllocationConfig(change_penalty=value)
        )
        rows.append(
            {
                "parameter": "change penalty",
                "value": value,
                "winner": best_portfolios_by_mandate(table)[mandate_name],
            }
        )
    return pd.DataFrame(rows)


def bootstrap_winner_stability(
    returns: pd.DataFrame,
    scenarios: pd.DataFrame,
    *,
    samples: int = 500,
    seed: int = 7,
) -> pd.DataFrame:
    """Resample estimation months and report winner frequencies."""
    rng = np.random.default_rng(seed)
    counts: dict[tuple[str, str], int] = {}
    for _ in range(samples):
        indices = rng.integers(0, len(returns), len(returns))
        sample = returns.iloc[indices].reset_index(drop=True)
        scenario_sample = scenarios.iloc[indices].reset_index(drop=True)
        winners = best_portfolios_by_mandate(
            build_reference_table(sample, scenario_sample, AllocationConfig())
        )
        for mandate, winner in winners.items():
            counts[(mandate, winner)] = counts.get((mandate, winner), 0) + 1
    return pd.DataFrame(
        [
            {
                "mandate": mandate,
                "portfolio": portfolio,
                "frequency": count / samples,
                "samples": samples,
            }
            for (mandate, portfolio), count in counts.items()
        ]
    )
