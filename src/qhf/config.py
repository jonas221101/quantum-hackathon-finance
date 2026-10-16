"""All model, data and solver parameters in one place.

Mandate values are teaching assumptions taken from the organiser configuration, not regulation.
Profiles are chosen actively by each insured person (team decision, 16 Oct 2026); the sector cap is a
preference expressed through ``cap_penalty`` (kappa), not a binding rule.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Profile:
    name: str
    risk_aversion: float  # lambda: weight on monthly variance
    loss_threshold: float  # L: one-month loss that counts as a breach
    loss_tolerance: float  # alpha: tolerated breach probability (binding rule H3)
    hitec_cap: float  # preferred maximum HiTec weight (preference, penalised with kappa)


@dataclass(frozen=True)
class QaoaSettings:
    layers: tuple[int, ...] = (1, 2, 3)
    seeds: int = 10
    starts_per_seed: int = 5
    maxiter: int = 500
    rhobeg: float = 0.4
    tol: float = 1e-7
    shots: int = 4096
    cvar_alpha: float = 0.25  # used only by the CVaR-objective variant
    penalty_margin: float = 0.001  # organiser rule: P = full cost range + margin
    tuned_penalty_margin: float = 0.10  # tuned baseline: critical penalty × (1 + margin)
    shot_noise_seeds: int = 3
    shot_noise_shots: int = 1024  # shots per evaluation in the one shot-noisy optimisation run


@dataclass(frozen=True)
class AnalysisSettings:
    """Grids and ranges for break-even search, decision maps and robustness checks."""
    break_even_ranges: tuple[tuple[str, float, float, bool], ...] = (
        ("risk_aversion", 0.1, 100.0, True),
        ("hitec_shift", -0.02, 0.01, False),
        ("change_penalty", 0.0, 0.05, False),
        ("cap_penalty", 0.0, 0.1, False),
    )
    break_even_points: int = 121
    bisection_iterations: int = 40
    map_risk_aversion: tuple[float, float, int] = (0.5, 50.0, 41)  # log grid
    map_hitec_shift: tuple[float, float, int] = (-0.012, 0.006, 37)
    map_change_penalty: tuple[float, float, int] = (0.0, 0.012, 25)
    robust_hitec_shifts: tuple[float, ...] = (-0.01, 0.005)
    robust_risk_aversion_factors: tuple[float, ...] = (0.5, 2.0)
    robust_loss_threshold_steps: tuple[float, ...] = (-0.01, 0.01)
    robust_loss_tolerances: tuple[float, ...] = (0.05, 0.15)
    robust_cap_penalties: tuple[float, ...] = (0.0, 0.05)
    robust_change_penalty_factors: tuple[float, ...] = (0.0, 3.0)
    robust_holding_horizon: float = 12.0
    robust_exclusion: tuple[str, ...] = ("Enrgy",)
    diagram_angles: tuple[float, float] = (0.3, 0.2)  # gamma, beta used only to draw example circuits


@dataclass(frozen=True)
class Config:
    data_path: str = "Database/returns_6_industries_monthly.csv"
    data_sha256: str = "083dbb4332bdea357f12fae310f7155624df12d14643e0eee574873586f811f5"
    industries: tuple[str, ...] = ("NoDur", "Manuf", "Enrgy", "HiTec", "Hlth", "Utils")
    estimation_start: str = "2015-01"
    estimation_end: str = "2019-12"
    evaluation_start: str = "2020-01"
    evaluation_end: str = "2024-12"
    current: tuple[str, ...] = ("NoDur", "Hlth", "Utils")
    proposal: tuple[str, ...] = ("HiTec", "Hlth", "Utils")
    cardinality: int = 3
    capped_industry: str = "HiTec"
    change_penalty: float = 0.002  # tau, per unit of one-way turnover (trading-cost proxy; public fund pays no tax)
    holding_horizon: float = 1.0  # H in months; tau is spread over H (organiser convention H = 1)
    cap_penalty: float = 0.01  # kappa, monthly return given up per unit of weight above the cap
    satellite_share: float = 0.10  # s, share of cohort equity in the tilt sleeve (whole-portfolio view only)
    excluded: tuple[str, ...] = ()  # exclusion set E (qubits removed)
    switch_margin: float = 0.0  # epsilon: required objective improvement over the current tilt
    bootstrap_samples: int = 500
    bootstrap_threshold: float = 0.70
    return_stress_industry: str = "HiTec"
    return_stress_shift: float = -0.005
    covariance_stress_mix: float = 0.25
    rebalance_thresholds: tuple[float, ...] = (0.02, 0.05)
    ddof: int = 1
    default_profile: str = "balanced"  # for insured people who make no active choice (open assumption)
    seed: int = 2026
    profiles: tuple[Profile, ...] = (
        Profile("growth", 1.0, 0.08, 0.10, 1.00),
        Profile("balanced", 5.0, 0.05, 0.10, 0.35),
        Profile("risk_sensitive", 20.0, 0.03, 0.10, 0.20),
    )
    qaoa: QaoaSettings = field(default_factory=QaoaSettings)
    analysis: AnalysisSettings = field(default_factory=AnalysisSettings)
    cvar_variant: bool = True  # also run the CVaR-objective QAOA variant

    def profile(self, name: str) -> Profile:
        for p in self.profiles:
            if p.name == name:
                return p
        raise KeyError(f"unknown profile {name!r}")

    def index(self, industry: str) -> int:
        return self.industries.index(industry)

    def data_file(self) -> Path:
        path = Path(self.data_path)
        return path if path.is_absolute() else REPO_ROOT / path


DEFAULT_CONFIG = Config()
FAST_QAOA = QaoaSettings(layers=(1, 2), seeds=3, starts_per_seed=2, maxiter=150)


def _coerce(value: str, current: Any) -> Any:
    if isinstance(current, bool):
        if value.lower() not in {"1", "true", "yes", "0", "false", "no"}:
            raise ValueError(f"not a boolean: {value!r}")
        return value.lower() in {"1", "true", "yes"}
    if isinstance(current, int):
        return int(value)
    if isinstance(current, float):
        return float(value)
    if isinstance(current, tuple):
        if value.strip() == "":
            return ()
        items = [v.strip() for v in value.split(",")]
        if current and isinstance(current[0], (int, float)):
            return tuple(type(current[0])(v) for v in items)
        return tuple(items)
    return value


def _replace_field(obj: Any, name: str, value: str) -> Any:
    names = {f.name for f in fields(obj)}
    if name not in names:
        raise KeyError(f"unknown parameter {name!r} for {type(obj).__name__}; valid: {sorted(names)}")
    return replace(obj, **{name: _coerce(value, getattr(obj, name))})


def apply_overrides(config: Config, overrides: list[str]) -> Config:
    """Apply ``key=value`` overrides, e.g. ``balanced.loss_threshold=0.04`` or ``qaoa.seeds=3``."""
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"override must look like key=value, got {item!r}")
        key, value = (s.strip() for s in item.split("=", 1))
        head, _, tail = key.partition(".")
        if tail and head in {"qaoa", "analysis"}:
            config = replace(config, **{head: _replace_field(getattr(config, head), tail, value)})
        elif tail:
            profile = config.profile(head)
            updated = _replace_field(profile, tail, value)
            config = replace(config, profiles=tuple(updated if p.name == head else p for p in config.profiles))
        else:
            if head in {"profiles", "qaoa", "analysis"}:
                raise KeyError(f"set {head} fields individually, e.g. balanced.risk_aversion=4")
            config = _replace_field(config, head, value)
    return config


def config_to_dict(config: Config) -> dict[str, Any]:
    return dataclasses.asdict(config)


def config_hash(config: Config) -> str:
    payload = json.dumps(config_to_dict(config), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
