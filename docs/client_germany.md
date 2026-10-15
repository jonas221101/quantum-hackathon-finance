# Client: German state pension investing in equities ("gesetzliche Kapitalrente")

Researched 2026-10-15. Primary source: the report of the Alterssicherungskommission (23/24 June 2026),
stored at `sources/papers/germany/2026-06-24_Bericht_Alterssicherungskommission.pdf` (+ `report_utf8.txt`).
Recommendations 27, 28 and 31 are on pp. 60–68. Status claims are from government pages and news, cited at the end.

---

## 1. Which program? (there are several, and they are easy to mix up)

| Program | What it is | Status (Oct 2026) | Relevant to us? |
|---|---|---|---|
| **Gesetzliche Kapitalrente** (Empfehlung 28) | Mandatory, capital-funded part *inside* the statutory pension (GRV). Additional 2% contribution invested on capital markets by a **public fund**, modelled on Sweden's premium pension | Recommended 23 June 2026. Coalition committee (2 July 2026) wants to implement all 33 recommendations "vollständig und zügig"; Merz targets legislation by end of 2026. **Not yet law** | **Yes, the best fit.** "The state invests part of pensions in stocks" |
| Frühstart-Rente | €10/month state premium per child aged 6–18 into a capital-funded depot; public default if parents do nothing | Cabinet bill 12 Aug 2026, retroactive to 1 Jan 2026; parliament still pending | Partly: same public fund should be used (Empfehlung 31) |
| Altersvorsorgedepot (Altersvorsorgereformgesetz) | Reformed subsidised *private* pension (replaces Riester), incl. a simple standard product with a cost cap | Passed Bundestag 27 Mar 2026; available from 1 Jan 2027 | Indirectly: allows a public standard depot by regulation |
| Generationenkapital (Ampel, 2024) | Debt-financed state fund (target ~€200bn), returns to subsidise the GRV | **Failed** with the coalition collapse (Nov 2024); superseded | Historical comparison only |
| Versorgungsfonds / Versorgungsrücklage des Bundes | Funds for civil-servant pensions, managed by the Bundesbank, equity quota historically 20% → 30%, sustainable indices since 2021 | Existing | Useful precedent for governance and quotas |
| KENFO | €24bn-scale public fund financing nuclear-waste disposal | Existing | Named by the commission as a **template** for the Kapitalrente fund |

**Recommendation:** use the **gesetzliche Kapitalrente public fund** as our client. It is current, real,
undecided (so open design choices remain), and it fits an EU / German policy setting exactly as the GTPP sheet requires.

---

## 2. What the commission actually proposes (Empfehlung 28, pp. 60–62)

- **Mandatory** for contributors to the GRV; **individual capital accounts** that are **not inheritable**.
  Risks are pooled ("Sozialversicherung, Risiken werden im Kollektiv ausgeglichen").
- **Contribution:** extra **2% of gross wage**, split equally between employer and employee, phased in at
  **+0.5pp per year, ideally from 2028**. Full 2% after four steps (≈ 2031).
- **Vehicle:** a **public, internationally competitive fund**, e.g. built like **KENFO**. Opt-out is possible
  into a **small number of certified private funds** that meet the same strict criteria.
- **Investment principles:**
  - professional, long-term
  - **as broadly diversified as possible** across single assets, asset classes, **sectors and countries**
  - **return orientation** comes first
  - **no political investment rules, no exclusion of whole countries or sectors**. Only **unethical
    investments**, after careful case-by-case review, may be excluded.
- **Risk management:** through broad international diversification, **lifecycle models** and long saving
  horizons. **No guarantees**: guarantees "have not proven themselves" because they conflict with return orientation.
- **Governance:**
  - capital protected from (political) misuse
  - investment decisions **independent of political influence**
  - **professional investment committee staffed by external experts**
- **Costs:** at most **10 basis points (0.1%) per year** effective. Sweden's AP7 is about 0.05–0.06%.
- **Transparency:** performance must be communicated openly, "also in difficult market phases".
- **Payout:** together with the pay-as-you-go pension as a **lifelong annuity**, using realistic life-expectancy estimates.
- **Transition factor** (from 2032 retirees, tax-financed): protects people who are too old to benefit from
  the capital part. It is phased out as the capital pension grows.
- **Frühstart link** (Empfehlung 31): each child gets a Kapitalrente account at the GRV at age 6. The capital
  can move into the Kapitalrente at 18, and the public fund could also serve as the public standard depot.

**Swedish reference (AP7 Såfa, the default fund the commission points to):** 100% equities up to age 55
(with leverage, about 1.25×; older sources say 1.5×). From 56 to 75 the allocation shifts yearly into bonds,
reaching about **1/3 equities, 2/3 bonds at 75**. Fees about 0.05%.

**Still open** (good to say explicitly in our project): the equity share and glide path for Germany, the
exact ESG / exclusion policy, the fund's legal form and supervisor, certification criteria for private funds,
and payout indexation. The Greens' Kleine Anfrage 21/7876 (7 Sep 2026) asks exactly these questions.

---

## 3. The variables

### 3.1 Program / policy variables (set by law)
| Variable | Value / range | Source |
|---|---|---|
| Contribution rate | 2% of gross wage (target) | Empf. 28 |
| Phase-in | +0.5pp/year, from 2028 | Empf. 28 |
| Split | 50/50 employer/employee | Empf. 28 |
| Coverage | all GRV contributors; later also self-employed, MPs, AG board members | Empf. 1x, FAQ |
| Account type | individual, non-inheritable, pooled risk | Empf. 28 |
| Vehicle | public fund (KENFO-like) + limited certified private funds | Empf. 28 |
| Cost cap | ≤ 0.10% p.a. effective | Empf. 28 |
| Guarantees | none | p. 307 ff. |
| Payout | lifelong annuity, joint with GRV pension | Empf. 28 |
| Transition factor | for retirees from 2032, tax-financed, phased out | Empf. 15 |
| Pension level floor (context) | 48% until 1 July 2031 (Haltelinie) | report p. 238 |
| Frühstart premium | €10/month, ages 6–18 (= €1,440) | BMF / Empf. 31 |

