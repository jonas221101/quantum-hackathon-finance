from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import INDUSTRIES


@dataclass(frozen=True)
class ScenarioTable:
    name: str
    returns: pd.DataFrame

    @property
    def probabilities(self) -> pd.Series:
        return self.returns["probability"]


def _with_equal_probabilities(returns: pd.DataFrame) -> pd.DataFrame:
    frame = returns.copy()
    frame["probability"] = 1.0 / len(frame)
    return frame


def build_base_scenarios(returns: pd.DataFrame) -> ScenarioTable:
    """Treat the observed estimation months as an equally weighted scenario table."""
    return ScenarioTable(name="base", returns=_with_equal_probabilities(returns))


def build_return_stress_scenarios(
    returns: pd.DataFrame, hi_tec_shift: float = -0.005
) -> ScenarioTable:
    """Shift HiTec returns while keeping the scenario probabilities fixed."""
    stressed = returns.copy()
    stressed["HiTec"] = stressed["HiTec"] + hi_tec_shift
    return ScenarioTable(
        name="return_stress", returns=_with_equal_probabilities(stressed)
    )


def build_covariance_stress_scenarios(
    returns: pd.DataFrame, mix_towards_one: float = 0.25
) -> ScenarioTable:
    """Move correlations partway toward +1 using a linear transform of centered observations."""
    frame = returns.loc[:, list(INDUSTRIES)].copy()
    means = frame.mean()
    centered = frame - means

    cov = centered.cov().to_numpy()
    std = np.sqrt(np.diag(cov))
    denom = np.outer(std, std)
    corr = cov / denom
    corr = np.where(np.isfinite(corr), corr, 0.0)
    np.fill_diagonal(corr, 1.0)

    target_corr = (1.0 - mix_towards_one) * corr + mix_towards_one * np.ones_like(corr)
    np.fill_diagonal(target_corr, 1.0)
    target_cov = np.outer(std, std) * target_corr

    ridge = 1e-12
    source_cov = cov + ridge * np.eye(cov.shape[0])
    target_cov = target_cov + ridge * np.eye(target_cov.shape[0])

    source_cholesky = np.linalg.cholesky(source_cov)
    target_cholesky = np.linalg.cholesky(target_cov)
    transform = np.linalg.solve(source_cholesky, target_cholesky)

    stressed = centered.to_numpy() @ transform + means.to_numpy()
    stressed_frame = pd.DataFrame(stressed, index=frame.index, columns=frame.columns)
    return ScenarioTable(
        name="covariance_stress", returns=_with_equal_probabilities(stressed_frame)
    )


def build_all_scenario_tables(returns: pd.DataFrame) -> dict[str, ScenarioTable]:
    base = build_base_scenarios(returns)
    return {
        base.name: base,
        "return_stress": build_return_stress_scenarios(returns),
        "covariance_stress": build_covariance_stress_scenarios(returns),
    }
