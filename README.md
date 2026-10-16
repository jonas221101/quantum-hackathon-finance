# Keep or tilt? Sector choices for the German "Kapitalrente" fund, solved with QAOA

TUM Quantum Hackathon (QuantWorld), Finance track, task "Portfolio decisions under changing assumptions".
Route chosen: **Allocation** (pick 3 of 6 industries with a quantum algorithm).

> **Honest headline:** with only 20 possible portfolios, a normal computer finds the exact answer instantly.
> We make **no claim of quantum advantage**. What we deliver is a *checked* quantum encoding that cannot break
> the rules, a clear decision per investor profile, and a map of what would change the answer.

---

## 1. The question in plain words

It is 31 December 2019. A public fund holds a small "tilt" (satellite) part of its equity money in three US
industries: **consumer staples (NoDur), healthcare (Hlth), utilities (Utils)**, one third each.
Someone proposes to **swap NoDur for technology (HiTec)**.

For each of three investor profiles (**growth, balanced, risk-sensitive**) we ask:

> Which 3 of the 6 industries should the tilt hold, and is leaving the current holding justified,
> given the binding rules, the cost of switching and the uncertainty in the numbers?

Possible answers per profile: **Keep**, **Switch**, or **Review** (not enough evidence to decide).
"Review" is a legitimate result, not a failure.

## 2. The client

The **German federal government**, as the sponsor of the planned public fund for the
**"gesetzliche Kapitalrente"** (recommended by the Alterssicherungskommission, June 2026; the fund is
modelled on KENFO). The fund's independent investment committee decides, the insured people bear the losses.

* The **core** of the fund is a broad index. Our 3-of-6 decision is the small **satellite tilt** on top.
* Each insured person **actively chooses** a profile (growth / balanced / risk-sensitive). It is not set by age.
  People who do not choose get a default. We assume **balanced** (open assumption).
* All mandate numbers (risk weights, loss limits, caps) are **assumptions** taken from the organiser's config,
  not figures from the commission.

## 3. How the model decides (short version)

* **Binding rules** (never traded against return): exactly 3 holdings, and a loss tolerance
  (probability of a monthly loss above 8 % / 5 % / 3 % must be at most 10 %). Checked exactly.
* **Preferences** (can be traded off): return, risk, cost of switching, and a soft cap on HiTec.
* The quantum algorithm is **QAOA with a Dicke start state and an XY mixer**. It only ever visits portfolios
  with exactly 3 holdings. We compare it with the organiser's penalty-based QAOA (quantum against quantum).
  Exact enumeration of the 20 portfolios is only the **answer key**.

More detail, in simple words: [docs/guide_plain_language.md](docs/guide_plain_language.md).

## 3b. Result in one table (canonical run)

| Profile | Verdict | Why |
|---|---|---|
| Growth | **Switch** to HiTec + Hlth + Utils | Same winner in all 3 scenarios; beats the current tilt in 89 % of 500 bootstrap resamples |
| Balanced (default for non-choosers) | **Review** | Winner flips to the current tilt under the supplied return stress; proposal wins in 74 % of resamples |
| Risk-sensitive | **Keep** NoDur + Hlth + Utils | Winner in all scenarios; passes the loss rule in 76 % of resamples |

Switching needs proof: same winner in all scenarios **and** at least 70 % bootstrap support. Quantum against quantum
(10 seeds, ideal simulation): our rule-preserving QAOA finds the exact best portfolio with median probability 0.77
(risk-sensitive) against 0.05 for the organiser's penalty QAOA, and always returns valid portfolios. Balanced is a near-tie
that both methods struggle with. **No quantum advantage is claimed.** Figures are in `results/canonical/figures/`
(`fig_risk_return`, `fig_decision_map`, `fig_decision_map_cost`, `fig_bootstrap`, `fig_qaoa_comparison`, `fig_circuits`, `fig_holdout`).

## 4. Documents

