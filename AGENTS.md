# AGENTS.md

Rules + context for every AI agent (Claude Code, Codex, Cursor, …) in this repo.
Source material lives in `Kontext/` (PDFs). This file = digest. Read this first, open PDFs only when detail needed.

---

## 1. How agents work here

### Talk caveman
- Terse. No filler, no praise, no recap of what user just said.
- Drop articles/pleasantries where meaning survives. Fragments OK. `Fixed bug. Penalty P too low. Now 0.5.`
- Code, math, numbers, file paths, error messages: always exact, never compressed.
- Explanations for slides / pitch / non-technical readers: write normal clear prose (caveman only for agent chatter).

### Plan with big model, execute with cheap model
- **Planning, architecture, math formulation, QUBO derivation, debugging hard failures, final review** → top model (e.g. Claude Opus).
- **Mechanical work** (boilerplate, refactors, plotting, data loading, running sweeps, writing tests from a spec, summarizing papers) → cheap/fast model (e.g. Claude Sonnet / Haiku) as subagent.
- Planner writes a short spec (goal, files, inputs/outputs, done-criteria) before handing off. Executor follows spec, does not redesign.
- Planner reviews executor output before it lands.

### Always check your code
- Run it. Every change. No "should work".
- Small instances first: verify QUBO / solver result against **brute-force enumeration** (n ≤ ~20) or exact solver (CP-SAT / HiGHS / Gurobi).
- Check feasibility of every returned bitstring (cardinality, budget, etc.) — never trust solver blindly.
- Check sign convention (min vs max) and keep the QUBO **constant offset** when reporting energies.
- Stochastic solvers (SA, QAOA, annealing): multiple seeds, report median + spread. One run ≠ evidence.
- Add/keep tests for core functions (`pytest`). Tests pass before commit.
- Report failures honestly. Wrong result + clear log > silent "success".

### Write clean code
- Python, type hints, small pure functions, descriptive names (`expected_returns`, not `mu2`).
- Separate: data loading → estimation (μ, Σ) → model building (QUBO) → solving → decoding → evaluation/plots.
- No magic numbers: parameters (K, λ/q, penalty P, window, seed) in one config/dataclass.
- Fix random seeds. Pin dependencies (`requirements.txt` / `pyproject.toml`).
- Notebooks for exploration only; reusable logic goes in `src/` modules.
- No dead code, no commented-out blocks, no committed secrets/API keys/tokens.
- Reproducible: someone else must run `README` steps and get same numbers (code on GitHub is graded).

### Context hygiene
- Summarize, don't dump. When reading papers/PDFs, store a short summary (claim, formulation, result, limitation) instead of pasting text.
- Keep this file updated when key decisions change (chosen formulation, data window, solver set).
- Long sessions: write decisions to `docs/decisions.md` so the next agent picks up without rereading everything.

---

## 2. Hackathon context (summary of `Kontext/`)

**Event:** TUM Quantum Hackathon (QuantWorld, SOT86140), guided interdisciplinary project. Track: **Finance**.

| Phase | Date | What |
|---|---|---|
| Pre-learning | 05–07 Oct 2026 | Quantum basics, QUBO/Ising/QAOA, responsibility, domain session |
| Sprint | 15–16 Oct 2026, 10:00–19:00 | Initial solution concept, architecture, project plan |
| Final pitch | 30 Oct 2026 | Internal 15:00–16:30, external w/ guests 17:00–20:00 |

**Grading**
- 40% sprint outcome: 15-min team presentation + PowerPoint, initial solution architecture + project plan.
- 60% final pitch: 20-min presentation + PowerPoint, **GitHub code graded**, assessment **individual** (each member must explain own contribution + overall logic, answer questions).
- Must show code / reproducible workflow and how feedback from the **Policy Practice Team** was used.

**Core principle (from syllabus):** technical complexity alone ≠ strong project. Strong = credible fit between problem, method, evidence, and real-world setting. Be honest about limits.

