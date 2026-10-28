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
SHORT_METHOD_NAMES = {"x_penalty": "Penalty QAOA\n(organiser)", "x_penalty_tuned": "Penalty QAOA\n(tuned penalty)",
                      "dicke_xy": "Rule-preserving\nQAOA (ours)"}
ROLE_COLORS = {"current": "#2a78d6", "proposal": "#eb6834"}  # same entity colours on every slide figure
INK, MUTED, BAND = "#0b0b0b", "#52514e", "#e4e3df"
SE_BANDS = {1: "#d6d5cf", 2: "#ecebe7"}  # ±1 and ±2 standard errors
HIST_BIN_BP = 4.0  # bootstrap histogram bin width; edges are aligned to zero


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


def _label_bars(ax: plt.Axes, bars, values, tops, fmt: str) -> None:
    """Value above each bar, placed above its error bar so the two never overlap."""
    for bar, value, top in zip(bars, values, tops):
        ax.text(bar.get_x() + bar.get_width() / 2, top, fmt.format(value),
                ha="center", va="bottom", fontsize=8, color=INK)


def success_rate(summary: pd.DataFrame, floors: dict[str, dict[str, float]], config: Config, path: Path) -> None:
    """Slide version of quantum vs quantum: measured valid shots and P(best) at the deepest layer, three main methods."""
    methods = [m for m in SHORT_METHOD_NAMES if m in set(summary.method)]
    deepest = int(summary.layers.max())
    data = summary[(summary.layers == deepest) & summary.method.isin(methods)]
    profiles = [name for name in floors if name in set(data.profile)]
    fig, axes = plt.subplots(2, len(profiles), figsize=(12, 6.8), sharey="row")
    rows = [("sampled_h1_share", "sampled_h1_share_min", "sampled_h1_share_max",
             "valid portfolios among measured shots\n(exactly 3 of 6 holdings)", "{:.0%}"),
            ("p_opt", "p_opt_min", "p_opt_max", "P(exact best portfolio)", "{:.2f}")]
    for col, profile in enumerate(profiles):
        part = data[data.profile == profile].set_index("method").loc[methods]
        colors = [COLORS["dicke_xy"] if m == "dicke_xy" else COLORS["x_penalty"] for m in methods]
        for row, (median, low, high, ylabel, fmt) in enumerate(rows):
            ax = axes[row, col]
            values = part[f"{median}_median"].to_numpy()
            err = [values - part[low].to_numpy(), part[high].to_numpy() - values]
            bars = ax.bar(range(len(methods)), values, 0.6, color=colors, yerr=err, capsize=3,
                          error_kw={"ecolor": MUTED, "lw": 1})
            _label_bars(ax, bars, values, np.maximum(values, part[high].to_numpy()) + 0.01, fmt)
            ax.set_xticks(range(len(methods)), [SHORT_METHOD_NAMES[m] for m in methods], fontsize=8)
            ax.spines[["top", "right"]].set_visible(False)
            if col == 0:
                ax.set_ylabel(ylabel)
        floor = axes[1, col].axhline(floors[profile]["valid_states"], color=INK, ls=":", lw=1)
        axes[0, col].set_title(profile.replace("_", "-"))
    axes[1, 0].legend([floor], [f"random guess among valid portfolios ({floors[profiles[0]]['valid_states']:.2f})"],
                      frameon=False, fontsize=8, loc="upper left")
    axes[0, 0].set_ylim(0, 1.15)
    axes[1, 0].set_ylim(0, 1.0)
    fig.suptitle(f"Quantum vs quantum at p = {deepest}: median over {config.qaoa.seeds} seeds, whiskers = min–max "
                 f"(ideal simulation, {config.qaoa.shots} shots per run)")
    _save(fig, path)


