# Paths, mandates and quantum models: explained

Companion to `docs/problem.md` (the problem), `docs/routes.md` (route requirements) and
`docs/solution_paths.md` (build plan). This file answers three questions:
1. What does each path *mean*, and what really separates them?
2. What is a mandate, which mandates are possible, and how does each translate into math?
3. Which quantum models exist for those math forms, and which fits which path and mandate?

All numbers come from `Database/returns_6_industries_monthly.csv`, estimation window 2015–19.

---

## Part 1: What the paths mean

### 1.1 One decision, three different questions

All paths serve the **same decision** (retain NoDur/Hlth/Utils, or switch to HiTec/Hlth/Utils, or something
else). They differ in **which question about that decision the quantum computer answers**.

| | Path A: Risk | Path B: Circuit | Path C: Allocation |
|---|---|---|---|
| Question | *How likely is a bad month for this portfolio?* | *Does this portfolio satisfy the rules?* | *Which portfolio should we hold?* |
| Analogy | Thermometer: measures one quantity | Checklist / gatekeeper: yes, no, or "can't tell" | Search engine: looks through all options |
| Input | **One fixed portfolio** + scenario table + loss threshold | **Condition flags** (or quantities) for one portfolio + the mandate's logic | **All 20 portfolios** implicitly + μ, Σ, mandate weights |
| Output | A **probability with a confidence interval** | A **logical verdict** (admit / reject / review) | A **selected portfolio** (bitstring) + how often it was sampled |
| Math object | Expectation over a distribution: `P = Σ p_s·1[loss_s > L*]` | Boolean function: `admit = cap ∧ risk ∧ evidence` | Optimisation: `min_x xᵀQx`, x ∈ {0,1}⁶ |
| Quantum primitive | State preparation + oracle + **amplitude estimation** | **Reversible logic** (CX, Toffoli, MCX) | **Variational sampling** (QAOA / VQE) or annealing |
| What stays classical | Scenario losses, which scenarios breach | Computing the flags (in design A) | Estimating μ, Σ; choosing λ, penalties |
| Where uncertainty sits | Estimation error (shots) vs scenario model vs threshold | Failed condition vs **missing evidence** | Estimate sensitivity: does the pick change with μ, λ, τ? |
| Decision-maker gets | "Within / breach / unresolved" for a *given* trade | "This trade meets / fails / cannot yet be judged against your rules" | "Under your mandate, hold X; it flips if…" |
| When the mandate changes | Threshold/tolerance change → re-estimate | Logic or threshold change → new truth table | Weights change → new Hamiltonian → new optimum |

**Key differences:**
- **A and B evaluate a portfolio someone else proposed. C proposes one itself.**
- A gives a **number** (graded), B a **category** (yes/no/unknown), C a **choice** (one of 20).
- A's quantum part is **estimation**, B's is **logic**, C's is **optimisation**. These are three different
  families of quantum algorithms (Part 3).

### 1.2 The same case through all three paths

Case: **risk-sensitive client, proposal (HiTec/Hlth/Utils)**.

- **Path A:** encode 60 months (6 qubits), mark the 6 months where the proposal lost more than 3%, and estimate
  P with IQAE. The estimate is ≈ 10.00% with a CI of up to ±1pp (ε = 0.01), and the tolerance is 10%, so the CI overlaps the limit and
  the result is **unresolved**. One month (−3.10%) decides it, and under both stresses it is a **breach** (11.67%, 15%).
  *Message: "The loss rule is borderline; the evidence can't settle it."*
- **Path B:** flags are cap_ok = 0 (33% > 20%), risk_ok = borderline, evidence_ok = 1. The AND gate gives
  **reject**, *regardless of the risk flag*, because the cap is binding.
  *Message: "Rejected by a binding rule; the return advantage is irrelevant."*
- **Path C:** with the cap encoded (HiTec excluded), the optimum over the remaining 10 portfolios is the
  **current portfolio**. Without the cap, the proposal is still worse at λ = 20, because the break-even
  is λ ≈ 11.2. *Message: "Hold the current portfolio; it is optimal even before the rule bites."*

Three paths, three angles, same conclusion (retain). The *justifications* differ, and that is the point:
the decision-maker gets a different kind of evidence from each.

### 1.3 How they combine (Path D)

