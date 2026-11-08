# Progress report: CP1–CP2 (as of 8 November 2026)

**Project:** The ECGT Apprentice, distilling a large open LLM's judgement on EU green claims
(Directive (EU) 2024/825) into a small local model. NLP class project, variant of P6 *The Apprentice Model*.
Deadline 15 December 2026. Plan: `docs/SPEC.md` (v2); checklist: `NEXT_STEPS.md`.

**Status:** CP1 (data, split, harness) done 1 Nov. CP2 (teacher + baselines) done 8 Nov, except the
methods-section draft. CP3 (students) starts 10 Nov. Money spent: about €7 (OpenRouter top-up incl. fees),
of which $0.37 used so far.

---

## 1. Task and data

Each input is one Italian product claim (with its footnote, if any); the output is one of three classes:
`IN_SCOPE` (problematic as written), `NEEDS_VERIFICATION` (NV, specific and checkable) or `OUT` (not an
ECGT claim).

Data are the expert-reviewed gold sets from the main project (Carrefour, Coop, Eurospin, NaturaSì; LLM-drafted,
reviewed by the author and supervisors), plus lighter-reviewed reserve sets.

**Split v1** (frozen 1 Nov, tag `split-v1-frozen`, hash in `splits/FROZEN`). Unit = unique normalised claim
text; lexical near-duplicates (character n-gram TF-IDF cosine ≥ 0.85) stay on one side.

| Set | Texts | OUT / NV / IN_SCOPE | Use |
|---|---|---|---|
| test_carrefour | 750 | 465 / 108 / 177 | test (frozen main-project gold) |
| test_ce (30% Coop + Eurospin) | 265 | 191 / 37 / 37 | test (same shops as train) |
| test_naturasi | 47 | 21 / 23 / 3 | test, qualitative (badge-only shop) |
| train (70% Coop + Eurospin) | 551 | 396 / 75 / 80 | student training (expert or teacher labels) |
| dev | 150 | 50 / 50 / 50 | tuning; fully reviewed by the author |
| t_large_extra | 574 | 491 / 14 / 69 | extra teacher-labelled training texts |

Decisions taken while building it:

- 3 gold label conflicts between shops were resolved by the author.
- The **slogan rule** (D34) came out of the dev review: a slogan is a claim when its words present nature or
  the environment as a merit, whatever the framing. The author's 5 initial disagreements are kept as notes.
- 17 of the 121 retrieval anchors overlap test claims, so they are excluded from retrieval.

## 2. Teacher

**Provider.** The Groq free tier counted cached prompt tokens in full against an 8K tokens/min limit, which
would have meant about 58 calls a day (weeks for the full run). Moved to OpenRouter, pinned to one provider
with no fallbacks: `coreweave/fp4`. It serves gpt-oss-20b and -120b at native 4-bit, with prompt caching.

**A failed first attempt.** Provider-side JSON mode broke gpt-oss's output: 20b returned empty answers on 150
of 150 claims, and 120b was only 7% valid. JSON enforcement is now off, and the JSON is parsed from the
answer. The failed runs are kept in `data/teacher/_discarded/`.

**Choosing the teacher and the prompt on dev** (150 claims; at most 3 prompt iterations; details in
`results/teacher_dev_iterations.md`):

| Iteration | Model | Dev macro-F1 | IN_SCOPE recall | Consistency |
|---|---|---|---|---|
| 1 | gpt-oss-20b | 0.780 | 0.84 | 93.3% |
| 1 | gpt-oss-120b | 0.815 | 0.88 | 98.7% |
| 2 | gpt-oss-120b | 0.946 (optimistic) | 1.00 | 100% |
| **3 (frozen)** | **gpt-oss-120b** | **0.912** | **0.98** | **99.3%** |

- **Teacher: gpt-oss-120b.** 20b missed both rules for choosing it: it was 3.5 points behind (the limit is 3)
  and below 95% consistency.
- **Iteration 2** fixed a systematic error: the teacher read the task as "environmental impact only". The fix
  was a scope note plus conventions for organic, natural wording, endorsements, farming practices and
  packaging materials.
- **Prompt leakage found and removed (iteration 3).** An audit of the prompt against the split found
  38 quoted examples that were test claims (inherited from the main project's prompt) or dev claims (added in
  iteration 2). All were replaced by invented examples teaching the same rule, and a unit test now blocks the
  problem from coming back.
  - The 3.4-point drop from iteration 2 to 3 estimates how much the leak was worth.
  - The prompt is frozen at hash `2ef529403276b34b`.

**Full run:** 2,187 claims (train, t_large_extra and the three test suites), 99.8% or more valid and
consistent, **$0.29**. The test outputs are stored separately and **not yet scored**; the teacher's test score
is measured once, in CP4.

