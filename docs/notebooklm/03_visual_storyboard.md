# Visual Storyboard and Asset Guide

## Overall visual style

- Professional public-sector finance presentation.
- Dark navy, white, and restrained teal accents.
- Clean charts, subtle motion, and generous on-screen spacing.
- Use the supplied project figures and dashboard screenshots.
- Prefer animated highlights and callouts over decorative stock footage.
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
| 2:15–2:55 | Classical answer | Use `fig_risk_return` and `fig_decision_map`. Highlight the three verdicts: Switch, Review, Keep. |
| 2:55–3:40 | Quantum encoding | Use `fig_circuits`. Animate six binary choices, then show the Dicke state and XY mixer preserving exactly three selections. |
| 3:40–4:15 | IBM simulator clarification | Show a simple local laptop → Qiskit Aer diagram. On screen: “IBM Qiskit Aer simulator — local ideal simulation”. |
| 4:15–4:50 | Comparison | Use `fig_qaoa_comparison`. Explain optimum probability, valid samples, and the exact classical answer key. |
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

## Chart handling

When showing a chart:

1. Display the chart title and axis labels.
2. Keep it on screen for at least 6 seconds.
3. Highlight only the data point being discussed.
4. Add a short caption explaining the implication.
5. Do not cover chart labels with narration graphics.

## On-screen numbers to prioritise

- 20 candidate portfolios.
- 60 estimation months.
- 60 holdout months.
- Growth: 89% bootstrap support for the switch.
- Risk-sensitive: 76% bootstrap support for the current tilt.
- Three possible decisions: Keep, Switch, Review.

Avoid putting too many percentages on one screen. The narration should carry
detail while the visuals reinforce the main idea.

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
