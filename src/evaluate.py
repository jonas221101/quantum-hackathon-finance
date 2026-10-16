from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from .config import AllocationConfig, Mandate
from .data import CURRENT_PORTFOLIO, INDUSTRIES


@dataclass(frozen=True)
class PortfolioMetrics:
    selection: tuple[str, ...]
    mean: float
    variance: float
    volatility: float
    worst_month: float
    hitec_weight: float
    turnover: float
    score: float | None = None
    loss_probability: float | None = None
    cap_ok: bool | None = None
    feasible: bool | None = None


def equal_weight_portfolio_return(
    returns: pd.DataFrame, selection: Iterable[str]
) -> pd.Series:
    columns = list(selection)
    if not columns:
        raise ValueError("selection must not be empty")
    return returns.loc[:, columns].mean(axis=1)


def turnover_from_current(
    selection: Iterable[str], current_portfolio: Iterable[str] = CURRENT_PORTFOLIO
) -> float:
    selected = set(selection)
    current = set(current_portfolio)
    return float(len(selected - current)) / float(len(current))


def hitec_weight(selection: Iterable[str]) -> float:
    return 1.0 / 3.0 if "HiTec" in set(selection) else 0.0


def portfolio_moments(
    returns: pd.DataFrame, selection: Iterable[str]
) -> PortfolioMetrics:
    series = equal_weight_portfolio_return(returns, selection)
    mean = float(series.mean())
    variance = float(series.var(ddof=1))
    volatility = float(np.sqrt(variance))
    worst_month = float(series.min())
    return PortfolioMetrics(
        selection=tuple(selection),
        mean=mean,
        variance=variance,
        volatility=volatility,
        worst_month=worst_month,
        hitec_weight=hitec_weight(selection),
        turnover=turnover_from_current(selection),
    )


def loss_probability(
    scenarios: pd.DataFrame, selection: Iterable[str], loss_threshold: float
) -> float:
    portfolio_returns = equal_weight_portfolio_return(scenarios, selection)
    losses = -portfolio_returns
    probabilities = (
        scenarios["probability"]
        if "probability" in scenarios.columns
        else pd.Series(1.0 / len(scenarios), index=scenarios.index)
    )
    breach_mask = losses > loss_threshold
    return float(probabilities.loc[breach_mask].sum())


def portfolio_score(
    returns: pd.DataFrame,
    selection: Iterable[str],
    mandate: Mandate,
    allocation_config: AllocationConfig,
) -> float:
    metrics = portfolio_moments(returns, selection)
    return (
        metrics.mean
        - mandate.risk_weight * metrics.variance
        - allocation_config.change_penalty * metrics.turnover
    )


def evaluate_selection(
    returns: pd.DataFrame,
    selection: Iterable[str],
    mandate: Mandate,
    scenarios: pd.DataFrame | None = None,
    allocation_config: AllocationConfig = AllocationConfig(),
) -> PortfolioMetrics:
    metrics = portfolio_moments(returns, selection)
    score = portfolio_score(returns, selection, mandate, allocation_config)
    loss_prob = (
        None
        if scenarios is None
        else loss_probability(scenarios, selection, mandate.loss_threshold)
    )
    cap_ok = metrics.hitec_weight <= mandate.hitec_cap + 1e-12
    feasible = cap_ok and (loss_prob is None or loss_prob <= mandate.tolerance + 1e-12)
    return PortfolioMetrics(
        selection=metrics.selection,
        mean=metrics.mean,
        variance=metrics.variance,
        volatility=metrics.volatility,
        worst_month=metrics.worst_month,
        hitec_weight=metrics.hitec_weight,
        turnover=metrics.turnover,
        score=score,
        loss_probability=loss_prob,
        cap_ok=cap_ok,
        feasible=feasible,
    )
