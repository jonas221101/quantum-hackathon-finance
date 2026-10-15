# Possible solution paths

Builds on `docs/problem.md` (what the problem is) and `docs/routes.md` (what each route requires).
This file answers: **what could our team actually build, how does it go beyond the organiser
notebook, and how do we get there by 30 Oct?**

Ground rule: the organiser notebook (`Database/Finance_Six_Industries_Verified.ipynb`) already solves
a basic version of every route. Re-running it scores nothing. Each path below names a **baseline** (reproduce
and verify the notebook) plus **differentiators** (our own contribution).

---

## 0. Shared backbone (needed by every path)

Build this first, ideally on sprint day 1. It is the part that lets us react when "the situation changes".

```
src/
  data.py        load CSV, split 2015–19 / 2020–24, checksum check
  config.py      mandates, stresses, penalties as one dataclass (from the notebook's CONFIG)
  scenarios.py   base / return stress / covariance stress tables (1/60 each)
  evaluate.py    exact metrics for any weight vector: mean, vol, P(loss > L*), cap check, score
  enumerate.py   all 20 portfolios × 3 mandates × 3 scenario sets → exact reference table
  decision.py    decision record: options, binding checks, preferences, verdict, reason, "flips if…"
  diff.py        rerun with a changed config → table of what changed and which condition flipped
  <route>.py     the quantum part (one of the paths below)
tests/           exact values from the notebook as regression tests (e.g. proposal P = 0.10 base)
```

Key design choices (these address the assessment directly):
- **Binding rules are filters, not weights.** `decision.py` separates `binding_ok` (cap, loss tolerance)
  from `preference_score`. A portfolio that fails a binding rule is never ranked.
- **Three-valued verdicts:** `accept` / `reject` / `review`. Review covers missing evidence or a result
  within the estimation uncertainty of a limit.
- **One config change → one diff.** When organisers change a threshold mid-hackathon, we run
  `python -m src.diff --set balanced.loss_threshold=0.04` and get the answer plus the explanation.
- **Break-even finder:** for any parameter (HiTec shift, λ, τ, L*), bisect where the verdict flips.
  This produces the "the one condition under which it should not be followed" line on the Decision Card.

---

## Path A: Risk route ("Is the loss probability acceptable, and how sure are we?")

**Our story:** "The risk-sensitive decision rests on a single month. We show which uncertainty
dominates: the quantum estimate, the scenario model, or the threshold choice."

### A0. Baseline
Reproduce the notebook's IQAE: 7 qubits (6 scenario + 1 event), ε = 0.01, α = 0.05, 2048 shots.
Check all 18 estimates against the exact encoded probabilities.

### A1. Differentiators
1. **Three uncertainty layers, side by side** (the core of the path):
   - *Computational:* IQAE confidence interval width vs ε / shots / seeds. Optionally run a noisy simulator
     (`qiskit-aer` noise model from a fake backend) to show hardware-like variation.
   - *Scenario model:* **leave-one-month-out (jackknife)** and **block bootstrap** over the 60 months.
     How much does P(loss > 3%) move when the sample changes slightly? (Expect ±1.7pp per month removed,
     far larger than the IQAE interval.)
   - *Threshold:* sweep L* from 2.5% to 3.5%. P is a **step function**: proposal goes 10% → 8.3% at L* = 3.10%.
   - Result graphic: three bars. "Quantum estimation: observed error ≈ 0.07pp, CI half-width ≤ 1pp (tunable via ε); scenario-sample error ≈ ±1.7pp;
     threshold choice ≈ ±2–5pp." Message: **the quantum part is not the bottleneck; the evidence is.**
2. **Proper three-state decision rule** (`within` / `breach` / `unresolved`), where "unresolved" uses the
   *combined* uncertainty, not just the IQAE interval. Proposal + risk-sensitive is the showcase.
3. **Honest oracle comparison:** design 1 (notebook): losses computed classically, breach indices marked
   with multi-controlled X. Design 2: sort scenarios by loss, then a single `IntegerComparator`
   (Woerner & Egger construction). Compare gate counts and depth, and state what each encodes.
4. **Extensions (pick ≤ 1):** VaR at 90% by bisection on the comparator; CVaR (expected loss beyond
   VaR, which matters because 2020–24 showed fat tails); or evaluating the 2020–24 scenarios as an
   explicitly *new information set*. That set gives 20% for both portfolios, so the tolerance would be breached.
5. **Resource statement:** queries IQAE needs vs classical Monte Carlo sampling for the same ε
   (O(1/ε) vs O(1/ε²)), with the caveat that a 60-row table is exact classically.

