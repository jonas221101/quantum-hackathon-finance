# Review of the MBB pitch deck (30 Oct 2026)

Reviewed file: `MBB_Pitch_Presentation_reviewed.pptx` (23 slides, slides 1 and 3 hidden and left as they were).
Every number was checked against `results/canonical/summary.json` and the CSVs next to it. Charts on slides 14 to 21
were redrawn by `python scripts/make_slide_figures.py` (output: `results/canonical/figures/slides/`), so anyone can
reproduce them from the canonical run.

## Factual errors fixed

| Slide | What it said | What is true (and now on the slide) | Source |
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

The three portraits are on slide 13 (the saver cards) and on the story slides 18, 19 and 20, as round crops with a
border in each saver's card colour: green = Lena, amber = Thomas, pink/red = Anna. Files: `docs/deck/assets/`.
Swap them if the team meant a different pairing.

## Open points for the team

1. Slide 2 lists "Ivan .", "Manyu ." and "Mingzhi .": surnames missing.
2. The deck said "10-Minute Executive Pitch"; the syllabus gives 20 minutes for the final pitch. Now it says "Final pitch,
   30 October 2026"; confirm your slot length.
3. Slide 22 labels the recommendations "REVISED" and "ADOPTED": say what was revised or adopted, and by whom (Policy
   Practice Team?).
4. Hidden slides 1 and 3 and the meme slides (4, 5, 7, 10) were not changed.
5. The deck has no speaker notes; the notes in `Quantum_Hackathon_28_10_updated.pptx` cover the same results.
