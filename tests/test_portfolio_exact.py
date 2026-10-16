from dataclasses import replace

import numpy as np
import pytest

from qhf.exact import enumerate_portfolios, optimum, rank_portfolios
from qhf.portfolio import (
    allowed_breaches,
    breach_count,
    cap_excess,
    objective,
    passes_loss_rule,
    selection,
    turnover,
    weights,
)
from qhf.scenarios import moments

CURRENT = "NoDur+Hlth+Utils"
PROPOSAL = "HiTec+Hlth+Utils"


def test_objective_of_current_by_hand(base_moments, config):
    mu, sigma = base_moments
    balanced = config.profile("balanced")
    w = np.array([1, 0, 0, 0, 1, 1]) / 3
    expected = -mu @ w + 5.0 * w @ sigma @ w  # no turnover, cap inactive
    assert objective(selection(config.current, config), mu, sigma, balanced, config) == pytest.approx(expected, abs=1e-15)


def test_turnover_is_linear_in_x(config):
    x0 = selection(config.current, config)
    for x in enumerate_portfolios(config):
        linear = ((1 - 2 * x0) * x + x0).sum() / (2 * config.cardinality)
        assert turnover(x, config) == pytest.approx(linear)
    assert turnover(selection(config.proposal, config), config) == pytest.approx(1 / 3)


def test_cap_term_zero_when_cap_at_least_one_third(base_moments, config):
    mu, sigma = base_moments
    proposal = selection(config.proposal, config)
    assert cap_excess(proposal, config.profile("balanced"), config) == 0.0  # cap 35% > 1/3
    assert cap_excess(proposal, config.profile("risk_sensitive"), config) == pytest.approx(1 / 3 - 0.2)
    rs = config.profile("risk_sensitive")
    with_cap = objective(proposal, mu, sigma, rs, config)
    without = objective(proposal, mu, sigma, rs, replace(config, cap_penalty=0.0))
    assert with_cap - without == pytest.approx(0.01 * (1 / 3 - 0.2))


@pytest.mark.parametrize("scenario, breaches", [("base", 6), ("return_stress", 7), ("covariance_stress", 9)])
def test_proposal_breaches_at_three_percent(scenarios, config, scenario, breaches):
    """Organiser README: 10%, 11.67% and 15% of 60 months."""
    assert breach_count(selection(config.proposal, config), scenarios[scenario], 0.03, config) == breaches


def test_loss_rule_boundary_is_integer_exact(scenarios, config):
    rs = config.profile("risk_sensitive")
    assert allowed_breaches(60, 0.10) == 6
    proposal = selection(config.proposal, config)
    assert passes_loss_rule(proposal, scenarios["base"], rs, config)  # 6/60 ≤ 10%
    assert not passes_loss_rule(proposal, scenarios["base"], rs, config, strict=True)  # 6/60 < 10% fails
    assert not passes_loss_rule(proposal, scenarios["return_stress"], rs, config)  # 7/60
    looser = replace(rs, loss_tolerance=0.125)  # α·n = 7.5: 7 breaches pass both readings
    assert passes_loss_rule(proposal, scenarios["return_stress"], looser, config)
    assert passes_loss_rule(proposal, scenarios["return_stress"], looser, config, strict=True)


def test_twenty_portfolios_and_exclusions(config):
    assert len(enumerate_portfolios(config)) == 20
    no_energy = enumerate_portfolios(replace(config, excluded=("Enrgy",)))
    assert len(no_energy) == 10 and all(x[config.index("Enrgy")] == 0 for x in no_energy)


@pytest.mark.parametrize(
    "profile, scenario, expected",
    [("growth", "base", PROPOSAL), ("balanced", "base", PROPOSAL), ("risk_sensitive", "base", CURRENT),
     ("balanced", "return_stress", CURRENT), ("balanced", "covariance_stress", PROPOSAL),
     ("risk_sensitive", "covariance_stress", CURRENT)],
)
def test_exact_optima(scenarios, config, profile, scenario, expected):
    outcomes = scenarios[scenario]
    mu, sigma = moments(outcomes, config.ddof)
    table = rank_portfolios(mu, sigma, outcomes, config.profile(profile), config)
    assert optimum(table)["holdings"] == expected
    assert table.tied_with_optimum.sum() == 1


def test_weights_sum_to_one(config):
    for x in enumerate_portfolios(config):
        assert weights(x, config).sum() == pytest.approx(1.0)
