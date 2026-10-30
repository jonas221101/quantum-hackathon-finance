**Final pitch deck for 30 October: `Pitch_Deck_30_10.pptx`** (22 slides, PDF preview `Pitch_Deck_30_10.pdf`). It is the
team's MBB deck rebuilt in one design system, so every slide looks the same:

* dark slides for the hook (slides 1 to 7) and the close (21, 22); light slides for the content (8 to 20);
* on every light slide the same places: small blue label, title = the message, one takeaway bar, one source line, page number;
* the three savers always in the same colours (Lena green, Thomas amber, Anna red), today's basket blue, tech basket orange;
* native, editable PowerPoint charts (no screenshots) and speaker notes on every slide.

Rebuild it from the canonical run with two commands (numbers are never typed in by hand):

```bash
python scripts/export_deck_data.py               # results/canonical -> results/canonical/deck_data.json
npm install pptxgenjs@3.12.0                      # once
node scripts/build_pitch_deck.js                  # -> docs/deck/Pitch_Deck_30_10.pptx
```

What changed against the MBB deck and why: [MBB_review.md](MBB_review.md), section "Final pass". Portraits and memes: `assets/`.

**Fact-checked MBB deck: `MBB_Pitch_Presentation_reviewed.pptx`** (the team's original layout after the fact check, with
redrawn charts and the saver portraits). Charts: `python scripts/make_slide_figures.py` → `results/canonical/figures/slides/`.

**Earlier deck (28 Oct): `Quantum_Hackathon_28_10_updated.pptx`** (18 slides, PowerPoint). It is the team's 28 October deck with
three new figure slides from the canonical run (slide 10 `fig_estimation_error`, slide 12 `fig_success_rate`, slide 14
`fig_loss_limits`), refreshed quantum numbers on slide 11, the "Next steps" column on slide 15 and page numbers 2 to 18.
What changed and why: `docs/sync_eden_2026-10-29.md`, section 7. Every number comes from `results/canonical/`.

## Older source (15-slide claude.ai deck, 16 October)

`deck.json` (order, sections, fonts) and `slides/*.html` (one slide each, 1920x1080, inline styles) are the source of the
earlier 15-slide deck published as a claude.ai Artifact (Slides type). Its figures are PNGs from
`results/canonical/figures/` (uploaded as artifact assets; in the slide files they appear as `/_blob/<id>` URLs).
