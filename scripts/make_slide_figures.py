"""Slide-ready figures for the pitch deck, drawn from the canonical results (no re-run needed).

Usage: python scripts/make_slide_figures.py [results/canonical]
Writes PNGs to <run>/figures/slides/. Colours match the MBB pitch deck; Carlito is the metric twin of its Calibri font.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from qhf.config import DEFAULT_CONFIG  # noqa: E402
from qhf.data import evaluation_slice, load_returns  # noqa: E402
from qhf.evaluation import buy_and_hold_wealth  # noqa: E402
from qhf.portfolio import selection, turnover, weights  # noqa: E402

NAVY, INK, MUTED, GRID, LIGHT = "#0A192F", "#334155", "#64748B", "#E2E8F0", "#F8FAFC"
CURRENT, TECH = "#2563EB", "#EA580C"  # today's basket, the tech basket (same on every chart)
OURS, ORGANISER, TUNED = "#2563EB", "#94A3B8", "#475569"
SAVERS = {"growth": "Lena", "balanced": "Thomas", "risk_sensitive": "Anna"}
DPI = 220

plt.rcParams.update({
    "font.family": ["Carlito", "DejaVu Sans"], "font.size": 12, "axes.titlesize": 13,
    "axes.labelcolor": INK, "axes.edgecolor": GRID, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
})


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(path)


def risk_return(run: Path, out: Path) -> None:
    table = pd.read_csv(run / "exact_rankings.csv")
    base = table[(table.scenario == "base") & (table.profile == "balanced")]
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.scatter(base.volatility * 100, base["mean"] * 100, s=55, color="#CBD5E1", label="the other 18 baskets", zorder=2)
    for holdings, color, name, text_xy in [("NoDur+Hlth+Utils", CURRENT, "Today: staples + health + utilities", (2.85, 0.61)),
                                           ("HiTec+Hlth+Utils", TECH, "Proposal: tech + health + utilities", (3.5, 0.90))]:
        row = base[base.holdings == holdings].iloc[0]
        x, y = row.volatility * 100, row["mean"] * 100
        ax.scatter(x, y, s=170, color=color, zorder=3, edgecolor="white", linewidth=1.5)
        ax.annotate(f"{name}\n{y:.2f}% return · {x:.2f}% risk", (x, y), xytext=text_xy, fontsize=11, color=color,
                    fontweight="bold", va="center", arrowprops={"arrowstyle": "-", "color": color, "lw": 1})
    ax.set_xlabel("risk: monthly volatility (%)")
    ax.set_ylabel("average monthly return (%)")
    ax.set_title("All 20 possible baskets, estimated on 2015–2019", loc="left")
    ax.grid(color=GRID, lw=0.8)
    ax.set_xlim(base.volatility.min() * 100 - 0.15, base.volatility.max() * 100 + 0.25)
    ax.legend(frameon=False, loc="lower right", fontsize=10)
    _save(fig, out / "slide_risk_return.png")


def _box(ax, x, y, w, h, text, face, edge, color=NAVY, size=10.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.025", facecolor=face,
                                edgecolor=edge, linewidth=1.6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=color,
            fontweight="bold" if bold else "normal", wrap=True)


def _arrow(ax, x0, x1, y, color=MUTED):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=14, color=color, lw=1.4))


def circuit(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    rows = [
        (0.70, "Organisers' penalty QAOA", ORGANISER, "#F1F5F9",
         ["Start: all 64\non/off patterns\n(44 are illegal)", "Score\n+ penalty for\nwrong count", "X mixer:\nflips sectors\non or off",
          "Measure:\nillegal answers\npossible"]),
        (0.22, "Our rule-preserving QAOA", OURS, "#EFF6FF",
         ["Start: Dicke state,\nonly the 20\nlegal baskets", "Score\n(return, risk,\nswitching cost)", "XY mixer:\nswaps sectors,\nalways 3",
          "Measure:\nonly legal\nanswers"]),
    ]
    xs, w, h = [0.02, 0.27, 0.52, 0.77], 0.21, 0.24
    for y, title, edge, face, steps in rows:
        ax.text(0.02, y + h + 0.045, title, fontsize=12.5, fontweight="bold", color=edge if edge == OURS else INK)
        for k, (x, step) in enumerate(zip(xs, steps)):
            last_bad = edge != OURS and k in (0, 3)
            _box(ax, x, y, w, h, step, "#FEF2F2" if last_bad else face, "#DC2626" if last_bad else edge, size=10)
            if k < 3:
                _arrow(ax, x + w + 0.005, xs[k + 1] - 0.005, y + h / 2)
        ax.annotate("", xy=(0.73, y - 0.03), xytext=(0.27, y - 0.03),
                    arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 1})
        ax.text(0.50, y - 0.065, "repeated in 3 layers; a laptop tunes the two dials (γ, β)", ha="center", fontsize=9.5,
                color=MUTED)
    _save(fig, out / "slide_circuit.png")


def quantum(run: Path, out: Path) -> None:
    summary = pd.read_csv(run / "quantum_summary.csv")
    deepest = summary.layers.max()
    methods = [("x_penalty", "Organisers' penalty circuit", ORGANISER), ("x_penalty_tuned", "Penalty, tuned", TUNED),
               ("dicke_xy", "Ours (rule-preserving)", OURS)]
    profiles = list(SAVERS)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(6.6, 4.9), sharex=True)
    width = 0.26
    for k, (method, label, color) in enumerate(methods):
        part = summary[(summary.layers == deepest) & (summary.method == method)].set_index("profile").loc[profiles]
        xs = np.arange(len(profiles)) + (k - 1) * width
        for ax, column, fmt in ((top, "sampled_h1_share_median", "{:.0%}"), (bottom, "p_opt_median", "{:.2f}")):
            bars = ax.bar(xs, part[column], width * 0.92, color=color, label=label)
            for bar, value in zip(bars, part[column]):
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, fmt.format(value), ha="center", va="bottom",
                        fontsize=9.5, color=INK, fontweight="bold" if method == "dicke_xy" else "normal")
    top.set_ylim(0, 1.18)
    top.set_ylabel("legal answers")
    top.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    top.set_title("How often is the answer a legal basket (exactly 3 sectors)?", loc="left", fontsize=12)
    bottom.set_ylim(0, 1.0)
    bottom.set_ylabel("chance of best basket")
    guess = bottom.axhline(0.05, color=NAVY, ls=":", lw=1.2)
    bottom.legend([guess], ["random guess (0.05)"], frameon=False, fontsize=9.5, loc="upper left")
    bottom.set_title("How often does it name the best basket?", loc="left", fontsize=12)
    bottom.set_xticks(range(len(profiles)), [f"{SAVERS[p]}\n({p.replace('_', '-')})" for p in profiles])
    handles, names = top.get_legend_handles_labels()
    fig.legend(handles, names, frameon=False, fontsize=9.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.06))
    for ax in (top, bottom):
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    fig.text(0.0, -0.02, f"Ideal simulation, {deepest} layers, median of 10 runs, 4,096 measured looks per run.", fontsize=9,
             color=MUTED)
    fig.tight_layout()
    _save(fig, out / "slide_quantum.png")


def replays(run: Path, out: Path, profile: str, filename: str) -> None:
    advantage = pd.read_csv(run / "bootstrap_advantage.csv")
    values = advantage[advantage.profile == profile].advantage.to_numpy() * 1e4
    estimate = pd.read_csv(run / "estimation_error.csv").set_index("profile").loc[profile, "advantage_base"] * 1e4
    width = 4.0
    bins = np.arange(np.floor(values.min() / width), np.ceil(values.max() / width) + 1) * width
    better = values > 0
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    ax.hist(values[better], bins=bins, color=TECH, rwidth=0.9, label=f"tech basket better: {better.mean():.0%} of replays")
    ax.hist(values[~better], bins=bins, color=CURRENT, rwidth=0.9, label=f"today's basket better: {1 - better.mean():.0%}")
    ax.axvline(0, color=NAVY, lw=1)
    ax.axvline(estimate, color=NAVY, ls="--", lw=1.2, label=f"on the real 60 months: +{estimate:.0f} bp")
    ax.set_xlabel("how much better the tech basket scores (basis points per month)")
    ax.set_ylabel(f"replays (of {len(values)})")
    ax.set_title(f"{SAVERS[profile]}: 500 replays of 2015–2019 history", loc="left")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.3)
    ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    _save(fig, out / filename)


def thomas_noise(run: Path, out: Path) -> None:
    curve = pd.read_csv(run / "estimation_error_curve.csv")
    curve = curve[curve.profile == "balanced"]
    info = pd.read_csv(run / "estimation_error.csv").set_index("profile").loc["balanced"]
    se, flip = info.hitec_mean_standard_error * 100, info.break_even_hitec_shift * 100
    stress = DEFAULT_CONFIG.return_stress_shift * 100
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    ax.axvspan(-2 * se, 2 * se, color="#F1F5F9", lw=0, label=f"±2 standard errors (±{2 * se:.2f} pt)")
    ax.axvspan(-se, se, color="#E2E8F0", lw=0, label=f"±1 standard error (±{se:.2f} pt)")
    ax.axhline(0, color=MUTED, lw=0.9)
    ax.plot(curve.hitec_shift * 100, curve.advantage * 1e4, color=NAVY, lw=2.4)
    ax.axvline(stress, color="#DC2626", ls=":", lw=1.5)
    ax.text(stress - 0.03, ax.get_ylim()[0] * 0.9, "organisers'\nstress test", ha="right", va="bottom", fontsize=10,
            color="#DC2626")
    ax.plot([flip], [0], "o", ms=10, color=TECH, zorder=3)
    ax.annotate(f"answer flips at {flip:+.2f} pt\n= {abs(info.break_even_in_standard_errors):.2f} standard errors",
                (flip, 0), xytext=(flip + 0.25, -14), fontsize=10.5, color=NAVY,
                arrowprops={"arrowstyle": "-", "color": MUTED})
    ax.set_xlabel("change in tech's expected return (percentage points per month)")
    ax.set_ylabel("tech basket's lead (bp/month)")
    ax.set_title("Thomas: the flip point lies inside the noise", loc="left")
    ax.legend(frameon=True, facecolor="white", edgecolor="none", framealpha=1, fontsize=10, loc="lower right")
    _save(fig, out / "slide_thomas_noise.png")


def anna_loss_rule(run: Path, out: Path) -> None:
    limits = pd.read_csv(run / "loss_limits.csv")
    anna = limits[limits.profile == "risk_sensitive"]
    windows = list(dict.fromkeys(anna.window))
    names = {"ex-ante: base": "2015–19\ndata", "ex-ante: return stress": "tech earns\n0.5 pt less",
             "ex-ante: covariance stress": "sectors move\nmore together"}
    labels = [names.get(w, "real\n2020–24") for w in windows]
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    width = 0.36
    for k, (role, color, text) in enumerate([("current", CURRENT, "today's basket"), ("proposal", TECH, "tech basket")]):
        part = anna[anna.portfolio == role].set_index("window").loc[windows]
        xs = np.arange(len(windows)) + (k - 0.5) * width
        bars = ax.bar(xs, part.breaches, width * 0.92, color=color, label=text)
        for bar, value in zip(bars, part.breaches):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", fontsize=11, color=INK)
    allowed = int(anna.allowed_breaches.iloc[0])
    ax.axhline(allowed, color="#DC2626", ls="--", lw=1.4, label=f"limit: at most {allowed} of 60")
    ax.axvspan(len(windows) - 1.5, len(windows) - 0.5, color="#F1F5F9", lw=0, zorder=0)
    ax.set_xticks(range(len(windows)), labels)
    ax.set_ylabel("months losing more than 3% (of 60)")
    ax.set_title("Anna: loss months by test setting", loc="left")
    ax.set_ylim(0, max(anna.breaches) + 2.5)
    ax.legend(frameon=False, fontsize=10.5, loc="upper left", bbox_to_anchor=(0, 0.93))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.text(0.0, -0.09, "Shaded: held-out years, never used to decide. Fixed one-third weights.", fontsize=9, color=MUTED)
    _save(fig, out / "slide_anna_loss_rule.png")


def reality_check(run: Path, out: Path) -> None:
    config = DEFAULT_CONFIG
    evaluation = evaluation_slice(load_returns(config), config)
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.7, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
    for names, color, text in [(config.current, CURRENT, "today's basket"), (config.proposal, TECH, "tech basket")]:
        x = selection(names, config)
        wealth = buy_and_hold_wealth(evaluation, weights(x, config), config.change_penalty * turnover(x, config))
        months = pd.to_datetime(wealth.index)
        left.plot(months, wealth.to_numpy(), color=color, lw=2.2, label=text)
        left.text(months[-1] + pd.Timedelta(days=25), wealth.iloc[-1], f"{wealth.iloc[-1]:.2f}", color=color,
                  fontsize=12, fontweight="bold", va="center")
    left.set_title("Growth of 1 unit invested, 2020–2024", loc="left")
    left.set_ylabel("wealth (after switching cost)")
    left.legend(frameon=False, fontsize=10.5, loc="upper left")
    left.grid(color=GRID, lw=0.8)
    limits = pd.read_csv(run / "loss_limits.csv")
    realised = limits[limits.window.str.startswith("realised")]
    profiles = list(SAVERS)
    width = 0.36
    for k, (role, color, text) in enumerate([("current", CURRENT, "today's basket"), ("proposal", TECH, "tech basket")]):
        part = realised[realised.portfolio == role].set_index("profile").loc[profiles]
        xs = np.arange(len(profiles)) + (k - 0.5) * width
        bars = right.bar(xs, part.breaches, width * 0.92, color=color, label=text)
        for bar, value in zip(bars, part.breaches):
            right.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", fontsize=11, color=INK)
    allowed = int(realised.allowed_breaches.iloc[0])
    right.axhline(allowed, color="#DC2626", ls="--", lw=1.4, label=f"limit: at most {allowed} of 60")
    thresholds = {p.name: p.loss_threshold for p in config.profiles}
    right.set_xticks(range(len(profiles)), [f"{SAVERS[p]}\nloss > {thresholds[p]:.0%}" for p in profiles])
    right.set_ylabel("loss months in 2020–2024 (of 60)")
    right.set_title("Loss months that really happened", loc="left")
    right.set_ylim(0, realised.breaches.max() + 2.5)
    right.legend(frameon=False, fontsize=10.5, loc="upper left")
    right.grid(axis="y", color=GRID, lw=0.8)
    right.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, out / "slide_reality_check.png")


def main() -> None:
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "results" / "canonical"
    out = run / "figures" / "slides"
    out.mkdir(parents=True, exist_ok=True)
    risk_return(run, out)
    circuit(out)
    quantum(run, out)
    replays(run, out, "growth", "slide_lena_replays.png")
    thomas_noise(run, out)
    anna_loss_rule(run, out)
    reality_check(run, out)


if __name__ == "__main__":
    main()
