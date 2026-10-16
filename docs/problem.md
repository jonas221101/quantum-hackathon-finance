# The actual problem and challenge

> **Update 16 Oct 2026:** the team chose the **allocation route (C)**. The formal problem statement
> (variables, objective, binding rules, solver, robustness design) is in `docs/problem_formulation.md`.
> This file remains the plain-language background.

Plain-language explanation for the whole team (finance, quantum, policy). All numbers were recomputed by us
from `Database/returns_6_industries_monthly.csv` and the supplied mandate parameters.
Per-route technical detail: `docs/routes.md`.

---

## 1. The situation in one paragraph

It is **31 December 2019**. An investment team manages money split equally across three U.S. industry
portfolios: **consumer staples (NoDur), healthcare (Hlth) and utilities (Utils)**. Someone proposes to
**sell consumer staples and buy technology (HiTec)** instead, because tech has had a great five years.
The team must decide whether to make that switch, keep what it has, or do something else. It must justify
the choice to an investment committee that has to sign off. The committee serves **three kinds of clients**
(growth, balanced, risk-sensitive), each with its own rules. The data, rules and assumptions may change
during the hackathon, and the answer has to show what changes and why.

**The task is not "find the best portfolio".** It is "build a case that lets a human decide, under explicit
rules and uncertain evidence, and show when that case would flip."

---

## 2. What exactly is being decided

| Element | In this challenge |
|---|---|
| Decision-maker | Investment committee (or a model-validation team / supervisor; the GTPP advisers pick one, EU setting) |
| Options | **Retain** NoDur/Hlth/Utils · **Accept** proposal HiTec/Hlth/Utils · **Other** 3-of-6 · **Review** (not enough evidence) |
| Evidence | 60 monthly returns, 2015–2019, for 6 industries (Ken French) |
| Rules | Mandate per client type: risk weight, loss limit, tolerated loss probability, tech cap |
| Friction | A change penalty (0.002 × turnover). It stands for reluctance to trade, not a real cost model |
| Held back | 2020–2024 data: for evaluating afterwards only, never for the decision itself |

"Review" is a legitimate outcome. The task stresses that a breach supports review, not an automatic trade,
and that missing evidence is different from a failed condition.

---

## 3. Why this is hard: four tensions

### 3.1 More return vs more risk, and the risk measures disagree
| (2015–19, per month) | Current | Proposal | Difference |
|---|---|---|---|
| Estimated return | 0.73% | 1.02% | **+0.29pp** (≈ +3.5%/yr) |
| Volatility | 2.71% | 3.05% | +0.34pp |
| Worst month | −8.11% | −7.08% | proposal is *better* |
| P(loss > 3%) | 8.33% | 10.00% | proposal is worse |

The current portfolio has the **lowest volatility of all 20 possible portfolios**. The proposal ranks 2nd of 20 on
return. By worst month the proposal looks safer; by volatility and loss frequency it looks riskier.
**Which risk measure counts is a mandate choice, not a fact.**

### 3.2 Binding rules vs tradeable preferences
The task explicitly says not to hide everything in one score:
- **Binding** (cannot be traded for return): the HiTec cap (risk-sensitive: max 20%, so a 1/3 tech position is
  forbidden). The loss-probability tolerance (10%) is probably binding too.
- **Preference** (can be traded): more return, less variance, less turnover.

If the cap is just a penalty term in a score, a big enough return can "buy" a violation. That is exactly what
the task warns against. The model must make binding rules **structural**: a hard filter, an AND gate, or a
verified constraint.

### 3.3 Estimates are not facts
- 60 months is a short sample. HiTec's 1.51%/month is driven by the 2015–19 tech rally.
- Proof from the hold-out period: **Energy**, the worst industry in 2015–19 (0.02%/mo), was the
  *second-best* in 2020–24 (1.56%/mo). Past ranking ≠ future ranking.
- The scenario model gives each past month probability 1/60. That is an assumption, not a forecast.
- The task wants three kinds of uncertainty kept apart: **financial estimates** (μ, Σ, scenarios),
  **mandate choices** (thresholds, λ), and **computation** (shots, seeds, QAOA settings).

### 3.4 Changing costs something
Each swap costs a change penalty, and the proposal changes 1/3 of the portfolio. Under MiFID II a switch
needs a cost-benefit justification. "Keep what you have" is a valid answer when the gain does not clearly
beat the cost and the uncertainty.

---

## 4. The three clients, worked through

Score used by the organisers: `return − λ·variance − 0.002·turnover`, cap enforced, over all 20 portfolios.

### Growth-oriented (λ = 1, loss limit 8%, tech cap none)
- Best: **proposal** in all three scenario sets. Score margin over current: +0.0020/month.
- P(loss > 8%): proposal 0%, current 1.67%. No risk issue.
- **Verdict: accept the switch.** Robust. Weak spot: relies entirely on HiTec's estimated return.

### Balanced (λ = 5, loss limit 5%, tech cap 35%), the swing case
- Base: **proposal** wins, but only by +0.0012/month.
- Return stress (HiTec −0.5pp/month): **current** wins. **The decision flips.**
- Covariance stress: proposal still wins, but nearly ties with NoDur+HiTec+Utils (0.00412 vs 0.00406).
- Break-evens (our calculation):
  - Proposal and current tie when HiTec's monthly return is **0.37pp lower**. The stress uses 0.5pp, so it flips.
  - They tie when the change penalty is **0.0057** instead of 0.002 (≈ 3× higher).
  - They tie at risk weight **λ ≈ 11.2**. Balanced is 5, so it is safe on that axis.
