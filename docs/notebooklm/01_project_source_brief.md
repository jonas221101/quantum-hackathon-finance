# Quantum Finance: Project Source Brief

## One-sentence explanation

This project helps an investment committee decide whether a small three-sector
satellite tilt in a public retirement fund should stay as it is or switch to
technology, while checking risk rules, uncertainty, and a quantum optimisation
experiment against an exact classical answer.

## The human decision

The model looks at 31 December 2019. The current satellite tilt is:

- NoDur: consumer staples
- Hlth: healthcare
- Utils: utilities

Each sector has one third of the satellite sleeve. The proposed change replaces
NoDur with HiTec, technology:

- Current: NoDur + Hlth + Utils
- Proposal: HiTec + Hlth + Utils

This is a small satellite tilt, not the whole pension portfolio. The core of
the fund remains broadly diversified.

## Data and candidates

- Six US industry series are used as a reproducible challenge-sized universe:
  NoDur, Manuf, Enrgy, HiTec, Hlth, and Utils.
- The estimation window is January 2015 through December 2019: 60 months.
- January 2020 through December 2024 is held out for after-the-fact evaluation.
- The model selects exactly three industries with equal weights.
- There are only 20 possible three-out-of-six portfolios.
- Exact enumeration of those 20 portfolios is the authoritative audit answer.

The six-industry universe is a prototype, not a complete public-fund
investment universe. The model does not include every asset class, liquidity,
tax, ESG, implementation, or liability consideration.

## Investor profiles

The profiles represent selected investment mandates, not age groups:

- **Growth:** risk weight 1; monthly loss threshold 8%.
- **Balanced:** risk weight 5; monthly loss threshold 5%.
- **Risk-sensitive:** risk weight 20; monthly loss threshold 3%.

The loss rule is binding: the probability of exceeding the profile's monthly
loss threshold must be no more than 10% in the estimation data. Return, risk,
switching cost, and the HiTec preference are tradeable objective terms. Exact
implementation details are in `docs/problem_formulation.md`.

## What the optimisation balances

The score combines:

1. Expected return: prefer higher estimated return.
2. Variance risk: penalise unstable combinations according to the profile.
3. Switching cost: make a change pay for itself rather than switching on a
   tiny numerical difference.
4. HiTec preference: express a concentration preference without pretending it
   is an absolute law.

The model must still select exactly three industries and pass the loss rule.
Those are not optional.

## Canonical recommendations

| Profile | Verdict | Recommendation | Evidence |
|---|---|---|---|
| Growth | Switch | HiTec + Hlth + Utils | Same winner in all three scenario sets; beats the current tilt in 89% of 500 bootstrap resamples. |
| Balanced | Review | Do not automatically switch | The proposed portfolio wins in the base case but flips under the supplied return stress; the score margin is very small. |
| Risk-sensitive | Keep | NoDur + Hlth + Utils | Current tilt wins across the scenarios; it passes the loss rule in 76% of bootstrap resamples. |

The responsible conclusion is not “technology always wins.” It is:

- Growth has the strongest case for switching.
- Balanced requires committee review because the result is fragile.
- Risk-sensitive investors should keep the current tilt under the model's
  assumptions.

## The quantum contribution

Each industry is represented by one binary decision:

- 1 means selected.
- 0 means not selected.

That gives six binary variables, corresponding to six qubits in the circuit.
The project uses QAOA, the Quantum Approximate Optimisation Algorithm. QAOA
alternates between:

1. A cost operation that gives better portfolios a better quantum phase.
2. A mixer operation that moves probability between candidate portfolios.

The main circuit starts in a Dicke state, a balanced superposition of states
with exactly three selected industries. Its XY mixer preserves the
three-selection rule. This is called a constraint-preserving or
rule-preserving approach.

The comparison baseline uses an X mixer and penalty terms. Invalid portfolios
are discouraged by a large penalty instead of being structurally excluded.

QAOA parameters are chosen by a classical optimiser, and the circuit is
sampled repeatedly. The quantum output is decoded and checked against the
same finance rules. The exact classical enumeration remains the answer key.

## IBM and simulator wording

Use this exact wording:

> “The experiment runs locally with IBM’s Qiskit Aer simulator.”

Do not say:

- IBM quantum hardware
- IBM cloud execution
- a production IBM Quantum service
- quantum advantage

No IBM hardware or IBM cloud Runtime execution was performed. The project
demonstrates a Qiskit/Aer quantum workflow on a local simulator.

## Why the result is credible

The pipeline:

1. Loads and validates the frozen data.
2. Separates estimation data from holdout data.
3. Enumerates all 20 candidates exactly.
4. Builds the optimisation objective.
5. Runs QAOA experiments with multiple seeds and depths.
6. Decodes samples and checks feasibility.
7. Compares quantum results with the exact answer.
8. Tests return stress, covariance stress, bootstrap stability, sensitivity, and
   holdout behaviour.
9. Presents Keep, Switch, or Review rather than hiding uncertainty.

## Limitations to state clearly

- Only 60 estimation months are available.
- The 2015–2019 technology rally strongly influences the estimates.
- Six US industries are not a complete pension-fund universe.
- Equal weights and exactly three holdings are simplifications.
- Switching cost is a proxy, not a measured transaction-fee schedule.
- Historical scenarios are not forecasts.
- The holdout is after-the-fact evidence, not a live prediction.
- The QAOA experiment is not evidence of quantum speedup or quantum advantage.
- Human investment-committee review is still required.
