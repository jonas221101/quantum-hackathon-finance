# Initiative Summary

This project frames the challenge as part of a planned German public Kapitalrente initiative starting in 2027.

## Short version

- Client: the public Kapitalrente fund.
- Decision-maker: the fund's independent investment committee.
- Main technical route: Allocation.
- Main benchmark: quantum vs quantum, meaning our rule-preserving QAOA against the organiser's penalty-QAOA.
- Exact enumeration of all 20 candidate portfolios is the answer key, not the main contest.

## Modelling assumptions

- Growth / balanced / risk-sensitive are profiles that each insured person chooses actively (team decision, 16 Oct); balanced is the default.
- The 3-holdings rule is structural in the allocation ansatz.
- The tech cap is a policy preference (penalty in the objective), not a binding rule (team decision, 16 Oct).
- The loss-tolerance rule remains a hard check.

## What was built locally

- Shared data loading and window splitting in `src/data.py`.
- Exact portfolio evaluation in `src/evaluate.py`.
- Full 20-portfolio enumeration in `src/enumerate.py`.
- Decision records in `src/decision.py`.
- Regression tests in `tests/test_backbone.py`.

## Why this matters

The technical goal is not to beat classical enumeration. It is to show a clean quantum allocation pipeline that is easy to verify, easy to explain, and robust to changes in assumptions.
