"""From exact rankings to a verdict per profile: keep / switch / review, plus break-even points.

Verdict rule (burden of proof on the change, but with a symmetric admissibility check):
- keep   : the current tilt is the admissible optimum in all scenario sets and stays admissible in
           ≥ threshold of bootstrap resamples;
- switch : the same X ≠ current is optimal in all scenario sets, beats the current tilt by more than
           ``switch_margin``, beats it in ≥ threshold of resamples and is admissible in ≥ threshold of resamples;
- review : anything else (default action: hold, the committee decides with a stated belief).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from typing import Callable, Iterator

import numpy as np

from qhf.config import Config, Profile
from qhf.exact import NoAdmissiblePortfolio, optimum, rank_portfolios
from qhf.portfolio import label, objective, passes_loss_rule, selection
from qhf.scenarios import moments, return_stress

DEFAULT_REVIEW_ACTION = "hold the current tilt; the committee decides with a stated belief"
NONE_ADMISSIBLE = "none admissible"


@dataclass(frozen=True)
class Evidence:
    modal: dict[str, float]  # how often each portfolio is the admissible optimum (diagnostic)
    target_beats_current: float
    target_admissible: float
    current_admissible: float
    none_admissible: float


@dataclass(frozen=True)
class Verdict:
    profile: str
    verdict: str  # keep | switch | review
    target: str  # recommended holdings (current tilt for keep / review)
    candidate: str  # base-case optimum the evidence refers to
    optima: dict[str, str]
    margin: float  # base objective of current minus that of the candidate (≥ 0)
    evidence: Evidence
    reason: str
    action: str
    is_default_profile: bool


def best_label(outcomes: np.ndarray, profile: Profile, config: Config, sigma: np.ndarray | None = None) -> str:
    mu, sample_sigma = moments(outcomes, config.ddof)
    table = rank_portfolios(mu, sample_sigma if sigma is None else sigma, outcomes, profile, config)
    return str(optimum(table)["holdings"])


def _safe_best(outcomes: np.ndarray, profile: Profile, config: Config) -> str:
    try:
        return best_label(outcomes, profile, config)
    except NoAdmissiblePortfolio:
        return NONE_ADMISSIBLE


def _profile_seed(profile: Profile, config: Config) -> np.random.SeedSequence:
    digest = int.from_bytes(hashlib.sha256(profile.name.encode()).digest()[:4], "little")
    return np.random.SeedSequence([config.seed, digest])


def bootstrap_draws(base: np.ndarray, profile: Profile, config: Config) -> Iterator[np.ndarray]:
    """The 60 estimation months resampled with replacement; the same draws per profile for every consumer."""
    rng = np.random.default_rng(_profile_seed(profile, config))
    for _ in range(config.bootstrap_samples):
        yield base[rng.integers(0, len(base), len(base))]


def bootstrap_evidence(base: np.ndarray, profile: Profile, config: Config, target: str) -> Evidence:
    """Resample the 60 estimation months with replacement (same draws for every candidate)."""
    current = selection(config.current, config)
    candidate = selection(tuple(target.split("+")), config)
    modal: dict[str, int] = {}
    beats = target_ok = current_ok = none = 0
    for sample in bootstrap_draws(base, profile, config):
        mu, sigma = moments(sample, config.ddof)
        winner = _safe_best(sample, profile, config)
        modal[winner] = modal.get(winner, 0) + 1
        none += winner == NONE_ADMISSIBLE
        beats += objective(candidate, mu, sigma, profile, config) < objective(current, mu, sigma, profile, config)
        target_ok += passes_loss_rule(candidate, sample, profile, config)
        current_ok += passes_loss_rule(current, sample, profile, config)
    n = config.bootstrap_samples
    freq = {k: v / n for k, v in sorted(modal.items(), key=lambda kv: (-kv[1], kv[0]))}
    return Evidence(freq, beats / n, target_ok / n, current_ok / n, none / n)


def decide(scenarios: dict[str, np.ndarray], profile: Profile, config: Config) -> Verdict:
    current = label(selection(config.current, config), config)
    optima = {name: _safe_best(outcomes, profile, config) for name, outcomes in scenarios.items()}
    candidate = optima["base"]
    if NONE_ADMISSIBLE in optima.values():
        empty = Evidence({}, 0.0, 0.0, 0.0, 1.0)
        return Verdict(profile.name, "review", label(selection(config.current, config), config), candidate, optima, 0.0,
                       empty, "no portfolio passes the binding loss rule in at least one scenario set",
                       DEFAULT_REVIEW_ACTION, profile.name == config.default_profile)
    mu, sigma = moments(scenarios["base"], config.ddof)
    margin = objective(selection(config.current, config), mu, sigma, profile, config) - objective(
        selection(tuple(candidate.split("+")), config), mu, sigma, profile, config)
    evidence = bootstrap_evidence(scenarios["base"], profile, config, candidate)
    threshold = config.bootstrap_threshold
    stable = len(set(optima.values())) == 1
    if stable and candidate == current:
        if evidence.current_admissible >= threshold:
            verdict, reason = "keep", "current tilt optimal in all scenario sets and robustly admissible"
        else:
            verdict, reason = "review", f"current tilt optimal but admissible in only {evidence.current_admissible:.0%} of resamples"
    elif not stable:
        verdict, reason = "review", "the optimum changes between the base case and a supplied stress"
    elif margin <= config.switch_margin:
        verdict, reason = "review", "improvement over the current tilt does not exceed the switch margin"
    elif evidence.target_beats_current < threshold:
        verdict, reason = "review", f"candidate beats the current tilt in only {evidence.target_beats_current:.0%} of resamples"
    elif evidence.target_admissible < threshold:
        verdict, reason = "review", f"candidate passes the loss rule in only {evidence.target_admissible:.0%} of resamples"
    else:
        verdict, reason = "switch", "same optimum in all scenario sets and robust under resampling"
    target = candidate if verdict == "switch" else current
    action = {"keep": "keep the current tilt", "switch": f"switch to {candidate}"}.get(verdict, DEFAULT_REVIEW_ACTION)
    return Verdict(profile.name, verdict, target, candidate, optima, float(margin), evidence, reason, action,
                   profile.name == config.default_profile)


def _setter(param: str, base: np.ndarray, profile: Profile, config: Config) -> Callable[[float], tuple[np.ndarray, Profile, Config]]:
    if param == "risk_aversion":
        return lambda v: (base, replace(profile, risk_aversion=v), config)
    if param == "hitec_shift":
        return lambda v: (return_stress(base, config, shift=v), profile, config)
    if param in {"change_penalty", "cap_penalty", "holding_horizon"}:
        return lambda v: (base, profile, replace(config, **{param: v}))
    raise ValueError(f"unknown break-even parameter {param!r}")


def break_even(
    base: np.ndarray, profile: Profile, config: Config, param: str, low: float, high: float, log_scale: bool = False,
) -> list[dict[str, float | str]]:
    """All values in [low, high] where the base-case optimum changes, refined by bisection."""
    points, iterations = config.analysis.break_even_points, config.analysis.bisection_iterations
    if log_scale and low <= 0:
        raise ValueError("log-scale break-even search needs low > 0")
    setter = _setter(param, base, profile, config)
    winner = lambda v: _safe_best(*setter(v))  # noqa: E731
    midpoint = (lambda a, b: np.sqrt(a * b)) if log_scale else (lambda a, b: (a + b) / 2)
    grid = np.geomspace(low, high, points) if log_scale else np.linspace(low, high, points)
    labels = [winner(v) for v in grid]
    changes = []

    def refine(lo: float, hi: float, from_label: str) -> tuple[float, str]:
        for _ in range(iterations):
            mid = midpoint(lo, hi)
            lo, hi = (mid, hi) if winner(mid) == from_label else (lo, mid)
        to_label = winner(hi)
        changes.append({"value": float(midpoint(lo, hi)), "from": from_label, "to": to_label})
        return hi, to_label

    for a, b, la, lb in zip(grid[:-1], grid[1:], labels[:-1], labels[1:]):
        lo, current = a, la
        while current != lb:  # several flips inside one grid cell are found one after another
            lo, current = refine(lo, b, current)
            if lo >= b:
                break
    return changes
