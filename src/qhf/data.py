"""Load the frozen organiser dataset and split it into estimation and evaluation windows."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from qhf.config import Config


class ChecksumError(ValueError):
    pass


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_returns(config: Config, path: Path | None = None, verify: bool = True) -> pd.DataFrame:
    """Monthly decimal returns, index 'YYYY-MM', columns = ``config.industries``."""
    path = path or config.data_file()
    if verify and sha256_of(path) != config.data_sha256:
        raise ChecksumError(f"{path} does not match the frozen checksum {config.data_sha256[:12]}…")
    returns = pd.read_csv(path, index_col=0)
    returns.index = returns.index.astype(str)
    missing = set(config.industries) - set(returns.columns)
    if missing:
        raise ValueError(f"missing industries: {sorted(missing)}")
    returns = returns.loc[:, list(config.industries)].astype(float)
    if returns.isna().any().any():
        raise ValueError("dataset contains missing values")
    return returns


def _window(returns: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    window = returns.loc[start:end]
    if window.empty or window.index[0] != start or window.index[-1] != end:
        raise ValueError(f"window {start}..{end} not fully covered by the data")
    return window


def estimation_slice(returns: pd.DataFrame, config: Config) -> pd.DataFrame:
    """The only data that may enter estimates and decisions (decision date 31 Dec 2019)."""
    return _window(returns, config.estimation_start, config.estimation_end)


def evaluation_slice(returns: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Held-out months, used only for after-the-fact evaluation."""
    return _window(returns, config.evaluation_start, config.evaluation_end)


def assert_estimation_only(frame: pd.DataFrame, config: Config) -> None:
    if frame.index[0] < config.estimation_start or frame.index[-1] > config.estimation_end:
        raise ValueError("data outside the estimation window reached an estimator")
