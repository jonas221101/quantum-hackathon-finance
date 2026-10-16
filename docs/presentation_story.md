# Presentation Story: A Defensible Quantum Allocation Decision

## One-line pitch

We help an independent investment committee decide whether a public pension
fund's satellite tilt should keep its current three-sector tilt or switch to
HiTec, Hlth and Utils—using a quantum optimiser that respects the cardinality
rule, while keeping an exact classical answer key and explicit uncertainty.

## The story arc

### 1. Start with the human decision

Retirement losses are borne by insured people, so a recommendation cannot be
just “the portfolio with the highest return.” The committee needs to answer:

> For each investor profile, is switching from NoDur + Hlth + Utils to another
> three-sector tilt justified by the evidence, the risk tolerance, and the
> rules?

The six-sector choice is a **satellite tilt**, not the whole pension portfolio.
The core remains broadly diversified. This keeps the model aligned with the
initiative's diversification goal without pretending that six US industries
represent a complete public fund.

### 2. Make the decision concrete

At 31 December 2019, the model uses 60 months of estimation data and compares
all 20 equal-weighted combinations of three out of six industries. The next
60 months are held out for an after-the-fact evaluation, not used to choose the
portfolio.

The three profiles are decision mandates that each insured person **chooses actively** (not by age);
*balanced* is the default for people who do not choose:

| Profile | Risk weight | Loss threshold | HiTec preference |
|---|---:|---:|---:|
| Growth-oriented | 1 | 8% | up to 100% |
| Balanced | 5 | 5% | up to 35% |
| Risk-sensitive | 20 | 3% | up to 20% |

The model treats the loss-tolerance check as binding. The HiTec cap is shown
as a preference in the current formulation, while the exact feasible-set
check remains visible. That distinction should be said aloud.

### 3. Explain the quantum contribution simply

The decision is encoded as six binary choices:

- `1` means an industry is selected;
- exactly three choices must be `1`;
- the objective balances return, covariance risk, and reluctance to switch;
- the loss rule is checked exactly after decoding.

Our QAOA design starts in the valid three-selection subspace and uses an XY
mixer, so it searches among structurally valid allocations. In the canonical run (ideal simulation,
10 seeds, depth 3) it finds the best portfolio with median probability 0.77 for risk-sensitive and
0.23 for growth, against 0.05 for the organiser's penalty QAOA. For the balanced near-tie its
CVaR-objective variant reaches 0.25. It never proposes an invalid portfolio. The organiser
baseline uses an X mixer and penalty terms. This makes the comparison
meaningful: **rule-preserving QAOA versus penalty-based QAOA**, not quantum
versus a trivial brute-force problem.

The exact enumeration of 20 portfolios is deliberately retained as the audit
answer key. We make no claim of quantum advantage.

### 4. Show the result as a committee recommendation

The base-case winners are:

| Profile | Verdict (canonical run) | Why |
|---|---|---|
| Growth-oriented | **Switch** to HiTec + Hlth + Utils | Same winner in all three scenario sets; beats the current tilt in 89% of bootstrap resamples. |
| Balanced (default) | **Review**: hold NoDur + Hlth + Utils for now | HiTec + Hlth + Utils wins the base case, but the supplied return stress flips it back; break-even is a tech edge 0.37 points per month lower. |
| Risk-sensitive | **Keep** NoDur + Hlth + Utils | The current tilt is optimal everywhere; the loss rule removes 13 of 20 options. |

The key insight is not one universal winner. It is that the answer changes with
the mandate, and the constraints are part of the investment decision rather
than an afterthought.

### 5. Make uncertainty part of the product

Show the base case next to return stress and covariance stress. Then explain
the three verdicts:

- **Switch**: the same candidate wins the base case and both supplied stresses, beats the current tilt
  in at least 70% of bootstrap resamples and passes the loss rule in at least 70% of them;
- **Keep**: the current portfolio is optimal everywhere and stays admissible in at least 70% of resamples;
- **Review**: anything else; the default action is to hold and let the committee decide with a stated belief.

The burden of proof is on the change. For the balanced profile the verdict is **review**: the switch is
only justified if the committee believes tech's monthly edge stays above about 0.37 points. Liquidity,
global assets, real cohort data, and the final policy interpretation are still
evidence gaps.

### 6. Close with responsible quantum claims

The demo proves a complete and inspectable pipeline:

1. load and checksum the frozen data;
2. split estimation from evaluation;
3. enumerate the exact answer key;
4. solve the same encoded decision with QAOA;
5. decode, check feasibility, and compare;
6. expose stress scenarios and limitations.

The value is explainability and disciplined experimentation: a committee can
see what the optimiser did, what rules were binding, and where human review is
still required.

## Suggested five-minute demo

1. **0:00–0:45 — The decision:** current tilt, proposed tilt, and who bears the risk.
2. **0:45–1:30 — The data:** 60-month estimation window, 60-month holdout, 20 candidates.
3. **1:30–2:15 — The model:** three binary selections, return/risk/switching objective, hard loss check.
4. **2:15–3:15 — The dashboard:** show each profile's verdict, then use the *What if?* tab to change one assumption live (the mid-hackathon change).
5. **3:15–4:15 — Quantum comparison:** show QAOA's most probable feasible result beside the exact winner.
6. **4:15–5:00 — Responsible conclusion:** balanced is fragile, risk-sensitive stays put, and no quantum advantage is claimed.

## Questions the team should answer explicitly

- Why only six US industries?
  This is a reproducible challenge-sized satellite model, not the final fund
  universe.
- Why enumerate if the goal is quantum?
  Because exact enumeration is the audit key for a six-industry prototype.
- Is the HiTec cap hard or soft?
  The current formulation treats it as a preference in the objective; the
  presentation must not describe it as a binding constraint.
- Why use 2015–2019 to decide?
  It creates a clean decision date and keeps 2020–2024 as held-out evidence.
- What does QAOA add?
  It demonstrates a constraint-aware quantum allocation workflow and gives a
  fair comparison against the penalty-based baseline; it is not presented as
  faster than checking 20 portfolios.
