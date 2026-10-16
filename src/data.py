from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import pandas as pd

INDUSTRIES: tuple[str, ...] = ("NoDur", "Manuf", "Enrgy", "HiTec", "Hlth", "Utils")
CURRENT_PORTFOLIO: tuple[str, ...] = ("NoDur", "Hlth", "Utils")
PROPOSAL_PORTFOLIO: tuple[str, ...] = ("HiTec", "Hlth", "Utils")

ESTIMATION_START = pd.Period("2015-01", freq="M")
ESTIMATION_END = pd.Period("2019-12", freq="M")
EVALUATION_START = pd.Period("2020-01", freq="M")
EVALUATION_END = pd.Period("2024-12", freq="M")

DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "Database"
    / "returns_6_industries_monthly.csv"
)


@dataclass(frozen=True)
class ChallengeData:
    returns: pd.DataFrame
    estimation: pd.DataFrame
    evaluation: pd.DataFrame


def sha256_hex(path: Path | str) -> str:
    """Return the SHA-256 digest of a file as a hex string."""
    target = Path(path)
    digest = sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_returns(csv_path: Path | str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the frozen six-industry monthly return panel."""
    csv_path = Path(csv_path)
    frame = pd.read_csv(csv_path)
    if "month" not in frame.columns:
        raise ValueError("CSV missing required month column")

    missing = [industry for industry in INDUSTRIES if industry not in frame.columns]
    if missing:
        raise ValueError(f"CSV missing required industry columns: {missing}")

    frame["month"] = pd.PeriodIndex(frame["month"].astype(str), freq="M")
    frame = frame.set_index("month")
    frame = frame.loc[:, list(INDUSTRIES)].astype(float)
    frame.index.name = "month"
    frame.attrs["source_path"] = str(csv_path)
    return frame


def split_challenge_data(returns: pd.DataFrame) -> ChallengeData:
    """Split the panel into estimation and evaluation windows."""
    estimation = returns.loc[ESTIMATION_START:ESTIMATION_END]
    evaluation = returns.loc[EVALUATION_START:EVALUATION_END]

    if len(estimation) != 60:
        raise ValueError(f"Expected 60 estimation months, found {len(estimation)}")
    if len(evaluation) != 60:
        raise ValueError(f"Expected 60 evaluation months, found {len(evaluation)}")

    return ChallengeData(returns=returns, estimation=estimation, evaluation=evaluation)


def load_challenge_data(csv_path: Path | str = DEFAULT_DATA_PATH) -> ChallengeData:
    """Load and split the frozen challenge data."""
    returns = load_returns(csv_path)
    return split_challenge_data(returns)