**Effort:** medium. **Strength:** clearest uncertainty narrative, best fit to "distinguish uncertainty in
the estimated probability from uncertainty about the scenario model". **Risk:** quantum part is a known
recipe, so all value comes from the analysis.

---

## Path B: Circuit route ("Under which conditions is the decision defensible?")

**Our story:** "We turned the client's mandate into explicit, checkable logic, separating rules from
preferences and *failed* from *unknown*, and used it to search the decision space."

### B0. Baseline
Reproduce the notebook's 5-qubit / 3-Toffoli circuit (risk_ok ∧ policy_ok ∧ evidence_complete) and its
8-row truth table.

### B1. Differentiators
1. **Richer, finance-grounded condition set** (each tied to evidence and a type):

   | Condition | Type | Evidence | Missing evidence when… |
   |---|---|---|---|
   | tech weight ≤ cap | binding | weights | never |
   | P(loss > L*) ≤ tolerance (beyond the uncertainty) | binding | scenario table | stress table not available |
   | return gain ≥ change penalty | preference | μ, τ | — |
   | gain survives return stress | preference | stress run | stress not run |
   | liquidity adequate | binding | **none in data** | always → forces `review` |

   The liquidity row is deliberate: the README says liquidity "needs additional evidence". Showing that
   the circuit *withholds admission* for missing evidence, rather than failing it, is exactly what the task asks for.
2. **Two qubits per condition** (`evidence`, `satisfied`) and **three-valued output**
   (`admit` / `reject` / `review`). Binding conditions are combined with AND (Toffoli / `mcx`). Preferences are combined with
   a **majority / k-of-n** gate, so they can be traded off. Every ancilla is uncomputed, and inputs are preserved.
3. **Both designs, compared honestly:** (a) flags loaded from classical calculation; (b) one condition
   computed *inside* the circuit (e.g. tech weight from the 6 selection bits via a comparator), with the
   discretisation choice stated.
4. **Make the logic useful with Grover search:** feed the 6 portfolio-selection qubits into the condition
   oracle, then use **Grover amplification to find admissible portfolios** among the 64 bitstrings
   (20 valid). This connects the circuit route to the allocation question without QAOA, and gives
   superposition a role. It must be stated honestly: admissibility flags per portfolio are precomputed lookups.
5. **Worked cases** for all 3 mandates × current / proposal, plus a "missing-evidence" case and a
   "boundary" case (proposal at 10.00%).

**Effort:** low–medium. **Strength:** most transparent; maps 1:1 onto "binding vs preference" and
MiFID suitability, and is easiest for the policy team to engage with. **Risk:** can look "too simple". The Grover
extension and condition design must carry it.

---

## Path C: Allocation route ("Which 3 of 6, and how stable is that choice?")

**Our story:** "The answer depends on the client. For the balanced client, it depends on one belief
about tech returns. We show exactly where it flips, and our quantum method finds the right answer reliably
where the baseline did not."

### C0. Baseline
Reproduce the notebook's penalty QUBO + QAOA (p = 2, 3 seeds, COBYLA 100). Confirm its weakness: for
risk-sensitive, none of the 3 seeds returns the exact optimum (current portfolio).

### C1. Differentiators
1. **Constraint-preserving QAOA:** initial state = **Dicke state |D₆³⟩** (uniform over the 20 valid
   portfolios), **XY-ring mixer** keeps exactly 3 selected. No cardinality penalty and 100% feasible samples.
   **Tech cap as structure:** for risk-sensitive, fix x_HiTec = 0, which leaves 5 qubits and C(5,3) = 10 options.
   A binding rule becomes a smaller search space, not a soft penalty, and that directly addresses the task.
2. **Proper solver metrics vs the exact optimum:** P(optimum), approximation ratio, feasible mass, and the
   rank of the returned portfolio. Across p = 1…4, ≥ 10 seeds, and both formulations (penalty vs Dicke/XY).
   Show "our method finds the optimum in X/10 runs vs baseline Y/10". Optional: CVaR-QAOA objective,
   warm start from the current portfolio, simulated annealing as the quantum-inspired comparison.
3. **Decision maps (the financial core):** heatmap of the optimal portfolio over
   (λ, HiTec return shift) and over (λ, change penalty τ), with each mandate marked. Break-even lines:
   λ* ≈ 11.2, HiTec shift ≈ −0.37pp/month, τ* ≈ 0.0057. You can see at a glance why balanced is fragile.
4. **Robust selection:** bootstrap the 60 months (≥ 500 resamples); how often is each portfolio optimal
   per mandate? "Balanced chooses the proposal in N% of resamples." This is estimation uncertainty made visible.
   Optionally use Ledoit–Wolf Σ and shrunk μ.