```
       B: Gatekeeper            C: Search                A: Risk check
  [binding rules per mandate] → [best admissible pick] → [P(loss) of the pick with CI]
   cap, exclusions, evidence     QAOA / Grover on QUBO     IQAE on scenario table
          ↓ reject / review              ↓ pick                ↓ within / breach / unresolved
                         ───────────────→ Decision record + "flips if…" ──→ Decision Card
```
The task asks for **one** focused contribution. In D, only one block is quantum; the others are classical
versions of the same idea.

---

## Part 2: Mandates

### 2.1 What a mandate is

A mandate is the client's instruction set for managing their money (MiFID II suitability: objectives,
risk tolerance, ability to bear losses). It has three kinds of components:

| Component | Meaning | Can it be traded off? | Example here |
|---|---|---|---|
| **Objective / preference** | What the client wants more or less of | Yes | Return vs variance via λ; change reluctance τ |
| **Binding restriction** | What must never happen | **No** | HiTec cap; loss-probability tolerance |
| **Process rule** | How and when to act | Rule-dependent | Rebalance at 2pp / 5pp drift; required evidence |

The task's central demand is to make this distinction **visible in the model**, not to hide it in one score.

### 2.2 The three supplied mandates, interpreted

| | Growth-oriented | Balanced | Risk-sensitive |
|---|---|---|---|
| Typical client | Long horizon, can absorb losses (e.g. young saver, endowment) | Mixed goals (e.g. standard private-banking client) | Short horizon / low loss capacity (e.g. near retirement, liability-driven) |
| λ (risk weight) | 1: variance barely matters | 5: moderate | 20: variance dominates |
| Loss threshold L* | 8% in one month | 5% | 3% |
| Tolerated P(loss > L*) | 10% | 10% | 10% |
| HiTec cap | none (100%) | 35% → a 1/3 position allowed | **20% → a 1/3 position forbidden** |
| Optimum (base) | Proposal | Proposal (fragile) | Current |
| Binding rule actually bites? | No | No | **Yes, the cap** |

Note: with equal 1/3 weights, a cap behaves like **inclusion / exclusion**: a cap below 33% excludes the
asset, a cap at or above 33% has no effect. Caps only become "continuous" with unequal weights (§2.4).

### 2.3 Potential additional mandates (for sensitivity, the policy hook or the mid-hackathon change)

These are **our** ideas, not supplied. Each tests a different kind of rule. Values recomputed on 2015–19:

| Mandate idea | Rule (math) | Current | Proposal | What it would do |
|---|---|---|---|---|
| **CVaR-limited** ("bad months must not be too bad on average") | avg loss in worst 10% of months ≤ c | **4.62%, best of 20** | 5.08%, rank 4 | Favours current; tail-focused alternative to variance |
| **Drawdown-limited** (pension-like) | max peak-to-trough loss ≤ d | **−8.1%, best of 20** | −10.2%, rank 3 | Favours current; path-dependent rule |
| **Benchmark-relative** (fund tracking a broad index) | tracking error vs equal-weight 6-industry proxy ≤ t | 1.51%, **worst of 20** | 1.23%, rank 12 | Pushes *away* from current: low risk ≠ close to benchmark |
| **Diversification** | avg pairwise correlation ≤ ρ | 0.41, rank 5 | **0.37, rank 3** | Favours proposal: Utils/Hlth/HiTec move least together |
| **Exclusion / ESG-style** (e.g. no fossil energy, EU SFDR Art. 8 type product) | x_Enrgy = 0 | — | — | No effect on any optimum (Enrgy is never chosen), but a clean binding-rule example |
| **Turnover-limited** | ≤ 1 position change per decision | 0 changes | 1 change | Proposal allowed, any 2-swap forbidden |
| **Liquidity-required** | min liquidity score | **no data** | **no data** | Forces **review**: the "missing evidence" case the task asks for |
| **Income-oriented** | dividend yield ≥ y | not in our data | — | Would need extra French data; out of scope, but a good "what we can't assess" point |

Takeaways:
- **Different risk definitions pick different portfolios.** CVaR and drawdown favour current; the
  diversification and benchmark-relative views favour moving. That makes the choice of risk measure a
  *mandate* decision, which is exactly the task's point about priorities.
- Two of these (liquidity, income) **cannot be assessed** with the supplied evidence. That is a feature
  for the responsibility note, not a gap to fill with invented numbers.

### 2.4 How each mandate rule becomes math, and what that means for quantum

This is the bridge to Part 3: **the mathematical type of a rule decides which quantum model can handle it.**

