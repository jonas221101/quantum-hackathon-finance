from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.analysis import run_analysis
from src.config import MANDATES
from src.data import DEFAULT_DATA_PATH


MANDATE_LABELS = {
    "growth_oriented": "Growth-oriented",
    "balanced": "Balanced",
    "risk_sensitive": "Risk-sensitive",
}


@st.cache_data(show_spinner=False)
def _cached_analysis() -> dict:
    """Cache the responsive classical dashboard analysis."""
    return run_analysis(DEFAULT_DATA_PATH, include_quantum=False)


def _decision_label(base: str, scenarios: list[str]) -> tuple[str, str, str]:
    changed = [scenario for scenario in scenarios if scenario != base]
    if any(portfolio != base for portfolio in changed):
        return "REVIEW", "Review before trading", "#9a6700"
    if base == "NoDur+Hlth+Utils":
        return "KEEP", "Retain current tilt", "#176b4d"
    return "SWITCH", f"Switch to {base}", "#176b4d"


def _decision_card(mandate: str, base: str, scenario_rows: list[dict[str, str]]) -> None:
    scenario_portfolios = [row["portfolio"] for row in scenario_rows]
    status, action, color = _decision_label(base, scenario_portfolios)
    stress_text = " · ".join(
        f"{row['scenario'].replace('_', ' ').title()}: {row['portfolio']}"
        for row in scenario_rows
    )
    st.markdown(
        f"""
        <div style="border:1px solid {color};border-left:8px solid {color};
        border-radius:10px;padding:16px 20px;margin:12px 0;background:#fbfcfd">
        <div style="font-size:14px;color:#52606d">{MANDATE_LABELS[mandate].upper()} MANDATE</div>
        <div style="font-size:28px;font-weight:700;color:{color};margin:4px 0">{status}</div>
        <div style="font-size:18px;font-weight:600">{action}</div>
        <div style="font-size:13px;color:#52606d;margin-top:8px">{stress_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Quantum Finance Allocation", layout="wide")
st.title("A defensible quantum allocation decision")
st.caption(
    "Committee view: inspect the exact classical answer key and its evidence."
)

mandate = st.selectbox(
    "Mandate",
    list(MANDATES),
    format_func=lambda value: MANDATE_LABELS[value],
)
with st.expander("What this demo answers", expanded=True):
    st.markdown(
        "At the 31 Dec 2019 decision date, which **three of six industries** "
        "should the fund's satellite tilt hold? We compare all 20 equal-weight "
        "portfolios, apply the mandate's loss rule, and keep Jan 2020-Dec 2024 "
        "as held-out evaluation data."
    )
    st.info(
        "The six-industry model is a challenge-sized satellite sleeve, not the "
        "complete pension portfolio. No quantum advantage is claimed. "
        "The full QAOA benchmark is available from scripts\\run_all.py."
    )

if st.button("Run analysis", type="primary"):
    with st.spinner("Loading classical analysis..."):
        st.session_state["analysis_result"] = _cached_analysis()

if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    table = result["reference_table"].copy()
    base_portfolio = result["classical_winners"][mandate]
    stress_portfolios = [
        winners[mandate]
        for name, winners in result["scenario_winners"].items()
        if name != "base"
    ]
    scenario_rows = [
        {"scenario": name, "portfolio": winners[mandate]}
        for name, winners in result["scenario_winners"].items()
    ]
    _decision_card(mandate, base_portfolio, scenario_rows)
    st.subheader("Exact classical answer key")
    st.success(f"Base-case recommendation: {result['classical_winners'][mandate]}")
    st.caption(
        "This is the auditable reference. QAOA is evaluated against it, rather "
        "than replacing it."
    )
    st.subheader("Scenario recommendations")
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
        ]
        .sort_values(f"score__{mandate}", ascending=False)
        .style.apply(
            lambda row: [
                "background-color: #174e35; color: white"
                if row["portfolio"] == base_portfolio
                else "background-color: #3d3d1f; color: white"
                if row["portfolio"] == "HiTec+Hlth+Utils"
                else ""
                for _ in row
            ],
            axis=1,
        ),
        use_container_width=True,
    )
    st.subheader("Risk / return map")
    st.caption(
        "Each point is one of the 20 candidate portfolios. Higher mean and lower "
        "volatility are generally preferable."
    )
    current_name = "NoDur+Hlth+Utils"
    chart_data = table[
        ["portfolio", "mean", "volatility", f"feasible__{mandate}"]
    ].copy()
    chart_data["status"] = chart_data[f"feasible__{mandate}"].map(
        {True: "Feasible", False: "Not feasible"}
    )
    chart_data["portfolio_type"] = chart_data["portfolio"].map(
        lambda value: "Current"
        if value == current_name
        else "Recommended"
        if value == base_portfolio
        else "Other"
    )
    st.scatter_chart(
        chart_data,
        x="volatility",
        y="mean",
        color="portfolio_type",
        use_container_width=True,
    )
    st.caption(
        f"Highlighted portfolios: current = {current_name}; "
        f"recommended = {base_portfolio}. Feasibility is shown in the table."
    )

    st.subheader("Current versus recommended allocation")
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
    stable_count = int(scenario_table["same_as_base"].sum())
    st.metric(
        "Stress scenarios matching base",
        f"{stable_count}/{len(scenario_table)}",
        help="A mismatch means the committee decision should be reviewed.",
    )
    st.subheader("Held-out evaluation (2020–2024)")
    st.caption("These returns are not used to choose the portfolio.")
    st.dataframe(
        result["holdout"].style.format(
            {"mean": "{:.2%}", "volatility": "{:.2%}", "worst_month": "{:.2%}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
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
        "- **Admissible** means the portfolio has exactly three holdings and "
        "passes the mandate's binding loss rule. The HiTec cap is a soft "
        "preference in the canonical model, not a binding feasibility check.\n\n"
        "The balanced result is a base-case recommendation with sensitivity to "
        "stress assumptions. The risk-sensitive mandate is deliberately more "
        "constrained, so a covariance-stress flip is a review signal."
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