### Finance challenge: portfolio decisions under uncertain estimates
- Investment decision = purpose, horizon, exposure, restrictions. Same data ≠ same portfolio for different investors.
- Separate tasks: define decision → model outcomes → estimate inputs → choose allocation → evaluate/monitor.
- Return: `r = (P1 − P0 + D) / P0`. Portfolio return `R_p = Σ w_i r_i`, fully invested `Σ w_i = 1`, no shorts `w_i ≥ 0`.
- Risk ≠ only volatility: also loss probability, expected loss, expected shortfall (CVaR). Choose measure that fits decision.
- Diversification: two assets 20% vol each, equal weight → ρ=1: 20%, ρ=0: 14.1%, ρ=−0.5: 10%.
- Mean–variance: `max μᵀw − λ wᵀΣw`, w in permitted set.
- **Estimation error matters:** document window, frequency, universe, data treatment, estimator. Sample covariance is noisy → consider Ledoit–Wolf shrinkage.
- **Sensitivity:** perturb μ, Σ → does allocation change? Which assumption drives it? What is stable?
- **Rebalancing:** is improvement worth trading cost `c·‖w_new − w_cur‖₁` vs holding?
- Non-optimizer baselines are legit: 1/N equal weight (DeMiguel 2009), hold, target, threshold rebalancing, scenario eval.
- **Where quantum enters:** discrete asset selection — choose exactly K of N assets, equal weight:
  `min −μᵀx + q·xᵀΣx  s.t. Σx_i = K, x_i ∈ {0,1}`
- Verify output per approach: exact (feasibility + optimality certificate), classical heuristic (quality, repeatability), quantum-inspired (why "quantum-inspired"?), hybrid (which steps classical/quantum?), quantum sampling (are samples feasible & useful?).

### QUBO / solver toolkit
- QUBO: `min xᵀQx`, x ∈ {0,1}ⁿ. Linear terms on diagonal (x² = x), pair terms upper triangle.
- Constraint → penalty: square the violation. Cardinality: `P(Σx − K)² = P(1−2K)Σx_i + 2PΣ_{i<j}x_i x_j + PK²`.
- Assembled: `Q_ii = −μ_i + qΣ_ii + P(1−2K)`, `Q_ij = 2qΣ_ij + 2P` (i<j), offset `PK²`.
- Penalty P: too small → infeasible optimum; too large → objective signal squashed. Sweep P, check feasibility.
- Other patterns: one-of-group `P(Σ_G x − 1)²`; not both `P x_i x_j`; if i then j `P x_i(1−x_j)`; inequality needs slack bits (`s` binary-encoded). Too many auxiliary bits → rethink formulation.
- Ising: `s = 2x − 1`. Annealers use Ising form (`bqm.to_ising()`).
- Solvers: brute force (tiny), CP-SAT / HiGHS (exact baseline, ~20 lines), greedy / top-k (baseline, know where it fails), simulated annealing, tabu, simulated bifurcation (quantum-inspired, legit), quantum annealing (D-Wave, embedding/chain breaks), QAOA (cost + mixer layers, classical optimizer loop).
- **No established quantum advantage for optimization.** Formulation, verification, benchmarking are the value.
- Benchmark metrics: gap to reference within budget `E_best,r(B) − E_ref` (median + spread over runs), time-to-target. Repeat across seeds + instances.
- Workflow: problem → model → algorithm → decode to domain → evaluate vs baseline. Loop back anytime.

### Responsibility (must appear in pitch)
- Model decides for someone else. Ask: who is affected, who is left out, what does model not see, who notices if it fails, how to explain the number in 30 s.
- Finance example: opaque quantum risk scores that a regulator can't reproduce.
- Kop et al. (2024) principles: inclusion, societal relevance, responsibility (feedback loops).
- Engage Policy Practice Team advice and document what changed because of it.

### Key references (Finance)
- Mandatory: Markowitz (1952); Qiskit Finance portfolio optimization tutorial; Ken French Data Library (data source); PennyLane QUBO + QAOA demos; Qamomile (cross-SDK bridge, model→backend flow).
- Recommended: Ledoit & Wolf (2004); Herman et al. (2023); Stopfer & Wagner (2025/26) quantum portfolio benchmark; Sakuler et al. (2025) real-world quantum annealing test.
- Further: Egger et al. (2020); Orús et al. (2019); Acharya et al. (2025) decomposition; Soloviev & Krompiec (2026) Pauli correlation encoding; Chang et al. (2026) quantum stochastic walks.
- Out of scope: option pricing papers. **Exception:** Woerner & Egger (2019) quantum risk analysis / amplitude estimation IS in scope for the task's risk route (see §3).

