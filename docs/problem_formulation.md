# Problem formulation: Allocation route (Route C)

**Status:** route decided on 16 Oct 2026 (allocation). **Client: German government, as the public fund of the planned
"gesetzliche Kapitalrente"** (see §1.3 and §11).
This is the single reference for *what exactly we solve*. Background: `docs/problem.md`; method and
prototype: `docs/route_c.md`. All numbers below were recomputed from `Database/returns_6_industries_monthly.csv`.

---

## 1. The decision

### 1.1 Question
At the review date **31 Dec 2019**, for each investor profile: **which three of six industry portfolios
should the model portfolio hold, and is moving away from the current holding (NoDur, Hlth, Utils) justified,
given the binding rules, the switching cost and the uncertainty in the estimates?**

### 1.2 Possible outcomes per profile
| Verdict | Meaning |
|---|---|
| **Keep** | Current portfolio is the admissible optimum, or no alternative beats it robustly |
| **Switch to X** | X is the admissible optimum in the base case **and** under the supplied stresses |
| **Review** | Optimum changes under a supplied stress / plausible estimate change, or evidence is missing. The committee must decide with a stated belief |

### 1.3 Who decides, who is affected
- **Client: German federal government.** The fund is the public, KENFO-like fund for the gesetzliche Kapitalrente
  (Alterssicherungskommission, Recommendation 28, June 2026; `docs/client_germany.md`).
- **Decision-maker:** the fund's independent investment committee of external experts.
- **Users:** the fund's portfolio managers.
- **Loss bearers:** the insured, by age cohort.
- **Approver of the framework:** the legislator / BMAS. The supervisor is still an open question.
- **Profiles are chosen actively by each insured person** (growth / balanced / risk-sensitive), not by age. This avoids unequal treatment between generations (team decision 16 Oct). Default for non-choosers: balanced (proposal, open).
- **Supervision (researched):** not yet fixed by law. KENFO, the named template, is under the Rechtsaufsicht of the BMWE (in agreement with BMF and BMUV, EntsorgFondsG §13); the BMF issues its investment guidelines (§9, VAG §124 principles); BaFin is not named. If the fund sits inside the GRV, the DRV Bund is supervised by the Bundesamt für Soziale Sicherung. DORA likely does not apply to the foundation itself (not a listed financial entity), but it does to its external managers and ICT providers. This is our reading, to confirm.
- **What the 3-of-6 choice means:** the commission demands the broadest possible diversification, so we model the
  **satellite (tilt) sleeve** of each cohort's equity portfolio. The core stays a broad index; the satellite tilts
  into 3 of 6 sectors at equal weights. The 3-of-6 decision is therefore a *tilt decision*, not the whole portfolio.
  The parameters for this are in §11.

---

## 2. Sets, data and estimates

| Symbol | Definition | Value |
|---|---|---|
| I | industries | {NoDur, Manuf, Enrgy, HiTec, Hlth, Utils}, n = 6 |
| K | number of holdings | 3, equal weights 1/K, no shorting or borrowing |
| M | profiles | {growth, balanced, risk-sensitive} |
| r_t,i | observed monthly return, t = 1…60 | Jan 2015 – Dec 2019 (estimation only) |
| μ̂ | sample mean of r | e.g. HiTec 1.51%, NoDur 0.65% per month |
| Σ̂ | sample covariance (T − 1) | 6×6 |
| x⁰ | current holding | (1,0,0,0,1,1) → NoDur, Hlth, Utils |
| S | scenario sets | base (60 months at 1/60), return stress (HiTec −0.5pp), covariance stress (corr 25% → +1) |

Jan 2020 – Dec 2024 is **never** used for estimation. It is used only for after-the-fact evaluation (§7).

---

## 3. Decision variables

`x_i ∈ {0,1}` for i ∈ I (1 = industry i is held). Weights `w = x / K`.

---

## 4. Objective (tradeable preferences)

```
minimise   f_m(x) = − μ̂ᵀw  +  λ_m · wᵀΣ̂w  +  τ · ½‖w − w⁰‖₁  +  κ · max(0, w_HiTec − cap_m)
                    return     risk penalty    switching cost      cap preference
```

| Parameter | growth | balanced | risk-sensitive | Meaning |
|---|---|---|---|---|
| λ_m | 1 | 5 | 20 | risk aversion |
| τ | 0.002 | 0.002 | 0.002 | cost per unit of one-way turnover. A reluctance-to-switch proxy (tax + trading), **not** a measured fee |

