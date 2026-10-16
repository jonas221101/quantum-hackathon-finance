# Finance Team: Decisions, Parameters, Open Questions

Status: 15 Oct 2026 (sprint day 1). Detailed notes live in the GitHub repo under docs/.

## 1. Decisions made

- Track: Finance, "Portfolio decisions under changing assumptions".
- Client: the planned German public pension fund for the "gesetzliche Kapitalrente" (Alterssicherungskommission, Recommendation 28, June 2026). The decision-maker is the fund's investment committee of external experts. The insured people bear the losses.
- The three supplied mandates are reinterpreted as age cohorts: growth = under 55, balanced = 55 to 65, risk-sensitive = 65 to 75.
- Data: the organiser file Database/returns_6_industries_monthly.csv, verified (checksum matches, identical to the Ken French source).
- Estimation window Jan 2015 to Dec 2019, decision date 31 Dec 2019. Jan 2020 to Dec 2024 is used only for evaluation afterwards.
- Binding rules (tech cap, loss tolerance) are hard filters, never traded against return.
- Every verdict has three states: accept, reject, review. Review covers missing evidence or a result within the uncertainty of a limit.
- Every quantum result is shown next to the exact classical answer. No quantum advantage is claimed.
- The organiser reference notebook is treated as the AI baseline: inspect it, do not adopt it. Every deviation goes into the decision log.

## 2. Parameters

### Portfolios
- Universe: NoDur, Manuf, Enrgy, HiTec, Hlth, Utils (US value-weighted industry portfolios, monthly).
- Current portfolio: NoDur, Hlth, Utils at one third each.
- Proposal: replace NoDur with HiTec, giving HiTec, Hlth, Utils.
- Candidates: all 20 combinations of 3 of 6 at equal weights. No shorting, no borrowing.

### Mandates (organiser teaching values)
- Growth (under 55): risk coefficient 1, loss threshold 8 percent, tolerance 10 percent, HiTec cap 100 percent.
- Balanced (55 to 65): risk coefficient 5, loss threshold 5 percent, tolerance 10 percent, HiTec cap 35 percent.
- Risk-sensitive (65 to 75): risk coefficient 20, loss threshold 3 percent, tolerance 10 percent, HiTec cap 20 percent. A one-third HiTec position is not allowed.
- Change penalty: 0.002 times one-way turnover. This is a preference, not a fee. Our reading: discipline under the 0.1 percent cost cap.
- Rebalancing rule test: 2 and 5 percentage point drift thresholds.

### Scenarios
- Base: 60 months, each with probability 1/60.
- Return stress: HiTec minus 0.5 percentage points per month.
- Covariance stress: correlations moved 25 percent towards 1, means and variances kept.

### Kapitalrente (from the commission report)
- Extra contribution of 2 percent of gross wage, split 50/50 between employer and employee.
- Phase-in of 0.5 points per year, ideally from 2028.
- Individual accounts that cannot be inherited; risk is pooled.
- Public fund modelled on KENFO, with an opt-out into a few certified private funds.
- Cost cap of 0.1 percent per year.
- No guarantees. Risk is controlled through diversification and lifecycle.
- Broadest possible diversification. No country or sector exclusions; only unethical investments, case by case.
- Independent investment committee of external experts.
- Paid out as a lifelong annuity together with the state pension.
- Swedish reference fund (AP7): 100 percent equities until age 55, then a shift to one-third equities by age 75.

## 3. Key results so far

- Current portfolio: lowest volatility of all 20 (2.71 percent per month).
- Proposal: 2nd highest return (+0.29 points per month). P(loss above 3 percent) is 10.00 percent, exactly at the tolerance.
- Growth cohort: switch (robust).
- Balanced cohort: switch, but fragile. The decision flips if HiTec's edge is 0.37 points per month lower, or if the change penalty is above 0.0057. The return stress flips it.
- Risk-sensitive cohort: keep. The tech cap forbids the proposal.
- 2020 to 2024 hindsight: the proposal grew to 1.86 against 1.38. Both portfolios lost more than 3 percent in 20 percent of months, double the model estimate.
- Organiser QAOA misses the exact optimum for the risk-sensitive mandate in all 3 seeds.

## 4. Open questions

### Team decisions
- DECIDED 16 Oct: Allocation route (C). Client = German government (Kapitalrente fund), 3-of-6 = cohort satellite tilt.
- Roles: finance lead, quantum lead, engineering lead, policy liaison.
- Which responsibility issue do we build into the model with the GTPP advisers?

### Mandate and client
- Are the age-cohort boundaries (55, 65, 75) right, or should we follow the AP7 glide path more closely?
- Is the 20 percent tech cap a binding obligation or a preference? Can we justify it from the commission's diversification rule?
- Should an energy exclusion be modelled? The commission says no sector bans; the Greens push for ESG criteria.
- How should the 0.1 percent cost cap translate into the change penalty?
- Which supervisor is responsible for the public fund (BaFin or another body)? Does DORA apply?

### Evidence gaps
- Liquidity data is missing, so it forces review.
- Real cohort data is missing.
- Our data is US industries, while the real fund would be global and multi-asset. This must be stated as a limitation.
- The commission sets no numbers for equity share, glide path or caps. All of these are our assumptions.

### Technical
- Can we reproduce the notebook with qiskit 2.2.3 and Python 3.12 on our laptops?
- What should we do with the boundary case at exactly 10.00 percent: is the rule less-or-equal or strictly-less?
- How do we react to the mid-hackathon change, and which config changes do we prepare?

## 5. Next steps

- Route chosen: Allocation (C). Formal problem in docs/problem_formulation.md.
- Build the shared code: data, config, exact evaluation of all 20, decision record, diff tool.
- Turn the notebook's numbers into tests.
- Prepare the sprint presentation for 16 Oct: problem, client, architecture, plan, first results.
- Start the decision log, including where we did not follow the AI baseline.
