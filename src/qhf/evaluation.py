"""After-the-fact evaluation on 2020–2024. Never used to choose a portfolio or a parameter."""
from __future__ import annotations

import numpy as np
import pandas as pd

from qhf.config import Config
from qhf.portfolio import turnover as turnover_vs_current
from qhf.portfolio import weights


def buy_and_hold_wealth(returns: pd.DataFrame, w: np.ndarray, initial_cost: float = 0.0) -> pd.Series:
    """Weights drift with prices; wealth per initial unit after an optional one-off switching cost."""
    return pd.Series((1 - initial_cost) * ((1 + returns).cumprod().to_numpy() @ w), index=returns.index)


def max_drawdown(wealth: pd.Series) -> float:
    path = np.concatenate([[1.0], wealth.to_numpy()])
    return float((path / np.maximum.accumulate(path) - 1).min())


def monthly_returns_from_wealth(wealth: pd.Series) -> np.ndarray:
    path = np.concatenate([[1.0], wealth.to_numpy()])
    return path[1:] / path[:-1] - 1


def replay_rule(
    returns: pd.DataFrame, target: np.ndarray, threshold: float | None, cost_rate: float = 0.0, initial_cost: float = 0.0
) -> dict[str, float]:
    """Hold, or restore the target when any weight drifts more than ``threshold`` (decided after each month).

    Returns are earned on start-of-month weights; a rebalance happens after the month and costs
    ``cost_rate`` × one-way turnover.
    """
    w = target.astype(float).copy()
    wealth, peak, worst, trades, turnover = 1.0 - initial_cost, 1.0 - initial_cost, 0.0, 0, 0.0
    for row in returns.to_numpy():
        port = float(w @ row)
        wealth *= 1 + port
        peak = max(peak, wealth)
        worst = min(worst, wealth / peak - 1)
        w = w * (1 + row) / (1 + port)
        if threshold is not None and np.abs(w - target).max() > threshold:
            traded = float(np.abs(w - target).sum() / 2)
            turnover += traded
            wealth *= 1 - cost_rate * traded
            trades += 1
            w = target.astype(float).copy()
    return {"terminal_wealth": wealth, "max_drawdown": worst, "trades": trades, "turnover": turnover}


def holdout_table(evaluation: pd.DataFrame, portfolios: dict[str, np.ndarray], config: Config) -> pd.DataFrame:
    rows = []
    for profile in config.profiles:
        for role, x in portfolios.items():
            switch_cost = config.change_penalty * turnover_vs_current(x, config)
            wealth = buy_and_hold_wealth(evaluation, weights(x, config), initial_cost=switch_cost)
            monthly = monthly_returns_from_wealth(buy_and_hold_wealth(evaluation, weights(x, config)))
            rows.append({
                "profile": profile.name, "portfolio": role, "switch_cost": switch_cost,
                "terminal_wealth": float(wealth.iloc[-1]), "max_drawdown": max_drawdown(wealth),
                "breach_frequency_drifting_weights": float(np.mean(-monthly > profile.loss_threshold)),
                "loss_tolerance": profile.loss_tolerance,
            })
    return pd.DataFrame(rows)


def rule_table(evaluation: pd.DataFrame, portfolios: dict[str, np.ndarray], config: Config) -> pd.DataFrame:
    rows = []
    for role, x in portfolios.items():
        for threshold in (None, *config.rebalance_thresholds):
            name = "hold" if threshold is None else f"rebalance at {threshold:.0%} drift"
            initial = config.change_penalty * turnover_vs_current(x, config)
            result = replay_rule(evaluation, weights(x, config), threshold, config.change_penalty, initial)
            rows.append({"portfolio": role, "rule": name, **result})
    return pd.DataFrame(rows)