---

## 3. THE TASK: "Portfolio decisions under changing assumptions" (source: `Task/` photos)

**Question:** when is keeping an existing portfolio vs changing it justified? Keep / accept proposal / pick new portfolio can each be defensible. Model must separate **binding restrictions** (loss tolerance, concentration limit) from **tradeable preferences** — do not hide everything in one score.

**Setup**
- Universe: 6 Ken French industry portfolios (from 10 Industry, value-weighted, monthly): `NoDur, Manuf, Enrgy, HiTec, Hlth, Utils`. US research portfolios, not stocks/ETFs.
- Data: 120 months, Jan 2015 – Dec 2024. **Estimation window Jan 2015 – Dec 2019 (60 months)**, decision date 31 Dec 2019. Jan 2020 – Dec 2024 = held-out evaluation only. **No later data in initial estimates.**
- Current portfolio: NoDur, Hlth, Utils, 1/3 each.
- Supplied proposal: replace NoDur with HiTec.
- **Supplied data: `Database/returns_6_industries_monthly.csv`** (verified, SHA-256 `083dbb43…`). Organiser reference notebook: `Database/Finance_Six_Industries_Verified.ipynb`. It solves all 3 routes, is probably AI-generated, so inspect it rather than adopt it. Review: `docs/routes.md` §−1.
- 3 mandates (λ / loss threshold / tolerance / HiTec cap): growth 1 / 8% / 10% / 100%; balanced 5 / 5% / 10% / 35%; risk-sensitive 20 / 3% / 10% / 20%. Change penalty 0.002 × one-way turnover. Scenarios: 60 months at 1/60 each, plus return stress (HiTec −0.5pp) and covariance stress (corr 25% → +1).
- Simplified holdings-change term allowed (reluctance to switch). Not a full trading-cost model — say so.
- Laptop + local simulator enough. No hardware/accounts needed.
- Mid-hackathon: we get an AI assistant's 5-minute answer → treat as baseline to inspect, not adopt. Situation will change (e.g. mandate threshold, input assumption) → pipeline must re-run fast and show what changed and why.

**Problem explained in plain language, with per-mandate verdicts and break-evens: `docs/problem.md`. Deep dive per route + data review: `docs/routes.md`. Concrete solution paths, shared code backbone, timeline, roles: `docs/solution_paths.md`. What the paths mean + mandate types + quantum model catalog: `docs/paths_mandates_models.md`. Client research (German "gesetzliche Kapitalrente" public fund, mandates = age cohorts): `docs/client_germany.md`. **Route C deep dive (robo-advisor client, Dicke+XY QAOA, prototype results): `docs/route_c.md`.** **ROUTE DECIDED (16 Oct): Allocation (C). Formal problem = `docs/problem_formulation.md` (single source of truth). Decision log = `docs/decisions.md`.** **Client: German government / Kapitalrente public fund; profiles = age cohorts; 3-of-6 = satellite tilt.** Parameters + algorithms: `docs/problem_formulation.md` §11–12. Downloaded sources + index: `sources/README.md`.**

**Pick ONE route** (each complete on its own):
1. **Risk route** — fixed allocation; P(one-month loss > declared threshold) consistent with mandate? Use supplied discrete scenario table + amplitude-estimation starter (Qiskit, local sim). Scenario probabilities = modelling inputs, not derived from μ/Σ. Repeat under supplied alternative scenario settings. Breach → supports review, not a trade.
   Deliver: working local example, documented state prep + event marking, estimated probability **with estimation uncertainty**, interpretation of what it does/doesn't establish.
2. **Circuit-design route** — define small set of conditions from evidence; reversible circuit (CX, Toffoli/CCX) encoding their logic. Binding vs tradeable distinguished. Be honest: flag loaded after classical calc ≠ comparison done inside circuit.
   Deliver: annotated circuit, input/output definitions, truth table, worked accepted + rejected financial cases.
