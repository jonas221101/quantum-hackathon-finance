"""Collect every number the pitch deck shows into one JSON file (input for scripts/build_pitch_deck.js).

Usage: python scripts/export_deck_data.py [results/canonical]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from qhf.config import DEFAULT_CONFIG
from qhf.data import evaluation_slice, load_returns
from qhf.evaluation import buy_and_hold_wealth
from qhf.portfolio import selection, turnover, weights

CURRENT, PROPOSAL = "NoDur+Hlth+Utils", "HiTec+Hlth+Utils"
PROFILES = ("growth", "balanced", "risk_sensitive")
HIST_BIN_BP = 4.0


def main() -> None:
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "results" / "canonical"
    config = DEFAULT_CONFIG
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    rankings = pd.read_csv(run / "exact_rankings.csv")
    base = rankings[(rankings.scenario == "base") & (rankings.profile == "balanced")]
    baskets = [{"holdings": r.holdings, "mean": round(r["mean"] * 100, 3), "vol": round(r.volatility * 100, 3)}
               for _, r in base.iterrows()]

    quantum = pd.read_csv(run / "quantum_summary.csv")
    deepest = int(quantum.layers.max())
    q = {m: {p: {"legal": round(float(row.sampled_h1_share_median), 3), "best": round(float(row.p_opt_median), 3)}
             for p, row in quantum[(quantum.layers == deepest) & (quantum.method == m)].set_index("profile").iterrows()}
         for m in ("x_penalty", "x_penalty_tuned", "dicke_xy")}

    advantage = pd.read_csv(run / "bootstrap_advantage.csv")
    growth = advantage[advantage.profile == "growth"].advantage.to_numpy() * 1e4
    edges = np.arange(np.floor(growth.min() / HIST_BIN_BP), np.ceil(growth.max() / HIST_BIN_BP) + 1) * HIST_BIN_BP
    counts, _ = np.histogram(growth, bins=edges)
    centres = (edges[:-1] + edges[1:]) / 2

    errors = pd.read_csv(run / "estimation_error.csv").set_index("profile")
    limits = pd.read_csv(run / "loss_limits.csv")
    windows = list(dict.fromkeys(limits.window))

    evaluation = evaluation_slice(load_returns(config), config)
    wealth = {}
    for role, names in (("current", config.current), ("proposal", config.proposal)):
        x = selection(names, config)
        path = buy_and_hold_wealth(evaluation, weights(x, config), config.change_penalty * turnover(x, config))
        wealth[role] = [round(float(v), 4) for v in path]

    holdout = pd.read_csv(run / "holdout.csv")
    hb = holdout[holdout.profile == "growth"].set_index("portfolio")
    data = {
        "baskets": baskets,
        "current": CURRENT, "proposal": PROPOSAL,
        "verdicts": {p: {k: summary["verdicts"][p][k] for k in ("verdict", "bootstrap_candidate_beats_current",
                                                                 "bootstrap_current_admissible", "margin")}
                     for p in PROFILES},
        "quantum": {"layers": deepest, "methods": q},
        "lena_hist": {"centres": [float(c) for c in centres], "counts": [int(c) for c in counts],
                      "share_better": round(float(np.mean(growth > 0)), 3),
                      "estimate_bp": round(float(errors.loc["growth", "advantage_base"] * 1e4), 1)},
        "noise": {"se": round(float(errors.loc["balanced", "hitec_mean_standard_error"] * 100), 2),
                  "thomas_flip": round(float(errors.loc["balanced", "break_even_hitec_shift"] * 100), 2),
                  "lena_flip": round(float(errors.loc["growth", "break_even_hitec_shift"] * 100), 2),
                  "stress": config.return_stress_shift * 100,
                  "thomas_lead_bp": round(float(errors.loc["balanced", "advantage_base"] * 1e4), 1),
                  "thomas_share": round(float(errors.loc["balanced", "bootstrap_share_proposal_better"]), 3),
                  "hitec_mean": round(float(errors.loc["balanced", "hitec_mean"] * 100), 2),
                  "anna_gap_bp": round(float(errors.loc["risk_sensitive", "advantage_base"] * 1e4), 1)},
        "loss_months": {p: {role: [int(limits[(limits.profile == p) & (limits.portfolio == role) & (limits.window == w)]
                                       .breaches.iloc[0]) for w in windows]
                            for role in ("current", "proposal")} for p in PROFILES},
        "loss_windows": windows,
        "allowed": int(limits.allowed_breaches.iloc[0]),
        "thresholds": {p.name: p.loss_threshold for p in config.profiles},
        "wealth": {"months": list(evaluation.index), **wealth},
        "drawdown": {"current": round(float(hb.loc["current", "max_drawdown"]) * 100), "proposal":
                     round(float(hb.loc["proposal", "max_drawdown"]) * 100)},
        "satellite_share": config.satellite_share,
    }
    out = run / "deck_data.json"
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
