# Allocation route: committee report

## Method

All 20 equal-weight portfolios (3 of 6 industries) are scored exactly; this enumeration is the auditable answer key. QAOA is compared quantum vs quantum: the rule-preserving design (Dicke start + XY mixer) against the organiser's penalty QAOA. Ideal local simulation; no quantum-advantage claim.

## Data

- Source: `Database/returns_6_industries_monthly.csv` (checksum verified)
- Estimation: 2015-01 to 2019-12; evaluation (never used for decisions): 2020-01 to 2024-12

## Verdicts

| Profile | Verdict | Holdings | Candidate beats current (resamples) | Reason |
|---|---|---|---:|---|
| balanced (default) | **review** | `NoDur+Hlth+Utils` | 74% | the optimum changes between the base case and a supplied stress |
| growth | **switch** | `HiTec+Hlth+Utils` | 89% | same optimum in all scenario sets and robust under resampling |
| risk_sensitive | **keep** | `NoDur+Hlth+Utils` | 0% | current tilt optimal in all scenario sets and robustly admissible |

## Optimum per scenario set

| Profile | Base | Return stress | Covariance stress |
|---|---|---|---|
| balanced | `HiTec+Hlth+Utils` | `NoDur+Hlth+Utils` | `HiTec+Hlth+Utils` |
| growth | `HiTec+Hlth+Utils` | `HiTec+Hlth+Utils` | `HiTec+Hlth+Utils` |
| risk_sensitive | `NoDur+Hlth+Utils` | `NoDur+Hlth+Utils` | `NoDur+Hlth+Utils` |

## Quantum vs quantum (p = 3, median over seeds)

| Profile | Method | P(best) | min–max | Valid share | Decoded = exact |
|---|---|---:|---|---:|---:|
| balanced | dicke_xy | 0.04 | 0.02–0.10 | 100% | 0% |
| balanced | dicke_xy_cvar | 0.25 | 0.25–0.26 | 100% | 90% |
| balanced | x_penalty | 0.06 | 0.04–0.07 | 98% | 10% |
| balanced | x_penalty_cvar | 0.09 | 0.07–0.15 | 86% | 30% |
| balanced | x_penalty_tuned | 0.15 | 0.13–0.24 | 56% | 100% |
| balanced | x_penalty_tuned_cvar | 0.24 | 0.17–0.25 | 59% | 100% |
| growth | dicke_xy | 0.23 | 0.05–0.50 | 100% | 40% |
| growth | dicke_xy_cvar | 0.25 | 0.25–0.29 | 100% | 100% |
| growth | x_penalty | 0.05 | 0.04–0.05 | 98% | 20% |
| growth | x_penalty_cvar | 0.07 | 0.06–0.10 | 76% | 70% |
| growth | x_penalty_tuned | 0.09 | 0.07–0.12 | 50% | 100% |
| growth | x_penalty_tuned_cvar | 0.12 | 0.09–0.13 | 47% | 100% |
| risk_sensitive | dicke_xy | 0.77 | 0.61–0.80 | 100% | 100% |
| risk_sensitive | dicke_xy_cvar | 0.27 | 0.25–0.35 | 100% | 100% |
| risk_sensitive | x_penalty | 0.05 | 0.04–0.05 | 97% | 10% |
| risk_sensitive | x_penalty_cvar | 0.06 | 0.05–0.09 | 84% | 80% |
| risk_sensitive | x_penalty_tuned | 0.07 | 0.04–0.07 | 32% | 100% |
| risk_sensitive | x_penalty_tuned_cvar | 0.17 | 0.07–0.17 | 49% | 100% |

## Limitations

- ideal noiseless simulation
- Dicke+XY searches the valid states only, penalty QAOA all basis states
- optimisation on exact expectations is optimistic; see shot_noisy_optimisation
- mean-cost optimisation does not maximise P(opt); see min-max and share_below_random_floor
- budget = equal restarts and maxiter per method; evaluations reported as nfev
- no quantum-advantage claim: the options are enumerated exactly in milliseconds
- Historical returns and stress transformations are not forecasts.
- US industry data stands in for a global, multi-asset public fund.
