# Decision log

Variants tried or discarded, and why. Includes where we did not follow an AI suggestion (task requirement).
Newest first.

| Date | Decision | Alternatives considered | Reason | AI involvement |
|---|---|---|---|---|
| 2026-10-16 | **Profiles chosen actively by each insured person** (growth / balanced / risk-sensitive), not by age. Default for non-choosers: balanced (proposal, open) | Age cohorts (lifecycle, AP7) | Team answer: age-based tilts create unequal treatment between generations | Claude had proposed age cohorts; **team rejected** |
| 2026-10-16 | **Sector cap = preference**, moved into the objective as a penalty κ·max(0, w_HiTec − cap) | Cap as a binding rule (removed qubit) | Team answer. Base-case verdicts unchanged: risk-sensitive keeps the current portfolio even without the cap (λ = 20 > break-even 11.2) | Claude had treated it as binding; **team changed it** |
| 2026-10-16 | Mandate values (λ, L, α, caps) labelled as assumptions (from the organiser config) | — | Team note | — |
| 2026-10-16 | Client confirmed: **public Kapitalrente fund**; satellite tilt accepted | Private pension (Altersvorsorgedepot) | Team answers in the shared doc | — |
| 2026-10-16 | **Main comparison: quantum vs quantum** (rule-preserving Dicke+XY QAOA vs organiser penalty QAOA); enumeration only as answer key | Quantum vs classical benchmark | Team note in the shared doc; avoids an unwinnable "beat classical" framing at 20 options | — |
| 2026-10-16 | **Client: German government (Kapitalrente public fund)**; 3-of-6 modelled as the cohort *satellite tilt*, core = broad index | Robo-advisor (Claude's recommendation for Route C) | Team choice. The tilt framing resolves the conflict with the commission's diversification principle | **Did not follow Claude's robo-advisor suggestion** |
| 2026-10-16 | **Route: Allocation (C)** | Risk (A), Circuit (B), Pipeline (D) | Team preference; richest sensitivity story; measurable improvement over the organiser baseline (prototype) | Claude recommended Route A for the pension-fund client. **Team chose C instead** |
| 2026-10-16 | Binding rules as structure / post-check, not penalties | Penalty-only QUBO (organiser notebook) | The task demands that binding restrictions are visible and respected; the penalty baseline produced 1–44% invalid samples in the prototype | Deviates from the organiser (AI-generated) notebook |
| 2026-10-16 | Loss tolerance H3 as an exact post-check | Encode it in the QUBO with auxiliary bits | A scenario probability is not quadratic in x; encoding would add many auxiliary bits (warning sign from the lecture) | — |
| 2026-10-16 | Three-state verdict: keep / switch / review | Single "optimal portfolio" | The balanced profile flips under the supplied return stress | — |
| 2026-10-15 | Client framing explored: robo-advisor vs German Kapitalrente | VC client (poor data fit) | A public pension fund holding 3 sectors conflicts with the commission's diversification principle | Claude suggested the robo-advisor |
| 2026-10-15 | Data: `Database/returns_6_industries_monthly.csv` as the single source | Own French download | Checksum verified, identical to our download (max diff 1e-16) | — |
| 2026-10-15 | Treat the organiser notebook as the "AI baseline" | Adopt it | It looks AI-generated (`/opt/codex` paths); its QAOA misses the risk-sensitive optimum in all 3 seeds | — |
