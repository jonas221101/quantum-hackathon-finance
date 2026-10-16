# NotebookLM Generation Prompt

Copy the prompt below into NotebookLM after uploading the source materials
listed in `README.md`.

---

Create a polished, professional 5–6 minute explanatory video about the
Quantum Finance portfolio-allocation project.

## Audience

The audience is a mixed investment-committee and technology audience. They
understand basic investing but may not know QAOA, qubits, QUBO, Dicke states,
or XY mixers. Explain each technical idea in plain language before using its
technical name.

## Editorial goal

Tell the story as a responsible investment decision supported by a quantum
computing experiment. The human decision comes first; quantum computing is the
methodological experiment, not the headline claim.

The central question is:

“Should the public fund’s small satellite tilt keep NoDur + Hlth + Utils, or
switch to HiTec + Hlth + Utils, for each investor mandate?”

## Required narrative

Follow this order:

1. Introduce the current tilt and proposed switch.
2. Explain that this is a satellite sleeve, not the whole pension fund.
3. Explain the six industries, the 2015–2019 estimation window, the
   2020–2024 holdout, and the 20 possible portfolios.
4. Explain Growth, Balanced, and Risk-sensitive mandates.
5. Explain the return, risk, switching-cost, concentration-preference, and
   binding loss-rule concepts.
6. Present the canonical recommendations:
   - Growth: Switch to HiTec + Hlth + Utils.
   - Balanced: Review because the answer flips under return stress.
   - Risk-sensitive: Keep NoDur + Hlth + Utils.
7. Explain binary variables, qubits, QAOA, the Dicke start state, and the XY
   mixer with a simple analogy followed by the accurate technical explanation.
8. Explain the comparison with the X-mixer penalty baseline and the exact
   classical enumeration.
9. Explain that IBM Qiskit Aer is used locally. Explicitly state that no IBM
   hardware or IBM cloud execution was used.
10. Close with robustness, limitations, and the statement that no quantum
    advantage is claimed.

## Tone

Use a calm, authoritative, transparent tone. Sound like a strong documentary
or public-sector technology presentation. Do not sound like an advertisement,
venture-capital pitch, or children's cartoon.

Use short sentences and natural transitions. Define jargon immediately. Say
“review” as a legitimate evidence-based outcome, not as a failure.

## Visual instructions

Use the supplied project figures and dashboard evidence wherever possible:

- risk/return figure
- decision map
- bootstrap figure
- QAOA comparison
- circuit diagram
- holdout figure

Use restrained motion: highlight a bar, trace a timeline, reveal a portfolio,
or zoom into a circuit. Do not generate generic stock footage, cartoon
characters, fake quantum particles, unrelated city shots, or invented data.

If a source figure is not readable in video format, recreate only its layout
and values from the source documents. Do not invent new values.

Keep important charts visible long enough to read. Use large captions:

- “Exact classical answer key”
- “IBM Qiskit Aer simulator, running locally”
- “No quantum advantage claimed”
- “Exactly 3 of 6 industries”

## Audio and pacing requirements

- Use one consistent professional narrator.
- Use a natural speaking speed with clear pronunciation.
- Add a short pause between sections and after each recommendation.
- Do not cut sentences, syllables, or word endings.
- Do not overlap narration with another narrator.
- Keep background music very quiet or omit it.
- Keep narration volume consistent across the whole video.
- Do not use sudden transitions, rapid montage editing, or overly short slides.
- Generate subtitles that match the final narration exactly.

## Accuracy guardrails

Never claim:

- quantum advantage
- faster performance than exact enumeration
- IBM hardware execution
- IBM cloud Runtime execution
- that the model represents the entire pension fund
- that historical returns are forecasts
- that the recommendations are personal investment advice

Use this wording:

“The experiment runs locally with IBM’s Qiskit Aer simulator.”

End with this message:

“The value of the project is an inspectable workflow: explicit rules, an exact
answer key, a constraint-aware QAOA experiment, robustness tests, and honest
limitations. Switch when the evidence survives the relevant stresses, keep
when risk and admissibility dominate, and choose review when the result is
fragile.”

---

## Optional NotebookLM follow-up prompts

### Improve the first draft

Make the narration 10 percent shorter without removing the explanation of the
three investor profiles, the exact classical answer key, local IBM Qiskit Aer
simulation, or the no-quantum-advantage limitation. Preserve all canonical
recommendations and percentages.

### Improve technical clarity

Rewrite the QAOA section so that a non-technical investment committee
understands the difference between a penalty-based X mixer and a
constraint-preserving Dicke-plus-XY approach. Keep the explanation technically
accurate and under 50 seconds.

### Improve visual pacing

Replace any generic or invented visual with a supplied project chart, a
dashboard capture, a clean portfolio diagram, or a readable timeline. Keep
each important chart visible for at least six seconds.