### 3.2 Investment-mandate variables (set by the fund's investment committee): **our model's levers**
| Variable | Commission position | Open range to model |
|---|---|---|
| Objective | return-oriented, long-term | λ (risk aversion) per age cohort |
| Strategic equity share | not fixed; lifecycle | e.g. 100% (young) → 33% (75), as in AP7 |
| Glide path start/end age | not fixed | AP7: 55 → 75 |
| Diversification | max broad: assets, sectors, countries | **sector / concentration caps** |
| Exclusions | no country/sector bans; only unethical, case by case | exclusion yes/no; ESG integration |
| Leverage | not mentioned | 1.0× vs AP7 1.25× |
| Turnover / rebalancing | implied by cost cap | change penalty τ calibrated to the 10 bp budget |
| Private assets / VC | not mentioned; asked by the Greens (Q13) | out of scope / extension |
| Transparency | performance shown also in bad markets | decision record, Decision Card |

### 3.3 Member variables
Age / remaining horizon, wage path, contribution years, life expectancy, choice (public fund vs certified fund).

### 3.4 Outcome and risk variables
Expected real return (the Greens cite about 3.5% real global equity 2000–2025, UBS), volatility, drawdown
near retirement (sequence risk), probability of a loss above a threshold, costs vs the 0.1% cap, the
resulting pension level, and the contribution burden (WSI estimate: −1pp growth, −250,000 jobs from 2028,
which is contested).

---

## 4. Mapping onto our hackathon model

| Hackathon element | Kapitalrente interpretation |
|---|---|
| **Client / decision-maker** | The **investment committee of the public Kapitalrente fund** (external experts, independent). The **next-stage decision**: approve a sector rebalancing rule for the equity sleeve. Approvers = committee; users = fund managers; loss bearers = **insured people**, especially those near retirement |
| 6 industry portfolios | Sector sleeves of the fund's equity portfolio. Caveat: US data, while a real fund would be global. Treat it as a stand-in and state that |
| Current portfolio (NoDur/Hlth/Utils) | Existing defensive sector tilt |
| Proposal (→ HiTec) | "Rotate into tech for higher expected return" |
| **Growth mandate** | **Cohort under 55**: 100% equity phase, long horizon |
| **Balanced mandate** | **Cohort 55–65**: inside the glide path |
| **Risk-sensitive mandate** | **Cohort 65–75**: near or in payout, high sequence risk |
| HiTec cap (20/35/100%) | **Concentration limit** implementing "breit gestreut … Branchen". Binding, and it comes from the commission's diversification principle rather than an ESG judgement |
| Loss threshold + tolerance | Risk budget per cohort ("no guarantees" means risk control via lifecycle, so a loss-probability limit is the natural tool) |
| Change penalty τ | **Cost discipline from the 10 bp cap**: turnover consumes the cost budget |
| Evidence missing → review | Liquidity of positions, real cohort data, ESG facts: not in our data |
| Exclusion idea (e.g. Enrgy) | **Live policy conflict**: the commission says *no sector exclusions*, while the Greens push ESG. Our model can show the cost of an exclusion (here zero, since Enrgy is never optimal), which is a strong policy finding |
| Responsibility hook | Independence from politics, transparency in bad markets, DORA / external provider if a quantum service were used, explaining to 40+ million insured people |

This mapping makes the existing three mandates **meaningful as age cohorts** and gives each parameter a
real-world justification. That is exactly what the task means by "a defensible financial problem".

**Honest limits:** the commission sets *principles*, not numbers for caps, loss tolerances or λ. Those
remain our documented assumptions. A real public fund would be global and multi-asset; our 6 US sectors
are a teaching instance.

---

## Sources
- Alterssicherungskommission report, 24 Jun 2026 (local PDF): https://www.bundesregierung.de/resource/blob/975228/2444780/0fcbf810775351c64007ee6cb2c7cad9/2026-06-24-bericht-alterssicherungskommission-data.pdf
- BMAS, Rentenkommission 2026 – 33 Empfehlungen: https://www.bmas.de/DE/Soziales/Rente-und-Altersvorsorge/Rentenreform-2025/Rentenkommission-2026/rentenkommission-2026.html
- Bundesregierung FAQ: https://www.bundesregierung.de/breg-de/aktuelles/faq-rentenreform-2444534
- BT-Drs. 21/7876, Kleine Anfrage (Greens) on the Kapitalrente (local PDF): https://dserver.bundestag.de/btd/21/078/2107876.pdf
- Frühstart-Rente cabinet bill (BMF, 12 Aug 2026): https://www.bundesfinanzministerium.de/Content/DE/Pressemitteilungen/Finanzpolitik/2026/08/2026-08-12-regierungsentwurf-fruehstartrente.html
- Frühstart-Rente key points: https://www.bundesregierung.de/breg-de/aktuelles/kabinett-fruehstart-rente-2399880
- Altersvorsorgereformgesetz passed: https://www.dihk.de/de/newsroom/bundestag-verabschiedet-altersvorsorgereformgesetz-175842
- Generationenkapital bill (2024): https://dserver.bundestag.de/btd/20/118/2011898.pdf
- AP7 Såfa lifecycle: https://www.ap7.se/english/ap7-safa/
- Versorgungsfonds equity quota (Bundestag): https://dserver.bundestag.de/btd/19/182/1918270.pdf
