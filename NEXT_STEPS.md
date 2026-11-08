# Next steps: checklist and timeline

Working plan for `docs/SPEC.md` v2. Deadline **Tue 15 Dec 2026**. Solo, ≤ €10, Kaggle T4 + MacBook Air M3.
Tick boxes as you go. The decision references (D…) point to the spec's decisions log.

## Timeline at a glance

| Week | Dates                  | Checkpoint                                  | Gate                                                                                                 |
| ---- | ---------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1    | ✅ done Sun 1 Nov       | **CP1** Data, freeze, harness               | `eval.py` scores the gold labels, fed in as predictions, at 1.0; `check_split` passes; suites frozen |
| 2    | Mon 2 – Mon 9 Nov      | **CP2** Teacher + baselines                 | Teacher dev macro-F1 ≥ 0.80 and consistency ≥ 95% (sanity check, not a blocker)                      |
| 3    | Tue 10 – Sun 15 Nov    | **CP3a** Kaggle notebook working end to end | One H@551 + one T@551 run, scored, with a row in `results.csv`                                       |
| 4    | Mon 16 – Sun 22 Nov    | **CP3b** All runs                           | All 27 LoRA runs logged; T@551 beats S0 on dev_w (D35)                                               |
| 5    | Mon 23 – Sun 29 Nov    | **CP4** Analysis                            | Every RQ has a table or figure                                                                       |
| 6    | Mon 30 Nov – Sun 6 Dec | **CP5** Report                              | Report drafted                                                                                       |
| 7    | Mon 7 – Tue 15 Dec     | **Buffer**                                  | Revisions; submitted by Tue 15 Dec                                                                   |

### Trip-wires (when to apply the cut order, SPEC §9)

- **Fri 13 Nov:** the Kaggle notebook still can't train and score one run → switch to the Mac `mlx-lm` fallback and drop T-1.7B.
- **Thu 19 Nov:** fewer than half of the 27 runs done → drop the 150 point and go to 2 seeds. **All 27 done → start the scrape stretch (D17, T-xl).**
- **Sun 22 Nov:** the minimum viable project (S0-noLegal, S0, S1, H@551, T@551, T+R, Teacher) is not complete → drop T-large and the curve; finish the minimum first.
- **Sun 29 Nov:** analysis not done → skip D13 and cut the slice analysis to the top 5 categories.

---

## Week 0 (before Mon 2 Nov)

- [x] Delete the old `APPRENTICE_ECGT_SPEC.md` from `greenwashing-claim-detector` (untracked; `docs/SPEC.md` here replaces it)
- [x] Create the GitHub repo and push `main`
- [x] Groq account on the **free tier** (paid upgrades closed for now); API key in `.env` as `GROQ_API_KEY` (never commit)
- [x] Kaggle: T4 x2 available, 30 h/week. Keep the accelerator **off** until CP3
- [ ] _Optional:_ read the Kaggle Benchmarks model proxy terms. Does the Daily credit allow generating training labels? (a possible free fallback for the full teacher run, D9)
- [x] Kaggle: verify your phone number (needed for GPU), check the weekly GPU quota in settings, confirm a **T4** is selectable

## CP1: data, freeze, harness (✅ done Sun 1 Nov)

- [x] ~~Email the instructor~~ (D27): not needed; the RAG reinterpretation is explained in the report
- [x] Confirm the student model (D10): **Qwen3-4B / Qwen3-1.7B** (Qwen3.5 checked and rejected)
- [x] `apprentice/data.py`: load the 8 vendored JSONs, map `DISCARDED → OUT`, skip `needs_review`, normalise (claim + footnote), compute `text_id`. ≈ ½ day
- [x] `apprentice/split.py` (draft split v1 built; see SPEC §4.2):
  - [x] lexical near-dup clusters at cosine ≥ 0.85 (D25, changed from e5): 100 clusters, 239 texts
  - [x] assign suites: `test_carrefour` (all), `test_naturasi` (all), Coop/Eurospin 70% train / 30% `test_ce`, grouped by cluster, seed 0
  - [x] drop reserve texts that collide with test or train; sample **dev ≈ 50 per class**; the rest → `t_large_extra`
  - [x] write `splits/split_v1.jsonl` with every field in SPEC §4.3 (incl. `gold_label`, `gold_triggers`, `source_git_sha`)
  - ≈ 1 day
