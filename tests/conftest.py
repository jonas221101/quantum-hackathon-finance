from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from qhf.config import DEFAULT_CONFIG, Config
from qhf.data import estimation_slice, evaluation_slice, load_returns
from qhf.scenarios import moments, scenario_sets


@pytest.fixture(scope="session")
def config() -> Config:
    return DEFAULT_CONFIG


@pytest.fixture(scope="session")
def returns(config: Config) -> pd.DataFrame:
    return load_returns(config)


@pytest.fixture(scope="session")
def estimation(returns: pd.DataFrame, config: Config) -> pd.DataFrame:
    return estimation_slice(returns, config)


@pytest.fixture(scope="session")
def evaluation(returns: pd.DataFrame, config: Config) -> pd.DataFrame:
    return evaluation_slice(returns, config)


@pytest.fixture(scope="session")
def scenarios(estimation: pd.DataFrame, config: Config) -> dict[str, np.ndarray]:
    return scenario_sets(estimation, config)


@pytest.fixture(scope="session")
def base_moments(scenarios: dict[str, np.ndarray], config: Config) -> tuple[np.ndarray, np.ndarray]:
    return moments(scenarios["base"], config.ddof)
