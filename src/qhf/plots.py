"""Figures for docs and slides (headless backend)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from qhf.config import Config  # noqa: E402
from qhf.evaluation import buy_and_hold_wealth  # noqa: E402
from qhf.portfolio import label, turnover, weights  # noqa: E402

METHOD_NAMES = {
    "x_penalty": "Penalty QAOA (organiser)",
    "x_penalty_tuned": "Penalty QAOA, tuned penalty",
    "dicke_xy": "Rule-preserving QAOA (ours)",
    "x_penalty_cvar": "Penalty QAOA + CVaR objective",
    "x_penalty_tuned_cvar": "Tuned penalty + CVaR objective",
    "dicke_xy_cvar": "Rule-preserving + CVaR objective",
}
COLORS = {"x_penalty": "#9aa5b1", "x_penalty_tuned": "#5b6b7c", "dicke_xy": "#1f77b4",
          "x_penalty_cvar": "#c9ced4", "x_penalty_tuned_cvar": "#8a96a3", "dicke_xy_cvar": "#7fb3e0"}


def _save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def risk_return(table: pd.DataFrame, config: Config, path: Path) -> None:
    """All 20 portfolios: monthly volatility vs mean, current and proposal highlighted."""
    current, proposal = "+".join(config.current), "+".join(config.proposal)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(table.volatility * 100, table["mean"] * 100, color="#c0c7cf", s=40, label="other 3-of-6 tilts")
    for name, color, text in [(current, "#2ca02c", "current"), (proposal, "#d62728", "proposal")]:
        row = table[table.holdings == name].iloc[0]
        ax.scatter(row.volatility * 100, row["mean"] * 100, color=color, s=110, zorder=3, label=f"{text}: {name}")
    ax.set_xlabel("risk: monthly volatility (%)")
    ax.set_ylabel("expected monthly return (%)")
    ax.set_title(f"The {len(table)} possible tilts (estimated on {config.estimation_start} to {config.estimation_end})")
    ax.legend(frameon=False, fontsize=8)
    _save(fig, path)


def decision_map(grid: pd.DataFrame, config: Config, path: Path, axis: str = "hitec_shift") -> None:
    labels = sorted(grid.optimum.unique())
    lookup = {name: i for i, name in enumerate(labels)}
    lams = np.sort(grid.risk_aversion.unique())
    ys = np.sort(grid[axis].unique())
    values = grid.pivot(index=axis, columns="risk_aversion", values="optimum").loc[ys, lams].map(lookup.get)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    cmap = plt.get_cmap("tab10", len(labels))
    scale = 100 if axis == "hitec_shift" else 1e4
    mesh = ax.pcolormesh(lams, ys * scale, values.to_numpy(), cmap=cmap, vmin=-0.5, vmax=len(labels) - 0.5, shading="nearest")
    ax.set_xscale("log")
    for profile in config.profiles:
        ax.axvline(profile.risk_aversion, color="k", lw=0.8, ls="--")
        ax.text(profile.risk_aversion, ys.max() * scale, f" {profile.name}", rotation=90, va="top", fontsize=8)
    marker = config.return_stress_shift * 100 if axis == "hitec_shift" else config.change_penalty * 1e4
    ax.axhline(marker, color="k", lw=0.8, ls=":")
    ax.set_xlabel("risk aversion λ (log scale)")
    ax.set_ylabel("change in HiTec expected return (pp / month)" if axis == "hitec_shift" else "switching cost τ (bp per unit turnover)")
    note = "dotted = supplied stress" if axis == "hitec_shift" else "dotted = assumed τ"
    ax.set_title(f"Which tilt is best? ({config.default_profile} rules; {note})")
    bar = fig.colorbar(mesh, ax=ax, ticks=range(len(labels)))
    bar.ax.set_yticklabels(labels, fontsize=7)
    _save(fig, path)


def bootstrap(evidence: dict, config: Config, path: Path) -> None:
    """Resampling evidence per profile: does the candidate beat the current tilt, and does each pass the loss rule?"""
    metrics = [("target_beats_current", "best candidate beats current"),
               ("target_admissible", "candidate passes loss rule"),
               ("current_admissible", "current passes loss rule")]
    fig, ax = plt.subplots(figsize=(8, 4))
    names = list(evidence)
    width = 0.8 / len(metrics)
    for k, (attr, text) in enumerate(metrics):
        values = [getattr(evidence[n], attr) for n in names]
        ax.bar(np.arange(len(names)) + (k - 1) * width, values, width, label=text,
               color=["#1f77b4", "#d62728", "#2ca02c"][k])
    ax.axhline(config.bootstrap_threshold, color="k", ls="--", lw=0.8)
    ax.set_xticks(range(len(names)), names)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(f"share of {config.bootstrap_samples} resamples")
    ax.set_title(f"How robust is the evidence? (resampled estimation months; dashed = {config.bootstrap_threshold:.0%} threshold)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    _save(fig, path)


def qaoa_comparison(summary: pd.DataFrame, path: Path) -> None:
    profiles = list(dict.fromkeys(summary.profile))
    methods = [m for m in METHOD_NAMES if m in set(summary.method)]
    fig, axes = plt.subplots(2, len(profiles), figsize=(12, 6.5), sharey="row")
    for col, profile in enumerate(profiles):
        sub = summary[summary.profile == profile]
        layers = sorted(sub.layers.unique())
        width = 0.8 / len(methods)
        for k, method in enumerate(methods):
            part = sub[sub.method == method].set_index("layers").reindex(layers)
            xs = np.arange(len(layers)) + (k - (len(methods) - 1) / 2) * width
            err = [part.p_opt_median - part.p_opt_min, part.p_opt_max - part.p_opt_median]
            axes[0, col].bar(xs, part.p_opt_median, width, yerr=err, color=COLORS[method], capsize=2,
                             label=METHOD_NAMES[method] if col == 0 else None)
            axes[1, col].bar(xs, part.h1_mass_median, width, color=COLORS[method])
        for row in (0, 1):
            axes[row, col].set_xticks(range(len(layers)), [f"p={p}" for p in layers])
        axes[0, col].set_title(profile)
    axes[0, 0].set_ylabel("P(best portfolio)")
    axes[1, 0].set_ylabel("share of valid portfolios\n(exactly 3 holdings)")
    fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.suptitle("Quantum vs quantum: median over seeds (bars = min–max); ideal simulation")
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def circuits(diagram_text: dict[str, str], path: Path) -> None:
    fig, axes = plt.subplots(len(diagram_text), 1, figsize=(12, 3.2 * len(diagram_text)))
    for ax, (title, text) in zip(np.atleast_1d(axes), diagram_text.items()):
        ax.text(0, 1, text, family="monospace", fontsize=5.5, va="top")
        ax.set_title(title, loc="left")
        ax.axis("off")
    _save(fig, path)


def holdout(evaluation: pd.DataFrame, portfolios: dict[str, np.ndarray], config: Config, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for role, x in portfolios.items():
        wealth = buy_and_hold_wealth(evaluation, weights(x, config), config.change_penalty * turnover(x, config))
        ax.plot(pd.to_datetime(wealth.index), wealth.to_numpy(), label=f"{role}: {label(x, config)}")
    ax.set_ylabel("wealth per 1 invested (gross)")
    ax.set_title(f"Hindsight {config.evaluation_start} to {config.evaluation_end}, after switching cost (not used for the decision)")
    ax.legend(frameon=False, fontsize=8)
    _save(fig, path)