With K = 3, the turnover term is linear: `½‖w − w⁰‖₁ = (1/3) Σ_{i ∉ current} x_i`.

---

## 5. Constraints (binding, never traded against the objective)

| ID | Rule | Formula | Treatment |
|---|---|---|---|
| **H1** cardinality | exactly 3 holdings | Σ x_i = 3 | **structural**: Dicke start + XY mixer (baseline: penalty) |
| ~~H2~~ concentration cap | **now a preference (team decision 16 Oct)**: see the objective term κ·max(0, w_HiTec − cap_m) | with equal weights: κ·(1/3 − cap_m)·x_HiTec if cap_m < 1/3 (linear, QUBO-friendly) | moved to the objective; κ is swept |
| **H3** loss tolerance | P(one-month loss > L_m) ≤ α_m | (1/60) Σ_t 1[−wᵀr_t > L_m] ≤ α_m, with L = 8% / 5% / 3%, α = 10% | **post-check, exact.** A scenario probability is not a quadratic function of x, so it is not QUBO-encodable without heavy auxiliary bits |

**Admissible set:** `A_m = { x : H1, H3 }`. The cap is a preference since 16 Oct.
**Boundary convention:** "≤" with tolerance 1e-12, as in the organiser code. This decides the
proposal at exactly 10.00% for the risk-sensitive profile, so the convention must be stated in the pitch.

**Size of the admissible set (base case):**

| Profile | H1 only | + H2 | + H3 | Binding rule that matters |
|---|---|---|---|---|
| growth | 20 | 20 | **20** | none |
| balanced | 20 | 20 | **19** (Manuf+Enrgy+Hlth fails H3 at 11.67%) | barely |
| risk-sensitive | 20 | 10 | **2** (NoDur+Hlth+Utils, NoDur+Manuf+Utils) | **H2 and H3 decide almost everything** |

Implication: for the risk-sensitive profile the *rules*, not the optimiser, make the decision. That is a
finding to present, not a weakness to hide.

---

## 6. Solution method

### 6.1 Exact reference (classical)
Enumerate all 20 portfolios, apply H1–H3 and rank by f_m. This gives `x*_m` and serves as the answer key for every quantum run.

### 6.2 QUBO
Over the free qubits F_m (I minus capped industries):
```
f_m(x) = Σ_i d_i x_i + Σ_{i<j} Q_ij x_i x_j + c
d_i  = −μ̂_i/3 + λ_m Σ̂_ii/9 + τ(1 − 2x⁰_i)/6
Q_ij = 2 λ_m Σ̂_ij / 9
c    = τ · Σ_i x⁰_i / 6          (keep the offset when reporting energies)
```
Ising form for the circuit: `x_i = (1 − z_i)/2`.

### 6.3 Quantum solver
- **Main:** QAOA with **Dicke-state initialisation** (uniform over admissible-cardinality states) and an
  **XY ring mixer**, p = 1…4 layers.
- **Baseline (organiser):** X mixer + penalty `P(Σx − 3)² + P·x_HiTec`, with P larger than the full cost range.
- Classical optimiser: COBYLA / Nelder-Mead, ≥ 10 seeds per setting. Objective: expected cost, plus CVaR-α as a variant.
- Decoding: most probable sample that satisfies H1–H3. If the top sample fails H3, take the best sample that passes.

### 6.4 Verification metrics (against §6.1)
P(optimum), feasible-sample fraction, normalised expected gap, top-sample-correct. Median and spread over seeds.
Prototype results (`scripts/qaoa_mixer_comparison.py`, ideal statevector, p = 3):
- risk-sensitive: P(opt) 0.58 (ours) vs 0.03 (baseline)
- growth: 0.43 vs 0.05
- balanced: hard for both, because of a near-tie
- 100% feasible samples with ours, vs 56–99% for the baseline

---

## 7. Robustness design (required: base + ≥ 2 supplied changes)

| Category | Change | Range |
|---|---|---|
| (a) Financial assumptions | supplied return stress, supplied covariance stress | as given |
| | HiTec mean shift δ | −1.0 … +0.5 pp/month |
| | bootstrap of the 60 months | ≥ 500 resamples |
| | Ledoit–Wolf Σ, shrunk μ | on / off |
| (b) Mandate choices | λ | 0.5 … 50 (log grid) |
| | τ | 0 … 0.01 |
| | L_m, α_m, cap_m | ± one step around the supplied values |
| (c) Computational representation | mixer (XY vs X + penalty), p, seeds, shots, objective (mean vs CVaR), penalty P | — |

