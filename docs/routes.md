# The three routes in detail

Built from the task sheet (`Task/`), the named sources (`sources/`) and the supplied package in `Database/`.
The mandate values are now known (see −1 below). Where the route sections still say *(placeholder)*,
use the supplied values instead.

---

## −1. Supplied package (`Database/`): what is in it, and what we checked

**Files:** `returns_6_industries_monthly.csv` (120 × 6, decimal monthly returns), `README.md`, and
`Finance_Six_Industries_Verified.ipynb`. The notebook embeds the config, the helpers and the recorded outputs.
`instance_config.json`, `finance_core.py`, `results/` and `requirements.txt` from the README are **not** in
the folder, but the notebook contains everything it needs.

**Our checks (independent recomputation, 2026-10-15):**
- SHA-256 of the CSV = `083dbb43…f811f5`, the same as the notebook manifest.
- The CSV equals our own French extract (`sources/data/`) to within 1e-16. Data confirmed.
- The README's risk numbers reproduce exactly (see table below).

**Mandates** (organiser teaching parameters, *not* regulation):

| Mandate | risk coeff λ | loss threshold L* | tolerance P(loss > L*) | HiTec weight cap |
|---|---|---|---|---|
| growth_oriented | 1 | 8% | 10% | 100% |
| balanced | 5 | 5% | 10% | 35% |
| risk_sensitive | 20 | 3% | 10% | **20%**, so a 1/3 HiTec position is inadmissible |

Other parameters:
- Change penalty: 0.002 × one-way turnover. This is a preference, not a fee.
- Drift-rebalancing thresholds: 2pp and 5pp.

**Scenario model:** 60 estimation months, each with probability 1/60. Two stresses:
- **Return stress:** HiTec −0.5pp per month.
- **Covariance stress:** correlations moved 25% towards +1, with means and variances kept, via a linear transform of the centred data.

Both stresses are hypothetical, not new data.

**P(one-month loss > L*), empirical** (recomputed by us; identical to the README):

| Scenario | Mandate (L*) | Current | Proposal |
|---|---|---|---|
| base | growth (8%) | 1.67% | 0.00% |
| base | balanced (5%) | 3.33% | 5.00% |
| base | risk_sensitive (3%) | 8.33% | **10.00%**, exactly at the tolerance |
| return stress | risk_sensitive (3%) | 8.33% | **11.67%**, breach |
| cov stress | balanced (5%) | 5.00% | 6.67% |
| cov stress | risk_sensitive (3%) | 8.33% | **15.00%**, breach |

**Exact optimum** of `mean − λ·var − 0.002·turnover` with the cap enforced, over all 20 portfolios:

| Scenario | growth | balanced | risk_sensitive |
|---|---|---|---|
| base | proposal (HiTec+Hlth+Utils) | proposal | **current** |
| return stress | proposal | **current** ← flips | current |
| cov stress | proposal | proposal (barely: 0.00412 vs 0.00406 for NoDur+HiTec+Utils) | current |

**Key takeaways for us**
1. **Balanced is the swing mandate.** Its decision flips under the HiTec return stress. That is the most
   interesting sensitivity story: find the break-even HiTec shift / λ / change penalty.
2. **Risk-sensitive + proposal sits exactly on the boundary** (10.00% vs 10% tolerance). The decision
   depends on `≤` vs `<`, and on 1 of 60 months. IQAE cannot resolve it, so the notebook reports it as
   "unresolved". It is a good example of a decision driven by a single observation.
3. **The reference QAOA often misses the exact optimum.** It uses p=2, 3 seeds and 100 COBYLA evaluations,
   and reports the most probable feasible bitstring. For risk_sensitive, none of the 3 seeds returns the
   current portfolio (the exact optimum). The returned volatilities (4.16%, 3.87%, 3.02%) match Manuf+Enrgy+Hlth,
   NoDur+Manuf+Enrgy and Manuf+Hlth+Utils. One growth seed lands on NoDur+Enrgy+Utils.
   **This is room to improve:** a Dicke start + XY mixer, more layers, CVaR-QAOA or more optimizer budget,
   and report the approximation ratio and P(optimum) against the 20-portfolio enumeration.
