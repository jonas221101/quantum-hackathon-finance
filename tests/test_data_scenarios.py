from dataclasses import replace

import numpy as np
import pytest

from qhf.data import ChecksumError, assert_estimation_only, load_returns
from qhf.decision import decide
from qhf.scenarios import moments, scenario_sets


def test_frozen_dataset_shape_and_windows(returns, estimation, evaluation, config):
    assert returns.shape == (120, 6)
    assert list(returns.columns) == list(config.industries)
    assert (len(estimation), len(evaluation)) == (60, 60)
    assert estimation.index[-1] == "2019-12" and evaluation.index[0] == "2020-01"
    assert not returns.isna().any().any()


def test_checksum_mismatch_raises(config):
    with pytest.raises(ChecksumError):
        load_returns(replace(config, data_sha256="0" * 64))


def test_estimators_reject_holdout_data(returns, config):
    with pytest.raises(ValueError):
        assert_estimation_only(returns, config)


def test_perturbing_holdout_does_not_change_decisions(returns, config):
    """2020–2024 must never influence a decision."""
    from qhf.data import estimation_slice

    perturbed = returns.copy()
    perturbed.loc["2020-01":] = perturbed.loc["2020-01":] * 3 - 0.05
    for frame in (returns, perturbed):
        frame.attrs["verdicts"] = {
            p.name: decide(scenario_sets(estimation_slice(frame, config), config), p, replace(config, bootstrap_samples=30)).verdict
            for p in config.profiles
        }
    assert returns.attrs["verdicts"] == perturbed.attrs["verdicts"]


def test_return_stress_shifts_only_hitec_mean(scenarios, config):
    base_mu, base_cov = moments(scenarios["base"], config.ddof)
    mu, cov = moments(scenarios["return_stress"], config.ddof)
    shift = np.zeros(6)
    shift[config.index("HiTec")] = -0.005
    np.testing.assert_allclose(mu - base_mu, shift, atol=1e-15)
    np.testing.assert_allclose(cov, base_cov, atol=1e-15)


def test_covariance_stress_hits_target(scenarios, config):
    base_mu, base_cov = moments(scenarios["base"], config.ddof)
    mu, cov = moments(scenarios["covariance_stress"], config.ddof)
    sd = np.sqrt(np.diag(base_cov))
    target = 0.75 * base_cov + 0.25 * np.outer(sd, sd)
    np.testing.assert_allclose(mu, base_mu, atol=1e-12)
    np.testing.assert_allclose(cov, target, atol=1e-12)
    np.testing.assert_allclose(np.diag(cov), np.diag(base_cov), atol=1e-12)
