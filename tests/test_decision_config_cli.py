import json
from dataclasses import replace

import pytest

from qhf.config import DEFAULT_CONFIG, apply_overrides, config_hash
from qhf.decision import break_even, decide
from qhf.evaluation import replay_rule
from qhf.portfolio import selection
from qhf.sensitivity import robustness_table


@pytest.fixture(scope="module")
def verdicts(scenarios, config):
    return {p.name: decide(scenarios, p, config) for p in config.profiles}


def test_verdicts(verdicts):
    growth, balanced, risk = verdicts["growth"], verdicts["balanced"], verdicts["risk_sensitive"]
    assert growth.verdict == "switch" and growth.target == "HiTec+Hlth+Utils"
    assert growth.evidence.target_beats_current >= 0.70 and growth.evidence.target_admissible >= 0.70
    assert balanced.verdict == "review" and balanced.target == "NoDur+Hlth+Utils"  # flips under the return stress
    assert balanced.optima["return_stress"] == "NoDur+Hlth+Utils"
    assert risk.verdict == "keep" and risk.evidence.current_admissible >= 0.70
    assert balanced.is_default_profile


def test_switch_gate_uses_pairwise_evidence(scenarios, config):
    strict = replace(config, bootstrap_threshold=0.95)
    verdict = decide(scenarios, strict.profile("growth"), strict)
    assert verdict.verdict == "review" and "resamples" in verdict.reason


def test_no_admissible_portfolio_gives_review_not_crash(scenarios, config):
    from qhf.config import apply_overrides

    harsh = apply_overrides(config, ["risk_sensitive.loss_threshold=0.0", "risk_sensitive.loss_tolerance=0.01"])
    verdict = decide(scenarios, harsh.profile("risk_sensitive"), harsh)
    assert verdict.verdict == "review" and "no portfolio" in verdict.reason


def test_verdicts_unchanged_without_cap_preference(scenarios, config):
    no_cap = replace(config, cap_penalty=0.0)
    for profile in no_cap.profiles:
        assert decide(scenarios, profile, no_cap).optima == decide(scenarios, config.profile(profile.name), config).optima


def test_break_evens_balanced(scenarios, config):
    balanced = config.profile("balanced")
    shift = break_even(scenarios["base"], balanced, config, "hitec_shift", -0.02, 0.01)
    assert len(shift) == 1 and shift[0]["value"] == pytest.approx(-0.00366, abs=2e-5)
    tau = break_even(scenarios["base"], balanced, config, "change_penalty", 0.0, 0.05)
    assert tau[0]["value"] == pytest.approx(0.00566, abs=2e-5)
    lam = break_even(scenarios["base"], balanced, config, "risk_aversion", 0.1, 100, log_scale=True)
    assert [c["to"] for c in lam] == ["NoDur+HiTec+Utils", "NoDur+Hlth+Utils"]
    assert lam[0]["value"] == pytest.approx(7.51, abs=0.02) and lam[1]["value"] == pytest.approx(14.92, abs=0.02)


def test_pairwise_break_even_lambda_current_vs_proposal(base_moments, config):
    from qhf.portfolio import objective

    mu, sigma = base_moments
    bal = config.profile("balanced")
    cur, prop = selection(config.current, config), selection(config.proposal, config)
    gap = lambda lam: objective(prop, mu, sigma, replace(bal, risk_aversion=lam), config) - objective(cur, mu, sigma, replace(bal, risk_aversion=lam), config)  # noqa: E731
    root = -gap(0.0) / (gap(1.0) - gap(0.0))
    assert root == pytest.approx(11.23, abs=0.05)


def test_robustness_rows_are_categorised(scenarios, config):
    table = robustness_table(scenarios, config)
    assert set(table.category) == {"financial", "cost assumption", "mandate"}
    assert table.groupby("profile").size().min() >= 2 + 6  # ≥ 2 supplied changes plus mandate changes


def test_overrides_validated_and_deterministic():
    cfg = apply_overrides(DEFAULT_CONFIG, ["balanced.loss_threshold=0.04", "qaoa.seeds=3", "excluded=Enrgy", "change_penalty=0.004"])
    assert cfg.profile("balanced").loss_threshold == 0.04
    assert cfg.qaoa.seeds == 3 and cfg.excluded == ("Enrgy",) and cfg.change_penalty == 0.004
    assert config_hash(cfg) == config_hash(apply_overrides(DEFAULT_CONFIG, ["balanced.loss_threshold=0.04", "qaoa.seeds=3", "excluded=Enrgy", "change_penalty=0.004"]))
    assert config_hash(cfg) != config_hash(DEFAULT_CONFIG)
    for bad in ["nonsense=1", "balanced.nonsense=1", "unknown_profile.risk_aversion=1", "qaoa.nonsense=1", "novalue",
                "cvar_variant=maybe"]:
        with pytest.raises((KeyError, ValueError)):
            apply_overrides(DEFAULT_CONFIG, [bad])


def test_replay_rule_hold_matches_buy_and_hold(evaluation, config):
    from qhf.evaluation import buy_and_hold_wealth
    from qhf.portfolio import weights

    w = weights(selection(config.current, config), config)
    held = replay_rule(evaluation, w, None)
    assert held["trades"] == 0
    assert held["terminal_wealth"] == pytest.approx(float(buy_and_hold_wealth(evaluation, w).iloc[-1]), rel=1e-12)


@pytest.mark.slow
def test_cli_fast_run_is_reproducible_and_diffable(tmp_path):
    from qhf.cli import diff, main

    assert main(["run", "--fast", "--out", str(tmp_path / "a")]) == 0
    assert main(["run", "--fast", "--out", str(tmp_path / "b")]) == 0
    run_a = next((tmp_path / "a").iterdir())
    run_b = next((tmp_path / "b").iterdir())
    assert (run_a / "summary.json").read_text() == (run_b / "summary.json").read_text()
    summary = json.loads((run_a / "summary.json").read_text())
    assert {"config", "config_hash", "fast", "exact", "verdicts", "break_even", "bootstrap", "quantum", "holdout", "whole_portfolio"} <= set(summary)
    for name in ["fig_risk_return", "fig_decision_map", "fig_decision_map_cost", "fig_bootstrap", "fig_qaoa_comparison",
                 "fig_circuits", "fig_holdout"]:
        assert (run_a / "figures" / f"{name}.png").exists()
    assert main(["run", "--fast", "--set", "balanced.loss_threshold=0.04", "--out", str(tmp_path / "c")]) == 0
    run_c = next((tmp_path / "c").iterdir())
    lines = diff(run_a, run_c)
    assert lines[0].startswith("config fields changed: ['profiles']")


def test_fast_flag_keeps_explicit_overrides():
    from qhf.cli import build_config

    cfg = build_config(["qaoa.seeds=5", "bootstrap_samples=40"], fast=True, no_cvar=False)
    assert cfg.qaoa.seeds == 5 and cfg.bootstrap_samples == 40 and not cfg.cvar_variant
