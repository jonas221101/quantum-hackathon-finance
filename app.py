from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.analysis import run_analysis
from src.config import MANDATES
from src.data import DEFAULT_DATA_PATH


st.set_page_config(page_title="Quantum Finance Allocation", layout="wide")
st.title("Quantum Finance Allocation")
st.caption("Classical verifier plus QAOA on IBM's local Aer simulator")

mandate = st.selectbox("Mandate", list(MANDATES))
run_quantum = st.checkbox("Run IBM Aer QAOA", value=False)

if st.button("Run analysis", type="primary"):
    with st.spinner("Evaluating portfolios..."):
        result = run_analysis(DEFAULT_DATA_PATH, include_quantum=run_quantum)
    table = result["reference_table"].copy()
    st.subheader("Recommendation")
    st.success(f"Classical recommendation: {result['classical_winners'][mandate]}")
    st.subheader("Scenario recommendations")
    scenario_rows = [
        {"scenario": name, "portfolio": winners[mandate]}
        for name, winners in result["scenario_winners"].items()
    ]
    st.dataframe(scenario_rows, use_container_width=True, hide_index=True)
    st.dataframe(
        table[
            [
                "portfolio",
                "mean",
                "volatility",
                "worst_month",
                f"score__{mandate}",
                f"feasible__{mandate}",
            ]
        ].sort_values(f"score__{mandate}", ascending=False),
        use_container_width=True,
    )
    st.download_button(
        "Download portfolio CSV",
        table.to_csv(index=False),
        file_name="portfolio_reference.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download analysis JSON",
        json.dumps(
            {key: value for key, value in result.items() if key != "reference_table"},
            indent=2,
            default=str,
        ),
        file_name="analysis_summary.json",
        mime="application/json",
    )
    if run_quantum:
        quantum = result["quantum"]["mandates"][mandate]
        st.subheader("IBM Aer result")
        mixer_frame = pd.DataFrame({
            "mixer": ["X penalty", "Dicke + XY"],
            "statevector feasible probability": [
                quantum["x_mixer"]["probability_feasible"],
                quantum["xy_mixer"]["probability_feasible"],
            ],
            "sampled feasible probability": [
                quantum["x_mixer"]["sampled_probability_feasible"],
                quantum["xy_mixer"]["sampled_probability_feasible"],
            ],
        })
        st.bar_chart(mixer_frame, x="mixer")
        st.json(quantum)
        st.warning(
            "The XY mixer preserves the exactly-three-selection constraint. "
            "The X mixer uses penalties and may sample invalid bitstrings."
        )
        st.info(
            "QAOA is probabilistic. Exact enumeration is retained as the "
            "auditable answer key."
        )
