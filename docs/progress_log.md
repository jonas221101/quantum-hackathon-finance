# Challenge Progress Log

## 28 October 2026 — Draft plots for the slides and the sync with Eden

### Completed

- Re-ran the canonical pipeline (`python scripts/run_all.py run --canonical`, about 22 minutes, fixed seeds) and
  checked that the existing numbers reproduce.
- New slide figures in `results/canonical/figures/`:
  - `fig_success_rate.png`: rule-preserving QAOA vs penalty QAOA (organiser and tuned), valid share of measured shots
    and P(exact best portfolio) at p = 3.
  - `fig_estimation_error.png`: balanced profile, proposal's score lead vs a shift in HiTec's expected return, with
    ±1/±2 standard-error bands and the bootstrap distribution of the lead.
  - `fig_loss_limits.png`, `fig_loss_timeline.png`: binding loss rule, ex-ante scenario sets vs realised 2020–24.
- New tables: `estimation_error.csv`, `estimation_error_curve.csv`, `bootstrap_advantage.csv`, `loss_limits.csv`;
  `quantum_runs.csv` now has `sampled_h1_share` and `sampled_admissible_share`.
- Tests for all new functions (62 tests pass).
- Briefing for the supervisor sync: `docs/sync_eden_2026-10-29.md`.

### Open before the final pitch

- Decide with Eden: story order, how strongly to word the quantum claim, where the hindsight loss-rule failure goes.
- Done 28 Oct: new figures are slides 10, 12 and 14 of `docs/deck/Quantum_Hackathon_28_10_updated.pptx`; plain-language explanations in the README, `docs/guide_plain_language.md` and the briefing (`docs/sync_eden_2026-10-29.md` / `.pdf`).
- Check that Eden's questions 2 and 3 are covered (the deck's speaker notes mark only 1, 4, 5 and 6).
- Record which model changes came from the Policy Practice Team advisers.
- Split the 20-minute pitch so every member presents their own part.

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

- Run the full QAOA comparison with the intended number of seeds, reps, and
  shots; the checked-in summary uses a small local run.
- Decide how the committee wants to label the balanced result: switch with a
  review flag, or review before switching.
- Confirm the final interpretation of the HiTec cap and encode the chosen
  policy consistently in the narrative and configuration.
- Add broader/global data, liquidity evidence, and real cohort evidence if the
  challenge provides them.
- Rehearse the five-minute demo using the exact terminology in the presentation
  story.