| File | What it is |
|---|---|
| [docs/guide_plain_language.md](docs/guide_plain_language.md) | The whole project explained without jargon, with a glossary |
| [docs/findings.md](docs/findings.md) | Findings note (max. 2 pages) |
| [docs/decision_card.md](docs/decision_card.md) | A5 Decision Card |
| [docs/responsibility.md](docs/responsibility.md) | Responsibility note: what is in the model, what is outside |
| [docs/problem_formulation.md](docs/problem_formulation.md) | Formal model (single source of truth) |
| [docs/decisions.md](docs/decisions.md) | Decision log, including where we did not follow an AI suggestion |
| [docs/client_germany.md](docs/client_germany.md) | Research on the Kapitalrente and its fund |
| [docs/deck/](docs/deck/) | Slide deck content (and `allocation_route_deck.pptx`) |
| [docs/presentation_story.md](docs/presentation_story.md) | Pitch narrative and five-minute demo flow |
| [docs/progress_log.md](docs/progress_log.md) | What is done, what evidence exists, what is open |
| [docs/initiative_summary.md](docs/initiative_summary.md) | Short summary of the Kapitalrente initiative |

## 5. How to run

Needs **Python 3.11**.

```bash
pip install -e .
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/run_all.py run --canonical
python scripts/run_all.py run --set balanced.loss_threshold=0.04
python scripts/run_all.py diff <runA> <runB>
```

1. `pip install -e .` installs the package `qhf` from this repo.
2. `pip install -r requirements-dev.txt` adds test and plotting tools.
3. `python -m pytest -q` runs all tests (the quantum results are checked against exact enumeration).
4. `run --canonical` runs the full pipeline with the agreed settings and fixed random seeds. Output goes to
   `results/canonical/` (a `summary.json`, CSV tables and figures).
5. `run --set ...` re-runs with **one assumption changed** (here: the balanced profile's loss threshold becomes
   4 %). This is the "situation changes" use case.
6. `diff <runA> <runB>` shows what changed between two runs: which verdict flipped, and why.

All settings live in one config (`src/qhf/config.py`). Random seeds are fixed, so a second person gets the same numbers.

`python scripts/run_all.py report` writes a Markdown committee report (`results/canonical/report.md`).

### Dashboard

```bash
pip install -e ".[app]"
streamlit run app.py
```

The dashboard has two tabs. **Canonical result** shows the verdict, the exact answer key, the quantum-vs-quantum
comparison and the figures for the chosen profile, with downloads. **What if?** lets you change a mandate
parameter (risk aversion, loss threshold, tolerance, cap preference, switching cost), reruns the decision live,
and can run a quick QAOA comparison. It is built on the same tested `qhf` package.

## 6. Repo map

```
Database/                     supplied monthly returns (6 industries, 2015-2024) and organiser notebook
docs/                         documentation (see table above)
scripts/run_all.py            command line: run / diff / report
app.py                        Streamlit dashboard (committee view + live what-if)
src/qhf/
  config.py                   all parameters in one place (profiles, penalties, seeds, windows)
  data.py                     loads the returns, splits estimation (2015-19) and hold-out (2020-24)
  scenarios.py                the 60 monthly scenarios plus the two supplied stresses
  portfolio.py                returns, risk and loss probability of a 3-of-6 portfolio
  exact.py                    enumerates all 20 portfolios: the answer key
  bits.py                     bitstring helpers (which industries are held)
  qubo.py                     writes the decision as a QUBO / Ising problem
  circuits.py                 the quantum circuits (Dicke start, XY mixer, penalty baseline)
  kernel.py                   fast simulation kernel for the circuits
  qaoa.py                     QAOA loop: classical optimiser, seeds, depth p
  decision.py                 turns results into Keep / Switch / Review
  sensitivity.py              what-if sweeps, break-even points, bootstrap
  evaluation.py               checks against the answer key; 2020-24 hindsight
  plots.py                    all figures
  report.py                   Markdown committee report from a run's summary.json
  cli.py                      command line behind scripts/run_all.py
tests/                        pytest tests
results/                      outputs of runs (canonical run in results/canonical/)
sources/                      downloaded reference papers and reports
```

## 7. Limits (the short list)

* 60 months of data; the 2015-19 tech rally drives the estimates.
* US industries stand in for a global fund; no liquidity, ESG or tax data.
* Equal weights and exactly 3 holdings are simplifications; the switching cost is a proxy, not a fee model.
* Simulation on a laptop, no quantum hardware, no advantage claimed.
