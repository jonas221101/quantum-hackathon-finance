"""Financial quantities for an equal-weight selection x ∈ {0,1}^n."""
from __future__ import annotations

import math

import numpy as np

from qhf.config import Config, Profile


def selection(names: tuple[str, ...], config: Config) -> np.ndarray:
    x = np.zeros(len(config.industries), dtype=int)
    for name in names:
        x[config.index(name)] = 1
    return x


def label(x: np.ndarray, config: Config) -> str:
    return "+".join(name for name, bit in zip(config.industries, x) if bit)


def weights(x: np.ndarray, config: Config) -> np.ndarray:
    return np.asarray(x, dtype=float) / config.cardinality


def turnover(x: np.ndarray, config: Config) -> float:
    """One-way turnover vs the current tilt: ½ Σ |w − w⁰|."""
    return float(np.abs(weights(x, config) - weights(selection(config.current, config), config)).sum() / 2)


def cap_excess(x: np.ndarray, profile: Profile, config: Config) -> float:
    return max(0.0, float(weights(x, config)[config.index(config.capped_industry)]) - profile.hitec_cap)


def objective(x: np.ndarray, mu: np.ndarray, sigma: np.ndarray, profile: Profile, config: Config) -> float:
    """f(x) = −μᵀw + λ wᵀΣw + (τ/H)·turnover + κ·cap excess (lower is better)."""
    w = weights(x, config)
    return float(
        -mu @ w
        + profile.risk_aversion * w @ sigma @ w
        + config.change_penalty / config.holding_horizon * turnover(x, config)
        + config.cap_penalty * cap_excess(x, profile, config)
    )


def breach_count(x: np.ndarray, outcomes: np.ndarray, threshold: float, config: Config) -> int:
    """Number of scenarios whose one-month loss is strictly greater than ``threshold``."""
    losses = -(outcomes @ weights(x, config))
    return int(np.sum(losses > threshold))


def allowed_breaches(n_scenarios: int, tolerance: float) -> int:
    """Integer form of P(breach) ≤ α on an equally weighted table (avoids float boundary errors)."""
    return math.floor(tolerance * n_scenarios + 1e-9)


def passes_loss_rule(x: np.ndarray, outcomes: np.ndarray, profile: Profile, config: Config, strict: bool = False) -> bool:
    """Binding rule H3. ``strict=True`` uses P < α instead of P ≤ α (robustness line)."""
    breaches = breach_count(x, outcomes, profile.loss_threshold, config)
    if strict:
        return breaches < profile.loss_tolerance * len(outcomes) - 1e-9
    return breaches <= allowed_breaches(len(outcomes), profile.loss_tolerance)


def whole_portfolio_loss_probability(x: np.ndarray, outcomes: np.ndarray, profile: Profile, config: Config) -> float:
    """Loss probability of (1 − s)·core + s·tilt, with the core proxied by equal weights on all sectors."""
    n = len(config.industries)
    total = (1 - config.satellite_share) * np.full(n, 1 / n) + config.satellite_share * weights(x, config)
    return float(np.mean(-(outcomes @ total) > profile.loss_threshold))
