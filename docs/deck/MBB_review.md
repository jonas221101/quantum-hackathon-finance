# Review of the MBB pitch deck (30 Oct 2026)

**Final deck: `Pitch_Deck_30_10.pptx`** (see "Final pass" at the end). Reviewed file of the first two passes: `MBB_Pitch_Presentation_reviewed.pptx` (23 slides, slides 1 and 3 hidden and left as they were).
Every number was checked against `results/canonical/summary.json` and the CSVs next to it. Charts on slides 14 to 21
were redrawn by `python scripts/make_slide_figures.py` (output: `results/canonical/figures/slides/`), so anyone can
reproduce them from the canonical run.

## Factual errors fixed

| Slide | What it said | What is true | Source |
|---|---|---|---|
| 12 | Core 85 %, satellite 15 % | Core 90 %, satellite 10 % (`satellite_share = 0.10`) | `src/qhf/config.py` |
| 12 | Core = "MSCI World style" | A broad index, not modelled; we take it as given | README |
| 14, 17, 20, 23 | Today's basket volatility 3.01 % | 2.71 % a month (still the lowest of all 20) | `exact_rankings.csv` |
| 14, 17 | Proposal volatility 3.61 % | 3.05 % a month | `exact_rankings.csv` |
| 14 | "Tech delivered +29 % annual return" | +0.29 points a *month* for the basket (1.02 % vs 0.73 %); tech alone averaged 1.51 % a month | `exact_rankings.csv` |
| 17, 18 | Returns 1.25 % (Lena) and 0.96 % (Anna) | 1.02 % (tech basket) and 0.73 % (today's basket) | `exact_rankings.csv` |
| 17 | Thomas 1.08 %, 3.25 % volatility | Not in our results; replaced by the tech basket's lead (12 bp on the score) and 2.71 % vs 3.05 % | `summary.json` |
| 17 | Thomas "74 %, sub-decisive" | 74 % passes the 70 % bar; the *stress flip* is what sends him to review | `decision.py` |
| 17 | Anna "76.4 % optimal across resamples" | Today's basket *passes her loss limit* in 76 % of replays (it is optimal in 49 %) | `summary.json` |
| 17, 20, 23 | Proposal "breaches the strict legal safety rule" | It sits exactly on Anna's limit (6 of 60 months, 6 allowed); it fails under a strict "fewer than" reading and in both stress tests (7 and 9) | `loss_limits.csv` |
| 18 | Co-movement stress "+30 %" | Correlations moved 25 % closer to 1 | `config.py` |
| 18 | Transaction cost "0.2 %" | 0.2 % is the rate per unit of turnover; the actual one-off cost is about 0.07 % (one third of the basket changes) | `config.py` |
| 20 | "Switching net utility gain is exactly 0.0" | For Anna the tech basket scores 30 bp a month *worse* | `estimation_error.csv` |
| 20 | Chart: decision map with *balanced* rules on Anna's slide | Anna's own chart: her loss months per test setting | new figure |
| 11 | "Pension law requires monthly losses to stay within strict limits" | The loss limits are our mandate assumptions (organiser setup); the fund itself gives no guarantees | `docs/decisions.md` |
| 13 | Thomas: "By law, I represent all citizens who did not choose" | Non-choosers go to balanced in *our* model (an open assumption, not law) | `docs/decisions.md` |
| 9 | Advisee = "German public investment fund committee (BMF)" | The fund's independent investment committee; the BMF is a ministry | `docs/client_germany.md` |
| 9 | Savers "directly invest" | 2 % of gross wages go into a public fund from 2028 | `docs/client_germany.md` |
| 16 | "Only 32 % valid for standard quantum methods" | 32 % is the *tuned* penalty for Anna; the organisers' circuit reaches 97 to 98 % valid, but at guessing-level accuracy | `quantum_summary.csv` |
| 16 | 78 % "on Anna's portfolio" without context | Added: Lena 23 %, Thomas 4 % (no better than guessing) | `quantum_summary.csv` |
| 15, 23 | "Physically cannot", "hardware-enforced guardrails" | By construction, in ideal simulation; real noisy hardware would still need a check | `qaoa.py` |
| 23 | "15x precision advantage" | Only for Anna (0.78 vs 0.05); no better for Thomas; no quantum advantage | `quantum_summary.csv` |
| 23 | "Foundation for 50+ sector universes where classical enumeration fails" | Next step, not a result: test larger universes against strong classical solvers; no scaling claim | — |
| 22 | "The commission recommended active choice to avoid generational unfairness" | The commission relies on lifecycle models; active choice is *our* team decision | `docs/client_germany.md`, `docs/decisions.md` |
| 22 | The same "fiduciary implication" sentence three times | Three different implications, one per recommendation | — |
| 21 | "Tech boomed during COVID (1.86x)" | 1.86x is the whole of 2020 to 2024 | `holdout.csv` |
| 6 | €100 → ~€75 (2035), < €45 (2050), no assumption given | About €76 and €48 at 3 % inflation and 0 % interest; the assumption is now on the slide | arithmetic |
| 8 | "You have no clue about finances" (addresses the jury) | "We are students, not your financial advisers"; the joke stays | — |
| 16 | Typo "eisfies" | "keeps the 3-sector rule" | — |

## Pitch pass: less text, one message per slide

After the fact check, slides 11 to 23 were cut down for a spoken pitch (the details above are what the speaker
should be able to answer, not what the slide must show):

* **Title = the message**, 26 pt, at most about ten words (for example "Thomas: the data cannot tell the two
  baskets apart").
* **Cards: 2 to 4 short lines in 17 to 18 pt** instead of 8 to 10 bullets in 9.5 pt; big numbers where a number is
  the point (90 % / 10 % / 20 on slide 12; 100 % / 78 % / 4 % on slide 16).
* **Key takeaway: one short sentence in 15 pt** (for example "Too close to call → hold.").
* Portraits also on the results overview (slide 17), so each saver is recognisable at a glance.
* Section labels shortened ("3. THE SAVERS"); sources kept, one line per slide.

## Charts redrawn (slides 14 to 21)

All in the deck's colours (today's basket blue, tech basket orange, our circuit blue, the organisers' grey), Calibri-metric
font, values labelled on the chart.

| Slide | Old chart | New chart |
|---|---|---|
| 14 | Generic 20-basket scatter | Scatter with today's basket and the proposal labelled (return and risk) |
| 15 | Unreadable text dump of the circuits | Diagram: penalty circuit vs our circuit, step by step |
| 16 | Six-method grid, small text | Legal answers and best-basket chance per saver, three methods |
| 18 | Bootstrap bars for all profiles | Lena's 500 replays: tech basket better in 89 % |
| 19 | Decision map | Thomas: lead vs tech's return, with the noise bands; flip at −0.37 |
| 20 | Decision map with balanced rules (wrong profile) | Anna's loss months per test setting vs her limit |
| 21 | Two small charts | One wide chart: wealth 2020 to 2024 and real loss months per saver |

## Team portraits

The three portraits are on slide 13 (the saver cards), the results overview (slide 17) and the story slides 18, 19 and 20, as round crops with a
border in each saver's card colour: green = Lena, amber = Thomas, pink/red = Anna. Files: `docs/deck/assets/`.
Swap them if the team meant a different pairing.

## Final pass: one style everywhere (`Pitch_Deck_30_10.pptx`)

The MBB deck had two styles (meme intro on navy with pastel stripes, content slides on white with many card variants).
The final deck is generated by `scripts/build_pitch_deck.js` from `results/canonical/deck_data.json`, so the style and the
numbers cannot drift apart.

| What | Before | Now |
|---|---|---|
| Layouts | Every slide placed by hand | 4 layouts: dark title, dark, dark with picture, light content |
| Light slides | Title, cards and key takeaway in different places | Same label, title, takeaway bar, source and page number on every slide |
| Order | Quantum before results | Story first (problem → savers → decision → results), then the circuit, then the reality check |
| Text | 2 to 4 lines per card, 15 to 26 pt | One message per title; card text 18 to 22 pt; big numbers where the number is the point |
| Charts | PNG images | Native PowerPoint charts (scatter, histogram, bars with limit line, wealth line); Thomas's number line and the circuit diagram as shapes |
| Thomas | "74 % of replays: too close" (contradicts the 70 % rule) | 74 % passes the 70 % bar; the stress test (−0.5) flips him, his flip point (−0.37) lies inside the estimate's uncertainty (±0.58) |
| Quantum chart | Axis with decimals, crowded labels | Percent labels on the bars, no axis clutter, same three colours as the legend |
| Wealth chart | "Growth of 1 unit" | "€1 invested in 2020: €1.86 (tech) vs €1.38 (today)" |
| Hidden slides 1 and 3 | Kept hidden | Dropped |
| Speaker notes | None | 20 to 80 words on every slide, written to be read aloud |

## Open points for the team

1. Slide 2 lists "Ivan .", "Manyu ." and "Mingzhi .": surnames missing.
2. The deck said "10-Minute Executive Pitch"; the syllabus gives 20 minutes for the final pitch. Now it says "Final pitch,
   30 October 2026"; confirm your slot length.
3. Slide 22 labels the recommendations "REVISED" and "ADOPTED": say what was revised or adopted, and by whom (Policy
   Practice Team?).
4. The meme slides keep the team's jokes; the Pink Panther GIF is cropped so the makeagif.com watermark is gone. Check that you have the rights to use the memes in front of external guests.
5. Speaker notes are drafts: each speaker should say them in their own words and check the timing (22 slides, about 10 minutes at 25 to 30 s per slide).
