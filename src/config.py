from __future__ import annotations

from dataclasses import dataclass

from .data import CURRENT_PORTFOLIO, PROPOSAL_PORTFOLIO


@dataclass(frozen=True)
class Mandate:
    name: str
    risk_weight: float
    loss_threshold: float
    tolerance: float
    hitec_cap: float


@dataclass(frozen=True)
class AllocationConfig:
    change_penalty: float = 0.002
    current_portfolio: tuple[str, ...] = CURRENT_PORTFOLIO
    proposal_portfolio: tuple[str, ...] = PROPOSAL_PORTFOLIO


MANDATES: dict[str, Mandate] = {
    "growth_oriented": Mandate(
        "growth_oriented",
        risk_weight=1.0,
        loss_threshold=0.08,
        tolerance=0.10,
        hitec_cap=1.00,
    ),
    "balanced": Mandate(
        "balanced", risk_weight=5.0, loss_threshold=0.05, tolerance=0.10, hitec_cap=0.35
    ),
    "risk_sensitive": Mandate(
        "risk_sensitive",
        risk_weight=20.0,
        loss_threshold=0.03,
        tolerance=0.10,
        hitec_cap=0.20,
    ),
}

DEFAULT_ALLOCATION_CONFIG = AllocationConfig()