| Rule type | Examples | Form in x ∈ {0,1}⁶ | QUBO-friendly? | Best-fitting path |
|---|---|---|---|---|
| Linear preference | expected return, change penalty τ | `cᵀx` | ✅ native (diagonal) | C |
| Quadratic preference | variance λ·wᵀΣw, tracking error | `xᵀQx` | ✅ native (off-diagonal) | C |
| Exact count | "exactly 3 industries" | `Σx = 3` | ✅ penalty `P(Σx−3)²`, or a constraint-preserving mixer | C |
| Exclusion / cap (equal weights) | HiTec cap 20%, Enrgy exclusion | `x_i = 0` | ✅ trivial: **remove the qubit** | B, C |
| Linear inequality | "≤ 1 change", "at most 1 of {Manuf, Enrgy}" | `aᵀx ≤ b` | ⚠️ needs **slack bits** or a penalty | B, C |
| Quadratic inequality | vol ≤ cap, TE ≤ t | `xᵀQx ≤ b` | ⚠️ slack bits + precision; often better as a filter | B (flag), C (post-check) |
| Scenario probability | P(loss > L*) ≤ 10%, CVaR ≤ c | non-polynomial in x | ❌ not QUBO-able directly | **A** (estimate), B (flag) |
| Path-dependent | max drawdown, drift rebalancing | depends on the return sequence | ❌ | classical simulation; B (flag) |
| Evidence requirement | liquidity data present | not a function of x | ❌ | **B** (evidence qubit) |

Rule of thumb: **preferences → C; probabilistic risk limits → A; hard rules and evidence → B.**
The supplied mandates contain all three types, which is why the task offers three routes.

**Extension (unequal weights):** 2 bits per industry → weights {0, 1/6, 1/3, 1/2}. That is 12 qubits, plus the constraint
Σw = 1, which becomes an equality on weighted bits. Caps then become real linear inequalities. This is a credible
"scaling" extension for Path C, but optional.

---

## Part 3: Quantum models

### 3.1 The catalog

| Model | What it does | Problem form | Path | Qubits (our instance) | Notes |
|---|---|---|---|---|---|
| **QAOA (X-mixer + penalties)** | Alternates cost layer e^{−iγH_C} and mixer e^{−iβΣX}; a classical optimiser tunes γ, β; samples low-energy bitstrings | QUBO / Ising | C | 6 | The notebook's baseline. Penalties distort the landscape; infeasible samples; missed the optimum for risk-sensitive |
| **QAOA with XY mixer + Dicke start** (Quantum Alternating Operator Ansatz, Hadfield et al. 2019) | Starts in the uniform superposition of all weight-3 strings; the XY mixer swaps 1s and 0s, so exactly 3 always stay selected | QUBO **with exact cardinality** | C | 6 (5 with cap) | Feasible by construction; no P to tune; binding rule = structure. **Our main differentiator for C** |
| **CVaR-QAOA / CVaR-VQE** (Barkoutsos et al. 2020) | Optimises the average of the *best α%* of samples instead of the mean energy | QUBO | C | 6 | Converges to good bitstrings faster; easy switch in Qiskit (`aggregation=α`) |
| **Warm-start QAOA** (Egger et al. 2021) | Initial state biased towards a classical (relaxed) solution, e.g. the current portfolio | QUBO | C | 6 | Natural here: "start from what we hold" mirrors the change penalty |
| **SamplingVQE** (hardware-efficient ansatz) | Generic parametrised circuit (Ry + CZ), optimised like QAOA | QUBO | C | 6 | The Qiskit Finance tutorial uses it; less structure, more parameters |
| **Quantum annealing** (D-Wave) | Analog evolution from transverse field to problem Hamiltonian | Ising | C | 6 logical (+ embedding) | Needs an account / cloud, so not required. Talk about it, don't run it. DORA/provider dependency hook |
| **Simulated annealing / tabu** | Classical heuristics on the same QUBO | QUBO | C | — | The quantum-inspired / classical comparison the syllabus recommends |
| **Simulated bifurcation** (Goto et al. 2019) | Classical nonlinear-dynamics solver inspired by quantum bifurcation | Ising | C | — | Explicitly named in the syllabus as a legitimate quantum-inspired entry |
| **Grover search / Grover Adaptive Search** (Gilliam et al. 2021) | Amplifies bitstrings that pass an oracle; GAS repeatedly lowers a threshold to find the minimum | Oracle (B) or QUBO (C) | **B ↔ C** | 6 (B) / ~12–14 (GAS: 6 + value register) | Turns B's condition circuit into a *search*: "find all admissible portfolios". Quadratic speed-up in theory, irrelevant at 64 states. Say so |
| **Reversible logic** (CX, Toffoli, MCX, phase oracles) | Computes Boolean functions without information loss; ancillas uncomputed | Boolean | B | 5 (notebook) – ~12 (two qubits per condition + ancillas) | Exact and fully verifiable with a truth table |
| **Quantum comparator / arithmetic** (`IntegerComparator`, weighted adders) | Compares an encoded number with a threshold inside the circuit | Integer inequality | A, B | +n ancillas | "Compute inside the circuit" design; discretisation becomes an assumption |
| **Canonical QAE** (phase-estimation based) | Estimates amplitude a = P(event) with error O(1/M) | Expectation / probability | A | 7 + m evaluation qubits | Deeper circuits; textbook reference |
| **Iterative QAE (IQAE)** (Grinko et al. 2019) | Same goal without phase estimation, using Grover powers + classical statistics | Probability | **A** | 7 | The notebook's choice; best default |
| **Maximum-Likelihood QAE (MLAE)** (Suzuki et al. 2020) | Fixed Grover powers + likelihood fit | Probability | A | 7 | Simple alternative; nice robustness comparison |
| **QAE for VaR / CVaR** (Woerner & Egger 2019) | Bisection over the threshold (VaR); controlled-rotation payoff (CVaR) | Quantile / tail mean | A | 7–9 | Natural extension for a CVaR-limited mandate (§2.3) |