**Known so far (base estimates):**

| Profile | Base | Return stress | Cov stress | Break-even |
|---|---|---|---|---|
| growth | switch → HiTec+Hlth+Utils | same | same | — |
| balanced | switch → HiTec+Hlth+Utils | **keep** | switch (near-tie with NoDur+HiTec+Utils) | δ ≈ −0.37pp/month; τ ≈ 0.0057; λ ≈ 11.2 |
| risk-sensitive | keep | keep | keep | decided by H2/H3 |

**Provisional verdicts:**
- growth: **Switch**
- balanced: **Review** (flips under a supplied stress)
- risk-sensitive: **Keep**

### After-the-fact evaluation (2020–24, not a decision input)
- Proposal wealth 1.86 vs current 1.38.
- Both breached the 3%-loss frequency (20% of months vs 10% tolerance).
- We use this to test decision *rules* (hold vs 2pp / 5pp threshold rebalancing), not to pick winners in hindsight.

---

## 8. What counts as a justified conclusion
1. The recommended portfolio satisfies H1–H3. This is verified exactly, not taken from the solver.
2. It is optimal for f_m in the base case **and** under ≥ 2 supplied changes. Otherwise the verdict is "review", with the break-even belief stated.
3. The quantum result matches the exact reference, or the mismatch is reported with its metrics.
4. The recommendation states who gains and who loses, and the one condition under which it should not be followed.

---

## 9. Assumptions and limits (stated, not hidden)
- 60 monthly observations. μ̂ is dominated by the 2015–19 tech rally (estimation risk).
- Equal weights and K = 3 are product simplifications.
- τ is a single proxy for tax and costs, which in reality differ per investor.
- H3 uses an empirical scenario model (1/60 per month). 2020–24 shows it understated tail risk.
- US industry data as a stand-in for an EU / German client.
- Ideal simulation for the prototype; Qiskit with shots next.
- No liquidity or ESG data. Related questions get the verdict "review".
- No quantum-advantage claim: 20 options are enumerable instantly. The quantum contribution is a verified, rule-preserving encoding.

---

## 10. Inputs the mid-hackathon change may touch
λ_m, τ, L_m, α_m, cap_m, the stress definitions, the estimation window. All live in one config. A change
triggers: exact re-enumeration, then QAOA rerun, then a diff of verdicts and break-evens.

---

## 11. Parameters to model (client: German government / Kapitalrente fund)

Status codes:
- **G** = given by the task data or organiser config
- **K** = from the commission report (principle, no number)
- **A** = our documented assumption
- **O** = open, to clarify with the GTPP advisers or the team

### 11.1 Investment universe and data
| Parameter | Value | Status | Note |
|---|---|---|---|
| Sectors I | NoDur, Manuf, Enrgy, HiTec, Hlth, Utils | G | US data as a stand-in for a global fund |
| Estimation window | Jan 2015 – Dec 2019 (60 months) | G | Decision date 31 Dec 2019 |
| Evaluation window | Jan 2020 – Dec 2024 | G | Never an input |
| Estimators μ̂, Σ̂ | sample mean, sample covariance | G | Ledoit–Wolf / shrunk μ as sensitivity (A) |
| Current tilt x⁰ | NoDur, Hlth, Utils | G | Existing defensive tilt |

### 11.2 Cohort mandates (lifecycle model, "no guarantees")
| Parameter | growth (< 55) | balanced (55–65) | risk-sensitive (65–75) | Status |
|---|---|---|---|---|
| Risk aversion λ | 1 | 5 | 20 | G (values), A (cohort mapping) |
| Loss threshold L | 8% | 5% | 3% | G |
| Tolerance α | 10% | 10% | 10% | G |
| Sector cap (HiTec) | 100% | 35% | 20% | G (values). K: implements "broadest diversification" |
| Cohort age bounds | < 55 | 55–65 | 65–75 | A (from AP7: 100% equity to 55, de-risking 56–75) |
| Equity share of the cohort | ~100% | falling | ~33% at 75 | K/A (AP7 reference). Context only, not optimised |

