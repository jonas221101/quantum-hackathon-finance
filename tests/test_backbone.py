from __future__ import annotations

import math
import unittest

from src.config import MANDATES
from src.data import (
    CURRENT_PORTFOLIO,
    PROPOSAL_PORTFOLIO,
    DEFAULT_DATA_PATH,
    load_challenge_data,
    sha256_hex,
)
from src.enumerate import (
    all_portfolios,
    best_portfolios_by_mandate,
    build_reference_table,
)
from src.evaluate import evaluate_selection
from src.scenarios import build_all_scenario_tables
from src.analysis import export_analysis, run_analysis
from src.decision import decide_selection
from src.qaoa import _dicke_state


class BackboneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_challenge_data()
        cls.scenarios = build_all_scenario_tables(cls.data.estimation)
        cls.base_scenarios = cls.scenarios["base"].returns

    def test_csv_checksum_and_shape(self) -> None:
        digest = sha256_hex(DEFAULT_DATA_PATH)
        self.assertEqual(len(digest), 64)
        self.assertEqual(self.data.returns.shape, (120, 6))
        self.assertEqual(len(self.data.estimation), 60)
        self.assertEqual(len(self.data.evaluation), 60)

    def test_current_and_proposal_metrics_match_reference(self) -> None:
        current = evaluate_selection(
            self.data.estimation,
            CURRENT_PORTFOLIO,
            MANDATES["balanced"],
            self.base_scenarios,
        )
        proposal = evaluate_selection(
            self.data.estimation,
            PROPOSAL_PORTFOLIO,
            MANDATES["balanced"],
            self.base_scenarios,
        )

        self.assertTrue(math.isclose(current.mean, 0.0073, rel_tol=0, abs_tol=5e-4))
        self.assertTrue(
            math.isclose(current.volatility, 0.0271, rel_tol=0, abs_tol=5e-4)
        )
        self.assertTrue(math.isclose(proposal.mean, 0.0102, rel_tol=0, abs_tol=5e-4))
        self.assertTrue(
            math.isclose(proposal.volatility, 0.0305, rel_tol=0, abs_tol=5e-4)
        )
        self.assertTrue(
            math.isclose(
                current.loss_probability or 0.0,
                0.03333333333333333,
                rel_tol=0,
                abs_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                proposal.loss_probability or 0.0, 0.05, rel_tol=0, abs_tol=1e-12
            )
        )

    def test_portfolio_count(self) -> None:
        self.assertEqual(len(all_portfolios()), 20)

    def test_reference_winners_match_docs(self) -> None:
        table = build_reference_table(self.data.estimation, self.base_scenarios)
        winners = best_portfolios_by_mandate(table)
        self.assertEqual(winners["growth_oriented"], "HiTec+Hlth+Utils")
        self.assertEqual(winners["balanced"], "HiTec+Hlth+Utils")
        self.assertEqual(winners["risk_sensitive"], "NoDur+Hlth+Utils")

    def test_scenario_and_decision_surfaces(self) -> None:
        self.assertEqual(
            set(self.scenarios), {"base", "return_stress", "covariance_stress"}
        )
        decision = decide_selection(
            self.data.estimation,
            PROPOSAL_PORTFOLIO,
            MANDATES["balanced"],
            self.base_scenarios,
        )
        self.assertIn(decision.verdict, {"accept", "reject", "review"})
        self.assertIsNotNone(decision.metrics.loss_probability)

    def test_classical_pipeline_exports(self) -> None:
        import tempfile
        from pathlib import Path

        result = run_analysis(include_quantum=False)
        with tempfile.TemporaryDirectory() as directory:
            export_analysis(result, Path(directory))
            self.assertTrue((Path(directory) / "portfolio_reference.csv").exists())
            self.assertTrue((Path(directory) / "analysis_summary.json").exists())

    def test_dicke_initial_state_has_exact_cardinality(self) -> None:
        state = _dicke_state(6, 3)
        support = [index for index, amplitude in enumerate(state) if abs(amplitude)]
        self.assertEqual(len(support), 20)
        self.assertTrue(all(index.bit_count() == 3 for index in support))


if __name__ == "__main__":
    unittest.main()
