# Discarded teacher runs (kept for the record, never used)

- `2026-11-07_json_object/`: first dev runs (gpt-oss-20b and -120b, OpenRouter coreweave/fp4, prompt
  b450d75e7e10a6f0) with provider-side `response_format: json_object`. The JSON grammar constraint broke
  gpt-oss's output: 20b returned empty content on 150/150 calls; 120b produced degenerate JSON (valid 7%,
  invented triggers such as `out_of_word`). Fix: JSON enforcement off by default (`--json-mode none`),
  JSON parsed from the content. Cost of the discarded runs: $0.033.