4. The notebook was executed under `/opt/codex/...`, so it is **probably AI-generated**. It may be (or resemble)
   the "AI assistant baseline" the task says to inspect rather than adopt. Treat it that way: verify,
   critique, and record in the decision log where we deviate.
5. The notebook already implements all 3 routes (IQAE with 7 qubits, a 5-qubit 3-Toffoli condition circuit,
   and the QUBO with a penalty larger than the full energy range). **Our contribution must go beyond re-running it.**
   Options per route are in the sections below.

---

## 0. First look at the data (exploration only)

`python scripts/extract_six_industries.py sources/data/10_Industry_Portfolios.csv sources/data/six_industries_vw_monthly_2015_2024.csv`

Estimation window 2015-01 to 2019-12 (60 months), monthly, value-weighted:

| Industry | mean / month | vol / month | worst month |
|---|---|---|---|
| NoDur | 0.65% | 3.22% | −11.31% |
| Manuf | 0.86% | 4.17% | −9.79% |
| Enrgy | 0.02% | 6.02% | −13.06% |
| HiTec | **1.51%** | 4.49% | −8.82% |
| Hlth | 0.87% | 4.21% | −10.12% |
| Utils | 0.68% | **3.04%** | −5.27% |

Equal-weight portfolios of three industries:

| Portfolio | mean | vol | worst month | rank by mean (of 20) | rank by vol (of 20) |
|---|---|---|---|---|---|
| **Current**: NoDur + Hlth + Utils | 0.73% | **2.71%** | −8.11% | 12 | **1 (lowest)** |
| **Proposal**: HiTec + Hlth + Utils | 1.02% | 3.05% | −7.08% | 2 | 5 |
| Highest mean: Manuf + HiTec + Hlth | 1.08% | 3.86% | −9.13% | 1 | 16 |

What this suggests already:
- **The current portfolio has the lowest variance of all 20.** A variance-focused mandate (risk-sensitive)
  will keep it under almost any setting. A return-focused mandate (growth) will want HiTec.
- The proposal adds about +0.29%/month (≈ +3.5%/yr) of estimated return for +0.34%/month of vol.
  Its worst month in the sample is *better* (−7.1% vs −8.1%). **The risk measures disagree**, and that
  is good material for the pitch.
- HiTec's 1.51%/month comes from the 2015–19 tech rally. This is the clearest case of **estimation risk**:
  shrink μ (e.g. towards the cross-sectional mean) and check whether the proposal survives.
- Utils has low correlation with everything (0.20–0.52). That is why it appears in both low-vol candidates.
- Hold-out data (2020–2024: COVID crash, 2022 drawdown) is there for evaluation afterwards, not for estimation.

---

## Route 1: Risk ("is the loss probability acceptable?")

**Decision question.** For a *fixed* allocation (current or proposal), is
`P(one-month loss > L*) ≤ α_mandate`? `L*` = declared loss threshold, `α_mandate` = acceptable probability
*(both placeholders, from the mandate files)*. A breach triggers a **review**. It does not say which trade to make.

### Financial side
- Input: the supplied **discrete scenario table**. Each scenario `s` has probability `p_s` and returns per
  industry. Portfolio return `R_s = Σ w_i r_{i,s}` with `w = 1/3` on held industries.
  Loss `ℓ_s = −R_s`.
- The scenario probabilities are **modelling inputs**, not derived from μ/Σ. Say this explicitly.
- Exact answer is trivial classically: `P = Σ_s p_s · 1[ℓ_s > L*]`. That value is the **verification
  reference**. Show it next to every quantum estimate.