5. **Hold-out check of the *rule*, not the pick:** 2020–24 for the chosen portfolios under buy-and-hold and
   2pp / 5pp threshold rebalancing (the notebook has the replay function).

**Effort:** medium–high. **Strength:** richest sensitivity story, concrete technical improvement over the
baseline, and closest to the pre-learning QUBO/QAOA content. **Risk:** most teams pick this; QAOA tuning can eat time.
Time-box it.

---

## Path D: Integrated decision pipeline (combination)

The task says to pick **one** contribution, but borrowing ideas for robustness is fine. One defensible blend:

**Allocation (C) as the quantum contribution, with Risk (A1.1) and Circuit (B1.2) ideas as classical checks:**
1. Exact filter: binding rules (cap, loss tolerance with uncertainty) → admissible set per mandate.
2. Dicke/XY QAOA over the admissible set → preferred portfolio.
3. Break-even + bootstrap → stability.
4. Verdict `accept` / `reject` / `review` + "flips if…" → Decision Card.

Only one component is quantum, so it stays focused but tells the full decision story. Keep the extra parts
classical and small, otherwise it dilutes the result.

---

## Comparison and recommendation

| | A Risk | B Circuit | C Allocation | D Pipeline |
|---|---|---|---|---|
| Main question | is the loss risk acceptable? | which conditions hold? | which 3 of 6? | full decision |
| Beyond baseline | uncertainty decomposition | evidence-aware logic + Grover | Dicke/XY + decision maps | C + checks |
| Showcase case | risk-sensitive at 10.00% | missing liquidity evidence | balanced flip | all |
| Code effort | ●●○ | ●○○ | ●●● | ●●● |
| Finance depth | ●●● | ●●○ | ●●● | ●●● |
| Policy hook | uncertainty communication | MiFID suitability, binding vs preference | cost-benefit of switching | all |
| Time risk | low | low | medium | high |

**Recommendation:**
- **Coding-strong team → Path C**, with D's structure as the narrative frame. It has the clearest measurable
  improvement over the baseline, and the balanced-client flip is a compelling pitch.
- **Finance/policy-strong team → Path A.** "The quantum estimate is precise; the evidence isn't" is an
  honest, memorable message, and it is cheap to make rigorous.
- **Short on time → Path B** with the Grover extension.

Whatever we pick, the backbone (§0) plus break-even analysis stays the same. That makes it cheap to switch
paths after day 1 if needed.

---

## Timeline

| When | Goal | Output |
|---|---|---|
| **Sprint day 1 (15 Oct)** | Choose path; backbone `data / config / evaluate / enumerate`; reproduce the notebook numbers as tests | Exact reference table; path decision in `docs/decisions.md` |
| **Sprint day 2 (16 Oct)** | First quantum prototype; break-evens; GTPP adviser input | **15-min presentation + slides (40%)**: problem, architecture, plan, first results |
| 17–23 Oct | Differentiators (A1 / B1 / C1); robustness runs; respond to the mid-hackathon change | Sensitivity results, decision log |
| 24–28 Oct | Findings note (≤ 2 p), responsibility note with GTPP, Decision Card, README for reproducibility | Deliverables |
| 29 Oct | Dry-run pitch; everyone can explain their part and the whole | — |
| **30 Oct** | **20-min pitch + slides + GitHub (60%, individual)** | — |

Note: the sprint grade (40%) is about **architecture and plan**, not finished results. The backbone plus a
clear path choice plus one verified result is enough for day 2.

## Suggested roles (adapt to the team)
- **Finance lead:** mandates, binding vs preference, break-evens, Decision Card, findings note.
- **Quantum lead:** the route's circuit/algorithm, verification against exact values, resource statement.
- **Engineering lead:** backbone, tests, diff tool, reproducibility (README, pinned deps).
- **Policy liaison:** GTPP advisers, responsibility note, the one responsibility issue built into the model.
- Everyone keeps entries in `docs/decisions.md` for their part, which supports the individual grading.

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| QAOA tuning eats days | Time-box; Dicke/XY reduces the search; exact answer always available |
| Qiskit version issues | Pin the notebook's versions (qiskit 2.2.3, qiskit-algorithms 0.4.0, Python 3.12) |
| Mid-hackathon change breaks the pipeline | Everything config-driven; `diff.py` ready by day 2 |
| Looking like a copy of the notebook | Every slide states what is ours vs reproduced |
| Over-claiming | No advantage claims; every quantum number shown next to the exact value |
