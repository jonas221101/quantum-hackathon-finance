# Challenge Progress Log

## 16 October 2026 — Presentation and explainability pass

### Completed

- Confirmed the allocation route and the public Kapitalrente framing.
- Frozen the reproducible data split: Jan 2015–Dec 2019 for estimation and
  Jan 2020–Dec 2024 for held-out evaluation.
- Implemented the shared classical backbone for data loading, exact metrics,
  scenario generation, enumeration, and decision records.
- Added regression coverage for the data shape, reference metrics, all 20
  portfolios, mandate winners, and export surfaces.
- Kept exact enumeration as the audit answer key for every quantum run.
- Documented the distinction between binding loss tolerance and the current
  HiTec preference treatment.
- Added a presentation story and a five-minute demo flow in
  `docs/presentation_story.md`.
- Improved the README and dashboard copy so the user sees the decision,
  method, quantum comparison, and limitations rather than only a score table.

### Evidence currently available

- Growth-oriented winner: `HiTec+Hlth+Utils`.
- Balanced winner: `HiTec+Hlth+Utils` in the base case, with sensitivity to
  return stress.
- Risk-sensitive winner: `NoDur+Hlth+Utils`.
- The QAOA output is reported beside the exact classical winner.
- The prototype does not claim quantum advantage.

### Open work before the final pitch

- ~~Run the full QAOA comparison~~ done: `results/canonical/` (10 seeds, p = 1–3, six QAOA variants).
- ~~Label the balanced result~~ decided: **review** (hold, committee decides with a stated belief).
- ~~HiTec cap interpretation~~ decided: **preference** (κ penalty in the objective); verdicts are identical with κ = 0.
- Merged the dashboard branch into the tested `qhf` engine (one engine, one test suite).
- Add broader/global data, liquidity evidence, and real cohort evidence if the
  challenge provides them.
- Rehearse the five-minute demo using the exact terminology in the presentation
  story.
