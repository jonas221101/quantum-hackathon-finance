# Visual Storyboard and Asset Guide

This is a factual visualization specification, not a request for decorative
AI-generated footage. Every visual must be traceable to a source figure, a
dashboard table, or an explicitly stated calculation in the project.

## Overall visual style

- Professional public-sector finance presentation.
- Dark navy, white, and restrained teal accents.
- Clean charts, subtle motion, and generous on-screen spacing.
- Use the supplied project figures and dashboard screenshots.
- Prefer animated highlights and callouts over decorative stock footage.
- Put units directly on axes: “mean monthly return (%)”, “monthly volatility
  (%)”, “share of resamples (%)”, or “wealth per 1 invested”.
- Use one visual question per scene. Do not combine a risk/return scatter,
  scenario decision, and QAOA probability chart into one unreadable frame.
- No cartoon characters, generic robot imagery, crypto imagery, or fake
  “quantum” particle backgrounds.
- Never show a chart or number that is not present in the source files.

## Scene plan

| Time | Story beat | Suggested visual |
|---|---|---|
| 0:00–0:35 | Human decision | Split screen: current NoDur + Hlth + Utils versus proposed HiTec + Hlth + Utils. Add a small “satellite tilt” label. |
| 0:35–1:05 | Data | Timeline from Jan 2015–Dec 2019 labelled “estimation” and Jan 2020–Dec 2024 labelled “holdout”. Show six sector names. |
| 1:05–1:40 | 20 candidates | Six binary selection cards or a simple “choose 3 of 6 = 20” graphic. Show equal one-third weights. |
| 1:40–2:15 | Mandates | Three clean profile panels: Growth, Balanced, Risk-sensitive. Show risk weights and loss thresholds. |
| 2:15–2:55 | Classical answer | Use `fig_risk_return` with percent units and a separate decision card. Highlight the three verdicts: Switch, Review, Keep. |
| 2:55–3:40 | Quantum encoding | Use `fig_circuits`. Animate six binary choices, then show the Dicke state and XY mixer preserving exactly three selections. |
| 3:40–4:15 | IBM simulator clarification | Show a simple local laptop → Qiskit Aer diagram. On screen: “IBM Qiskit Aer simulator — local ideal simulation”. |
| 4:15–4:50 | Comparison | Use `fig_qaoa_comparison`. Label `P(optimum)` as simulator probability, and label valid/admissible mass separately. Explain the exact classical answer key. |
| 4:50–5:25 | Robustness | Use `fig_bootstrap`, `fig_holdout`, and the decision map. Show why balanced is Review. |
| 5:25–5:55 | Responsible close | Display the final three recommendations and a short limitations panel. |

## Required labels

Use these labels exactly where relevant:

- “Exact classical answer key”
- “IBM Qiskit Aer simulator, running locally”
- “No quantum advantage claimed”
- “60-month estimation window”
- “60-month holdout window”
- “Exactly 3 of 6 industries”
- “Review means the evidence is fragile”
- “Admissible = exactly 3 holdings + passes loss rule”
- “HiTec cap = soft preference, not binding rule”

## Chart handling

When showing a chart:

1. Display the chart title and axis labels, including units.
2. Keep it on screen for at least 6 seconds.
3. Highlight only the data point being discussed.
4. Add a short caption explaining the implication.
5. Do not cover chart labels with narration graphics.
6. State whether the chart uses estimation data, stress data, bootstrap
   resamples, ideal simulation, finite shots, or holdout data.
7. Never use a dual axis for return and volatility.
8. Never use a color alone to communicate feasibility; add text or symbols.

## Accuracy rules for the main visuals

### Risk/return map

The map contains all 20 equal-weighted portfolios. The x-axis is monthly
volatility and the y-axis is mean monthly return. Highlight the current tilt
and the base-case winner, but do not call the upper-left point “the winner”
without mentioning the selected mandate and the loss rule.

### Decision map

The decision map is a parameter sweep. It answers “which portfolio is optimal
when this assumption changes?” It does not show a probability distribution and
does not predict future market outcomes. Explain the log scale for risk
aversion and identify the dotted stress line.

### Bootstrap

Bootstrap bars show historical resample shares. They are not investor
confidence and not a forecast probability. Keep the 70% threshold visible.
Show “beats current” and “passes loss rule” as separate measures.

### QAOA comparison

The top panel is probability of the exact admissible optimum over the ideal
statevector, summarised across seeds. The lower panel is the probability mass
on exactly-three-holding states. These are different quantities. Do not label
either one “accuracy” without defining it.

### Holdout

The holdout wealth chart is hindsight from 2020–2024. It was not used to
choose the portfolio. Put that sentence on screen, not only in narration.

## On-screen numbers to prioritise

- 20 candidate portfolios.
- 60 estimation months.
- 60 holdout months.
- Growth: 89% bootstrap support for the switch.
- Risk-sensitive: 76% bootstrap support for the current tilt.
- Three possible decisions: Keep, Switch, Review.

Avoid putting too many percentages on one screen. The narration should carry
detail while the visuals reinforce the main idea. Prefer a small table with
three rows over three simultaneous bar charts.

## Final frame

Show:

| Profile | Final framing |
|---|---|
| Growth | Switch to HiTec + Hlth + Utils |
| Balanced | Review; hold unless the committee accepts the fragile edge |
| Risk-sensitive | Keep NoDur + Hlth + Utils |

Footer:

“Prototype analysis using historical data. Not investment advice. No quantum
advantage claimed.”
