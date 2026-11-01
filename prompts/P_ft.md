<!-- prompts/P_ft.md: system prompt for all fine-tuned students (H, T, T-large, T-1.7B, T+R) (D7, D21).
     Deliberately minimal: no legal context, no examples, no categories. User message: "CLAIM: <text>".
     Label-only students: target = the label string. T+R: target = {"reasoning": ..., "label": ...}.
     Everything above --- is stripped. -->
---
Classify the claim from an Italian product listing under Directive (EU) 2024/825 (ECGT) as IN_SCOPE, NEEDS_VERIFICATION or OUT.
