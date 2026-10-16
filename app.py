from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.analysis import run_analysis
from src.config import MANDATES
from src.data import DEFAULT_DATA_PATH


st.set_page_config(page_title="Quantum Finance Allocation", layout="wide")
st.title("A defensible quantum allocation decision")
st.caption(
    "Committee view: compare a rule-aware QAOA result with the exact classical "
    "answer key."
)

mandate = st.selectbox("Mandate", list(MANDATES))
run_quantum = st.checkbox("Run IBM Aer QAOA", value=False)

with st.expander("What this demo answers", expanded=True):
    st.markdown(
        "At the 31 Dec 2019 decision date, which **three of six industries** "
        "should the fund's satellite tilt hold? We compare all 20 equal-weight "
        "portfolios, apply the mandate's loss rule, and keep Jan 2020-Dec 2024 "
        "as held-out evaluation data."
    )
    st.info(
        "The six-industry model is a challenge-sized satellite sleeve, not the "
        "complete pension portfolio. No quantum advantage is claimed."
    )

if st.button("Run analysis", type="primary"):
    with st.spinner("Evaluating portfolios..."):
        result = run_analysis(DEFAULT_DATA_PATH, include_quantum=run_quantum)
    table = result["reference_table"].copy()
    base_portfolio = result["classical_winners"][mandate]
    stress_portfolios = [
        winners[mandate]
        for name, winners in result["scenario_winners"].items()
        if name != "base"
    ]
    if any(portfolio != base_portfolio for portfolio in stress_portfolios):
        st.warning(
            f"Decision framing: REVIEW. The base recommendation {base_portfolio} "
            "changes under at least one supplied stress."
        )
    elif base_portfolio == "NoDur+Hlth+Utils":
        st.success("Decision framing: KEEP the current allocation.")
    else:
        st.success(f"Decision framing: SWITCH to {base_portfolio}.")
    st.subheader("Exact classical answer key")
    st.success(f"Base-case recommendation: {result['classical_winners'][mandate]}")
    st.caption(
        "This is the auditable reference. QAOA is evaluated against it, rather "
        "than replacing it."
    )
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
    st.subheader("Risk / return map")
    st.caption(
        "Each point is one of the 20 candidate portfolios. Higher mean and lower "
        "volatility are generally preferable."
    )
    chart_data = table[
        ["portfolio", "mean", "volatility", f"feasible__{mandate}"]
    ].copy()
    chart_data["status"] = chart_data[f"feasible__{mandate}"].map(
        {True: "Feasible", False: "Not feasible"}
    )
    st.scatter_chart(
        chart_data,
        x="volatility",
        y="mean",
        color="status",
        use_container_width=True,
    )

    st.subheader("Current versus recommended allocation")
    current_name = "NoDur+Hlth+Utils"
    recommended_name = result["classical_winners"][mandate]
    comparison = table[table["portfolio"].isin([current_name, recommended_name])][
        ["portfolio", "mean", "volatility", "worst_month", "turnover"]
    ].set_index("portfolio")
    st.bar_chart(comparison[["mean", "volatility"]], use_container_width=True)
    st.dataframe(comparison, use_container_width=True)

    st.subheader("Scenario recommendation stability")
    scenario_table = pd.DataFrame(
        [
            {"scenario": name, "portfolio": winners[mandate]}
            for name, winners in result["scenario_winners"].items()
        ]
    )
    scenario_table["same_as_base"] = scenario_table["portfolio"].eq(
        scenario_table.iloc[0]["portfolio"]
    )
    st.dataframe(scenario_table, use_container_width=True, hide_index=True)
    st.bar_chart(
        scenario_table.assign(
            stable=scenario_table["same_as_base"].astype(int)
        ).set_index("scenario")[["stable"]],
        use_container_width=True,
    )
    st.subheader("Held-out evaluation (2020–2024)")
    st.caption("These returns are not used to choose the portfolio.")
    st.dataframe(result["holdout"], use_container_width=True, hide_index=True)
    st.bar_chart(
        result["holdout"].set_index("portfolio")[["mean", "volatility"]],
        use_container_width=True,
    )
    st.subheader("Sensitivity")
    sensitivity = pd.DataFrame(result["sensitivity"][mandate])
    st.dataframe(sensitivity, use_container_width=True, hide_index=True)
    st.bar_chart(
        sensitivity[sensitivity["parameter"] == "HiTec shift"].set_index("value")[
            ["winner"]
        ].assign(changed=lambda frame: frame["winner"].ne(base_portfolio).astype(int))[
            ["changed"]
        ],
        use_container_width=True,
    )
    st.subheader("How to read the result")
    st.markdown(
        "- **Mean** measures average monthly return.\n"
        "- **Volatility** measures monthly dispersion.\n"
        "- **Worst month** shows the largest observed monthly loss.\n"
        "- **Feasible** means the portfolio passes the mandate's binding loss "
        "tolerance; the HiTec limit is currently a model preference.\n\n"
        "The balanced result is a base-case recommendation with sensitivity to "
        "stress assumptions. The risk-sensitive mandate is deliberately more "
        "constrained."
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
        st.subheader("QAOA result on IBM Aer")
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
            "QAOA is probabilistic: the probability fields show confidence in "
            "the sampled decision. Exact enumeration remains the auditable "
            "answer key."
        )
