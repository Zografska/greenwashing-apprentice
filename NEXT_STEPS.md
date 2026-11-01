# Next steps: checklist and timeline

Working plan for `docs/SPEC.md` v2. Deadline **Mon 15 Dec 2026**. Solo, ≤ €10, Kaggle T4 + MacBook Air M3.
Tick boxes as you go. The decision references (D…) point to the spec's decisions log.

## Timeline at a glance

| Week | Dates | Checkpoint | Gate |
|---|---|---|---|
| 1 | Mon 2 – Sun 8 Nov | **CP1** Data, freeze, harness | `eval.py` scores the gold labels, fed in as predictions, at 1.0; `check_split` passes; suites frozen |
| 2 | Mon 9 – Sun 15 Nov | **CP2** Teacher + baselines | Teacher dev macro-F1 ≥ 0.80 and consistency ≥ 95% (sanity check, not a blocker) |
| 3 | Mon 16 – Sun 22 Nov | **CP3a** Kaggle notebook working end to end | One H@571 + one T@571 run, scored, with a row in `results.csv` |
| 4 | Mon 23 – Sun 29 Nov | **CP3b** All runs | All 27 LoRA runs logged; T@571 beats S0 on dev |
| 5 | Mon 30 Nov – Sun 6 Dec | **CP4** Analysis | Every RQ has a table or figure |
| 6 | Mon 7 – Mon 15 Dec | **CP5** Report | Submitted |

### Trip-wires (when to apply the cut order, SPEC §9)

- **Fri 20 Nov:** the Kaggle notebook still can't train and score one run → switch to the Mac `mlx-lm` fallback and drop T-1.7B.
- **Thu 26 Nov:** fewer than half of the 27 runs done → drop the 150 point and go to 2 seeds.
- **Sun 29 Nov:** the minimum viable project (S0-noLegal, S0, S1, H@571, T@571, T+R, Teacher) is not complete → drop T-large and the curve; finish the minimum first.
- **Sun 6 Dec:** analysis not done → skip D13 and cut the slice analysis to the top 5 categories.

---

## Week 0 (before Mon 2 Nov)

- [ ] Delete the old `APPRENTICE_ECGT_SPEC.md` from `greenwashing-claim-detector` (untracked; `docs/SPEC.md` here replaces it)
- [ ] Create the GitHub repo and push `main`
- [ ] Create a Groq account, add a card, generate an API key → put it in `.env` as `GROQ_API_KEY` (never commit)
- [ ] Kaggle: verify your phone number (needed for GPU), check the weekly GPU quota in settings, confirm a **T4** is selectable

## CP1: data, freeze, harness (Mon 2 – Sun 8 Nov)

- [ ] **Email the instructor** (D27): "RAG" now means retrieving labelled example claims + the directive text as static context; the S0-noLegal row measures what the directive text adds. ≈ 30 min
- [ ] Confirm the student model (D10): Qwen3 4B / 1.7B, or a newer small Qwen **only if** Unsloth, MLX and llama.cpp all support it out of the box. ≈ 30 min
- [ ] `apprentice/data.py`: load the 8 vendored JSONs, map `DISCARDED → OUT`, skip `needs_review`, normalise (claim + footnote), compute `text_id`. ≈ ½ day
- [ ] `apprentice/split.py`:
  - [ ] e5 embeddings for all texts; group near-duplicates at cosine ≥ 0.90 (D25), report the clusters merged
  - [ ] assign suites: `test_carrefour` (all), `test_naturasi` (all), Coop/Eurospin 70% train / 30% `test_ce`, grouped by cluster, seed 0
  - [ ] drop reserve texts that collide with test or train; sample **dev ≈ 50 per class**; the rest → `t_large_extra`
  - [ ] write `splits/split_v1.jsonl` with every field in SPEC §4.3 (incl. `gold_label`, `gold_triggers`, `source_git_sha`)
  - ≈ 1 day
- [ ] `apprentice/check_split.py`: a reusable `check_split(files…)` with all the assertions in SPEC §4.3 rule 2, plus a unit test. ≈ ½ day
- [ ] **Review the dev set** (≈ 150 texts) by hand: fix the labels in the manifest's dev rows and note how many changed. ≈ 2–3 h
- [ ] Settle the open items at the bottom of this file (they change the split)
- [ ] **Freeze:** commit `splits/split_v1.jsonl` and tag `split-v1-frozen`. **No teacher call before this tag.**
- [ ] `apprentice/eval.py`: macro-F1, per-class F1, IN_SCOPE recall, flagged recall, κ, bootstrap CIs, McNemar + Holm, per-suite output, appends to `results/results.csv` (columns per D28). Test: feeding in the gold labels as predictions gives 1.0. ≈ 1 day
- [ ] `prompts/legal_block.md`: hand-pick from `vendor/legal/` → Art. 2 definitions (environmental claim, generic environmental claim, sustainability label, certification scheme), Annex I 2a/4a/4b/4c, Art. 7(7); ≤ 2k tokens. ≈ ½ day
- [ ] Draft the prompt files (they can still change in CP2):
  - `prompts/P_teacher.md`: the classifier prompt + legal block + the conventions from `vendor/golden/golden_set_ecgt_100_README.md` + `reasoning` (before the label) + the teacher's stated label. No anchors.
  - `prompts/P_student.md`: 3-class instructions; slots for the legal block and anchors; 5 static few-shots. No categories.
  - `prompts/P_ft.md`: one instruction line + the claim.