def estimation_error(summary: dict, curve: pd.DataFrame, resampled: np.ndarray, config: Config, path: Path) -> None:
    """Break-even of the proposal against the estimation error of the HiTec mean, plus the bootstrap spread."""
    se = summary["hitec_mean_standard_error"] * 100
    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
    for k in (2, 1):
        left.axvspan(-k * se, k * se, color=SE_BANDS[k], lw=0,
                     label=f"±{k} standard error{'s' if k > 1 else ''} of the HiTec mean (±{k * se:.2f} pp)")
    left.axhline(0, color=MUTED, lw=0.8)
    left.plot(curve.hitec_shift * 100, curve.advantage * 1e4, color=INK, lw=2)
    left.axvline(config.return_stress_shift * 100, color=INK, ls=":", lw=1)
    left.text(config.return_stress_shift * 100, left.get_ylim()[0], " supplied stress", fontsize=8, va="bottom",
              ha="right", rotation=90, color=MUTED)
    if summary["break_even_hitec_shift"] is not None:
        x = summary["break_even_hitec_shift"] * 100
        left.plot([x], [0], "o", color=ROLE_COLORS["proposal"], ms=8, zorder=3)
        left.annotate(f"break-even {x:+.2f} pp\n= {summary['break_even_in_standard_errors']:+.2f} standard errors",
                      (x, 0), xytext=(12, -38), textcoords="offset points", fontsize=8,
                      arrowprops={"arrowstyle": "-", "color": MUTED})
    left.set_xlabel("change in HiTec expected return (pp / month)")
    left.set_ylabel("score advantage of proposal over current\n(bp / month, > 0 = switch looks better)")
    left.set_title(f"{summary['profile']}: the verdict flips well inside the estimation error", fontsize=10)
    left.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=1, fontsize=8, loc="lower right")
    better = resampled > 0
    bins = np.arange(np.floor(resampled.min() * 1e4 / HIST_BIN_BP), np.ceil(resampled.max() * 1e4 / HIST_BIN_BP) + 1) * HIST_BIN_BP
    right.hist(resampled[better] * 1e4, bins=bins, color=ROLE_COLORS["proposal"], rwidth=0.9,
               label=f"proposal better: {better.mean():.0%} of resamples")
    right.hist(resampled[~better] * 1e4, bins=bins, color=ROLE_COLORS["current"], rwidth=0.9,
               label=f"current better: {1 - better.mean():.0%}")
    right.axvline(0, color=MUTED, lw=0.8)
    right.axvline(summary["advantage_base"] * 1e4, color=INK, ls="--", lw=1,
                  label=f"estimate on the 60 months: {summary['advantage_base'] * 1e4:+.1f} bp")
    right.set_xlabel("score advantage of proposal over current (bp / month)")
    right.set_ylabel(f"resamples (of {len(resampled)})")
    right.set_title(f"Bootstrap: 5–95 % range {summary['bootstrap_advantage_p05'] * 1e4:+.1f} to "
                    f"{summary['bootstrap_advantage_p95'] * 1e4:+.1f} bp; switch gate needs "
                    f"{config.bootstrap_threshold:.0%}", fontsize=10)
    right.set_ylim(0, right.get_ylim()[1] * 1.35)
    right.legend(frameon=False, fontsize=8, loc="upper left")
    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def loss_limits(table: pd.DataFrame, config: Config, path: Path) -> None:
    """Breach share of the binding loss rule: ex-ante scenario sets vs realised hold-out months, per profile."""
    profiles = list(dict.fromkeys(table.profile))
    windows = list(dict.fromkeys(table.window))
    roles = list(dict.fromkeys(table.portfolio))
    fig, axes = plt.subplots(1, len(profiles), figsize=(13, 4.8), sharey=True)
    width = 0.8 / len(roles)
    for ax, profile in zip(np.atleast_1d(axes), profiles):
        part = table[table.profile == profile]
        for k, role in enumerate(roles):
            rows = part[part.portfolio == role].set_index("window").loc[windows]
            xs = np.arange(len(windows)) + (k - (len(roles) - 1) / 2) * width
            bars = ax.bar(xs, rows.breach_share, width * 0.92, color=ROLE_COLORS.get(role, MUTED),
                          label=f"{role}: {rows.holdings.iloc[0]}")
            for bar, n, months in zip(bars, rows.breaches, rows.months):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{n}/{months}",
                        ha="center", va="bottom", fontsize=7, color=INK)
        tolerance = part.loss_tolerance.iloc[0]
        ax.axhline(tolerance, color=INK, ls="--", lw=1, label=f"tolerance α = {tolerance:.0%} (≤ allowed)")
        ax.axvspan(len(windows) - 1.5, len(windows) - 0.5, color=BAND, alpha=0.6, lw=0, zorder=0)
        ax.set_xticks(range(len(windows)), [w.replace(": ", ":\n").replace("realised ", "realised\n") for w in windows],
                      fontsize=8)
        ax.set_title(f"{profile.replace('_', '-')}: loss > {part.loss_threshold.iloc[0]:.0%} in a month")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("share of months breaching the loss threshold")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0, 0.9))
    fig.suptitle("Binding loss rule: what the 2015–19 scenarios promised vs what 2020–24 delivered "
                 "(fixed 1/3 weights; shaded = hold-out, never a decision input)")
    _save(fig, path)


def loss_timeline(evaluation: pd.DataFrame, portfolios: dict[str, np.ndarray], config: Config, path: Path) -> None:
    """Realised monthly returns of the two options against every profile's loss threshold."""
    months = pd.to_datetime(evaluation.index)
    fig, ax = plt.subplots(figsize=(11, 4.4))
    for role, x in portfolios.items():
        ax.plot(months, evaluation.to_numpy() @ weights(x, config) * 100, color=ROLE_COLORS.get(role, MUTED), lw=1.6,
                marker="o", ms=3, label=f"{role}: {label(x, config)}")
    for profile in config.profiles:
        ax.hlines(-profile.loss_threshold * 100, months[0], months[-1], color=INK, ls="--", lw=0.8)
        ax.text(months[-1] + pd.Timedelta(days=20), -profile.loss_threshold * 100,
                f"−{profile.loss_threshold:.0%} {profile.name.replace('_', '-')}", va="center", fontsize=8, color=MUTED)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_ylabel("monthly return (%)")
    ax.set_title(f"Realised months {config.evaluation_start} to {config.evaluation_end} vs each profile's loss threshold "
                 "(hindsight only)")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(months[0], months[-1] + pd.Timedelta(days=260))
    _save(fig, path)
