"""Robustness: which changes move the optimum? Rows are tagged financial / cost assumption / mandate.

Computational-representation rows (QAOA variants) are appended by the CLI from the quantum experiment.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

from qhf.config import Config, Profile
from qhf.decision import NONE_ADMISSIBLE, best_label, bootstrap_draws
from qhf.exact import NoAdmissiblePortfolio, rank_portfolios
from qhf.portfolio import objective, selection, weights
from qhf.scenarios import moments, return_stress


def _row(category: str, change: str, profile: Profile, optimum_label: str, base_label: str) -> dict:
    return {"category": category, "change": change, "profile": profile.name,
            "optimum": optimum_label, "same_as_base": optimum_label == base_label}


def _safe(outcomes: np.ndarray, profile: Profile, config: Config, sigma: np.ndarray | None = None) -> str:
    try:
        return best_label(outcomes, profile, config, sigma)
    except NoAdmissiblePortfolio:
        return NONE_ADMISSIBLE


def robustness_table(scenarios: dict[str, np.ndarray], config: Config) -> pd.DataFrame:
    base = scenarios["base"]
    a = config.analysis
    rows = []
    for profile in config.profiles:
        ref = _safe(base, profile, config)
        financial = {
            "base (60 months, 1/60 each)": (base, None),
            "supplied return stress (HiTec −0.5pp)": (scenarios["return_stress"], None),
            "supplied covariance stress (corr 25% → +1)": (scenarios["covariance_stress"], None),
            **{f"HiTec mean {s * 100:+.1f}pp": (return_stress(base, config, shift=s), None) for s in a.robust_hitec_shifts},
            "Ledoit–Wolf covariance (loss table unchanged)": (base, LedoitWolf().fit(base).covariance_),
        }
        for change, (outcomes, sigma) in financial.items():
            rows.append(_row("financial", change, profile, _safe(outcomes, profile, config, sigma), ref))
        cost = {
            **{f"switching cost × {f:g}": (profile, replace(config, change_penalty=config.change_penalty * f))
               for f in a.robust_change_penalty_factors},
            f"holding horizon {a.robust_holding_horizon:g} months": (profile, replace(config, holding_horizon=a.robust_holding_horizon)),
        }
        mandate = {
            **{f"risk aversion × {f:g}": (replace(profile, risk_aversion=profile.risk_aversion * f), config)
               for f in a.robust_risk_aversion_factors},
            **{f"loss threshold {s * 100:+.0f}pp": (replace(profile, loss_threshold=profile.loss_threshold + s), config)
               for s in a.robust_loss_threshold_steps},
            **{f"loss tolerance {t:.0%}": (replace(profile, loss_tolerance=t), config) for t in a.robust_loss_tolerances},
            **{f"cap preference κ = {k:g}": (profile, replace(config, cap_penalty=k)) for k in a.robust_cap_penalties},
            f"exclude {'+'.join(a.robust_exclusion)}": (profile, replace(config, excluded=a.robust_exclusion)),
        }
        for category, changes in (("cost assumption", cost), ("mandate", mandate)):
            for change, (prof, cfg) in changes.items():
                rows.append(_row(category, change, profile, _safe(base, prof, cfg), ref))
    return pd.DataFrame(rows)


def strict_convention_optima(scenarios: dict[str, np.ndarray], config: Config) -> dict[str, dict[str, str]]:
    """Optimum when the loss rule is read as P < α instead of P ≤ α."""
    result: dict[str, dict[str, str]] = {}
    for profile in config.profiles:
        result[profile.name] = {}
        for name, outcomes in scenarios.items():
            mu, sigma = moments(outcomes, config.ddof)
            table = rank_portfolios(mu, sigma, outcomes, profile, config)
            strict = table[table.passes_loss_rule_strict]
            result[profile.name][name] = str(strict.iloc[0]["holdings"]) if len(strict) else NONE_ADMISSIBLE
    return result


def decision_map(base: np.ndarray, profile: Profile, config: Config, axis: str) -> pd.DataFrame:
    """Optimum over a grid of risk aversion × (HiTec shift | switching cost)."""
    a = config.analysis
    lams = np.geomspace(*a.map_risk_aversion[:2], int(a.map_risk_aversion[2]))
    if axis == "hitec_shift":
        values = np.linspace(*a.map_hitec_shift[:2], int(a.map_hitec_shift[2]))
        setting = lambda v: (return_stress(base, config, shift=float(v)), config)  # noqa: E731
    elif axis == "change_penalty":
        values = np.linspace(*a.map_change_penalty[:2], int(a.map_change_penalty[2]))
        setting = lambda v: (base, replace(config, change_penalty=float(v)))  # noqa: E731
    else:
        raise ValueError(f"unknown decision-map axis {axis!r}")
    rows = []
    for value in values:
        outcomes, cfg = setting(value)
        for lam in lams:
            rows.append({"risk_aversion": float(lam), axis: float(value),
                         "optimum": _safe(outcomes, replace(profile, risk_aversion=float(lam)), cfg)})
    return pd.DataFrame(rows)


def proposal_advantage(outcomes: np.ndarray, profile: Profile, config: Config) -> float:
    """Score of the current tilt minus that of the proposal (> 0: the proposal is better). Loss rule not included."""
    mu, sigma = moments(outcomes, config.ddof)
    current, proposal = selection(config.current, config), selection(config.proposal, config)
    return objective(current, mu, sigma, profile, config) - objective(proposal, mu, sigma, profile, config)


def estimation_error(base: np.ndarray, profile: Profile, config: Config) -> tuple[dict, pd.DataFrame, np.ndarray]:
    """Proposal-vs-current advantage against the estimation error of the HiTec mean that drives it.

    Returns a summary, the advantage along the HiTec mean shift and the advantage in every bootstrap resample
    (the same draws as the verdict's bootstrap evidence).
    """
    a = config.analysis
    shifts = np.linspace(*a.map_hitec_shift[:2], int(a.map_hitec_shift[2]))
    curve = pd.DataFrame({"hitec_shift": shifts,
                          "advantage": [proposal_advantage(return_stress(base, config, shift=float(s)), profile, config)
                                        for s in shifts]})
    resampled = np.array([proposal_advantage(sample, profile, config) for sample in bootstrap_draws(base, profile, config)])
    stressed = config.index(config.return_stress_industry)
    standard_error = float(base[:, stressed].std(ddof=config.ddof) / np.sqrt(len(base)))
    slope = float(weights(selection(config.proposal, config), config)[stressed]
                  - weights(selection(config.current, config), config)[stressed])  # d advantage / d shift
    advantage = proposal_advantage(base, profile, config)
    break_even_shift = -advantage / slope if slope else None
    p05, p50, p95 = np.quantile(resampled, [0.05, 0.5, 0.95])
    summary = {
        "profile": profile.name, "advantage_base": advantage, "break_even_hitec_shift": break_even_shift,
        "hitec_mean": float(base[:, stressed].mean()), "hitec_mean_standard_error": standard_error,
        "break_even_in_standard_errors": None if break_even_shift is None else break_even_shift / standard_error,
        "supplied_stress_in_standard_errors": config.return_stress_shift / standard_error,
        "bootstrap_share_proposal_better": float(np.mean(resampled > 0)),
        "bootstrap_advantage_p05": float(p05), "bootstrap_advantage_p50": float(p50), "bootstrap_advantage_p95": float(p95),
    }
    return summary, curve, resampled
