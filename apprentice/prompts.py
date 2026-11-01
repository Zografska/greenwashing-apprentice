"""Load and render the versioned prompt files in prompts/ (D21). Every prompt has a hash that is
logged with results (D28); the hash covers the rendered template, not the comment header."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apprentice.data import ROOT

PROMPTS = ROOT / "prompts"


def load(name: str) -> str:
    """Prompt text with the <!-- header --> stripped (everything up to the first line '---')."""
    text = (PROMPTS / name).read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    return body.strip("\n") + "\n" if sep and head.lstrip().startswith("<!--") else text


def prompt_hash(*parts: str) -> str:
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:16]


def fewshots(name: str) -> list[dict]:
    return [json.loads(l) for l in (PROMPTS / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def user(claim: str) -> str:
    return f"CLAIM: {claim}"


def teacher_messages(claim: str) -> list[dict]:
    system = load("P_teacher.md").replace("{{LEGAL_BLOCK}}", load("legal_block.md").strip())
    msgs = [{"role": "system", "content": system}]
    for fs in fewshots("fewshot_teacher.jsonl"):
        out = {"reasoning": fs["reasoning"], "triggers": fs["triggers"], "label": fs["label"]}
        msgs += [{"role": "user", "content": user(fs["claim"])},
                 {"role": "assistant", "content": json.dumps(out, ensure_ascii=False)}]
    return msgs + [{"role": "user", "content": user(claim)}]


def student_messages(claim: str, legal: bool = True, examples: list[dict] | None = None) -> list[dict]:
    """S0-noLegal (legal=False), S0 (legal=True), S1 (legal=True, examples=top-3 anchors as
    [{"claim":..., "label":...}]). The assistant turn to score is the bare label string."""
    legal_s = ("\nLegal context:\n" + load("legal_block.md").strip() + "\n") if legal else ""
    ex_s = ("\nSimilar labelled examples:\n" +
            "\n".join(f"CLAIM: {e['claim']} -> {e['label']}" for e in examples) + "\n") if examples else ""
    system = load("P_student.md").replace("{{LEGAL_SECTION}}", legal_s).replace("{{EXAMPLES_SECTION}}", ex_s)
    msgs = [{"role": "system", "content": system}]
    for fs in fewshots("fewshot_student.jsonl"):
        msgs += [{"role": "user", "content": user(fs["claim"])}, {"role": "assistant", "content": fs["label"]}]
    return msgs + [{"role": "user", "content": user(claim)}]


def ft_messages(claim: str) -> list[dict]:
    return [{"role": "system", "content": load("P_ft.md").strip()}, {"role": "user", "content": user(claim)}]