- [x] `apprentice/check_split.py`: a reusable `check_split(files…)` with all the assertions in SPEC §4.3 rule 2, plus a unit test. ≈ ½ day
- [x] **Review the dev set** (150 texts), done 2026-11-01: 0 net changes after the slogan rule (D34); 5 initial disagreements kept as notes. Edited `splits/dev_review_v1.xlsx` (change `reviewed_label` only where you disagree, add a `note`), then `python3 -m apprentice.dev_review apply`. ≈ 1–2 h
- [x] Resolve the 3 gold label conflicts (D32): `splits/label_resolutions_v1.json`
- [x] Settle the open items at the bottom of this file (they change the split)
- [x] **Freeze:** commit `splits/split_v1.jsonl` and tag `split-v1-frozen`. **No teacher call before this tag.**
- [x] `apprentice/eval.py`: macro-F1, per-class F1, IN_SCOPE recall, flagged recall, κ, bootstrap CIs, McNemar + Holm, per-suite output, appends to `results/results.csv` (columns per D28). Test: feeding in the gold labels as predictions gives 1.0. ≈ 1 day
- [x] `prompts/legal_block.md`: verbatim Art. 2 definitions o–s and Annex I 2 bis, 4 bis–4 quater, 10 bis (≈ 1.3k tokens)
- [x] Draft the prompt files (they can still change in CP2):
  - `prompts/P_teacher.md`: the classifier prompt + legal block + the conventions from `vendor/golden/golden_set_ecgt_100_README.md` + `reasoning` (before the label) + the teacher's stated label. No anchors.
  - `prompts/P_student.md`: 3-class instructions; slots for the legal block and anchors; 5 static few-shots. No categories.
  - `prompts/P_ft.md`: one instruction line + the claim.
- [x] ✅ **CP1 gate** (passed Sun 1 Nov: self-test 1.0, `check_split` ok, split frozen)

## CP2: teacher + baselines (Mon 2 – Mon 9 Nov)

- [x] **Day 1:** check the Groq limits on console.groq.com/settings/limits for gpt-oss-20b and -120b; send the same `P_teacher` twice and check `usage.prompt_tokens_details.cached_tokens` on the second call (≈ 3k means caching works). ≈ 30 min
- [x] `apprentice/teacher.py`: OpenAI-compatible client (base URL switchable: Groq / Kaggle proxy / OpenRouter / llama.cpp), rate-limit aware (RPM/TPM/TPD backoff), resumable, saves raw JSONL (model string, date, prompt hash, raw output, reasoning tokens, cost), computes the POST label and the stated-vs-POST consistency. Writes test outputs **only** to `data/teacher/test/`. ≈ 1 day
- [x] Teacher on dev with **both gpt-oss-20b and gpt-oss-120b**; ≤ 3 prompt iterations, logging the macro-F1 and consistency of each. ≈ ½–1 day, €0
- [x] **Choose the teacher (D9):** → **gpt-oss-120b**, prompt frozen at iteration 3 (dev macro-F1 0.912). 20b if within 3 macro-F1 points of 120b and consistency ≥ 95%, otherwise 120b. Record the numbers for the report
- [x] **Choose the provider for the full run (D9):** → OpenRouter pinned to `coreweave/fp4` (Groq free counted cached tokens in full). Groq free if caching works; otherwise Kaggle proxy (if its terms allow) / OpenRouter pinned (≈ €6) / self-hosted 20b on a Kaggle T4
- [x] Freeze `P_teacher` (hash `2ef529403276b34b`, `prompts/FROZEN`)
- [x] Full teacher run on **one provider** (gpt-oss-120b, OpenRouter `coreweave/fp4`), done Sun 8 Nov, total $0.29:
  - [x] `train` (551)
  - [x] `t_large_extra` (574)
  - [x] `test` (1,062, not scored until CP4: test_carrefour 750, test_ce 265, test_naturasi 47; written only to `data/teacher/test/`)
- [x] Report teacher label noise: teacher vs gold on the 551 train texts → macro-F1 0.841, accuracy 0.913 (`results/teacher_dev_iterations.md`)
- [x] `apprentice/retrieve.py`: e5 (pinned revision, `query:` prefix) over `vendor/retriever/anchors_v4.jsonl`, `top3(claim)` with the D8 guard, plus a count of skipped anchors. ≈ ½ day
- [x] `apprentice/score_lp.py` (prefix KV-cache reuse; matches naive scoring to 1e-6 in `tests/test_score_lp.py`): log-prob scoring of the 3 label strings for a HF model + prompt. Shared with the Kaggle notebook. ≈ ½ day
- [x] Run S0-noLegal, S0 and S1 (Qwen3-4B) on dev, then **once** on test (done 8 Nov, `results/cp2_baselines.md`): Kaggle notebook `notebooks/cp2_baselines_kaggle.ipynb` (`apprentice/baselines.py`)
- [x] B0-T / B0-H: e5 + logistic regression → dev, then test (same notebook)
- [ ] **Draft the report's methods section** (data, split, teacher, conditions, metrics). ≈ 1 day
- [ ] ✅ **CP2 gate** (Mon 9 Nov)