### Quantum side (Woerner & Egger 2019)
1. **State preparation `A`**: load the distribution into `n = ⌈log₂ S⌉` qubits:
   `|ψ⟩ = Σ_s √p_s |s⟩`. For a small table use `StatePreparation` / `initialize` with amplitudes `√p_s`
   (pad to 2ⁿ with zeros). Generic loading costs O(2ⁿ) gates (paper, Sec. III). That is fine for a small
   table, but it is the honest bottleneck.
2. **Event marking `F`**: flip an objective qubit when scenario `s` is a breach:
   `|s⟩|0⟩ → |s⟩|1[ℓ_s > L*]⟩`.
   - *Option a (simple, transparent):* sort scenarios by loss so breaches are the indices `s ≥ k`. Then an
     **integer comparator** (`IntegerComparator(n, k)`) marks them. This matches the paper's VaR construction
     (comparator over a sorted, discretised loss).
   - *Option b:* multi-controlled X on each breach index. The breach list is computed classically, so say so.
   - Both encode a classical pre-computation. **Document which one you use.**
3. **Amplitude estimation**: `P(objective = 1) = a = P(breach)`. Use `IterativeAmplitudeEstimation`
   (`qiskit_algorithms`) with `EstimationProblem(state_preparation=A·F, objective_qubits=[obj])`,
   target precision `ε` and confidence `1 − α_conf`. Output: estimate `â` and confidence interval `[a_lo, a_hi]`.
   Error scales as O(1/M) in oracle calls vs O(1/√M) for Monte Carlo. That is the paper's quadratic
   speed-up claim. **We claim no advantage** (task rule). A tiny table is exact classically.
4. Optional extension: VaR by bisection on `L*` (paper Sec. II). CVaR (expected loss beyond VaR) by
   adding a controlled-Ry payoff, as in the paper.

### Decision rule: build in three states, not two
| CI vs mandate | Output |
|---|---|
| `a_hi ≤ α_mandate` | consistent with mandate |
| `a_lo > α_mandate` | breach → review |
| CI contains `α_mandate` | **inconclusive**: more shots/precision needed, or more evidence |

This directly addresses the responsibility point "separate computational uncertainty from financial uncertainty".

### Robustness (≥ 2 supplied changes)
- **Computational uncertainty:** vary `ε`, shots, seeds. Does the CI shrink around the exact value?
- **Scenario-model uncertainty:** rerun under the supplied alternative scenario settings. Does the
  *exact* probability cross `α_mandate`?
- **Mandate:** change `L*` / `α_mandate` per mandate. Which mandate flips first?
- Report a matrix: {current, proposal} × {base, alt scenarios} × {3 mandates} → consistent / breach / inconclusive.

### Deliverables
Working local example, documented state prep + event marking, `â` with CI, the exact reference, and an
interpretation of what it does and does not establish. It does **not** establish that the scenarios are
right, and it does not say what trade to make.

**Pros:** strong finance story (loss tolerance = binding mandate condition), clean verification, clear
uncertainty narrative. **Cons:** quantum part is a fixed recipe; value comes from interpretation.
Needs `qiskit`, `qiskit-algorithms`, `qiskit-aer`.

---

## Route 2: Circuit design ("when is the decision defensible?")

**Decision question.** Under which declared conditions is *retain* or *accept proposal* consistent with
a mandate? Build a reversible circuit that encodes the **logical relationship** between conditions.

### Choose a small condition set (example; tie each to the evidence)
| Flag | Condition | Type | Evidence |
|---|---|---|---|
| `c1` | portfolio vol ≤ vol cap | binding (risk-sensitive) | sample Σ, 60 m |
| `c2` | P(1-month loss > L*) ≤ α | binding | scenario table |
| `c3` | max weight per industry ≤ cap | binding | weights (always 1/3 here, so trivially true; say so) |
| `c4` | Δ expected return ≥ hurdle + switching cost | preference | μ estimate, change term |
| `c5` | improvement robust to μ shrinkage | preference | sensitivity run |

Values are *(placeholders)* until the mandate files arrive.

### Circuit design
- Logic: `accept_change = (c1 ∧ c2 ∧ c3) ∧ (c4 ∨ c5)` (example). Binding conditions combine with AND.
  Preferences combine with OR / majority, which allows trade-offs.
