# greenwashing-apprentice

Distilling a large open LLM's judgement on EU greenwashing claims (Directive (EU) 2024/825, "ECGT") into a
small model that runs on a laptop. NLP class project, a variant of *P6: The Apprentice Model*.

- **Task:** classify one Italian e-commerce product claim as `IN_SCOPE` (problematic as written),
  `NEEDS_VERIFICATION` (specific, checkable) or `OUT` (not an environmental claim).
- **Teacher:** gpt-oss-120b (Groq). **Students:** Qwen3 ≈ 4B / ≈ 1.7B, QLoRA on a Kaggle T4, run locally as GGUF.
- **Key comparison:** a student trained on teacher labels vs. one trained on expert-reviewed labels for the
  same texts; prompted retrieval (labelled examples + directive context) vs. fine-tuning.

Plan and decisions: [`docs/SPEC.md`](docs/SPEC.md). Data provenance: [`VENDORED.md`](VENDORED.md).

Status: scaffolding done; CP1 in progress.
