"""Scenario tables: 60 equally likely monthly outcomes (base) and the two supplied hypothetical stresses."""
from __future__ import annotations

import numpy as np
import pandas as pd

from qhf.config import Config
from qhf.data import assert_estimation_only


def _matrix_root(matrix: np.ndarray, inverse: bool = False) -> np.ndarray:
    eigenvalues, vectors = np.linalg.eigh(matrix)
    if eigenvalues.min() <= 1e-12:
        raise ValueError("covariance matrix is not positive definite")
    scale = 1 / np.sqrt(eigenvalues) if inverse else np.sqrt(eigenvalues)
    return (vectors * scale) @ vectors.T


def return_stress(base: np.ndarray, config: Config, shift: float | None = None) -> np.ndarray:
    stressed = base.copy()
    stressed[:, config.index(config.return_stress_industry)] += config.return_stress_shift if shift is None else shift
    return stressed


def covariance_stress(base: np.ndarray, config: Config) -> np.ndarray:
    """Move every correlation a fraction ``mix`` towards +1, keeping means and variances (linear transform)."""
    mean = base.mean(axis=0)
    sigma = np.cov(base, rowvar=False, ddof=config.ddof)
    sd = np.sqrt(np.diag(sigma))
    mix = config.covariance_stress_mix
    target = (1 - mix) * sigma + mix * np.outer(sd, sd)
    stressed = (base - mean) @ _matrix_root(sigma, inverse=True) @ _matrix_root(target) + mean
    assert np.allclose(stressed.mean(axis=0), mean, atol=1e-12)
    assert np.allclose(np.cov(stressed, rowvar=False, ddof=config.ddof), target, atol=1e-12)
    return stressed


def scenario_sets(estimation: pd.DataFrame, config: Config) -> dict[str, np.ndarray]:
    assert_estimation_only(estimation, config)
    base = estimation.to_numpy(copy=True)
    return {
        "base": base,
        "return_stress": return_stress(base, config),
        "covariance_stress": covariance_stress(base, config),
    }


def moments(outcomes: np.ndarray, ddof: int) -> tuple[np.ndarray, np.ndarray]:
    return outcomes.mean(axis=0), np.cov(outcomes, rowvar=False, ddof=ddof)
