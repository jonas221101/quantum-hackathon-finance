# Technical Implementation Guide

## 1. Purpose and scope

This guide describes the canonical implementation of the Quantum Finance
allocation prototype. It is intended for engineers, reviewers, and presenters
who need to reproduce the results or explain exactly what the code does.

The system answers a deliberately small allocation question:

> Select exactly three of six industries, at equal weights, for a satellite
> tilt, subject to a profile-specific monthly-loss rule.

The system is **not** a complete pension optimiser, a live trading system, or
evidence of quantum advantage.

The canonical implementation is under `src/qhf/` and is orchestrated by
`scripts/run_all.py`. The root-level `src/analysis.py`, `src/qaoa.py`, and
`app.py` are an earlier integrated application surface retained for the
Streamlit demo. They should not be treated as a second source of truth for the
formal model. When numbers conflict, use `src/qhf/`, `results/canonical/`, and
the formal documents in `docs/`.

## 2. Reproducibility contract

### Inputs

The frozen input is:

`Database/returns_6_industries_monthly.csv`

`src/qhf/data.py` validates the SHA-256 checksum in `src/qhf/config.py` before
analysis. Do not edit the CSV in place. If the data changes, update the
checksum deliberately and regenerate every result.

### Windows

The estimation window is January 2015 through December 2019, inclusive:

- 60 monthly observations
- used to estimate means, covariance, scenarios, rankings, and bootstrap
  evidence

The evaluation window is January 2020 through December 2024, inclusive:

- 60 monthly observations
- never used to choose the portfolio
- used only for after-the-fact holdout reporting

### Determinism

`Config.seed = 2026`. The seed is combined with profile, layer, and run
indices so that QAOA starts and sampling streams are reproducible. Fixed seeds
do not make a quantum optimisation deterministic in the conceptual sense; they
make this experiment repeatable.

### Canonical commands

```text
pip install -e .
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/run_all.py run --canonical
```

Outputs are written below `results/canonical/`:

- `summary.json`: headline results and configuration
- `exact_rankings.csv`: all portfolios and scenario/profile scores
- `quantum_runs.csv`: individual QAOA seed results
- `quantum_summary.csv`: median and min/max seed summaries
- `sensitivity.csv`: robustness and computational comparisons
- `decision_map_*.csv`: parameter-grid decisions
- `figures/`: generated evidence figures

## 3. Data model

The six industries are ordered as:

```text
NoDur, Manuf, Enrgy, HiTec, Hlth, Utils
```

A portfolio is a binary vector:

```text
x = (x_NoDur, x_Manuf, x_Enrgy, x_HiTec, x_Hlth, x_Utils)
```

where `x_i = 1` means that industry is selected. The current portfolio is:

```text
NoDur + Hlth + Utils = (1, 0, 0, 0, 1, 1)
```

The proposal is:

```text
HiTec + Hlth + Utils = (0, 0, 0, 1, 1, 1)
```

The cardinality rule is:

```text
sum(x_i) = K = 3
```

The weight vector is equal-weighted:

```text
w_i = x_i / K
```

There are `C(6, 3) = 20` cardinality-valid portfolios. The exact solver in
`src/qhf/exact.py` enumerates them and is the authoritative answer key.

## 4. Financial quantities

Let `r_t` be a row of six monthly industry returns.

### Estimated moments

For the estimation data:

```text
mu = column means
Sigma = sample covariance matrix, ddof = 1
```

For a portfolio `x`:

```text
portfolio_return_t = r_t · w
mean_return = mu · w
variance = wᵀ Sigma w
volatility = sqrt(variance)
```

The code stores returns as decimals. For example, `0.015` means 1.5% per
month. Figures intended for people must convert these values to percentage
points and label the unit explicitly.

### Loss rule

For profile `m`, let `L_m` be the monthly loss threshold and `alpha_m` the
allowed breach probability:

```text
loss_t = -(r_t · w)
breaches = count(loss_t > L_m)
admissible if breaches / 60 <= alpha_m
```

The implementation uses an integer boundary:

```text
allowed_breaches = floor(alpha_m * number_of_observations + 1e-9)
```

This avoids floating-point ambiguity at exactly 10%. For the canonical
profiles, the thresholds are 8% / 5% / 3%, with 10% tolerance.

The loss rule is binding. It is checked in `portfolio.py`, in exact
enumeration, and again after QAOA decoding.

## 5. Objective function

For profile `m`, the lower-is-better objective is:

```text
f_m(x) =
    - muᵀw
    + lambda_m * wᵀ Sigma w
    + (tau / H) * turnover(x)
    + kappa * max(0, w_HiTec - cap_m)
```

Definitions:

- `lambda_m`: risk-aversion weight, 1 / 5 / 20
- `tau`: switching-cost proxy, 0.002
- `H`: holding horizon, 1 month in the organiser convention
- `turnover(x) = 0.5 * ||w - w0||_1`
- `kappa`: HiTec concentration preference, 0.01
- `cap_m`: preferred HiTec weight, 100% / 35% / 20%

The HiTec cap is a **soft preference** in the canonical implementation. It
adds cost when exceeded; it does not make a portfolio inadmissible. The exact
binding rules are cardinality and the loss rule.

This distinction must appear in tables and visualisations:

- **Admissible**: exactly three holdings and passes the loss rule.
- **Cap-respecting**: also stays below the soft HiTec preference.
- **Optimal**: lowest objective among admissible portfolios.

Do not label a cap violation “infeasible” unless discussing a separate
experiment that explicitly makes the cap binding.

## 6. Exact classical reference

`src/qhf/exact.py` evaluates every three-of-six vector. For each profile and
scenario it:

1. Calculates return, covariance risk, turnover, cap penalty, and objective.
2. Calculates loss breaches and allowed breaches.
3. Removes portfolios that fail the binding loss rule.
4. Sorts the remaining portfolios by objective.
5. Applies deterministic tie-breaking by portfolio index.

This is computationally trivial for six industries. It is retained because a
quantum experiment must have an independent answer key.

## 7. Scenarios and decision logic

`src/qhf/scenarios.py` creates:

- `base`: the original estimation observations
- `return_stress`: HiTec returns shifted down by 0.5 percentage points per
  month
- `covariance_stress`: correlations mixed 25% toward 1 while preserving the
  intended covariance construction

`src/qhf/decision.py` turns the scenario and bootstrap evidence into a
committee-facing verdict.

### Switch

The same target must be optimal in all three scenarios, improve over the
current holding by the configured margin, and satisfy the required bootstrap
evidence gates.

### Keep

The current holding must remain the defensible optimum across scenarios and
pass the relevant bootstrap admissibility gate.

### Review

Anything else. Review is the default hold-and-escalate outcome when a stress
flips the winner, evidence is weak, or no admissible portfolio exists.

The canonical results are:

- Growth: Switch to `HiTec + Hlth + Utils`
- Balanced: Review
- Risk-sensitive: Keep `NoDur + Hlth + Utils`

## 8. QUBO construction

`src/qhf/qubo.py` converts the financial objective into:

```text
f(x) = c + sum_i d_i x_i + sum_{i<j} Q_ij x_i x_j
```

For `K = 3`:

```text
d_i =
    -mu_i / K
    + lambda * Sigma_ii / K²
    + (tau / H) * (1 - 2*x0_i) / (2K)
    + kappa * (1/K - cap)       if i is capped and cap < 1/K

Q_ij = 2 * lambda * Sigma_ij / K²

c = (tau / H) * sum_i x0_i / (2K)
```

Excluded industries, if configured, are removed from the free-qubit list.
The current-portfolio constant is retained so reported energies remain
consistent.

### Ising conversion

The circuit uses `x_i = (1 - z_i) / 2`, producing:

```text
H = offset + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j
```

`to_sparse_pauli_op()` emits the corresponding `Z` and `ZZ` terms for Qiskit.
The constant is a global phase in the cost circuit and does not affect
probabilities.

### Penalty baseline

The baseline adds:

```text
P * (sum_i x_i - K)²
```

This expands into altered linear terms, pairwise terms, and a constant. It is
used only for the penalty X-mixer baseline. The financial objective itself
should not be confused with the penalty-augmented baseline objective.

## 9. QAOA circuit implementation

The relevant files are `src/qhf/circuits.py`, `src/qhf/kernel.py`, and
`src/qhf/qaoa.py`.

### Dicke-plus-XY method

1. `dicke_circuit(m, K)` prepares an equal superposition of all weight-`K`
   bitstrings using the Bärtschi–Eidenbenz split-and-cyclic-shift procedure.
2. Each layer applies the Ising cost unitary.
3. Each layer applies an XY ring mixer using `XXPlusYYGate`.
4. Every mixer factor preserves Hamming weight, so exactly three selected
   industries remain structurally preserved.

### Penalty X method

1. Apply Hadamards to create a uniform superposition over all `2^m` states.
2. Apply the penalty-augmented cost unitary.
3. Apply single-qubit `RX(2 beta)` mixers.
4. Invalid cardinality states remain possible but are discouraged by the
   penalty.

### Cost layer

For each layer, `cost_layer()` applies:

- `RZ` rotations for `h_i Z_i`
- `RZZ` rotations for `J_ij Z_i Z_j`
- normalisation by the energy range over cardinality-valid states

