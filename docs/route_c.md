# Route C in detail: Allocation with QAOA

Client framing: a **digital asset manager (robo-advisor)** reviewing its ETF model portfolios for three
MiFID II risk profiles. Background: `docs/problem.md`, `docs/paths_mandates_models.md`.
Prototype: `scripts/qaoa_mixer_comparison.py` (numpy statevector, no Qiskit needed).

---

## 1. The idea in one paragraph

Each risk profile has a model portfolio with **three equal-weight sector slots**. At the review date
(31 Dec 2019) the committee asks: *which three sectors should each profile hold, and is moving away from
the current slots (NoDur, Hlth, Utils) worth the tax and trading cost?* We write that question as a
**binary optimisation problem** (6 yes/no variables). We solve it with a **quantum algorithm (QAOA)** that is
built so the product rules (exactly 3 slots, sector cap) can *never* be violated. We verify it against the
exact answer for all 20 portfolios. Then we show **when the recommendation flips**.

---

## 2. Client mapping (robo-advisor)

| Model element | Meaning for the robo-advisor |
|---|---|
| x_i ∈ {0,1} | Sector ETF i is in the model portfolio |
| Σx = 3, weights 1/3 | Product rule: 3 slots, equal weights (explainable, cheap to rebalance) |
| growth / balanced / risk-sensitive | Risk profiles from the suitability questionnaire (Wachstum / Ausgewogen / Konservativ) |
| λ = 1 / 5 / 20 | How strongly each profile penalises variance |
| HiTec cap 100% / 35% / 20% | Concentration limit per risk class. For conservative clients it forbids a 1/3 tech slot |
| Loss threshold + 10% tolerance | Risk-class limit: P(monthly loss > 8% / 5% / 3%) ≤ 10% |
| τ = 0.002 × turnover | Switching cost: trading costs + **realised capital-gains tax** (26.375% on gains in Germany) |
| Decision-maker | The robo-advisor's investment committee (approves model-portfolio changes) |
| Loss bearers | Retail clients in each profile. Supervisor: BaFin (MiFID II, ESMA suitability guidelines) |

---

## 3. The model, step by step

### 3.1 Inputs (all from the supplied data, estimation window 2015–19)
- μ: mean monthly return per sector (6 numbers).
- Σ: 6×6 sample covariance.
- x⁰ = (1,0,0,0,1,1): current model portfolio.
- Profile parameters (λ, cap, loss threshold, tolerance) and τ.

### 3.2 Objective: what "better" means
For a selection x with weights w = x/3:

```
score(x) = μᵀw            expected monthly return              (more is better)
         − λ · wᵀΣw       risk penalty, scaled by profile      (less risk is better)
         − τ · turnover   switching cost vs current portfolio  (fewer changes is better)
```
QAOA minimises **cost(x) = −score(x)**. Turnover = ½ Σ|w_i − w⁰_i|. With 3 slots it is
(number of replaced slots)/3, which is **linear in x**: Σ_{i ∉ current} x_i / 3.

### 3.3 Constraints: what is *not allowed*
| Rule | Type | How we enforce it |
|---|---|---|
| Exactly 3 slots | hard (product rule) | **Dicke state + XY mixer** keeps exactly three 1s (baseline: penalty) |
| Sector cap | hard (risk class) | Cap < 1/3 means that sector is impossible, so **remove its qubit** (baseline: penalty) |
| P(loss > L*) ≤ 10% | hard (risk class) | Not expressible as a QUBO (scenario probability), so **checked exactly after** selection. If the pick fails, take the next best that passes |
| Missing evidence (e.g. liquidity) | process | Verdict "review", outside the optimisation |

This split matters: **binding rules are structure or checks, never a price the optimiser can pay.**

### 3.4 QUBO form
Expanding cost(x) with x_i² = x_i gives `cost(x) = Σ_i d_i x_i + Σ_{i<j} Q_ij x_i x_j + c`:
- `d_i = −μ_i/3 + λ Σ_ii/9 + τ(1 − 2x⁰_i)/6` (return, own risk, switching)
- `Q_ij = 2λ Σ_ij/9` (joint risk of sectors i and j)
- `c = τ · Σx⁰ / 6` (constant; keep it when reporting energies)

Baseline only (penalty version): add `P(Σx − 3)²` and `P · x_HiTec` (if capped), with P larger than the
whole range of financial costs, so a violation can never pay off.