**Further reading only (scale, not our 6-asset instance):** Pauli correlation encoding (Soloviev &
Krompiec 2026: many binary variables in few qubits); quantum stochastic walks (Chang et al. 2026);
decomposition pipelines (Acharya et al. 2025). Use them in the pitch's "what would scale" slide.
**Qamomile** (mandatory reading) is a *tool*, not a model: write the QUBO once and send it to different
SDKs and backends. Good for Path C reproducibility and the "provider dependency" argument.

### 3.2 Which model for which mandate rule

| Mandate rule | Path A model | Path B model | Path C model |
|---|---|---|---|
| Return vs variance (λ) | — | flag from classical score | **QAOA / XY-QAOA / CVaR-QAOA** |
| Exactly 3 industries | — | count check (adder + comparator) | **Dicke + XY mixer** (exact) or penalty |
| HiTec cap / exclusion | — | Toffoli AND on cap flag | **drop qubit** (exact) |
| Change penalty τ | — | preference flag | linear term in H_C; or warm start from current |
| P(loss > L*) ≤ tol | **IQAE / MLAE** on scenario table | flag (with an "unresolved" state) | post-check of the pick (classical or IQAE) |
| CVaR ≤ c | **QAE-CVaR** (Woerner & Egger) | flag | post-check |
| Drawdown ≤ d | — (path-dependent) | flag | post-check |
| Liquidity evidence | — | **evidence qubit → review** | — |
| Find all admissible | — | **Grover over 6 selection qubits** | — |

### 3.3 Practical guidance

- **Everything here runs on a laptop simulator** (Qiskit 2.2.3 + qiskit-algorithms 0.4.0 + Aer, as in the
  notebook). No hardware or account needed.
- **Verification is always possible:** 64 bitstrings / 60 scenarios / 2ⁿ truth-table rows. Every quantum
  output must be shown next to the exact value (AGENTS.md rule).
- **No speed-up claims.** At this size, enumeration is instant. The value is: correct encoding, binding
  rules represented structurally, uncertainty made visible, and a clear statement of what would need to
  hold for the method to matter at scale.
- **Choose a model for a reason the jury can follow:** "XY mixer because the client's '3 industries'
  rule must never be violated"; "IQAE because it gives a confidence interval without phase-estimation depth";
  "Toffoli logic because rules must be checkable line by line by a compliance officer".

---

## One-page summary

- **Path A (Risk)** = *measure* the loss risk of a given trade → amplitude estimation → "within / breach / unresolved".
- **Path B (Circuit)** = *check* a trade against rules and evidence → reversible logic (+ Grover) → "admit / reject / review".
- **Path C (Allocation)** = *search* for the best portfolio under preferences → QAOA (XY mixer) → "hold X; flips if…".
- **Mandates** mix preferences (→ C), probabilistic limits (→ A) and hard rules / evidence (→ B). Our extra
  mandate ideas show that **the choice of risk measure changes the answer**: CVaR and drawdown favour the current portfolio;
  diversification and benchmark tracking favour switching.
- **Quantum models** split into three families: optimisation (QAOA family, annealing), logic and search
  (Toffoli, Grover), and estimation (QAE family). The math type of the mandate rule decides the family.
