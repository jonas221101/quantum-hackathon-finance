# Slide deck source

`deck.json` (order, sections, fonts) and `slides/*.html` (one slide each, 1920x1080, inline styles) are the source of the
published 15-slide deck (claude.ai Artifact, Slides type). Slide order is in `deck.json`.

Figures on slides 6, 7, 9, 10, 11 and 12 are PNGs from `results/canonical/figures/` (uploaded as artifact assets; in the slide files they appear as `/_blob/<id>` URLs). Numbers come from `results/canonical/summary.json`. After a re-run, re-upload the PNGs and update the numbers.

## PowerPoint

`Quantum Hackathon Finance – Project Plan 16-10.pptx` is the sprint presentation (19 slides, 16:9, speaker notes).
It merges the team's "Project Plan" deck into ours (16 Oct 2026):

- **Design:** ours (Cambria titles, Calibri body, navy / teal / gold / orange).
- **Naming convention:** the team's.
  - File names follow `Quantum Hackathon Finance – <Name> DD-MM.pptx`.
  - Kickers are unnumbered ("CLIENT", "HOW IT WORKS", "RESULTS · CANONICAL RUN").
  - Terms: "the insured", "rule-preserving QAOA", "organiser's penalty QAOA", "pts".
- **Added from the team deck:** "The story we want to tell", "What happened so far", "Major milestones", "Fallbacks"
  and "What we need from you" (which closes with the Decision Card condition).
- **Replaced:** our old "Next steps" slide, now covered by the milestones slide.

Order:
1. title
2. story
3. problem
4. client
5. what happened so far
6. decision
7. rules
8. 20 options
9. how it works
10. quantum vs quantum
11. QAOA results
12. verdicts
13. what would change the answer
14. hindsight
15. responsibility
16. limits
17. milestones
18. fallbacks
19. what we need from you