- **Verdict: conditional.** "Accept only if you believe HiTec's edge is above ~0.37pp/month." That condition is what the Decision Card should say.

### Risk-sensitive (λ = 20, loss limit 3%, tech cap 20%)
- The proposal is **forbidden by the tech cap** (33% > 20%). The current portfolio is the optimum in all scenario sets.
- Even without the cap, the proposal is on the edge of the loss rule: P(loss > 3%) = **10.00%**, tolerance 10%.
  It is 6 of 60 months. The smallest of those losses is **3.10%**, so a threshold of 3.1% instead of 3.0%
  would drop it to 8.3%. Under the stresses it breaches (11.67%, 15%).
- **Verdict: retain.** The decision rests on the cap (binding), not on a tiny score difference. That is a
  clean, defensible story. The open question for the policy side: is a 20% tech cap a real obligation
  or an arbitrary preference? The task explicitly asks you to justify that.

**Summary:** growth → switch · balanced → switch, but fragile · risk-sensitive → retain.
The interesting work is in **balanced** (sensitivity) and **risk-sensitive** (binding rule + boundary case).

---

## 5. What a strong answer looks like (from the assessment criteria)

| Weak | Strong |
|---|---|
| "QAOA found portfolio X" | "Under mandate M, X is preferred; it flips when HiTec's edge falls below 0.37pp/month" |
| One run, one number | Base + ≥ 2 stresses, seeds, with stable vs changing results labelled |
| Cap hidden as a soft penalty | Cap as a hard rule, verified on every output |
| "Probability = 10%" | "10.00% ± CI. Equal to the tolerance, so unresolved. Driven by one month at −3.1%" |
| Big quantum circuit, unclear purpose | Small circuit; clear statement of what enters, what it computes, what stays classical |
| Claims quantum advantage | Explicitly none; quantum is a demonstrated, verified component |
| Copies the AI baseline | Inspects it, finds its gaps, logs where we deviated and why |

Assessment rewards: financial meaning, correctness of the representation, traceability, investigation of
changing assumptions, reproducibility, and clear limitations and responsibility. "A small result that makes its
assumptions and decision consequences visible is stronger than a larger result that cannot explain why the
recommendation changed."

---

## 6. Where quantum fits

Quantum is **one component** in a decision pipeline, chosen through one route:
- **Risk:** estimates P(loss > threshold) for a fixed portfolio with amplitude estimation. The scenario
  table and the loss marking are prepared classically; the circuit estimates a probability with a confidence interval.
- **Circuit:** encodes "all binding conditions hold AND evidence complete" as reversible logic. Checks
  declared conditions; does not judge whether they are right.
- **Allocation:** encodes the 3-of-6 choice as a QUBO and samples it with QAOA. With only 20 options,
  the exact answer is known, so quantum is verified against it, not compared with it.

On this scale classical computation is exact and instant. The honest value is: **correct encoding,
verified against the exact answer, showing how the method would plug into a real workflow, and what it would cost
(external providers, DORA dependency, explainability).**

---

## 7. Hindsight: 2020–2024 (evaluation only, never a decision input)

| 2020–24 | Current | Proposal |
|---|---|---|
| Wealth (buy & hold, start = 1) | 1.38 | **1.86** |
| Max drawdown | −17.0% | −21.0% |
| Monthly volatility | 4.18% | 4.58% |
| P(loss > 3%), realised | **20%** | **20%** |

Lessons:
- The proposal did much better in wealth terms. **That does not prove the 2019 decision was right**: one
  path, and tech then had an exceptional run.
- Realised P(loss > 3%) was **20% for both**, double the 8–10% the 2015–19 scenario model suggested.
  The risk-sensitive tolerance would have been breached by *both* portfolios. The empirical
  scenario model understated tail risk (COVID 2020, 2022). This is a strong limitation point for the findings note.
- Use this period to test **decision rules** (hold vs threshold rebalancing at 2pp/5pp), not to pick a winner afterwards.

---

## 8. The moving target

- **AI baseline:** during the hackathon we get an AI assistant's 5-minute answer. The organiser
  notebook in `Database/` looks AI-generated and may be it. It is solid, but its QAOA often misses the
  optimum, the boundary case is reported but not explained, and it adds no break-even analysis. That gives us
  concrete room to improve. Log every deviation in `docs/decisions.md`.
- **Mid-hackathon change:** expect a mandate threshold or input assumption to be changed. The pipeline must
  rerun in minutes and output a diff: what changed, which condition flipped, why.

---

## 9. Draft answers to the guiding questions

| Question | Draft answer |
|---|---|
| What is the decision? | Retain NoDur/Hlth/Utils vs switch NoDur → HiTec, per client mandate, on 31 Dec 2019 |
| What does the mandate require? | Binding: tech cap, loss tolerance. Tradeable: return vs variance vs turnover |
| What does the evidence support? | Observed: 60 monthly returns. Estimated: μ, Σ. Assumed: 1/60 scenario weights, stresses, all mandate parameters |
| What changes the answer? | Balanced: HiTec edge < 0.37pp/month or change penalty > 0.0057. Risk-sensitive: nothing in the tests; the cap decides |
| What does the quantum part do? | Route-dependent (§6); always verified against the exact classical answer |
| Who needs the result? | Investment committee: a recommendation, a confidence statement, the one condition under which not to follow it |
