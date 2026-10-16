# Decision Card (A5)

**Question:** Which three of six US industries should the Kapitalrente fund's satellite tilt hold on 31 Dec 2019?
Client: German government (public Kapitalrente fund). Profiles are chosen actively by each insured person; non-choosers get *balanced* (open assumption).
Numbers: `results/canonical/summary.json`.

## Recommendation (one sentence per profile)

* **Growth: switch** from NoDur + Hlth + Utils to **HiTec + Hlth + Utils**; same winner in all three scenario sets, and it beats the current tilt in 89 % of bootstrap resamples.
* **Balanced: review.** Hold for now; switch to HiTec + Hlth + Utils only if the committee states a belief that tech's monthly edge stays above about 0.37 points.
* **Risk-sensitive: keep** NoDur + Hlth + Utils; it wins in every scenario set and passes the loss rule in 76 % of resamples.

## Who gains, who loses

| | Gains | Loses |
|---|---|---|
| Switch (growth) | Higher expected return (about +0.29 points per month in 2015-19) | More sector concentration and bigger swings; pay the switching cost |
| Keep (risk-sensitive) | Lowest volatility of all 20 portfolios; no switching cost | Give up return if tech keeps winning |
| Review (balanced) | Nobody is committed on a thin margin (score margin 0.0012) | Delay; people on the default profile wait for a decision |

The insured bear the losses. People on the default (*balanced*) are the most exposed to the fragile answer.

## Confidence and why

* **Growth: fairly high.** Robust to both stresses; beats current in 89 % of resamples; far from its break-even (HiTec edge −0.60 points).
* **Risk-sensitive: moderate to high.** Winner everywhere, but it passes the loss rule in only 76 % of resamples, and in 12.6 % no portfolio passes at all.
* **Balanced: low.** Near-tie; flips under the return stress; proposal beats current in only 74 % of resamples.
* Overall limit: 60 months, US data, assumed mandate numbers.

## The one condition under which NOT to follow it

**Do not follow the switch if tech's 2015-19 edge came from a rally you do not expect to continue.**
Do not rely on the model's loss estimate either: in 2020-24 the share of months with a loss above the profile's own threshold was higher than estimated (20 % for the risk-sensitive threshold of 3 %).

## What the AI tool suggested vs what we did

| AI suggestion | What we did |
|---|---|
| Organiser notebook (probably AI-written): penalty QAOA, rules as score penalties | Dicke + XY QAOA; binding rules are structure or exact checks; every result graded against the exact answer; penalty version also tuned and compared fairly |
| Claude recommended the risk route and a robo-advisor client | Team chose the allocation route and the German Kapitalrente fund |
| Claude proposed age-based profiles | Team rejected: profiles are chosen actively, to avoid unequal treatment of generations |
| Claude treated the HiTec cap as binding | Team changed it to a preference (penalty 0.01); verdicts identical with the penalty at zero |
| Claude's first verdict rule (optimum alone) | Tightened after code review: switching needs 70 % bootstrap support; burden of proof on the change |

Full log: [decisions.md](decisions.md). No quantum advantage is claimed.
