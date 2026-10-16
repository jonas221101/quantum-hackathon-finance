# Narration Script: The Portfolio Decision Behind the Quantum Experiment

## Production direction

Target length: 5 to 6 minutes.

Read in a calm, confident, human tone. This is an investment-committee
explainer, not a children's cartoon and not a sales pitch. Pronounce sector
codes as follows:

- NoDur: “no-dur”
- HiTec: “high-tech”
- Hlth: “health”
- Utils: “utilities”
- QAOA: “KWAH-oh”

Pause briefly after each recommendation. Do not rush tables, percentages, or
technical terms.

## Scene 1 — The decision, not the buzzword

Every investment decision begins with a human question.

At the end of 2019, a public retirement fund has a small satellite tilt spread
equally across consumer staples, healthcare, and utilities. In the model, these
sectors are called NoDur, Hlth, and Utils.

Someone proposes replacing consumer staples with technology: HiTec, Hlth, and
Utils.

The question is not simply, “Which portfolio had the highest return?”

The real question is: for each investor mandate, is changing the portfolio
worth the extra risk, the switching cost, and the uncertainty in the evidence?

The core of the retirement fund would remain broadly diversified. This
three-sector choice is only a small satellite tilt.

## Scene 2 — The data and the candidates

The project uses six industry return series: consumer staples, manufacturing,
energy, technology, healthcare, and utilities.

We use 60 months from January 2015 through December 2019 to make the decision.
The following 60 months, from January 2020 through December 2024, are held out
for an after-the-fact check.

The rule is simple: select exactly three industries, with one third in each.

Because there are six industries, there are only 20 possible portfolios. A
normal computer can check every one of them instantly. That exact calculation
is important. It gives us an answer key with which to audit the quantum
experiment.

## Scene 3 — Different people need different answers

The project does not assume that one portfolio fits everyone.

The growth mandate gives more weight to return. The balanced mandate gives
return and risk more equal importance. The risk-sensitive mandate puts much
more weight on stability and uses a stricter monthly loss tolerance.

The loss rule is binding. A portfolio cannot simply score well on return and
buy its way around the rule.

The model also includes a cost for switching and a preference that limits
technology concentration. These are preferences in the score. Exactly three
holdings and the loss tolerance are the rules that must be satisfied.

## Scene 4 — The classical result

Here is the canonical recommendation.

For the growth mandate, switch to HiTec, Hlth, and Utils. It is the same winner
under all three supplied scenario sets, and it beats the current tilt in 89
percent of 500 bootstrap resamples.

For the balanced mandate, review the decision. The proposed portfolio wins in
the base case, but the winner changes under the supplied return stress. The
margin is too small for an automatic switch.

For the risk-sensitive mandate, keep NoDur, Hlth, and Utils. The current tilt
wins across the scenarios and passes the loss rule in 76 percent of bootstrap
resamples.

This is why “Review” matters. It means the evidence does not justify pretending
that a fragile result is certain.

## Scene 5 — Turning the decision into a quantum problem

Now we encode the decision for a quantum experiment.

Each industry becomes one binary choice. A one means the industry is selected;
a zero means it is not. Six binary choices correspond to six qubits.

The objective combines estimated return, covariance risk, switching cost, and
the technology preference.

QAOA, the Quantum Approximate Optimisation Algorithm, searches for low-cost
choices by alternating two operations.

The cost operation marks better and worse choices. The mixer operation moves
probability between choices, so the circuit explores many candidates before
measurement.

Our main circuit starts in a Dicke state: a superposition containing only
states with exactly three selected industries. It then uses an XY mixer that
preserves that three-selection structure.

The baseline uses a more familiar X mixer. It allows invalid states during the
search and discourages them with penalty terms.

## Scene 6 — What IBM actually means here

This is an IBM Qiskit experiment running locally with IBM’s Qiskit Aer
simulator. It is not a run on IBM quantum hardware, and it is not an IBM cloud
execution.

The circuit parameters are adjusted by a classical optimiser. The circuit is
then sampled repeatedly, and the samples are decoded back into portfolios.

Every decoded result is checked against the exact three-holding rule and the
loss rule. We compare the quantum samples with the exact classical answer key.

The rule-preserving circuit produces valid portfolios by construction and is
more reliable than the penalty baseline in the tested settings. Balanced is
still difficult because the competing choices are nearly tied.

That is an engineering result, not a claim of quantum advantage.

## Scene 7 — Robustness is part of the answer

A useful investment tool must show what happens when assumptions change.

The project tests return stress, covariance stress, bootstrap resamples,
sensitivity to risk and switching assumptions, and a held-out period.

These tests reinforce the three different conclusions.

Growth has the clearest case for a switch, but the technology rally may not
repeat.

Balanced is a committee question, not an automatic instruction.

Risk-sensitive investors have the strongest reason to keep the current tilt,
although even that result is limited by the historical sample and the loss
rule.

## Scene 8 — Responsible conclusion

The main achievement is not that a quantum circuit replaces an investment
committee.

The achievement is an inspectable workflow: a real decision, explicit rules,
an exact answer key, a constraint-aware QAOA experiment, stress tests, and
honest limitations.

The final message is simple.

Switch only when the evidence survives the relevant stresses.
Keep the current tilt when risk and admissibility dominate.
Choose Review when the answer is fragile.

And always remember: this prototype demonstrates a disciplined quantum-finance
workflow. It does not claim quantum advantage, and it is not a substitute for
professional investment, legal, or policy review.
