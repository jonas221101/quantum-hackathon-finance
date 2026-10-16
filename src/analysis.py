from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import AllocationConfig, MANDATES
from .data import DEFAULT_DATA_PATH, load_challenge_data
from .enumerate import best_portfolios_by_mandate, build_reference_table
from .scenarios import build_all_scenario_tables
from .robustness import holdout_table, sensitivity_table


def run_analysis(
    csv_path: Path | str = DEFAULT_DATA_PATH,
    *,
    include_quantum: bool = True,
    qaoa_reps: int = 1,
    qaoa_starts: int = 2,
    shots: int = 1024,
) -> dict[str, Any]:
    """Run the reproducible classical and optional IBM Aer analysis."""
    data = load_challenge_data(csv_path)
    scenarios = build_all_scenario_tables(data.estimation)
    reference = build_reference_table(
        data.estimation, scenarios["base"].returns, AllocationConfig()
    )
    winners = best_portfolios_by_mandate(reference)
    scenario_winners = {}
    for name, scenario in scenarios.items():
        table = build_reference_table(
            scenario.returns.drop(columns=["probability"]),
            scenario.returns,
            AllocationConfig(),
        )
        scenario_winners[name] = best_portfolios_by_mandate(table)
    result: dict[str, Any] = {
        "data": {
            "source": str(Path(csv_path)),
            "estimation_months": len(data.estimation),
            "evaluation_months": len(data.evaluation),
        },
        "classical_winners": winners,
        "reference_table": reference,
        "scenario_names": list(scenarios),
        "scenario_winners": scenario_winners,
        "holdout": holdout_table(data.evaluation, winners),
        "sensitivity": {
            mandate: sensitivity_table(
                data.estimation, scenarios["base"].returns, mandate_name=mandate
            )
            for mandate in MANDATES
        },
        "quantum": {},
    }
    if include_quantum:
        from .qaoa import run_ibm_aer_comparison

        result["quantum"] = run_ibm_aer_comparison(
            data.estimation,
            reps=qaoa_reps,
            starts=qaoa_starts,
            shots=shots,
        )
    return result


def export_analysis(result: dict[str, Any], output_dir: Path | str) -> None:
    """Write analysis tables and metadata in portable CSV/JSON formats."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    table = result["reference_table"]
    table.drop(columns=["selection"], errors="ignore").to_csv(
        target / "portfolio_reference.csv", index=False
    )
    metadata = {
        key: _json_value(value)
        for key, value in result.items()
        if key != "reference_table"
    }
    (target / "analysis_summary.json").write_text(
        json.dumps(metadata, indent=2, default=_json_default), encoding="utf-8"
    )


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, pd.Period)):
        return str(value)
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def _json_value(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value
