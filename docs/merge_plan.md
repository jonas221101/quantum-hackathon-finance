# Merge plan: `main` ← `feature/quantum-finance-app`

Status: plan only, nothing merged (16 Oct 2026).

## 1. What each branch contains

Both branches start from `a817d92` ("updated to allocation").

| | `main` (054fbee) | `feature/quantum-finance-app` (69c4b04, AhmadOthmann, 2 commits) |
|---|---|---|
| Engine | `src/qhf/` package (16 modules), installed with `pip install -e .` | flat `src/*.py` modules imported as `src.x` (analysis, config, data, decision, enumerate, evaluate, qaoa, report, scenarios) |
| Quantum | Dicke (Bärtschi–Eidenbenz) + XY ring mixer vs penalty QAOA, plus tuned-penalty and CVaR variants. Gates checked against Qiskit; numpy kernel. 3 profiles × p 1–3 × 10 seeds | X-penalty vs Dicke+XY on the Aer statevector simulator. Cost applied as one `Diagonal` gate, p = 1, 2 starts |
| Decision logic | keep / switch / review with bootstrap evidence, break-evens, robustness categories, hold-out with switching cost | winner per mandate and scenario, simple decision record |
| Tests | 52 pytest tests (fast + slow, reproducibility) | 1 unittest file (`tests/test_backbone.py`) |
| Results | `results/canonical/` (summary.json, CSVs, 7 figures) | `outputs/`, not committed |
| UI / report | CLI (`scripts/run_all.py`), slide deck | **Streamlit dashboard `app.py`**, **Markdown report generator `src/report.py`**, root `cli.py` |
| Docs | problem formulation, decisions log, README, guide, findings, decision card, responsibility, deck | **`presentation_story.md`** (5-minute demo flow), **`progress_log.md`**, **`initiative_summary.md`**, `.github/skills/kid-friendly-explainer` |
| Deps | pinned numpy, pandas, scipy, qiskit 2.2.3, matplotlib, scikit-learn | numpy, pandas, scipy, qiskit `>=1.2,<3`, **qiskit-aer**, **streamlit** (ranges, not pins) |

**Only on the feature branch (worth keeping):**
- the Streamlit dashboard
- the Markdown report
- the presentation story and progress log
- the initiative summary
- the explainer skill

**Duplicated (keep only one):**
- data loading, config, scenarios, enumeration, evaluation, decision, QAOA, CLI

`main`'s version is more complete and tested, so keep that one.

**Out of date on the feature branch versus team decisions:**
- profiles described as **age cohorts**; the team decided on an active choice
- the cap is "hard filter or soft penalty"; the team decided it is a **preference**
- mandate key `growth_oriented` instead of `growth`
- numbers come from a small QAOA run
- the balanced label is still open there; it is now **review**

## 2. Conflicts (from `git merge-tree`)

| File | Type | Resolution |
|---|---|---|
| `.gitignore` | add/add | union; add `outputs/` |
| `README.md` | add/add | keep `main`'s README as the base and add a "Dashboard" section plus links to the presentation story and progress log. Drop the age-cohort and cap wording |
| `requirements.txt` | content | `main`'s pins plus `qiskit-aer` and `streamlit`, **pinned** after a test install. Put streamlit under an optional `app` extra in `pyproject.toml` |

No other file conflicts, since the two engines live in different folders. But two engines would confuse graders and readers, so step 3 is needed.

## 3. Steps

1. **Merge branch:** `git switch -c merge/feature-app main`, then `git merge origin/feature/quantum-finance-app`. Use a merge commit so Ahmad's history is preserved.
2. **Resolve the 3 conflicts** as in §2.
3. **One engine:**
   - Port `app.py` to `qhf`. It reads `results/canonical/summary.json` for an instant view and calls `qhf` functions for live reruns with changed parameters (good for the mid-hackathon change demo).
   - Port `src/report.py` to read `summary.json`.
   - Move the useful assertions from `tests/test_backbone.py` into the pytest suite (current / proposal mean and volatility, winners).
   - Then delete the duplicate `src/*.py` modules, `src/__init__.py`, the root `cli.py` and `tests/__init__.py`.
4. **Align the docs with team decisions:**
   - update `presentation_story.md`, `progress_log.md` and `initiative_summary.md` to: active choice, cap as preference, canonical verdicts (growth switch, balanced review, risk-sensitive keep) and canonical QAOA numbers
   - keep the 5-minute demo flow, using the dashboard
5. **Decision log:** add "merged dashboard / report from feature branch; one engine (`qhf`)".
6. **Verify:**
   - `python -m pytest -q`: all green
   - `python scripts/run_all.py run --fast`
   - `streamlit run app.py`: smoke test, every profile renders, and a live rerun with `--set` works
   - `git merge-tree` is clean
7. **PR** `merge/feature-app` → `main`, with **Ahmad as reviewer**. He authored the dashboard and should confirm the port. Do not push directly to main.

## 4. Risks
- **Module name clash:** the feature branch's top-level `src` package. Removing `src/__init__.py` after the port avoids two import styles.
- **qiskit-aer wheel on Python 3.11 / Windows:** check it during the pinned install. The dashboard can run without Aer, because `qhf` uses Qiskit's built-in sampler.
- **Teammates still committing to the feature branch:** agree a short freeze, or rebase the merge branch before the PR.
