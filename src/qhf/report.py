"""Compact Markdown committee report from a run's summary.json (ported from the dashboard branch)."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.0%}"


def markdown_report(summary: dict[str, Any]) -> str:
    cfg = summary["config"]
    lines = [
        "# Allocation route: committee report",
        "",
        "## Method",
        "",
        "All 20 equal-weight portfolios (3 of 6 industries) are scored exactly; this enumeration is the "
        "auditable answer key. QAOA is compared quantum vs quantum: the rule-preserving design "
        "(Dicke start + XY mixer) against the organiser's penalty QAOA. Ideal local simulation; "
        "no quantum-advantage claim.",
        "",
        "## Data",
        "",
        f"- Source: `{cfg['data_path']}` (checksum verified)",
        f"- Estimation: {cfg['estimation_start']} to {cfg['estimation_end']}; "
        f"evaluation (never used for decisions): {cfg['evaluation_start']} to {cfg['evaluation_end']}",
        "",
        "## Verdicts",
        "",
        "| Profile | Verdict | Holdings | Candidate beats current (resamples) | Reason |",
        "|---|---|---|---:|---|",
    ]
    for name, v in summary["verdicts"].items():
        default = " (default)" if v["is_default_profile"] else ""
        lines.append(f"| {name}{default} | **{v['verdict']}** | `{v['target']}` | "
                     f"{_pct(v['bootstrap_candidate_beats_current'])} | {v['reason']} |")
    lines += ["", "## Optimum per scenario set", "", "| Profile | Base | Return stress | Covariance stress |", "|---|---|---|---|"]
    for name, v in summary["verdicts"].items():
        o = v["optima"]
        lines.append(f"| {name} | `{o['base']}` | `{o['return_stress']}` | `{o['covariance_stress']}` |")
    rows = summary["quantum"]["summary"]
    deepest = max(r["layers"] for r in rows)
    lines += ["", f"## Quantum vs quantum (p = {deepest}, median over seeds)", "",
              "| Profile | Method | P(best) | min–max | Valid share | Decoded = exact |", "|---|---|---:|---|---:|---:|"]
    for r in rows:
        if r["layers"] == deepest:
            lines.append(f"| {r['profile']} | {r['method']} | {r['p_opt_median']:.2f} | "
                         f"{r['p_opt_min']:.2f}–{r['p_opt_max']:.2f} | {_pct(r['h1_mass_median'])} | "
                         f"{_pct(r['decoded_is_optimum_share'])} |")
    lines += ["", "## Limitations", ""] + [f"- {note}" for note in summary["quantum"]["notes"]] + [
        "- Historical returns and stress transformations are not forecasts.",
        "- US industry data stands in for a global, multi-asset public fund.",
    ]
    return "\n".join(lines) + "\n"


def write_markdown_report(summary: dict[str, Any], path: Path | str) -> None:
    Path(path).write_text(markdown_report(summary), encoding="utf-8")
