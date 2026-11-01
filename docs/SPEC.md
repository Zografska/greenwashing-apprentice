# The ECGT Apprentice: distilling a large LLM's green-claim judgement into a small local model

**NLP class project** (variant of **P6, The Apprentice Model**) · spec **v2** · 2026-11-01 · deadline **2026-12-15**

Built on the `greenwashing-claim-detector` repo, which is also the seed for a later thesis.

v2 incorporates an independent review of v1. All of its must-fix, should-fix and nice-to-have items were accepted; the changes are listed in §13.

> **Paths in this repo:** the spec was drafted in the main repo. Files it names there (`golden/labeled/…`, `retriever/…`, `classifier/…`, `tools/…`, the legal chunks from git history) are vendored under `vendor/` here; see `VENDORED.md`. "All new code lives in `apprentice/`" holds as written, and the main repo's files are no longer touched at all.

---

## 0. Constraints (these shape every choice below)

| Constraint | Value | Consequence |
|---|---|---|
| People | **1 (solo)** | Reuse everything possible. Every experiment is a loop in one notebook. The cut order is set in advance (§9). |
| Time | **Nov 1 → Dec 15 (≈ 6.5 weeks)**, alongside other work | 5 checkpoints. CP1 finished on Nov 1, so the plan was pulled a week earlier: the report is drafted by Dec 6, leaving **Dec 7–15 as buffer**. |
| Labour outside coding | ≈ 2–3 h to review the dev set (CP1); ≈ 1–2 h for the reasoning rubric (CP4); optional ≈ 1 h human ceiling | Nothing else needs manual labelling. |
| Money | **€0 preferred, ≤ €10 total** | Teacher on the **Groq free tier** first (Groq's paid tier is closed to new upgrades as of 2026-11-01). A paid fallback for the full run only if needed (≈ €1–6, D9). Students on Kaggle's free GPU. Inference on the Mac. No other paid services. |
| Hardware | MacBook Air M3, 16 GB; Kaggle free tier, **T4 only**: Unsloth does not support the P100. ≤ 12 h sessions; weekly quota shown in account settings, reportedly about 30 h. | Student ≤ 4B, 4-bit QLoRA. Fallback: everything on the Mac with `mlx-lm`. |
| Language | Report in English; data and model reasoning in Italian | – |

---

## 1. Problem statement and task

From 27 September 2026, Directive (EU) 2024/825 (ECGT) applies. It amends the UCPD and is transposed in Italy by D.Lgs. 30/2026. It bans generic environmental claims, "climate neutral" claims based on offsets and unaccredited sustainability labels, and requires comparisons to name what they compare against. Italian retailer product pages carry many such claims. A large LLM can screen them, but it is costly, runs only in the cloud and changes over time.

**We distil a large open LLM's ECGT judgement into a small open model that runs on a laptop. We measure what the student keeps and what it loses, and compare learning from the teacher with learning from expert-reviewed labels.**

**Task.** Input: one Italian claim, plus its footnote if any. Output: one of three classes; one student variant also writes a short reasoning in Italian.

| Class | Meaning |
|---|---|
| `IN_SCOPE` | Problematic as written: vague green language, offset-based climate neutrality, a comparison with no comparator, a brand eco-slogan, … |
| `NEEDS_VERIFICATION` (NV) | Specific and checkable: a named certification, a stated %, vegan, a concrete farming practice, a defined term |
| `OUT` | Not an ECGT environmental claim |

**Out of scope:**

- Finding claims in a page. The repo's retriever already does this, at 97.6% recall on gold.
- Fine-grained categories.
- Citable Italian statute references.
- Teacher-labelled data from the raw scrapes, unless the gated stretch in D17 is triggered.

All four are thesis items (§11).

---

## 2. Research questions

- **RQ1 (teacher labels vs. reviewed labels):** at the same training texts and size, does a student trained on teacher labels match one trained on expert-reviewed labels? How many reviewed labels is the teacher worth? (learning curve)
- **RQ2 (knowledge in the prompt or in the weights):** do prompted students, given the static legal context and retrieved labelled examples, compete with fine-tuned students? How much does the legal context itself add?
- **RQ3 (compression):** how much of the teacher's macro-F1 do a 4B and a 1.7B student keep, and at what latency and cost? Teacher and students are compared **as deployed systems** (each with its own prompt).
- **RQ4 (inheritance):** does the student copy the teacher's errors? Compare κ(student, teacher) with κ(student, gold). Compare the overlap between T's errors and the teacher's errors with the overlap for **H** (whose training never saw teacher labels) as a control.
- **RQ5 (reasoning):** does training on the teacher's reasoning, written **before** the label, improve labels over training on labels only? How good is the student's reasoning?

---

## 3. Decisions log

| # | Decision |
|---|---|
| D1 | Pure P6: students are trained on teacher outputs (hard labels ± reasoning, at the sequence level). Soft-label / logit distillation is thesis scope. |
| D2 | Key experiment: **teacher labels (T) vs. expert-reviewed gold labels (H)**, on identical training texts and sizes. |
| D3 | Output = 3 classes (+ reasoning for T+R); no categories. Fallback: binary (flag vs. OUT) if the 4B student fails at 3 classes. |
| D4 | ECGT trigger categories are never shown to the students. They are used only to slice errors in the analysis (report n; no F1 for slices with n < 20). |
| D5 | Split by **unique normalised (claim + footnote) text**, with near-duplicate grouping (D25). The student sees only the text, so identical or near-identical text is the leak that matters. |
| D6 | "RAG" = the repo's **anchor retriever**: top-3 labelled example claims as few-shot (retrieval-augmented in-context learning). The relevant directive provisions (≈ 1–2k tokens) go into the prompt as **static context**. Row S0-noLegal measures what that context adds. |
| D7 | Framing: knowledge in the prompt vs. knowledge in the weights. Fine-tuned students get no legal context and no anchors. |
| D8 | Anchor leak guard: skip any anchor whose normalised text matches the claim or whose e5 cosine is ≥ 0.95. Report how many were skipped. (48 of the 121 anchors appear word for word in the Coop gold 100.) |
| D9 | Teacher: **gpt-oss, chosen on dev between 20b and 120b** (both Apache-2.0, sizes public). On the dev set (≈ 150 texts), run both with the same `P_teacher`. **Use 20b if its macro-F1 is within 3 points of 120b and its consistency (D30) is ≥ 95%; otherwise use 120b.** Report the comparison. **Provider:** Groq **free tier** for dev (synchronous; Batch isn't available on the free tier). **CP2 day 1:** check the account limits and whether prompt caching works (`usage.prompt_tokens_details.cached_tokens` on a repeated system prompt; cached tokens don't count toward limits). With caching, the full run stays on Groq free in daily batches (≈ 1 week, started by Wed Nov 4). Without it, the full run goes to one alternative: the Kaggle Benchmarks model proxy (free daily credit, **only if its terms allow generating training data**), OpenRouter with a pinned provider and no fallbacks (≈ €6 incl. fees), or, for 20b, self-hosted on a Kaggle T4 with llama.cpp. The whole final run uses **one provider**, logged on every response; switching provider between dev and the final run is allowed because the model is the same. Temperature 0, low reasoning effort. Every raw response is saved (temperature 0 is not guaranteed to be deterministic). Students learn from the final `reasoning` field, never from the raw thinking trace. (DeepSeek-flash was considered: cheapest paid option, but its size is undisclosed and it silently remaps model versions.) The teacher stays outside the Claude family to avoid circularity with the Claude-drafted gold. |
| D10 | Students: **Qwen3-4B** (main) and **Qwen3-1.7B** (size ablation), same family, thinking off. **Confirmed at CP1 (2026-11-01):** Qwen3.5 (0.8B/2B/4B/9B) was checked and rejected: Unsloth advises against 4-bit QLoRA for it, its hybrid kernels compile slowly on a T4, and it is a vision-language model. |
| D11 | Compute: Kaggle **T4**, pinned versions (allow about 10 min of reinstalling per session), Unsloth QLoRA. **No vLLM.** Inference uses HF Transformers (D23). The Mac does the GGUF export, re-scoring and latency. Fallback: `mlx-lm` on the Mac. |
| D12 | Gold = LLM-drafted (Claude) and **expert-reviewed** (author + professors, several rounds; no inter-annotator agreement is reported, so "expert-reviewed" is used throughout, not "adjudicated"). The reserves had a lighter review and are never used as human training labels. Consequence: H means "expert-reviewed LLM-drafted labels". |
| D13 | Optional (if week 5 has slack): blind self-re-labelling of 50 test texts as a human ceiling. |
| D14 | Row T-large: teacher labels on train + the reserve texts that are not in dev. |
| D15 | Statistics: McNemar on 4 pre-registered pairs, **Holm-corrected**: H@571 vs T@571, T vs T+R, S1 vs T@571, T@571 vs Teacher. The primary test uses majority-vote predictions across the 3 seeds; the per-seed range is reported too. Per-class F1 gets bootstrap 95% intervals. Minimum detectable difference ≈ 0.04 macro-F1 on the pooled headline suites. |
| D16 | Students: 3 seeds. **Each seed also redraws the nested 150/300 subsets, shared between H and T**, so the curve reflects data variance as well as initialisation noise. Class imbalance is handled by **minority oversampling** computed from each label source's own distribution (gold for H, teacher for T), because generative SFT trainers have no class weights. LoRA hyperparameters are fixed in advance and identical for all runs; they are never tuned per run. |
| D17 | **Raw scrape data: gated stretch.** Out of scope by default. Added **only if CP3b (all 27 runs) is complete by Thu 19 Nov**: about 3k claims cut from the main repo's `server/` records with its segmenter + retriever candidate filter (on the Mac, where e5 works), labelled by the chosen teacher, passed through `check_split`, trained as one extra row **T-xl** (4B, 3 seeds) at the end of the learning curve. Otherwise it is the first thesis experiment. |
| D18 | Headline = macro-F1 (3 classes) on the pooled `test_ce` + `test_carrefour` suites, always shown together with the per-suite numbers. |
| D19 | Scope as fixed by §0; cut order in §9. |
| D20 | Report in English; data and reasoning in Italian. |
| D21 | **Separate prompts:** `P_teacher` (repo classifier prompt with triggers + legal block + conventions + reasoning; static few-shots, **no anchors**); `P_student` (S0/S1: 3-class instructions, ± legal block, ± top-3 anchors; no categories); `P_ft` (fine-tuned students: one short instruction line + the claim). All prompts are versioned files whose hash is logged. |
| D22 | **Named test suites**, reported separately: `test_ce` (30% of the Coop + Eurospin gold texts), `test_carrefour` (frozen Carrefour gold), `test_naturasi` (qualitative: a badge-only shop whose claims look different from the training data). The report states that the headline is mostly cross-retailer transfer, since Carrefour is ≈ 75% of it and absent from training. |
| D23 | **Scoring:** label-only models (S0, S1, H, T, T-large, T-1.7B) are scored by the **log-probability of each of the three label strings** after the prompt; the highest wins. This always gives a valid output, needs no constrained decoding and gives probabilities for free. **T+R** generates freely, `{"reasoning": …, "label": …}` (**reasoning first**); the label is parsed, invalid output counts as wrong, and the share of valid JSON is reported unconstrained. The teacher uses the provider's JSON mode. |
| D24 | **Dev set** = about 50 texts per class (≈ 150) sampled from the reserve texts and **fully reviewed by the author** at CP1 (≈ 2–3 h). The dev IDs stay reserved permanently, even if the reserves are reviewed later. The teacher gate on dev is a **sanity check**, not a blocker. |
| D25 | **Near-duplicate grouping (lexical):** character 3–5-gram TF-IDF cosine between all unique texts (`apprentice/neardup.py`); pairs ≥ **0.85** are merged (union-find) and each cluster stays on one side. Changed from e5 at CP1: the leak to catch is the same claim with small surface changes (gender/number agreement, a product name, a percentage), which a lexical measure targets directly, and it needs no model download (Hugging Face is blocked in the build environments). Threshold lowered from 0.90 to 0.85 at CP1 after inspecting sampled pairs per similarity band: 0.85–0.90 still holds clear variants («Lavorati / Lavorato dal fresco», «Confezione Riciclabile» / «Questa confezione è riciclabile»), while below 0.85 distinct claims start to merge and chain (largest group 14 at 0.80). Split v1: 100 multi-text clusters covering 239 texts, largest 5. A semantic (e5) no-near-duplicate subset of each test suite is still reported in CP4 as a robustness check. |
| D26 | **Manifest and freeze:** see §4.3. The test suites are frozen **at CP1, before the teacher sees any text**. |
| D27 | **Instructor:** no email needed (author's decision, 2026-11-01). The reinterpretation of "RAG" (D6) and the S0-noLegal row that measures the directive context are explained in the report instead. |
| D28 | **Logging:** every `results.csv` row records run id, condition, seed, train size, model + revision, library versions, LoRA hyperparameters, prompt hash, manifest version, date and per-suite metrics. Every teacher response records model string, date, raw output, reasoning tokens and cost. |
| D29 | The **GGUF (Q4)** export of T-4B and T-1.7B is re-scored on `test_ce` on the Mac (llama-cpp-python, log-prob scoring), because Q4 GGUF quality differs from bitsandbytes 4-bit. The chat template (Qwen3 with thinking off, including the empty `<think>` block) is **identical** in training, Kaggle inference and the GGUF/Ollama template. |
| D30 | **Teacher consistency:** the teacher also states its own label; the training label is always the POST label computed from its triggers. The share of disagreements between the two is reported. If it is above 5% on dev, fix the prompt before the full run. Disagreeing examples are kept so that T and T+R stay matched, and are flagged in the data. |
| D32 | **Gold label conflicts:** a text with different labels in two gold sets takes, in a test suite, the label of that suite's own gold (Carrefour gold stays frozen). Conflicts are listed in the split report and resolved by the author before the freeze. |
| D33 | **Dev review:** `python3 -m apprentice.dev_review export` writes `splits/dev_review_v1.csv` with `reviewed_label` pre-filled with the light label (change only disagreements, to fit the time budget); `apply` writes it back as `dev_reviewed_label`, which `eval.py` uses as dev gold. The number of changes is reported. |
| D34 | **Slogan rule** (settled during the dev review, 2026-11-01): a slogan, brand or line name is a claim when its words present nature or the environment as a merit without defining it («Vivi Verde», «Più natura, più qualità», «Solo il meglio della natura» → IN_SCOPE); framing (lifestyle, "più") is irrelevant; a vague green part beats a specific one («Planet lovers – 100% Carta riciclabile» → IN_SCOPE); out_of_scope only when the word means something else in the claim itself («Rispetta la tua natura»); truth is never judged; the words alone decide. This matches the expert-reviewed test labels. Added to `P_teacher` conventions and the review read-me. Dev review result: 0 net label changes; the author's 5 initial disagreements (all slogan cases) are kept as notes in the manifest. |
| D31 | **Cost units:** everything is reported in € (USD converted at the run date's rate). Local inference is reported as 0 € marginal cost (electricity and hardware ignored, stated explicitly) plus ms/claim and peak RAM. |

---

## 4. Data

### 4.1 Sources

| Source | Labels | Used as |
|---|---|---|
| `golden/labeled/golden_set_ecgt_100.json` (Carrefour) | Expert-reviewed, frozen by the main project | `test_carrefour` |
| `golden_set_ecgt_{coop,eurospin}_100.json` | Expert-reviewed | Grouped split: 70% train / 30% `test_ce` |
| `golden_set_ecgt_naturasi_100.json` | Expert-reviewed; badge-only (301 claims → 55 unique texts) | `test_naturasi` |
| `golden_set_ecgt_*reserve.json` (4 files) | Lighter review | Dev (≈ 150, re-reviewed) + extra unlabelled teacher input (T-large) |

Gold `DISCARDED` is mapped to `OUT`. Claims with `needs_review: true` are skipped. Normalisation: lowercase, non-word characters collapsed to spaces, trimmed; the footnote is appended when present.

### 4.2 Split v1 numbers

Draft split v1, built 2026-11-01 (`python3 -m apprentice.split`; seed 0, lexical near-dup grouping at 0.85, dev 50 per class). Final once frozen.

| Set | Unique texts | OUT | NV | IN_SCOPE |
|---|---|---|---|---|
| `test_carrefour` | 750 | 465 | 108 | 177 |
| `test_ce` (30% of Coop/Eurospin gold clusters) | 265 | 191 | 37 | 37 |
| `test_naturasi` | 47 | 21 | 23 | 3 |
| **all test** | **1,062** | 677 | 168 | 217 |
| **Train** (70% of Coop/Eurospin gold clusters) | **551** | 396 | 75 | 80 |
| **Dev** (reserve-only clusters, 50 per class; fully reviewed, D33/D34) | 150 | 50 | 50 | 50 |
| **T-large extra** (remaining reserve-only texts) | 574 | 491 | 14 | 69 |
| Excluded (reserve texts in a cluster that already holds gold texts) | 54 | 26 | 9 | 19 |
| **total unique texts** | **2,391** | | | |

T-large total = 551 + 574 = **1,125** texts. The dev sample uses most of the reserve's NV texts, so T-large adds few NV examples (14).

**Gold label conflicts:** 3 identical texts carry different labels in two gold sets (all three land in `test_carrefour`). Resolved by the author on 2026-11-01 («Senza OGM» → OUT; «100% Di origine naturale» → NV; «La Carta del Mulino … ISCC Plus …» → NV), recorded in `splits/label_resolutions_v1.json` (D32).

### 4.3 ⚠️ FLAGGED FOR FINAL REVIEW: data separation and future expansion

**Manifest** `apprentice/splits/split_v1.jsonl`, one row per unique text:

`text_id` (hash of normalised claim + footnote) · `text` · `footnote` · `source_file` · `source_git_sha` · `gold_label` (frozen copy) · `gold_triggers` (frozen; analysis only) · `suite` (train / dev / t_large_extra / test_ce / test_carrefour / test_naturasi) · `near_dup_cluster` · `seed` · `created`.

**Rules:**

1. **Freeze at CP1**, before any teacher call. After that, test rows are never edited. A later relabel by the professors produces `split_v2`; v1 results are always reported against v1's frozen labels.
2. **`check_split(files…)`** is a reusable function, not a one-off script. It asserts:
   - no `text_id` or near-duplicate cluster appears on two sides;
   - the anchors pass the D8 guard against test;
   - the curve subsets are subsets of train;
   - **no test text appears in any training file**, including teacher-labelled files.

   Every training and evaluation job calls it. Every future data source must pass it, the 50k scrape included.
3. **Teacher labels on test exist only for the Teacher row.** They are stored in a separate file that the training loader refuses to read.
4. **The dev IDs are reserved permanently.**
5. **Expansion:** new labelled data never changes v1 suites. New texts go to train (after `check_split`); new test material becomes a **new named suite** (e.g. `test_coop_v2`), reported next to v1.

**Reviewed 2026-11-01:** 70/30 kept; NaturaSì kept test-only (plus a CP4 slice on certification badges across all suites); near-dup threshold lowered to 0.85; scrape data as a gated stretch (D17).

---

## 5. Conditions

All rows are evaluated on every test suite.

| Row | Model | Learns from | Prompt at inference | Scoring | Runs |
|---|---|---|---|---|---|
| B0-T / B0-H | e5-base + logistic regression | teacher / gold labels, 571 | – | classifier | 2 |
| S0-noLegal | Qwen3-4B, prompted | – | `P_student`, no legal block, 5 static few-shots | log-prob | 1 |
| S0 | Qwen3-4B, prompted | – | `P_student` + legal block + 5 static few-shots | log-prob | 1 |
| S1 | Qwen3-4B, prompted | – | S0 + top-3 anchors (D8) | log-prob | 1 |
| H@n | Qwen3-4B, LoRA | **gold labels**, n ∈ {150, 300, 571} | `P_ft` | log-prob | 9 |
| T@n | Qwen3-4B, LoRA | **teacher labels**, n ∈ {150, 300, 571} | `P_ft` | log-prob | 9 |
| T+R | Qwen3-4B, LoRA | teacher reasoning → label, 571 | `P_ft` | generation | 3 |
| T-large | Qwen3-4B, LoRA | teacher labels, ≈ 1,200 | `P_ft` | log-prob | 3 |
| T-1.7B | Qwen3-1.7B, LoRA | teacher labels, 571 | `P_ft` | log-prob | 3 |
| Teacher | gpt-oss-20b or -120b (D9) | – | `P_teacher` (no anchors) | JSON mode → POST label | 1 |

That makes **27 LoRA runs** (≈ 10–15 GPU-min each, about 5–6 h of Kaggle T4 in total), plus 6 prompted, baseline and teacher runs.

H@n and T@n always share exactly the same texts for a given seed. H, T, T-large and T-1.7B train on the target `<label>`; T+R trains on `{"reasoning": …, "label": …}`.

### Teacher prompt and label

`P_teacher` is the repo's `classifier/ECGT_CLAIM_CLASSIFIER_PROMPT.md`, plus:

- the legal-context block;
- the labelling conventions from `golden_set_ecgt_100_README.md`;
- a `reasoning` field, written before the label.

The training label is computed from the teacher's triggers with the repo's POST rule:

```python
IN_SCOPE_T = {"generic_green","undefined_natural","climate_neutral",
              "vague_comparison","brand_eco_slogan","vague_supply_chain"}
def label(triggers):
    t = set(triggers) - {"out_of_scope"}
    if not t: return "OUT"
    if "defined_term" in t: t.discard("undefined_natural")
    return "IN_SCOPE" if t & IN_SCOPE_T else "NEEDS_VERIFICATION"
```

The teacher runs on train + reserve + test, ≈ 2,400 texts, plus ≤ 3 dev iterations on ≈ 150 texts for each of the two candidate teachers. That's ≈ 3,300 calls at ≈ 3.8k tokens each (mostly the shared system prompt, so keep `P_teacher` lean). **€0 on Groq free with caching**; ≈ €1–6 on a paid fallback. Its agreement with gold on the 571 train texts is reported as **teacher label noise**, the key context for RQ1.

The **disclosed confound:** the classifier prompt and the anchors were developed on Carrefour data in the main project. The teacher's and S1's scores on `test_carrefour` may therefore be optimistic, which is why per-suite numbers are always shown.

---

## 6. Metrics

| Role | Metric |
|---|---|
| **Headline** | Macro-F1 over {IN_SCOPE, NV, OUT}, pooled `test_ce` + `test_carrefour`, plus each suite separately |
| Safety | Recall of IN_SCOPE; recall of "flagged" (IN_SCOPE + NV vs. OUT) |
| Distillation | κ(student, teacher) and κ(student, gold); overlap between student and teacher errors, with H's overlap as the control (RQ4) |
| Reasoning (T+R, teacher) | Rubric on 50 samples stratified by correct vs. wrong: (1) supports the label, (2) cites the right element of the claim, (3) consistent with the legal block, each yes/no; report the % yes per item. Plus the teacher's stated-vs-POST label consistency (D30). |
| Validity | % valid JSON for T+R (unconstrained); not applicable to log-prob-scored rows |
| Cost | Parameters, GGUF size, peak RAM, ms/claim on the M3, € per 1,000 claims, training GPU-minutes (D31) |
| Statistics | D15: Holm-corrected McNemar on the 4 pairs, bootstrap 95% CIs; error slices by gold trigger category and suite (counts and examples) |

**Figures:**

1. **Learning curve:** macro-F1 against training size, with H and T lines (mean ± SD), the T-large point, and horizontal lines for S0-noLegal, S0, S1 and the teacher.
2. **Cost vs. quality:** macro-F1 against ms/claim, one point per deployed system (1.7B GGUF, 4B GGUF, teacher).

---

## 7. Checkpoints

| Wk | Dates | Checkpoint | Deliverable | Gate / if it fails |
|---|---|---|---|---|
| 1 | **done Sun Nov 1** | **CP1 Data, freeze, harness** | Manifest with near-duplicate grouping; **suites frozen**; `check_split`; dev set reviewed (≈ 2–3 h); `eval.py`; legal block; prompt files; student model confirmed | `eval.py` scores the gold labels, fed in as predictions, at 1.0; `check_split` passes. |
| 2 | Mon Nov 2 – Mon Nov 9 | **CP2 Teacher + baselines** | Day 1: Groq limits + caching check. ≤ 3 dev iterations with 20b and 120b → choose the teacher (D9) → full run on one provider (raw JSONL saved); S0-noLegal, S0, S1, B0 results; teacher consistency rate; **methods section drafted** | Sanity check: teacher macro-F1 on dev ≥ 0.80 and consistency ≥ 95%. If not met after 3 iterations, proceed anyway and report it as a finding. |
| 3–4 | Tue Nov 10 – Sun Nov 22 | **CP3 Students** (CP3a: one run end to end by Sun Nov 15; CP3b: all runs by Sun Nov 22) | Kaggle T4 notebook (pinned stack) looping conditions × sizes × seeds; test predictions; `results.csv` | T@571 beats S0 on dev. If not: check the template and scoring first, then the learning rate (once), then accept it and report. |
| 5 | Mon Nov 23 – Sun Nov 29 | **CP4 Analysis** | 2 figures, Holm-McNemar, slices, reasoning rubric (≈ 1–2 h), GGUF export + M3 re-scoring and latency; optional D13 | Every RQ has a table or figure. |
| 6 | Mon Nov 30 – Sun Dec 6 | **CP5 Report** | Report drafted; code, prompts and the manifest tagged in git | – |
| 7 | Mon Dec 7 – Tue Dec 15 | **Buffer** | Revisions, slack for anything that slipped; submit by Dec 15 | – |

Test predictions are produced **once per final model** and logged with a timestamp. Nothing is tuned on test.

---

## 8. Reuse from the repo, and new work

| Need | Reuse | New work (estimate) |
|---|---|---|
| Teacher prompt and label rule | `classifier/ECGT_CLAIM_CLASSIFIER_PROMPT.md`, the POST function | Reasoning field, legal block, conventions, stated label (½ day) |
| Legal context | Project doc `legal-framework-ecgt-ucpd.md`; `git show f0f1b57~1:src/knowledge/chunks/ecgt.json` (and `ucpd.json`) | Verbatim Art. 2 definitions o–s and Annex I 2 bis, 4 bis–4 quater, 10 bis (done: `prompts/legal_block.md`). Art. 6(2)(d)–(e) and Art. 7(7) are not in the vendored corpus. Note: ECGT's Art. 7(7) concerns comparison *services*, not vague comparisons, so it is not cited for `vague_comparison`. |
| Labelling conventions | `golden/labeled/golden_set_ecgt_100_README.md` | Report appendix |
| Retrieval (S1) and near-duplicate grouping | `retriever/score.py` (e5-base, pinned revision, `query:` prefix), `retriever/knowledge/anchors_v4.jsonl`, the embedding cache | `top3(claim)` + guard; cosine clustering (½ day) |
| Data | The 8 gold/reserve JSONs | Manifest, freeze, `check_split` (1 day) + dev review (2–3 h) |
| Teacher runner | `tools/groq_relabel.py` (never run; reference only) | OpenAI-compatible client (Groq / proxy / OpenRouter / llama.cpp server via base URL), rate-limit aware, resumable, raw JSONL (1 day) |
| Training and scoring | Unsloth's Qwen3 Kaggle notebook template | Loop, loader, log-prob scorer, T+R generation (2–3 days incl. debugging) |
| Evaluation | – | `eval.py`: metrics, κ, Holm-McNemar, bootstrap (1 day) |
| Inspection | `tools/jsonl_viewer.html` | – |

All new code lives in `apprentice/`. It must not change `eval/gold_spans_v1.jsonl`, `retriever/ecgt_retriever.yaml` or the anchors.

---

## 9. Cut order (if behind schedule)

1. Drop T-1.7B (RQ3 then compares 4B with the teacher).
2. Drop the 150 point of the curve.
3. Use 2 seeds instead of 3.
4. Drop B0.
5. Drop T-large.
6. Drop the curve entirely (n = 571 only).
7. Use 1 seed.

**Minimum viable project:** S0-noLegal, S0, S1, H@571, T@571, T+R and the teacher, at 4B, on the frozen suites. Realistically done by about Nov 22.

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Kaggle setup, version drift or chat-template mismatch eats week 3 | T4 only; pinned stack; HF inference instead of vLLM; one shared template function (D29); Mac `mlx-lm` fallback |
| Teacher disagrees with gold on convention-heavy cases | Conventions in the prompt; dev sanity check; noise reported as a finding |
| Thin positive classes (87 NV / 81 IN_SCOPE in train) | Oversampling, 3 seeds with data redraws, learning curve, binary fallback (D3) |
| Teacher self-inconsistency | D30 check and flag |
| Near-duplicate or template leakage | D25 grouping + a no-near-duplicate robustness subset |
| Carrefour-developed prompt and anchors flatter `test_carrefour` | Disclosed; per-suite reporting; `test_ce` as the cleanest suite |
| Groq free limits too low, or no caching | Caching check on CP2 day 1; one-provider fallback per D9 (Kaggle proxy / OpenRouter ≈ €6 / self-hosted 20b); start the full run by Wed Nov 4 |
| Accidental tuning on test | Frozen suites, a loader that refuses teacher-on-test files, predictions once per model |

---

## 11. Bridge to the thesis

This project delivers the **Pass 2 classifier** that the main pipeline lacks, plus frozen named test suites and a split protocol that can be extended (§4.3). Thesis extensions:

1. End to end: retriever + distilled classifier; page-level recall and cost per 1,000 products.
2. Teacher-labelled data from the ~50k raw records (`server/`), gated by `check_split`; scale curves beyond 1,200 texts.
3. Soft-label / logit distillation from a local same-family teacher (e.g. Qwen-32B → 4B), using the log-probabilities already collected; multi-teacher agreement as a noise filter.
4. Fine-grained categories and Italian citations (Codice del Consumo arts. 18/21/22/23, via D.Lgs. 30/2026).
5. Robustness: new retailers as new suites; drift after 27 Sept 2026.

---

## 12. Open items for the final review

- None for §4.3: 70/30, NaturaSì test-only, the 0.85 threshold and the scrape stretch (D17) were settled on 2026-11-01.
- Confirm the student model version at CP1 (D10).

## 13. Changes from v1 (independent review, 2026-11-01)

- **Must fix:**
  - separate teacher and student prompts (D21);
  - named test suites (D22);
  - the manifest freezes labels and git SHA, hashes text + footnote, freezes before the teacher run, and `check_split` becomes reusable (§4.3);
  - near-duplicate grouping (D25);
  - the teacher no longer sees anchors, and the H confounds are disclosed (D21, §5, D12);
  - log-prob scoring replaces constrained JSON decoding (D23).
- **Should fix:**
  - a fully reviewed dev set of about 50 per class, with the gate as a sanity check (D24);
  - oversampling instead of class weights, and seed-redrawn subsets (D16);
  - Holm correction and how seeds are aggregated (D15);
  - reasoning before label plus a rubric (D23, §6);
  - an RQ4 control;
  - T4 only and no vLLM (D11);
  - template and GGUF re-scoring (D29);
  - the S0-noLegal row (§5); the instructor email (D27) was later dropped;
  - an extended cut order (§9).
- **Nice to have:**
  - sync vs. Batch use and raw logging (D9, D28);
  - B0 on gold labels;
  - logging fields (D28);
  - € units and the local-cost assumption (D31);
  - "expert-reviewed" terminology (D12).
