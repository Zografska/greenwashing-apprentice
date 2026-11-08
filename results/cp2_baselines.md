# CP2 baselines (2026-11-08)

Kaggle T4, Qwen/Qwen3-4B (fp16, thinking off, log-prob scoring with a reused prefix cache), e5-base for S1/B0.
Model revision of Qwen3-4B was not recorded on this run (transformers 5 dropped `_commit_hash`; fixed in
`score_lp.py` for later runs): it is the Hugging Face `main` revision as of 2026-11-08.
Predictions: `results/preds/<condition>/{dev,test}.jsonl`; metrics rows: `results/results.csv`.

| Condition | Dev macro-F1 | Test headline macro-F1 [95% CI] | Test IN_SCOPE recall | test_ce | test_carrefour | test_naturasi* | ms/claim (T4) |
|---|---|---|---|---|---|---|---|
| S0-noLegal | 0.636 | **0.741** [0.707, 0.772] | 0.729 | 0.676 | 0.756 | 0.455 | 245 |
| S0 (+ legal text) | 0.662 | 0.706 [0.674, 0.735] | 0.785 | 0.659 | 0.715 | 0.484 | 297 |
| S1 (+ 3 retrieved examples) | **0.767** | 0.702 [0.669, 0.733] | 0.799 | 0.628 | 0.723 | 0.556 | 325 |
| B0-H (e5 + LR, expert labels) | 0.711 | **0.745** [0.710, 0.774] | 0.785 | 0.764 | 0.737 | 0.522 | – |
| B0-T (e5 + LR, teacher labels) | 0.733 | 0.713 [0.679, 0.746] | **0.827** | 0.727 | 0.707 | 0.638 | – |

\* NaturaSì: 47 texts, qualitative only (D15/D22).

**Dev and test rank the conditions differently; the class balance explains part of it.** Dev is balanced by
construction (50 per class); the headline test is 65% OUT (656 OUT, 214 IN_SCOPE, 145 NV). The legal text and
the retrieved examples make the 4B model flag more claims: OUT recall falls 0.86 → 0.77 → 0.74 while IN_SCOPE
recall rises 0.73 → 0.79 → 0.80 (S0-noLegal → S0 → S1). On balanced dev that trade is rewarded; on OUT-heavy
test the extra false positives cost IN_SCOPE/NV precision (S1: IN_SCOPE precision 0.61, NV 0.46) and macro-F1
drops. So "the legal text / retrieval help" holds for the safety metric (IN_SCOPE recall), not for macro-F1
under the real class mix.

Per-class precision/recall on the headline suites (test_ce + test_carrefour, n = 1,015):

| Condition | IN_SCOPE P / R | NV P / R | OUT P / R | Predicted OUT / IS / NV |
|---|---|---|---|---|
| S0-noLegal | 0.68 / 0.73 | 0.55 / 0.70 | 0.94 / 0.86 | 604 / 228 / 183 |
| S0 | 0.58 / 0.79 | 0.50 / 0.70 | 0.97 / 0.77 | 524 / 289 / 202 |
| S1 | 0.61 / 0.80 | 0.46 / 0.74 | 0.98 / 0.74 | 500 / 282 / 233 |
| B0-H | 0.68 / 0.79 | 0.61 / 0.60 | 0.92 / 0.88 | 626 / 247 / 142 |
| B0-T | 0.60 / 0.83 | 0.62 / 0.50 | 0.93 / 0.85 | 601 / 297 / 117 |

B0-H vs B0-T on test: expert labels give the better macro-F1 (0.745 vs 0.713), teacher labels the better
IN_SCOPE recall (0.827 vs 0.785), consistent with the teacher's tendency to over-flag (teacher label noise,
`results/teacher_dev_iterations.md`). Paired tests (Holm) are left for CP4, together with the students.

## Re-weighting dev to the test class mix (D35, added 2026-11-08)

`dev_w` weights each dev claim by p_test(class) / p_dev(class) (OUT ≈ 1.94, IN_SCOPE ≈ 0.63, NV ≈ 0.43),
gold labels only.

| Condition | Dev | Dev_w [95% CI] | Test headline |
|---|---|---|---|
| S0-noLegal | 0.636 | 0.622 [0.537, 0.694] | 0.741 |
| S0 | 0.662 | 0.617 [0.530, 0.700] | 0.706 |
| S1 | 0.767 | 0.729 [0.648, 0.804] | 0.702 |
| B0-H | 0.711 | 0.698 [0.622, 0.773] | 0.745 |
| B0-T | 0.733 | 0.710 [0.636, 0.792] | 0.713 |

Re-weighting removes S0's dev advantage over S0-noLegal (as on test) and lowers the over-flagging conditions,
but S1 stays first on dev_w while it is last-but-one on test. So the class mix is only part of the explanation.
The rest is ordinary dev/test difference: dev is 150 reserve claims (intervals of about ±8 points, wide
enough to contain all the test values except S0-noLegal's), test is 1,015 gold claims from other products.
Checked and ruled out as a main cause: anchor proximity to dev (top-1 retrieved anchor's lexical similarity
to the claim 0.149 on dev vs 0.132 on test; its label matches gold on 55% vs 49%; 3 of the 59 real anchors are
dev texts, but the guard skips exact matches). Conclusion for CP3: decisions on dev use `dev_w`, and
differences on dev smaller than about 8 points are treated as ties.
