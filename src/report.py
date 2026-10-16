from __future__ import annotations

from pathlib import Path
from typing import Any


def write_markdown_report(result: dict[str, Any], path: Path | str) -> None:
    """Write a compact, reproducible committee/demo report."""
    lines = [
        "# Quantum Finance Allocation Report",
        "",
        "## Method",
        "",
        "The analysis evaluates all 20 equal-weight portfolios formed by selecting "
        "three of six industries. Exact enumeration is the auditable verifier. "
        "QAOA is run on IBM Aer with both an X mixer and a Dicke-initialized XY mixer.",
        "",
        "## Data",
        "",
        f"- Source: `{result['data']['source']}`",
        f"- Estimation months: {result['data']['estimation_months']}",
        f"- Evaluation months: {result['data']['evaluation_months']}",
        "",
        "## Classical recommendations",
        "",
        "| Mandate | Portfolio |",
        "|---|---|",
    ]
    lines.extend(
        f"| {mandate} | `{portfolio}` |"
        for mandate, portfolio in result["classical_winners"].items()
    )
    lines.extend(["", "## Scenario recommendations", "", "| Scenario | Mandate results |", "|---|---|"])
    lines.extend(
        f"| {scenario} | "
        + "; ".join(f"{mandate}: `{portfolio}`" for mandate, portfolio in winners.items())
        + " |"
        for scenario, winners in result["scenario_winners"].items()
    )
    if result.get("quantum"):
        lines.extend(["", "## IBM Aer QAOA", "", "| Mandate | X feasible | XY feasible |", "|---|---:|---:|"])
        for mandate, values in result["quantum"]["mandates"].items():
            lines.append(
                f"| {mandate} | {values['x_mixer']['sampled_probability_feasible']:.3f} | "
                f"{values['xy_mixer']['sampled_probability_feasible']:.3f} |"
            )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Aer is a local simulator, not quantum hardware.",
            "- Historical returns and stress transformations are not forecasts.",
            "- QAOA probabilities are stochastic; exact enumeration remains the answer key.",
        ]
    )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