- Build with **CCX/Toffoli** (`sources/tutorials/ibm_ccxgate.md`):
  - AND of binding flags → chain of CCX onto ancillas (or one `mcx`).
  - OR of preferences = NOT(AND(NOT, NOT)) → `ccx` with `ctrl_state=0`, then X.
  - Final CCX writes `decision`.
  - **Uncompute** ancillas (apply the CCX chain in reverse) so the circuit is clean and reversible.
- **Fail vs missing evidence** (explicitly asked for): use **two qubits per condition**,
  `e_k` = evidence available, `s_k` = satisfied. Output three-valued: accept / reject / *cannot decide
  (evidence missing)*. Two output qubits: `decision`, `evidence_complete`.
- Two designs. Describe honestly which one you build:
  - **(A) Flag loading:** classical code computes `c_k`, the circuit receives them as X gates. The
    circuit is a verifiable logic gate, nothing more.
  - **(B) In-circuit comparison:** encode a quantity (e.g. discretised vol in k bits) and compare it inside
    the circuit with `IntegerComparator`. More "quantum", but discretisation error is now a modelling choice.

### Verification
- **Truth table:** loop over all 2ⁿ input basis states on `Statevector` / Aer, read outputs, compare with the
  Python boolean function. Must match 100%. Check that ancillas return to |0⟩.
- **Worked cases** (real numbers from §0): current vs proposal under each mandate.
  Example: risk-sensitive with vol cap 2.9%/month → current passes `c1` (2.71%), proposal fails (3.05%)
  → retain. Growth mandate without vol cap → proposal passes binding conditions, `c4` decides → accept.

### Robustness
Change a threshold (vol cap, `L*`, hurdle) → which flag flips → does the decision flip? Separate
*condition fails* from *evidence missing* (for example, no scenario table for an alternative setting).

### Deliverables
Annotated circuit diagram, input/output definitions, truth table, worked accepted and rejected cases.
The circuit shows whether declared conditions are satisfied. It does **not** show that they are
financially or ethically right.

**Pros:** lowest compute risk; very transparent; maps 1:1 to "binding vs preference", which the task
stresses. **Cons:** the quantum part is classical reversible logic (no superposition advantage). You must
own that openly, and the strength must come from the condition design.

---

## Route 3: Allocation ("which 3 of 6?")

**Decision question.** Which three industries to hold under a mandate (1/3 each, no shorts or borrowing),
and is moving away from the current holding worth it?

### Formulation
- `x_i ∈ {0,1}`, i ∈ {NoDur, Manuf, Enrgy, HiTec, Hlth, Utils}. Constraint `Σ x_i = 3`. Weights `w = x/3`.
- Objective (minimise):
  `−(1/3) μᵀx + q·(1/9) xᵀΣx + γ·Σ_{i∉current} x_i + P(Σx_i − 3)²`
  - `q` = mandate risk aversion (growth low, risk-sensitive high).
  - **Change term:** with exactly 3 selected, the number of replaced positions equals
    `Σ_{i∉current} x_i`, which is *linear* in x. `γ` = reluctance to switch, **not** a trading-cost model.
  - `P` = cardinality penalty. Expanded: diagonal `P(1−2K)`, off-diagonal `2P`, offset `PK²` (AGENTS.md §2).
- **Scale matters:** μ ≈ 0.01, Σ ≈ 0.001. Rescale (e.g. annualise or normalise) before choosing `P`.
  Otherwise the penalty swamps the objective. Sweep `P` and plot the feasible fraction.
- **Binding mandate limits** (e.g. vol cap) are quadratic inequalities. Adding them needs slack bits.
  Better: keep them as hard filters and **verify afterwards** that the chosen portfolio respects them.
  Say this, because the task explicitly asks you to verify that binding restrictions hold.

### Solving
1. **Exact enumeration** of the 20 feasible portfolios (supplied enumerator). This is the reference
   for feasibility and objective values, not a competitor.