### 11.3 Government / commission-specific parameters
| Parameter | Value | Status | How it enters the model |
|---|---|---|---|
| **Satellite share s** | e.g. 10% of the cohort's equity | A/O | Scales the tilt's impact. The core is a broad index (commission: max diversification) |
| **Switching cost τ** | 0.002 per unit one-way turnover (= 20 bp) | G (value), A (meaning) | **A public fund pays no capital-gains tax**, so τ = trading costs only |
| **Cost cap** | ≤ 0.10% p.a. effective | K | Turnover budget: at τ = 20 bp, ≤ 0.5 one-way turnover per year. The proposal (1/3 turnover) uses 6.7 bp, i.e. 2/3 of a year's budget |
| **Exclusion set E** | default ∅. Test case: Enrgy | K/O | Commission: no sector bans, only "unethical" after case review. Modelled as x_i = 0 (qubit removed). Its cost is reported |
| **New contributions** | 2% of wages, +0.5pp/yr from 2028 | K | Inflows can fund a tilt without selling. Lowers the effective τ (sensitivity τ → 0) |
| Independence / governance | external committee | K | Not a model parameter. Shapes the Decision Card (who approves, who can override) |
| Transparency | "also in difficult market phases" | K | Report the stress results and 2020–24 hindsight openly |
| Compute provider | local simulation | A | DORA / sovereignty: a public fund depending on a foreign quantum cloud = responsibility question (O) |

### 11.4 Computational parameters
| Parameter | Range | Status |
|---|---|---|
| Mixer | XY ring (main), X + penalty (baseline) | A |
| Layers p | 1–4 | A |
| Seeds | ≥ 10 per setting | A |
| Shots | 4096 (Qiskit port) | A |
| Optimiser | COBYLA, Nelder-Mead | A |
| Objective | expected cost; CVaR-α (α = 0.1–0.25) | A |
| Penalty P (baseline only) | > full financial cost range | G (organiser rule) |

### 11.5 Open questions for this client
- Is a satellite tilt acceptable at all under the commission's principles, and at what size s?
- Who supervises the public fund (BaFin, BMF, or a special statute like KENFO)? Does DORA apply?
- Do cohort-specific tilts create unequal treatment between generations inside one social insurance?
- Is the 20% sector cap a binding rule (diversification principle) or a committee preference?

---

## 12. Algorithms

| Model part | Algorithm | Role | Tool |
|---|---|---|---|
| Estimation | sample mean / covariance; Ledoit–Wolf; bootstrap (≥ 500) | inputs + estimation uncertainty | numpy / scikit-learn |
| **Exact reference** | enumeration of all 20 (or 10 / 2 admissible) | answer key, optimality certificate | numpy |
| Exact (scalable check) | MIQP (Gurobi) or CP-SAT with linearised x_i x_j | shows the problem is solved exactly at any realistic size | OR-Tools |
| Classical heuristics | greedy / top-k by score; 1-swap local search; simulated annealing; tabu | classical comparison; greedy shows where "best single sectors" fail | numpy / dwave-neal |
| Quantum-inspired | simulated bifurcation | legitimate entry per syllabus | `simulated-bifurcation` (optional) |
| **Quantum, main** | **QAOA with Dicke start + XY ring mixer** (cap / exclusions = qubits removed) | rule-preserving search; 100% admissible-cardinality samples | Qiskit 2.2.3 + qiskit-algorithms + Aer |
| Quantum, baseline | QAOA with X mixer + penalties (organiser) | comparison: shows the cost of penalties | Qiskit |
| Quantum, variants | CVaR-QAOA; warm start from x⁰; SamplingVQE | sharpen the near-tie (balanced); "start from what we hold" | Qiskit |
| Quantum, discussion only | quantum annealing (D-Wave); Grover adaptive search | scaling / provider-dependency discussion | — |
| Loss rule H3 | exact scenario count (main); optional IQAE (from the risk route) | binding post-check. IQAE would show the estimation uncertainty around 10.00% | numpy / Qiskit |
| Sensitivity | grid sweeps (λ, τ, δ, s), bisection for break-evens, bootstrap selection frequency | robustness section | numpy |
| Evaluation | buy-and-hold vs 2pp / 5pp threshold rebalancing, 2020–24 | rule test, not a pick test | numpy (notebook replay) |

**Team decision (shared doc): the main comparison is quantum vs quantum.** Ours (Dicke + XY) vs the organiser's penalty QAOA, plus quantum variants. Enumeration is only the answer key; classical heuristics are optional context.

**Minimum viable set for the pitch:**
1. enumeration (answer key)
2. simulated annealing (optional classical context)
3. QAOA X + penalty (organiser baseline)
4. **QAOA Dicke + XY (ours)**
5. sensitivity sweeps + bootstrap

Optional: CVaR-QAOA, IQAE for H3, CP-SAT scaling demo.
