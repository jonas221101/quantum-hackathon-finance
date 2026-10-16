from __future__ import annotations

from itertools import combinations

import pandas as pd

from .config import AllocationConfig, MANDATES
from .data import INDUSTRIES
from .evaluate import evaluate_selection


def all_portfolios(
    universe: tuple[str, ...] = INDUSTRIES, size: int = 3
) -> list[tuple[str, ...]]:
    return [tuple(combo) for combo in combinations(universe, size)]


def build_reference_table(
    returns: pd.DataFrame,
    scenarios: pd.DataFrame,
    allocation_config: AllocationConfig = AllocationConfig(),
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for selection in all_portfolios():
        base_metrics = evaluate_selection(
            returns,
            selection,
            mandate=next(iter(MANDATES.values())),
            scenarios=scenarios,
            allocation_config=allocation_config,
        )
        row: dict[str, object] = {
            "portfolio": "+".join(selection),
            "selection": selection,
            "mean": base_metrics.mean,
            "variance": base_metrics.variance,
            "volatility": base_metrics.volatility,
            "worst_month": base_metrics.worst_month,
            "hitec_weight": base_metrics.hitec_weight,
            "turnover": base_metrics.turnover,
            "cap_penalty": base_metrics.cap_penalty,
        }
        for mandate in MANDATES.values():
            metrics = evaluate_selection(
                returns,
                selection,
                mandate=mandate,
                scenarios=scenarios,
                allocation_config=allocation_config,
            )
            row[f"loss_prob__{mandate.name}"] = metrics.loss_probability
            row[f"score__{mandate.name}"] = metrics.score
            row[f"feasible__{mandate.name}"] = metrics.feasible
            row[f"cap_ok__{mandate.name}"] = metrics.cap_ok
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["portfolio"]).reset_index(drop=True)


def best_portfolios_by_mandate(reference_table: pd.DataFrame) -> dict[str, str]:
    winners: dict[str, str] = {}
    for mandate_name in MANDATES:
        feasible = reference_table[reference_table[f"feasible__{mandate_name}"]].copy()
        if feasible.empty:
            raise ValueError(f"No feasible portfolios for mandate {mandate_name}")
        winners[mandate_name] = str(
            feasible.sort_values(f"score__{mandate_name}", ascending=False).iloc[0][
                "portfolio"
            ]
        )
    return winners
