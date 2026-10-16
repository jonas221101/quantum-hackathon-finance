from __future__ import annotations

from dataclasses import dataclass

from .config import AllocationConfig, Mandate
from .evaluate import PortfolioMetrics, evaluate_selection


@dataclass(frozen=True)
class DecisionRecord:
    selection: tuple[str, ...]
    mandate: str
    verdict: str
    reason: str
    metrics: PortfolioMetrics


def decide_selection(
    returns,
    selection: tuple[str, ...],
    mandate: Mandate,
    scenarios=None,
    allocation_config: AllocationConfig = AllocationConfig(),
) -> DecisionRecord:
    metrics = evaluate_selection(
        returns,
        selection,
        mandate=mandate,
        scenarios=scenarios,
        allocation_config=allocation_config,
    )

    if (
        metrics.loss_probability is not None
        and metrics.loss_probability > mandate.tolerance
    ):
        return DecisionRecord(
            selection=selection,
            mandate=mandate.name,
            verdict="reject",
            reason="Loss tolerance exceeded",
            metrics=metrics,
        )
    if metrics.loss_probability is None:
        return DecisionRecord(
            selection=selection,
            mandate=mandate.name,
            verdict="review",
            reason="Missing scenario evidence",
            metrics=metrics,
        )
    return DecisionRecord(
        selection=selection,
        mandate=mandate.name,
        verdict="accept",
        reason="Binding rules satisfied",
        metrics=metrics,
    )