Ising form for the circuit: `x_i = (1 − z_i)/2`, z_i ∈ {+1, −1}. This gives single-qubit Z terms and two-qubit ZZ terms.

### 3.5 The quantum algorithm (QAOA)
One QAOA layer = **cost step** + **mixer step**, repeated p times. A classical optimiser tunes the angles.

```
start state ──► [ e^{−iγ₁·Cost} ] ──► [ e^{−iβ₁·Mixer} ] ──► … p layers … ──► measure ──► bitstrings
                   phase by cost           moves amplitude          ▲
                   (RZ, RZZ gates)         between candidates       └── classical optimiser adjusts γ, β
```

| | Baseline (organiser notebook) | **Ours** |
|---|---|---|
| Start state | uniform over all 64 bitstrings (H gates) | **Dicke state**: uniform over the 20 (or 10) valid portfolios only |
| Mixer | X mixer (RX on each qubit): flips single bits, so it leaves the valid set | **XY ring mixer** (RXX + RYY on neighbours): swaps a 1 with a 0, so the count stays 3 |
| Cardinality | penalty P(Σx−3)² | **impossible to violate** |
| Sector cap | penalty | **qubit removed** (5 qubits, 10 options for the conservative profile) |
| Infeasible samples | many | **none** |
| Qubits | 6 | 6 (5 with cap) |

Reference: Hadfield et al. (2019), Quantum Alternating Operator Ansatz. In Qiskit, the Dicke state can be
prepared with a known circuit, and the XY mixer is a `PauliEvolutionGate` of (XX+YY)/2 terms.

### 3.6 Decoding and verification
- Read the sampled distribution. Pick the **most probable feasible** bitstring, and report the whole distribution.
- Compare with **exact enumeration** (20 portfolios). Metrics:
  - P(optimum)
  - feasible fraction
  - gap of the expected cost above the optimum (normalised)
  - whether the top sample is the optimum
- Repeat across seeds and depths p. Never one run.

---

## 4. Prototype result (already run)

`python scripts/qaoa_mixer_comparison.py Database/returns_6_industries_monthly.csv`
(ideal statevector, expected-cost objective, 20 Nelder-Mead starts per setting, seed 7, about 2 min)

Exact optima:
- growth: HiTec+Hlth+Utils (proposal)
- balanced: HiTec+Hlth+Utils (proposal)
- risk-sensitive: NoDur+Hlth+Utils (current)

| Profile | p | P(opt) X+penalty | P(opt) **Dicke+XY** | Feasible X+penalty | Feasible **Dicke+XY** | Gap X+penalty | Gap **Dicke+XY** |
|---|---|---|---|---|---|---|---|
| growth | 3 | 0.05 | **0.43** | 99% | **100%** | 0.57 | **0.10** |
| balanced | 3 | 0.14 | 0.07 | 90% | **100%** | 0.51 | **0.13** |
| risk-sensitive | 3 | 0.03 | **0.58** | 56% | **100%** | 2.47 | **0.08** |

Random-guess baselines: P(opt) = 0.05 with 20 options, 0.10 with 10 options.

**What this shows**
1. **The constraint-preserving design wins clearly.** It gives 100% valid portfolios and 4–30× smaller cost gaps.
   For the conservative profile, P(optimum) is 0.58 vs 0.03, and the top sample is correct at every depth.
2. **The penalty baseline wastes probability on invalid portfolios.** For conservative clients, 44% of the
   samples break a product rule at p = 3.
3. **Balanced is hard for *both* methods.** Its top two portfolios almost tie (score 0.00487 vs 0.00462).
   At low depth QAOA cannot separate them. **The quantum difficulty sits exactly where the financial
   decision is fragile.** That is a strong pitch point: the sampler's uncertainty mirrors the decision's uncertainty.
4. Results are not monotonic in p (local optimiser). That is a known QAOA issue, and the reason for multiple seeds.

**Next steps for the prototype:**
- port it to Qiskit (circuits, shot noise, Aer)
- use a CVaR objective to sharpen the near-tie (Barkoutsos et al. 2020)
- add a warm start from the current portfolio
- compare with simulated annealing.

---

## 5. Sensitivity program (the financial core, mostly classical)