The XY ring is Trotterised edge by edge. It is not claimed to be the exact
simultaneous exponential of the full ring Hamiltonian.

## 10. Parameter optimisation and sampling

For each profile, method, depth, and seed:

1. Draw shared initial points for fair method comparison.
2. Use COBYLA with the configured `maxiter`, `rhobeg`, and `tol`.
3. Run `starts_per_seed` restarts.
4. Select the best restart using the optimisation objective seen by that run.
5. Evaluate the final statevector probabilities.
6. Sample the Qiskit circuit with `StatevectorSampler` and the configured
   number of shots.

Canonical defaults include depths `p = 1, 2, 3`, 10 seeds, 5 starts per seed,
500 maximum COBYLA iterations, and 4096 final measurement shots.

The optional CVaR variant optimises the mean cost of the best probability
mass fraction (`alpha = 0.25`). It is reported as a separate method, not
silently combined with the ordinary expectation objective.

## 11. QAOA metrics and decoding

`run_metrics()` reports:

- `p_opt`: statevector probability of the exact admissible optimum
- `p_opt_given_valid`: optimum probability conditional on exactly three
  holdings
- `p_top2`: probability mass on the best two admissible answer-key states
- `h1_mass`: probability of exactly three holdings
- `h3_mass`: probability of passing the binding loss rule
- `cap_mass`: probability of respecting the soft HiTec preference
- `financial_gap`: expected financial objective gap from the optimum
- `sampled_p_opt`: measured-shot probability of the exact optimum
- `decoded_is_optimum`: whether the most frequent admissible measured sample is
  the exact optimum

Decoding does not accept the most frequent bitstring blindly. It chooses the
most frequent sample that satisfies the binding cardinality and loss rules.
This is essential for the penalty baseline and for any noisy or finite-shot
experiment.

## 12. Robustness and holdout analysis

The pipeline performs:

- 500 bootstrap resamples of the estimation months
- return-shift sensitivity
- risk-aversion sensitivity
- switching-cost sensitivity
- cap-penalty sensitivity
- loss-threshold and tolerance robustness
- exclusion and holding-horizon checks
- QAOA depth and seed comparisons
- exact versus finite-shot optimisation comparison
- 2020–2024 holdout evaluation

Bootstrap results are evidence about historical-sample stability, not
probabilities of future returns. The holdout is hindsight, not a forecast.

## 13. Visualization contract

Every chart must answer one question and state its units.

### Risk/return map

- x-axis: monthly volatility in percent
- y-axis: mean monthly return in percent
- one point per 3-of-6 portfolio
- current and base-case recommendation highlighted
- other candidates muted
- do not imply that “higher return and lower volatility” alone determines the
  answer; admissibility and profile objective still apply

### Scenario table

Show scenario name, winner, admissible count, and whether the winner matches
the base. A “stable” bar must be labelled as a count or fraction of supplied
scenarios, never as a probability of future performance.

### Bootstrap chart

Use shares from 0 to 100%, with the 70% decision threshold clearly marked.
Separate:

- candidate beats current
- candidate passes the loss rule
- current passes the loss rule

Do not combine these into one “confidence” number.

### QAOA comparison

Always label:

- ideal statevector versus finite-shot results
- profile
- circuit depth `p`
- median over seeds
- min–max or uncertainty range
- exact optimum versus valid/admissible sample mass

Do not call `P(opt)` “confidence.” It is a circuit measurement probability
under the specified simulator and parameters.

### Holdout chart

Use “after-the-fact holdout” in the title. Do not place holdout performance next
to training performance without a visible label.

## 14. Tests and acceptance checks

Run:

```text
python -m pytest -q
```

Important invariants:

- exactly 20 three-of-six portfolios are enumerated
- Dicke state support has exactly three selected bits
- XY mixing preserves Hamming weight
- loss-rule boundary at exactly 10% is deterministic
- QUBO energies agree with the direct objective
- QAOA decoded outputs obey binding rules
- canonical results are reproducible with fixed seeds

Before publishing a figure or video, verify:

1. Units are visible.
2. Current, proposal, and recommendation are not conflated.
3. Soft cap preference is not shown as a binding feasibility rule.
4. Scenario stability is not described as a forecast probability.
5. IBM Aer local simulation is identified accurately.
6. The exact classical answer key is visible.
7. No quantum-advantage claim appears.

## 15. Recommended presentation wording

Use:

> “We use exact enumeration as the auditable answer key and compare it with a
> constraint-aware QAOA experiment running locally on IBM’s Qiskit Aer
> simulator.”

Avoid:

- “The quantum computer found the answer faster.”
- “IBM hardware selected the portfolio.”
- “The model predicts the winning sector.”
- “The chart proves the recommendation.”
- “The quantum probability is investor confidence.”