- [ ] ✅ **CP1 gate** (Sun 8 Nov)

## CP2: teacher + baselines (Mon 9 – Sun 15 Nov)

- [ ] `apprentice/teacher.py`: Groq client (sync + Batch), resumable, saves raw JSONL (model string, date, prompt hash, raw output, reasoning tokens, cost), computes the POST label and the stated-vs-POST consistency. Writes test outputs **only** to `data/teacher/test/`. ≈ 1 day
- [ ] Teacher on dev, synchronously; ≤ 3 prompt iterations, logging the dev macro-F1 and consistency of each one. ≈ ½ day + ≈ €0.30
- [ ] Freeze `P_teacher` (hash it) → Batch run on train + `t_large_extra` + test (≈ 2,400 texts). ≈ €2; up to 24 h wait
- [ ] Report teacher label noise: teacher vs gold on the 571 train texts
- [ ] `apprentice/retrieve.py`: e5 (pinned revision, `query:` prefix) over `vendor/retriever/anchors_v4.jsonl`, `top3(claim)` with the D8 guard, plus a count of skipped anchors. ≈ ½ day
- [ ] `apprentice/score_lp.py`: log-prob scoring of the 3 label strings for a HF model + prompt. Shared with the Kaggle notebook. ≈ ½ day
- [ ] Run S0-noLegal, S0 and S1 (Qwen3-4B; on the Mac or Kaggle) on dev, then **once** on test
- [ ] B0-T / B0-H: e5 + logistic regression → dev, then test. ≈ 1 h
- [ ] **Draft the report's methods section** (data, split, teacher, conditions, metrics). ≈ 1 day
- [ ] ✅ **CP2 gate** (Sun 15 Nov)

## CP3: students (Mon 16 – Sun 29 Nov)

**Week 3: get one run working end to end**

- [ ] Kaggle dataset: `splits/split_v1.jsonl` + teacher train/`t_large_extra` labels (**not** `data/teacher/test/`) + prompt files
- [ ] `notebooks/train_score.ipynb` from Unsloth's Qwen3 template:
  - [ ] pin the library versions in the first cell; record them in the run log
  - [ ] one shared chat-template function (thinking off, identical everywhere: D29)
  - [ ] minority oversampling per label source (D16); fixed LoRA hyperparameters
  - [ ] `check_split()` call before training
  - [ ] log-prob scoring on dev + test; T+R generation (reasoning → label), with invalid output counted as wrong
  - [ ] append to `results.csv`; save the LoRA adapter
- [ ] Smoke test: H@571 and T@571, seed 0 → ✅ **CP3a** (Sun 22 Nov)

**Week 4: run the grid**

- [ ] Nested subsets 150 / 300 per seed, shared between H and T (D16)
- [ ] H@{150, 300, 571} × 3 seeds
- [ ] T@{150, 300, 571} × 3 seeds
- [ ] T+R × 3 seeds
- [ ] T-large × 3 seeds
- [ ] T-1.7B × 3 seeds
- [ ] All 27 rows in `results.csv`; test scored once per final model
- [ ] ✅ **CP3b gate** (Sun 29 Nov): T@571 beats S0 on dev. If not: check the template and scoring → the learning rate (once) → accept it and report.

## CP4: analysis (Mon 30 Nov – Sun 6 Dec)

- [ ] Figure 1: learning curve (H vs T, mean ± SD; T-large point; S0-noLegal / S0 / S1 / Teacher as horizontal lines)
- [ ] Figure 2: cost vs quality (macro-F1 vs ms/claim: 1.7B GGUF, 4B GGUF, Teacher)
- [ ] McNemar + Holm on the 4 pairs (majority vote across seeds, plus the per-seed range)
- [ ] RQ4: error overlap with the teacher, T vs H as the control; κ(student, teacher) vs κ(student, gold)
- [ ] Error slices by gold trigger category and by suite (counts and examples)
- [ ] No-near-duplicate robustness subset of each suite
- [ ] Reasoning rubric: 50 samples (T+R and Teacher), stratified correct/wrong, 3 yes/no items. ≈ 1–2 h
- [ ] GGUF export (T-4B, T-1.7B) → re-score `test_ce` on the M3 with llama-cpp-python; measure ms/claim and peak RAM (D29)
- [ ] Cost table in € (D31)
- [ ] *Optional:* D13 blind self-re-labelling of 50 test texts (≈ 1 h)
- [ ] ✅ **CP4 gate** (Sun 6 Dec)

## CP5: report (Mon 7 – Mon 15 Dec)

- [ ] Results + discussion (one subsection per RQ)
- [ ] Limitations: Claude-drafted gold, Carrefour-developed prompt and anchors, the transfer-heavy headline, small positive classes
- [ ] Appendix: labelling conventions, prompts, the split protocol (SPEC §4.3), run log
- [ ] Clean up the repo: README results table, tag `v1.0-submission`
- [ ] ✅ **Submit** (by Mon 15 Dec)

---

## Open items for the final review (SPEC §12): decide **before the CP1 freeze**

These change the split, so they can't be revisited after the `split-v1-frozen` tag.

- [ ] 70/30 train/test ratio on Coop/Eurospin
- [ ] NaturaSì as test-only
- [ ] 0.90 near-duplicate threshold
- [ ] Scrape data out of scope (thesis)
