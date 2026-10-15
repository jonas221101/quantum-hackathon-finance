# Sources named in the task sheet

Pulled 2026-10-15. Text versions (`.txt`) are for grepping by agents; the PDFs are the originals.

| Task sheet reference | File | Used by route |
|---|---|---|
| Ken French, 10 Industry Portfolios | `data/10_Industry_Portfolios.csv` (+ original zip). CRSP vintage 202608. | all |
| Extract of the 6 challenge industries, VW monthly, 2015-01..2024-12 | `data/six_industries_vw_monthly_2015_2024.csv` (made by `scripts/extract_six_industries.py`) | all |
| Qiskit Finance, Portfolio optimization tutorial | `tutorials/qiskit_finance_01_portfolio_optimization.ipynb` | 3 Allocation |
| Woerner & Egger (2019), Quantum risk analysis, arXiv 1806.06893 | `papers/Woerner_Egger_2019_quantum_risk_analysis.pdf` / `.txt` | 1 Risk |
| IBM Quantum, CCXGate docs | `tutorials/ibm_ccxgate.md` (condensed) | 2 Circuit |
| Kop et al. (2024), Ten principles for responsible quantum innovation | `papers/Kop_2024_responsible_quantum_innovation.pdf` / `.txt` | responsibility |

**Data caveat:** the organisers hand out a *frozen* challenge file. French revises history with each CRSP
vintage, so our extract can differ in the last decimals. Use the supplied file for final numbers; ours is
for early exploration only.

The organiser package is in `Database/`. Its CSV is identical to our extract (max diff 1e-16), so **use
`Database/returns_6_industries_monthly.csv` as the single source of truth.** Mandates, scenario stresses and
the starter code for all routes are embedded in `Database/Finance_Six_Industries_Verified.ipynb`.
