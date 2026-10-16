# Quantum Finance Allocation Report

## Method

The analysis evaluates all 20 equal-weight portfolios formed by selecting three of six industries. Exact enumeration is the auditable verifier. QAOA is run on IBM Aer with both an X mixer and a Dicke-initialized XY mixer.

## Data

- Source: `C:\Users\Ahmed Othman\Downloads\quantum-hackathon-finance-main\quantum-hackathon-finance\Database\returns_6_industries_monthly.csv`
- Estimation months: 60
- Evaluation months: 60

## Classical recommendations

| Mandate | Portfolio |
|---|---|
| growth_oriented | `HiTec+Hlth+Utils` |
| balanced | `HiTec+Hlth+Utils` |
| risk_sensitive | `NoDur+Hlth+Utils` |

## Scenario recommendations

| Scenario | Mandate results |
|---|---|
| base | growth_oriented: `HiTec+Hlth+Utils`; balanced: `HiTec+Hlth+Utils`; risk_sensitive: `NoDur+Hlth+Utils` |
| return_stress | growth_oriented: `HiTec+Hlth+Utils`; balanced: `NoDur+Hlth+Utils`; risk_sensitive: `NoDur+Hlth+Utils` |
| covariance_stress | growth_oriented: `HiTec+Hlth+Utils`; balanced: `HiTec+Hlth+Utils`; risk_sensitive: `HiTec+Hlth+Utils` |

## Limitations

- Aer is a local simulator, not quantum hardware.
- Historical returns and stress transformations are not forecasts.
- QAOA probabilities are stochastic; exact enumeration remains the answer key.
