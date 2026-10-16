# Findings note

Decision date 31 Dec 2019. Estimation data Jan 2015 - Dec 2019 (60 months). Client: German government, public
Kapitalrente fund; the 3-of-6 choice is a satellite tilt on a broad core. All numbers: `results/canonical/summary.json`
(ideal simulation, fixed seeds). Figures: `results/canonical/figures/`.

## What the result establishes

The burden of proof is on the change. **Switch** needs the same best portfolio in all three scenario sets *and* the
candidate beating the current tilt in at least 70 % of 500 bootstrap resamples *and* passing the loss rule in at least 70 %.
**Keep** needs the current tilt best everywhere and admissible in at least 70 % of resamples. Otherwise **Review**
(default action: hold, the committee decides with a stated belief).

| Profile (chosen by the insured) | Verdict | Evidence |
|---|---|---|
| Growth | **Switch** to HiTec + Hlth + Utils | Same winner in all 3 scenario sets; beats current in 89 % of resamples |
| Balanced (assumed default) | **Review** | Winner flips to current under the return stress; proposal beats current in 74 % of resamples |
| Risk-sensitive | **Keep** NoDur + Hlth + Utils | Winner in all 3 sets; admissible in 76 % of resamples |

* The binding checks (exactly 3 holdings, loss tolerance) were verified exactly for every recommended portfolio.
* **Balanced tipping points:** HiTec's monthly edge 0.37 points lower flips it to current (supplied stress: 0.5);
  switching cost 0.0057 (about 3x the base 0.002); risk weight 7.5 (proposal gives way to NoDur+HiTec+Utils) and 14.9 (to current), against 5 used. Score margin is only 0.0012 per month.
* The tech limit is a preference (penalty 0.01). Verdicts are identical with the penalty at zero.
* Risk-sensitive: only 7 of 20 portfolios pass the loss rule. The proposal passes at exactly 6 of 60 months (10 %) and
  **fails under a strict "less than" reading**.
* **Quantum against quantum** (ideal simulation, 10 seeds, 3 layers, median chance of the exact best portfolio; guessing 0.05):
  risk-sensitive 0.77 (ours, Dicke + XY) vs 0.05 (organiser penalty QAOA) and 0.07 (tuned penalty); growth 0.23 (CVaR variant 0.25) vs 0.05 and 0.09;
  balanced is a near-tie: ours 0.04 with the mean objective, 0.25 with CVaR (right answer decoded in 90 % of runs), penalty versions 0.06-0.15.
  Ours always returns valid portfolios; penalty versions 32-98 %. Results vary a lot between seeds and optimising the mean cost does not maximise the chance of the best portfolio. Exact enumeration is the answer key.

## What stays unresolved

* **Balanced profile.** It depends on one belief: does tech keep its edge over staples? The data cannot settle this.
* **Boundary case.** The risk-sensitive proposal sits exactly on the tolerance (6 of 60 months). The verdict "keep" does not depend on it, but the wording of the rule decides admissibility.
* **Tail risk was understated.** In 2020-24 the share of months with a loss above each profile's own threshold was 5 % (proposal) vs 3 % (current) for growth, 13 % vs 8 % for balanced and 20 % for both for risk-sensitive.
* **Hindsight is one path.** Including the switching cost, the proposal grew to 1.86 against 1.38 (drawdown −21 % vs −17 %). Rebalancing rules at 2 % or 5 % drift did not beat holding for the proposal. This does not prove the 2019 decision right or wrong.
* **Default profile.** If non-choosers land on *balanced*, the fragile answer applies to people who may not have chosen it.
* **Estimation vs computation.** Bootstrap shows how often each portfolio wins on other data; seeds show how steady the quantum search is. Reported separately.

## Whose priorities govern

* The **investment committee** decides. It must state its belief about tech's edge and the weight on switching costs.
* The **legislator** decides whether a tilt is acceptable at all (the commission asks for the broadest diversification), whether profiles are chosen actively, and what the default is.
* The **insured** bear losses; those who chose "growth" accepted more swings, those on the default did not necessarily choose.
* Profile numbers and the tech limit are **assumptions** (organiser config), not commission figures.

## Evidence needed before acting

1. Longer data history and a global universe instead of 60 months of US industries.
2. A committee decision on the tech belief and on whether the tech limit is binding or a preference.
3. A tail-risk model that does not replay 60 past months (2020-24 shows it was too optimistic).
4. Liquidity, real trading cost and cost-cap (0.1 % per year) checks.
5. Clarity on the supervisor; an ICT / compute-provider assessment if any external service is used.
6. Independent reproduction (`python scripts/run_all.py run --canonical`).

## Limits

No quantum advantage: 20 options are solved exactly in milliseconds. Ideal simulation only (a shot-noise check exists in the results). Equal weights, K = 3 and the
switching cost are simplifications. 2020-24 is hindsight only, never a decision input.