**Teacher label noise on train** (teacher vs expert labels, 551 claims): macro-F1 **0.841**, accuracy
**91.3%** (48 disagreements), F1 IN_SCOPE 0.82 / NV 0.74 / OUT 0.96.

- **Plant-based or renewable packaging** is the largest source of disagreement: the teacher adds a
  generic-green trigger and calls it IN_SCOPE, while gold says NV.
- **Over-flagging:** the teacher also flags some OUT claims, such as «Senza ammoniaca».
- **Dev vs train:** the train score (0.841) is below the dev score (0.912) because dev was used for prompt
  tuning. Train is the unbiased estimate.

## 3. Baselines

Qwen3-4B on a Kaggle T4, thinking off, scored by the probability of each label (0.25–0.34 s per claim, with a
reused prompt prefix). B0 = e5-base embeddings + logistic regression trained on the 551 train claims.

| Condition | Dev | Dev, test-mix weighted | **Test headline** [95% CI] | Test IN_SCOPE recall | Test flagged recall |
|---|---|---|---|---|---|
| S0-noLegal (prompt + 5 examples) | 0.636 | 0.622 | **0.741** [0.707, 0.772] | 0.73 | 0.90 |
| S0 (+ legal text) | 0.662 | 0.617 | 0.706 [0.674, 0.735] | 0.79 | 0.96 |
| S1 (+ 3 retrieved examples) | **0.767** | **0.729** | 0.702 [0.669, 0.733] | 0.80 | **0.97** |
| B0-H (expert labels) | 0.711 | 0.698 | **0.745** [0.710, 0.774] | 0.79 | 0.86 |
| B0-T (teacher labels) | 0.733 | 0.710 | 0.713 [0.679, 0.746] | **0.83** | 0.88 |

The headline is test_ce + test_carrefour pooled (n = 1,015). Full tables are in `results/cp2_baselines.md`.

## 4. Findings so far

1. **Retrieval and legal text buy recall at the cost of precision.** For the prompted 4B model, the legal
   text and the retrieved examples raise IN_SCOPE recall (0.73 → 0.79 → 0.80) and flagged recall
   (0.90 → 0.97), but lower OUT recall (0.86 → 0.74). On the OUT-heavy test (65% OUT), the extra false alarms
   lower macro-F1 (0.741 → 0.702). Whether "knowledge in the prompt" helps (RQ2) therefore depends on the
   metric: it helps the safety metric, not overall macro-F1.
2. **Dev and test disagree, and that's an evaluation-design lesson.** Dev ranked S1 first, while test ranks
   it near the bottom.
   - Part of the gap is class balance: dev is 50/50/50. Re-weighting dev to the test mix removes S0's
     advantage over S0-noLegal.
   - The rest is dev's small size (±8 points).
   - Consequence (D35): CP3 decisions use the re-weighted dev score, and dev differences under about
     8 points count as ties.
3. **A simple classifier is a strong baseline.** e5 + logistic regression on 551 labelled claims (B0-H 0.745)
   matches the best prompted 4B model and beats S0. The labels carry most of the signal, which is encouraging
   for fine-tuning.
4. **First evidence on teacher labels vs expert labels (RQ1).** With the same 551 claims, expert labels give
   the better macro-F1 (B0-H 0.745 vs B0-T 0.713), while teacher labels give the better IN_SCOPE recall
   (0.83 vs 0.79). This fits the teacher's measured tendency to over-flag (label noise, §2). The real test of
   RQ1 is the fine-tuned students in CP3 (H vs T).
5. **Prompt leakage is easy to introduce and worth auditing.** Inherited prompts and convention examples
   quoted test and dev claims verbatim. An automated check against the split caught it, and the 3.4-point
   iteration-2 inflation measures its effect.
6. **Cost is negligible, and the bottlenecks are elsewhere.** The teacher costs $0.29 for the full run plus
   cents for dev. The time went into provider limits and output-format issues, not compute.

## 5. Open issues and caveats

- **NaturaSì** (47 claims) is reported but too small to compare conditions: B0-T 0.64, S1 0.56, others ≈ 0.5.
- **Qwen3-4B revision** wasn't recorded on the baseline run (transformers 5 change); it was `main` as of
  8 Nov. This is fixed for later runs.
- **Paired significance tests** (McNemar with Holm correction) are deferred to CP4, together with the
  students.
- **The gold labels are LLM-drafted and expert-reviewed**, so "expert labels" means expert-reviewed, not
  independently annotated.

## 6. Next (CP3, 10–22 Nov)

Kaggle training notebook (Unsloth QLoRA on Qwen3-4B, the shared chat template, oversampling, `check_split`
before every run, probability scoring). Then a smoke test (H@551 and T@551, seed 0) by 15 Nov, and the full
grid of 27 runs by 22 Nov. The scrape-data stretch (T-xl) only if the grid is done by 19 Nov.
