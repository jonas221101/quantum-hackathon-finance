"""Checks ported from the dashboard branch (tests/test_backbone.py) onto the qhf engine, plus dashboard/report smoke tests."""
import json

import pytest

from qhf.config import REPO_ROOT
from qhf.exact import rank_portfolios
from qhf.portfolio import breach_count, selection
from qhf.report import markdown_report
from qhf.scenarios import moments

CANONICAL_SUMMARY = REPO_ROOT / "results" / "canonical" / "summary.json"


def _row(table, holdings):
    return table[table.holdings == holdings].iloc[0]


def test_current_and_proposal_reference_metrics(scenarios, config):
    mu, sigma = moments(scenarios["base"], config.ddof)
    table = rank_portfolios(mu, sigma, scenarios["base"], config.profile("balanced"), config)
    current, proposal = _row(table, "NoDur+Hlth+Utils"), _row(table, "HiTec+Hlth+Utils")
    assert current["mean"] == pytest.approx(0.0073, abs=5e-4) and current.volatility == pytest.approx(0.0271, abs=5e-4)
    assert proposal["mean"] == pytest.approx(0.0102, abs=5e-4) and proposal.volatility == pytest.approx(0.0305, abs=5e-4)


def test_balanced_loss_probabilities_at_five_percent(scenarios, config):
    base = scenarios["base"]
    assert breach_count(selection(config.current, config), base, 0.05, config) / len(base) == pytest.approx(1 / 30)
    assert breach_count(selection(config.proposal, config), base, 0.05, config) / len(base) == pytest.approx(0.05)


@pytest.mark.skipif(not CANONICAL_SUMMARY.exists(), reason="canonical run not present")
def test_markdown_report_from_canonical_summary():
    summary = json.loads(CANONICAL_SUMMARY.read_text(encoding="utf-8"))
    text = markdown_report(summary)
    for needle in ("## Verdicts", "growth", "balanced (default)", "risk_sensitive", "Quantum vs quantum", "## Limitations"):
        assert needle in text


@pytest.mark.slow
@pytest.mark.skipif(not CANONICAL_SUMMARY.exists(), reason="canonical run not present")
def test_dashboard_renders_without_errors():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(REPO_ROOT / "app.py"), default_timeout=120).run()
    assert not app.exception
    assert any("Verdict" in metric.label for metric in app.metric)