3. **Allocation route** — pick 3 of 6 industries (1/3 each, no shorts/borrowing). 6 binary vars → QUBO/Ising → QAOA or other justified quantum/quantum-inspired method on local sim. Only C(6,3)=20 portfolios → supplied exact enumerator = verification reference, not competition. If using a change penalty: explain meaning, verify binding restrictions respected.

**Robustness (required):** never one run. Base case + ≥2 supplied changes. Separate changes from (a) financial assumptions, (b) mandate choices, (c) computational representation.
- Risk: estimation-probability uncertainty vs scenario-model uncertainty.
- Circuit: condition that fails vs evidence missing.
- Allocation: are selected holdings stable when estimates / penalties / restrictions change? Unchanged conclusion also informative if test + limits explained.

**Responsibility:** work with GTPP policy advisers (EU Finance domain sheet). Pick ONE institutional/responsibility question and build it **into model / circuit / sensitivity / recommendation**, not just the note. Options: evidence an investment committee or model-validation team needs; mandate condition binding vs preference; explaining financial-estimate uncertainty vs computational variation (shots, noise); external compute provider dependency.

**Deliverables**
- Defensible financial problem: decision, mandate, evidence, restrictions, assumptions, what counts as justified conclusion.
- Concrete quantum contribution: reproducible implementation (or checkable circuit + truth table + cases).
- Mandate + sensitivity result: base case, changes, what is stable, what explains change.
- Findings note ≤ 2 pages.
- **Decision log** (`docs/decisions.md`): variants tried/discarded and why, incl. where we did NOT follow an AI suggestion. AI use allowed — document where/how.
- Responsibility note with GTPP advisers: issue that changed analysis, what's outside model, what's needed before real institution relies on it.
- 5-min pitch + **A5 Decision Card**: one-sentence recommendation, who gains/loses, confidence + why, the one condition it should not be followed, what AI suggested vs what we did.

**Assessment:** financial meaning, correctness of representation, traceability, changing assumptions, reproducibility/checkability, limitations + responsibility. Quantum calc alone not enough. Small transparent result > big unexplained one. **No quantum-advantage claims.**

**EU policy context (GTPP sheet):** client = e.g. investment committee (internal pilot), model-validation team, or supervisor. Separate approvers / users / investors bearing losses. MiFID II suitability (fit client objectives, risk tolerance, loss capacity; switching needs cost-benefit). ESMA + national competent authority (e.g. BaFin). DORA: ICT risk + external compute providers. GDPR if personal data. AI Act only if system qualifies. Mandate vs internal limit vs binding rule vs guidance = different legal status. Variance/covariance miss liquidity risk.

**Task sources:** Ken French 10 Industry data; Qiskit Finance portfolio tutorial; Woerner & Egger (2019) quantum risk analysis (arXiv 1806.06893); IBM CCXGate docs; Kop et al. (2024) responsible quantum innovation.

---

## 4. Code map (allocation route, `src/qhf/`)
- Setup: `pip install -e .` and `pip install -r requirements-dev.txt`. Tests: `python -m pytest -q` (add `-m "not slow"` for the fast subset).
- Run: `python scripts/run_all.py run --canonical` (full run → `results/canonical/`). Use `--fast` for a demo, `--set key=value` for the mid-hackathon change, and `diff <runA> <runB>` to see what changed.
- Modules:
  - `config` (all parameters), `data` (checksum + windows), `scenarios`
  - `portfolio` (objective, loss rule), `exact` (answer key), `decision` (verdict, break-even), `sensitivity`, `evaluation` (2020–24)
  - `bits`, `qubo`, `circuits` (Qiskit: Dicke, XY, cost), `kernel` (numpy twin of the circuits), `qaoa` (experiment)
  - `plots`, `cli`
- Invariants (all tested):
  - QUBO energy == objective for all 64 states
  - kernel == Qiskit statevector
  - XY mixer conserves Hamming weight
  - 2020–24 never changes a decision

## 5. Definition of done (per task)
1. Code runs from clean env, seeds fixed.
2. Result checked vs brute force or exact solver on small instance.
3. Feasibility of outputs checked.
4. Tests pass.
5. Assumptions + limitations written down (for slides).
6. Short caveman summary to team: what changed, what verified, what not.