| Analysis | Question | Known so far |
|---|---|---|
| **Decision map λ × HiTec shift** | Which portfolio wins for each risk appetite and belief about tech? | Proposal vs current break-even at λ ≈ 11.2; balanced flips at HiTec −0.37pp/month |
| **Decision map λ × τ** | How expensive must switching be to stay? | Balanced stays put if τ > 0.0057 (≈ 3× the base) |
| **Supplied stresses** | Return stress, covariance stress | Balanced flips under the return stress; the others are stable |
| **Bootstrap (≥ 500 resamples of the 60 months)** | How often is each portfolio optimal? | To do: "balanced picks the proposal in N% of resamples" |
| **Shrinkage** | Ledoit–Wolf Σ, shrunk μ | To do |
| **Loss-tolerance check** | Does the pick satisfy P(loss > L*) ≤ 10%? | Proposal: 0% / 5% / (capped) → OK for growth and balanced |
| **Tax heterogeneity** | Clients with large unrealised NoDur gains | Higher effective τ → may flip balanced clients individually |
| **Mid-hackathon change** | New threshold or input | Config change → rerun → diff of what flipped |

The quantum solver is rerun on each changed setting and must still match the exact answer.

---

## 6. Hold-out evaluation (2020–24, never a decision input)
- Proposal: wealth 1.86. Current: 1.38. Max drawdown −21% vs −17%.
- Both lost more than 3% in 20% of months, double the estimated rate.
- Test **rules**, not picks: buy-and-hold vs 2pp / 5pp threshold rebalancing (notebook replay function).

---

## 7. What is ours vs the organiser notebook

| Notebook (baseline) | Ours |
|---|---|
| X mixer + penalties, p = 2, 3 seeds | Dicke + XY mixer, cap as a removed qubit, p = 1…4, ≥ 10 seeds |
| Reports most probable feasible sample | Reports P(opt), feasible %, gap, vs exact optimum |
| Misses the optimum for risk-sensitive in all seeds | Top sample correct at all depths (prototype) |
| Sensitivity table only | Break-even maps, bootstrap, tax heterogeneity |
| Generic mandates | Robo-advisor risk profiles, τ grounded in tax and costs |

---

## 8. Decision Card (draft, robo-advisor)

> **Recommendation:** Conservative profile keeps NoDur/Hlth/Utils. Growth profile switches NoDur → HiTec.
> Balanced profile switches **only if** the committee believes tech's monthly edge over staples exceeds
> 0.37pp, otherwise it keeps.
> **Who gains / loses:** growth clients gain expected return; clients with large unrealised gains pay tax on
> the switch; all switched clients carry more sector concentration.
> **Confidence:** high for conservative (binding cap) and growth (robust to the stresses); low for balanced (near-tie,
> flips under the return stress, and the quantum sampler also can't separate it).
> **Do not follow if:** tech's estimated edge is driven by a short rally you don't expect to continue.
> **AI baseline:** the reference solution's QAOA missed the conservative optimum; we replaced penalties with a
> constraint-preserving design and verified every result against exact enumeration.

---

## 9. Work plan for Route C

| Package | Content | Who |
|---|---|---|
| WP1 Backbone | data, config (profiles), exact enumeration, decision record, diff tool, tests from notebook numbers | Engineering |
| WP2 Quantum | port the prototype to Qiskit: Dicke prep, XY mixer, CVaR objective, seeds × depths, metrics | Quantum |
| WP3 Finance | decision maps, break-evens, bootstrap, shrinkage, loss check, tax heterogeneity | Finance |
| WP4 Policy | GTPP: herding across clients, explainability, tax fairness, BaFin / DORA, responsibility note | Policy |
| WP5 Story | findings note (≤ 2 p), Decision Card, slides, decision log (incl. AI deviations) | All |

**Sprint day 2 (16 Oct) target:** problem + client, architecture (WP1–WP5), the prototype table above as the
first verified result, and the plan to 30 Oct.

---

## 10. Honest limits (say them before the jury does)
- 20 options: enumeration is instant. QAOA is **demonstrated and verified, not needed** at this size. The value
  is correct encoding of product rules and a path to larger, personalised problems.
- Ideal simulation: no hardware noise, no shot noise yet (Qiskit port adds shots).
- Estimates from 60 months; the tech rally drives the result. Hence the bootstrap and break-evens.
- Equal weights and 3 slots are product simplifications; real robo-portfolios have more slots and unequal weights.
- US sector data for a German / EU client: a teaching stand-in.
- τ as a single number simplifies very different client tax situations.