2. **QAOA** on 6 qubits (Qiskit tutorial pattern: `PortfolioOptimization` → `QuadraticProgram` →
   `MinimumEigenOptimizer(QAOA(...))`, Aer sampler, COBYLA). Report the probability of the optimum,
   the feasible-sample fraction, and the energy gap to the exact value. Use reps p = 1..3 and **≥ 5 seeds**
   (median + spread).
3. **Better-justified variant:** start from the **Dicke state |D₆³⟩** (all weight-3 strings) and use an
   **XY mixer**. This preserves `Σx = 3` exactly, so no penalty `P` is needed and every sample is
   feasible. This is a strong "why this method" argument.
4. Optional quantum-inspired comparison: simulated annealing on the same QUBO.

### Robustness (the core of this route)
- **Financial assumptions:** shrink μ (James–Stein towards the mean, or set all μ equal → pure min-variance),
  Ledoit–Wolf Σ, a different window. Does the selection change?
- **Mandate:** sweep `q` over the three mandates and plot the selected set vs `q`. Find the **break-even q**
  where the current portfolio stops being optimal.
- **Change term:** sweep `γ`. At which `γ` is retaining optimal for each mandate?
- **Computation:** P, reps, shots, seeds. Does QAOA still find the exact optimum?
- **Out-of-sample:** realised 2020–24 performance of current vs proposal vs optimum. This is evaluation,
  not re-estimation.
- An unchanged answer is also a finding: "the current portfolio stays optimal for q > q* under all tested changes".

### Deliverables
Reproducible code, QUBO matrix with offset, exact vs QAOA table, sensitivity plots (selection vs q, γ,
shrinkage), and a check that binding restrictions hold.

**Pros:** best tooling (Qiskit tutorial almost directly applicable), matches pre-learning QUBO content,
rich sensitivity story. **Cons:** the most crowded route, so stand out through the change term, the Dicke/XY
mixer and the break-even analysis. QAOA on 6 qubits proves nothing about scale, so say it.

---

## Route comparison

| | Risk | Circuit | Allocation |
|---|---|---|---|
| Decision assessed | retain / accept a fixed portfolio | retain / accept under declared conditions | which 3 of 6 |
| Quantum part | state prep + comparator + amplitude estimation | reversible logic (CCX) | QAOA / Ising |
| Verification | exact Σ p_s 1[breach] | full truth table | 20-portfolio enumeration |
| Main uncertainty story | CI vs scenario model | fail vs missing evidence | stability under μ, q, γ |
| Code effort | medium | low | medium–high |
| Risk of "just ran a tutorial" | medium | low | high |

**Recommendation:** choose **Allocation** if the team has ≥ 2 people comfortable in Python. It gives the
most sensitivity results and the strongest pitch, with the current = lowest-vol vs proposal = higher-return
tension. Choose **Risk** if the team is stronger in finance than in coding. The three-state CI decision rule
is a distinctive contribution. Choose **Circuit** if time is short or the team is analytical.
Whatever you pick, borrow the others' ideas for robustness:
- Use the vol / loss flags from Circuit as hard checks in Allocation.
- Use the inconclusive state from Risk in any decision card.

---

## Responsibility hook (pick one and build it into the model)
- **Binding vs preference** (all routes): make it a structural element (hard filter, AND gate, mandate threshold), not a weight.
- **Estimation vs computational uncertainty:** Risk → three-state rule. Allocation → separate μ-shrinkage
  plots from seed/shot plots.
- **Model-validation evidence:** what would the bank's validation team need? Exact reference, reproducibility,
  hold-out test.
- **External provider dependency (DORA):** the whole pipeline runs locally. State what would change with a cloud QPU.
- **MiFID II suitability:** mandate = client profile. A switch requires a cost-benefit analysis, and the change term `γ` is a placeholder for it.
- Kop et al. (2024): principles 6 (inclusion), 7 (societal relevance) and 9 (responsibility: feedback loops) are the
  ones the course highlights.
