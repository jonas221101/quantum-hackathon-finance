"""Streamlit dashboard: committee view of the allocation decision (run: ``streamlit run app.py``).

Instant view from results/canonical/summary.json, plus a live "what if" rerun with changed mandate
parameters (the mid-hackathon change). Built on the tested ``qhf`` package.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from qhf.config import DEFAULT_CONFIG, FAST_QAOA, REPO_ROOT, apply_overrides  # noqa: E402
from qhf.data import estimation_slice, load_returns  # noqa: E402
from qhf.decision import decide  # noqa: E402
from qhf.exact import rank_portfolios  # noqa: E402
from qhf.qaoa import build_problem, random_floors, run_experiment, summarise  # noqa: E402
from qhf.report import markdown_report  # noqa: E402
from qhf.scenarios import moments, scenario_sets  # noqa: E402

CANONICAL = REPO_ROOT / "results" / "canonical"
LIVE_BOOTSTRAP_SAMPLES = 200
METHOD_LABELS = {"x_penalty": "Penalty QAOA (organiser)", "dicke_xy": "Rule-preserving QAOA (ours)"}

st.set_page_config(page_title="Kapitalrente allocation", layout="wide")
st.title("Keep or tilt? A defensible allocation decision")
st.caption("Committee view for the satellite tilt of the planned public Kapitalrente fund. "
           "Exact enumeration of all 20 portfolios is the answer key; QAOA is compared quantum vs quantum.")

with st.expander("What this demo answers", expanded=True):
    st.markdown(
        "At the **31 Dec 2019** decision date: which **three of six industries** should each profile's "
        "satellite tilt hold, and is leaving the current tilt (NoDur, Hlth, Utils) justified? "
        "Profiles are chosen **actively** by each insured person; *balanced* is the default for people who "
        "do not choose. Jan 2020 – Dec 2024 is held out and never used for the decision."
    )
    st.info("The six-industry sleeve is challenge-sized, not the whole pension portfolio. "
            "No quantum advantage is claimed.")

profiles = [p.name for p in DEFAULT_CONFIG.profiles]
profile = st.selectbox("Profile", profiles, index=profiles.index(DEFAULT_CONFIG.default_profile))
canonical_tab, live_tab = st.tabs(["Canonical result", "What if? (live rerun)"])

with canonical_tab:
    summary_path = CANONICAL / "summary.json"
    if not summary_path.exists():
        st.warning("No canonical run found. Run `python scripts/run_all.py run --canonical` first.")
    else:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        v = summary["verdicts"][profile]
        cols = st.columns(3)
        cols[0].metric("Verdict", v["verdict"].upper())
        cols[1].metric("Hold", v["target"])
        cols[2].metric("Candidate beats current", f"{v['bootstrap_candidate_beats_current']:.0%} of resamples")
        st.write(f"**Why:** {v['reason']}. **Action:** {v['action']}.")
        st.subheader("Best portfolio in each scenario set")
        st.dataframe(pd.DataFrame([{"scenario": k, "portfolio": o} for k, o in v["optima"].items()]),
                     hide_index=True, use_container_width=True)
        rankings = pd.read_csv(CANONICAL / "exact_rankings.csv")
        base = rankings[(rankings.profile == profile) & (rankings.scenario == "base")]
        st.subheader("Exact answer key (base case)")
        st.dataframe(base[["rank", "holdings", "objective", "mean", "volatility", "breaches", "passes_loss_rule",
                           "cap_excess"]], hide_index=True, use_container_width=True)
        st.subheader("Quantum vs quantum (median over 10 seeds, ideal simulation)")
        quantum = pd.DataFrame(summary["quantum"]["summary"])
        part = quantum[quantum.profile == profile].pivot(index="layers", columns="method", values="p_opt_median")
        st.bar_chart(part)
        st.caption("P(best portfolio) by QAOA depth. Random guessing among valid portfolios gives "
                   f"{summary['quantum']['random_guess_p_opt'][profile]['valid_states']:.2f}.")
        for name in ["fig_decision_map", "fig_bootstrap", "fig_qaoa_comparison", "fig_holdout"]:
            figure = CANONICAL / "figures" / f"{name}.png"
            if figure.exists():
                st.image(str(figure), use_container_width=True)
        st.download_button("Download committee report (Markdown)", markdown_report(summary),
                           file_name="committee_report.md", mime="text/markdown")
        st.download_button("Download summary.json", summary_path.read_text(encoding="utf-8"),
                           file_name="summary.json", mime="application/json")

with live_tab:
    st.markdown("Change a mandate parameter and see whether the decision changes. Binding rules: exactly 3 "
                "holdings and the loss tolerance. The HiTec cap is a preference.")
    current = DEFAULT_CONFIG.profile(profile)
    c1, c2, c3 = st.columns(3)
    risk = c1.number_input("Risk aversion λ", 0.1, 100.0, float(current.risk_aversion), step=0.5)
    threshold = c2.number_input("Loss threshold (one month)", 0.0, 0.2, float(current.loss_threshold), step=0.005, format="%.3f")
    tolerance = c3.number_input("Tolerated breach probability", 0.0, 0.5, float(current.loss_tolerance), step=0.01, format="%.2f")
    c4, c5, c6 = st.columns(3)
    cap = c4.number_input("HiTec cap (preference)", 0.0, 1.0, float(current.hitec_cap), step=0.05)
    kappa = c5.number_input("Cap preference weight κ", 0.0, 0.2, float(DEFAULT_CONFIG.cap_penalty), step=0.005, format="%.3f")
    tau = c6.number_input("Switching cost τ", 0.0, 0.05, float(DEFAULT_CONFIG.change_penalty), step=0.001, format="%.3f")
    run_quantum = st.checkbox("Also run a quick QAOA comparison (≈ 30 s)", value=False)
    if st.button("Rerun decision", type="primary"):
        config = apply_overrides(DEFAULT_CONFIG, [
            f"{profile}.risk_aversion={risk}", f"{profile}.loss_threshold={threshold}",
            f"{profile}.loss_tolerance={tolerance}", f"{profile}.hitec_cap={cap}",
            f"cap_penalty={kappa}", f"change_penalty={tau}",
        ])
        config = replace(config, bootstrap_samples=LIVE_BOOTSTRAP_SAMPLES, qaoa=FAST_QAOA)
        with st.spinner("Scoring all 20 portfolios and resampling…"):
            scenarios = scenario_sets(estimation_slice(load_returns(config), config), config)
            verdict = decide(scenarios, config.profile(profile), config)
        cols = st.columns(3)
        cols[0].metric("Verdict", verdict.verdict.upper())
        cols[1].metric("Hold", verdict.target)
        cols[2].metric("Candidate beats current", f"{verdict.evidence.target_beats_current:.0%}")
        st.write(f"**Why:** {verdict.reason}.")
        st.dataframe(pd.DataFrame([{"scenario": k, "portfolio": o} for k, o in verdict.optima.items()]),
                     hide_index=True, use_container_width=True)
        mu, sigma = moments(scenarios["base"], config.ddof)
        table = rank_portfolios(mu, sigma, scenarios["base"], config.profile(profile), config)
        st.dataframe(table[["rank", "holdings", "objective", "breaches", "passes_loss_rule", "cap_excess"]],
                     hide_index=True, use_container_width=True)
        if run_quantum:
            with st.spinner("Running QAOA (ideal simulation)…"):
                try:
                    problem = {profile: build_problem(mu, sigma, scenarios["base"], config.profile(profile), config)}
                except ValueError as error:
                    st.error(str(error))
                else:
                    runs = run_experiment(problem, config, methods=("x_penalty", "dicke_xy"))
                    quick = summarise(runs, random_floors(problem))
                    quick["method"] = quick.method.map(METHOD_LABELS)
                    st.dataframe(quick[["method", "layers", "p_opt_median", "h1_mass_median", "decoded_is_optimum_share"]],
                                 hide_index=True, use_container_width=True)
                    st.caption("Quick run: few seeds and starts, so results are noisier than the canonical run.")