## CP3: students (Tue 10 – Sun 22 Nov)

**Week 3: get one run working end to end**

- [x] ~~Kaggle dataset~~: not needed, the notebook clones the public repo (split, teacher train labels and prompts are in it; `data/teacher/test/` is blocked by `check_split`)
- [x] `notebooks/cp3_train_kaggle.ipynb` + `apprentice/train.py` (D36), tested end to end on a tiny Qwen3:
  - [x] pin the library versions in the first cell; record them in the run log
  - [x] one shared chat-template function (thinking off, identical everywhere: D29)
  - [x] minority oversampling per label source (D16); fixed LoRA hyperparameters
  - [x] `check_split()` call before training
  - [x] log-prob scoring on dev + test; T+R generation (reasoning → label), with invalid output counted as wrong
  - [x] append to `results.csv`; save the LoRA adapter
- [ ] Smoke test: H@551 and T@551, seed 0 → ✅ **CP3a** (Sun 15 Nov)

**Week 4: run the grid**

- [x] Nested subsets 150 / 300 per seed, shared between H and T (D16), implemented in `train.ordered_train`
- [ ] H@{150, 300, 551} × 3 seeds
- [ ] T@{150, 300, 551} × 3 seeds
- [ ] T+R × 3 seeds
- [ ] T-large × 3 seeds
- [ ] T-1.7B × 3 seeds
- [ ] All 27 rows in `results.csv`; test scored once per final model
- [ ] *Stretch, only if all 27 runs are done by Thu 19 Nov (D17):* segment ≈ 3k scrape claims on the Mac (main repo segmenter + retriever filter) → `check_split` → teacher labels → T-xl × 3 seeds
- [ ] ✅ **CP3b gate** (Sun 22 Nov): T@551 beats S0 on `dev_w` (D35). If not: check the template and scoring → the learning rate (once) → accept it and report.

## CP4: analysis (Mon 23 – Sun 29 Nov)

- [ ] Figure 1: learning curve (H vs T, mean ± SD; T-large point; S0-noLegal / S0 / S1 / Teacher as horizontal lines)
- [ ] Figure 2: cost vs quality (macro-F1 vs ms/claim: 1.7B GGUF, 4B GGUF, Teacher)
- [ ] McNemar + Holm on the 4 pairs (majority vote across seeds, plus the per-seed range)
- [ ] RQ4: error overlap with the teacher, T vs H as the control; κ(student, teacher) vs κ(student, gold)
- [ ] Error slices by gold trigger category and by suite (counts and examples), incl. certification badges across all suites
- [ ] No-near-duplicate robustness subset of each suite
- [ ] Reasoning rubric: 50 samples (T+R and Teacher), stratified correct/wrong, 3 yes/no items. ≈ 1–2 h
- [ ] GGUF export (T-4B, T-1.7B) → re-score `test_ce` on the M3 with llama-cpp-python; measure ms/claim and peak RAM (D29)
- [ ] Cost table in € (D31)
- [ ] _Optional:_ D13 blind self-re-labelling of 50 test texts (≈ 1 h)
- [ ] ✅ **CP4 gate** (Sun 29 Nov)

## CP5: report (Mon 30 Nov – Sun 6 Dec) + buffer (Mon 7 – Tue 15 Dec)

- [ ] Results + discussion (one subsection per RQ)
- [ ] Limitations: Claude-drafted gold, Carrefour-developed prompt and anchors, the transfer-heavy headline, small positive classes
- [ ] Appendix: labelling conventions, prompts, the split protocol (SPEC §4.3), run log
- [ ] Clean up the repo: README results table, tag `v1.0-submission`
- [ ] Report drafted by Sun 6 Dec; use Mon 7 – Tue 15 Dec for revisions and anything that slipped
- [ ] ✅ **Submit** (by Tue 15 Dec)

---

## Open items for the final review (SPEC §12): decide **before the CP1 freeze**

These change the split, so they can't be revisited after the `split-v1-frozen` tag.

- [x] 70/30 train/test ratio on Coop/Eurospin (kept)
- [x] NaturaSì as test-only (kept; add a certification-badge slice across all suites in CP4)
- [x] Near-duplicate threshold: lowered to **0.85** (lexical char n-gram TF-IDF)
- [x] Scrape data: gated stretch (D17), only if CP3b is complete by Thu 19 Nov
