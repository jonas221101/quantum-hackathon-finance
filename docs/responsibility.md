# Responsibility note

Written for the GTPP policy advisers and for any investment committee or validation team that might see this work.
*(Numbers: `results/canonical/summary.json`. Statements about law and supervision are our reading from public sources and must be confirmed.)*

## 1. The issue we built into the model

> **When two answers differ, is the difference in the world, or in our computer?**

A committee must know which kind of uncertainty it is looking at. We keep two kinds apart, in the code and in every result:

| | Estimation uncertainty | Computational variation |
|---|---|---|
| Source | Only 60 months of data. A different sample would give different averages | Random starting points, number of shots, circuit depth, mixer |
| How we measure | **Bootstrap**: resample the 60 months at least 500 times, count how often each portfolio wins | **Seeds and shots**: repeat the quantum run many times (median and spread) |
| What it means | The *world* is uncertain | The *tool* is unsteady |
| Example | Balanced: two portfolios nearly tie, so resampling changes the winner | Median chance of sampling the best portfolio (risk-sensitive, 3 layers): 0.77, with seeds ranging 0.61-0.80; for balanced it is 0.04-0.25 depending on the objective |

How this changes the recommendation: a verdict is **Switch** or **Keep** only if the exact answer holds in all supplied scenarios and in at least 70 % of 500 bootstrap resamples (switch: beats current and passes the loss rule; keep: current passes). Growth: 89 %; balanced: 74 % but the optimum flips under the return stress, so Review; risk-sensitive: 76 %. If estimation uncertainty is large (balanced), the verdict is **Review**, and no amount of quantum
precision can fix that. The exact optimum is always computed, so the quantum search never decides a recommendation.

## 2. Informed, active choice of profile

* Each insured person **chooses** growth, balanced or risk-sensitive. It is not decided by age: age-based tilts would
  treat generations differently.
* A choice is only meaningful if the person understands what it means. The profiles differ in how much loss they accept; a
  monthly loss limit of 8 % versus 3 % must be explained in words, not just as a percentage.
* **Default effect.** Many people do not choose. We assume non-choosers get **balanced**. That is the profile with the
  most fragile answer. A default is a decision made for people, so it needs its own justification and a review date.
* Open: who designs the information given to the insured, and who is accountable if a default turns out badly?

## 3. What is outside the model

* **The size of the tilt** (the satellite share). The model decides which three sectors, not how large the tilt is.
* **The core.** The broad index that holds most of the money is not modelled.
* **Liquidity, real trading costs, taxes (a public fund pays none), ESG.** No data, so such questions get the verdict *Review*.
* **Global scope and other asset classes.** We use 6 US industries as a stand-in.
* **Pooled risk and the annuity.** The Kapitalrente is paid out as a lifelong annuity with pooled risk; our model only looks at monthly losses.
* **Politics.** The commission wants decisions independent of political influence. A tilt that follows a political view would break that. Our model has no such input, but someone must guard it.
* **Real mandate numbers.** Risk weights, loss limits and the tech limit are our assumptions.
* **Tail risk.** The loss estimate replays 60 months. In 2020-24 the realised frequency was higher (20 % for the risk-sensitive threshold of 3 %).

## 4. Before a real institution relies on it

1. **Governance:** the committee states its beliefs (tech edge, switching cost) and whether the tech limit is binding or a preference. Written and signed.
2. **Independent validation:** a team outside the project reruns `python scripts/run_all.py run --canonical` and compares results.
3. **Data:** longer history, global universe, tail-risk model beyond 60 replayed months.
4. **Explainability:** a 30-second explanation of each recommendation that a non-expert can follow, including its break-even.
5. **Disclosure:** show the stress results and the hindsight openly, "also in difficult market phases", as the commission asks.
6. **Cost cap:** check the effect of switching against the 0.1 % per year cost cap. The proposal uses about two thirds of a year's turnover budget at the assumed cost.
7. **Fairness check:** study who ends up in the default and whether they are worse off.
8. **Monitoring and re-run:** a trigger for when assumptions change, so the pipeline reruns and shows a diff of what flipped.

## 5. Context: Germany and the EU (our reading)

* **The fund.** The Kapitalrente fund is not yet law. The commission proposed a public fund *like KENFO* with an external expert committee, a cost cap of 0.1 % and no guarantees.
* **Supervision.** Open. For KENFO, legal supervision lies with a ministry (BMWE) and the finance ministry issues investment guidelines; BaFin is not named. If the fund sits inside the statutory pension, the pension insurer's supervisor (Bundesamt für Soziale Sicherung) would apply. A private-sector rule such as MiFID II suitability is **not** automatically applicable to a public fund; we use it as a good-practice yardstick.
* **DORA.** Probably does not apply to the foundation itself (not a listed financial entity), but it likely applies to its external asset managers and ICT providers. If any quantum cloud service were used, it would be an outside ICT dependency. We use local simulation only. A public fund dependent on a foreign quantum cloud is a sovereignty and resilience question.
* **Data protection.** Not an issue with market data; it would be with real member data (GDPR).
* **Status of rules.** A mandate, an internal limit, a binding rule and a guideline have different legal weight. That is why the tech limit is a preference in our model until the committee decides otherwise.

## 6. Who is affected

| Group | Effect |
|---|---|
| Insured who chose actively | Live with the consequences of their choice |
| Insured in the default | Bear a decision made for them |
| Committee | Must justify a switch, or a decision to keep |
| Future cohorts | May get a different tilt if assumptions change |
| Left out | People not covered by the statutory scheme; people who do not understand the profile choice |
