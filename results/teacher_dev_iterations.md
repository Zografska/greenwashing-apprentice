# Teacher prompt iterations on dev (SPEC D9, CP2)

Dev = 150 fully reviewed texts (50 per class), gold = `dev_reviewed_label`. Provider: OpenRouter pinned to
`coreweave/fp4`, temperature 0, reasoning effort low, no provider JSON mode. At most 3 iterations.

| Iter | Prompt hash | Model | Macro-F1 | Acc | Valid | Consistency | F1 IS / NV / OUT | IS recall | Cost |
|---|---|---|---|---|---|---|---|---|---|
| 1 | b450d75e7e10a6f0 | gpt-oss-20b | 0.780 | 0.773 | 0.967 | 0.933 | 0.832 / 0.700 / 0.807 | 0.840 | $0.017 |
| 1 | b450d75e7e10a6f0 | gpt-oss-120b | 0.815 | 0.820 | 1.000 | 0.987 | 0.838 / 0.756 / 0.850 | 0.880 | $0.018 |

**Teacher choice (D9), after iteration 1:** gpt-oss-120b. 20b fails both conditions (3.5 macro-F1 points
behind, threshold 3; consistency 93.3% < 95%).

**Iteration 1 → 2 changes** (from the 27 errors of 120b): the teacher read the task as environmental impact
only. Added a SCOPE note (green and ethical claims; no green word required; any matching part triggers) and
conventions: organic/certification anywhere (incl. EU organic codes, bare scheme names, «filiera certificata»);
undefined "naturale" in any sentence; named endorsements in any domain; concrete farming/fishing practices vs
vague supply chain; packaging material with a figure → NV; ingredient-growing region = origin.
