# Quantum Hackathon Finance

This repo supports the finance track for the quantum hackathon challenge around the planned German public Kapitalrente initiative starting in 2027.

The chosen route is **Allocation**: select 3 of 6 industries at equal weight, formulate the problem as a QUBO / Ising model, and solve it with a quantum allocation method. The main comparison is **quantum vs quantum**:

- our rule-preserving QAOA design vs the organiser's penalty-based QAOA
- exact enumeration of all 20 portfolios as the answer key only

The presentation should lead with the committee decision, not a claim of
quantum advantage: growth and balanced favour `HiTec+Hlth+Utils` in the base
case, while risk-sensitive keeps `NoDur+Hlth+Utils`. The balanced result is
fragile under stress and should be presented with a review flag. See
[`docs/presentation_story.md`](docs/presentation_story.md) for the narrative
and demo flow, and [`docs/progress_log.md`](docs/progress_log.md) for the
current evidence and remaining work.

## What was built

- A shared classical backbone in `src/` for loading data, splitting the estimation / evaluation windows, computing exact portfolio metrics, and enumerating the 20 candidate portfolios.
- Regression tests in `tests/` that verify the frozen CSV checksum, the current/proposal baseline statistics, and the expected winning portfolios.
- A local initiative summary in `docs/initiative_summary.md` that reflects the public 2027 framing.
- A decisions log in `docs/decisions.md` so the team can track what was chosen, what was assumed, and what remains open.

## Current modelling assumptions

- The client is the public Kapitalrente fund, not the private certified-fund alternative.
- The age-cohort mapping (growth / balanced / risk-sensitive) is a lifecycle modelling assumption.
- The 3-holdings rule is treated as structural in the allocation ansatz.
- The tech cap is currently documented as a policy preference and can be enforced as either a hard filter or a soft penalty depending on the final narrative.

## How to run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the regression tests:

```powershell
python -m unittest discover -s tests -v
```

Run the complete classical analysis and export CSV/JSON results:

```powershell
python cli.py --classical-only
```

Run the QAOA comparison on IBM's local Aer simulator:

```powershell
python cli.py
```

Generate the same analysis plus a Markdown report:

```powershell
python cli.py --report
```

The quantum comparison reports both penalty-based X-mixer QAOA and
constraint-preserving Dicke-state plus XY-mixer QAOA. The latter starts in the
exactly-three-industries subspace and preserves that cardinality during the
mixing layers.

Launch the interactive dashboard:

```powershell
streamlit run app.py
```

The QAOA path requires `qiskit` and `qiskit-aer`. It uses the local IBM Aer
statevector simulator, so no IBM Quantum account or API key is needed. The
exact 20-portfolio enumeration remains the verifier and should be shown
alongside probabilistic QAOA results.

## Repository map

- `src/` - data loading, config, scenario generation, exact evaluation, enumeration, and decision records.
- `tests/` - regression checks for the frozen data and the baseline portfolio statistics.
- `docs/` - problem framing, route comparison, solution plan, and client context.
- `Database/` - frozen CSV and organiser reference notebook.
- `cli.py` - end-to-end reproducible analysis command.
- `app.py` - Streamlit dashboard.
- `src/report.py` - Markdown report generator.
- `outputs/` - generated CSV/JSON reports (not committed).

## Notes

- The organiser notebook remains the baseline to inspect, not copy.
- The exact 20-portfolio enumeration is the verifier, not the main competitor.
- If the final committee wording changes, the cap / preference treatment can be tightened in code later without changing the backbone.
