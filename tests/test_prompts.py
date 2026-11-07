import json

from apprentice import prompts
from apprentice.check_split import DEFAULT_MANIFEST, check_split


def _all_text(msgs):
    return "\n".join(m["content"] for m in msgs)


def test_rendered_prompts_have_no_placeholders_or_headers():
    for msgs in (prompts.teacher_messages("x"), prompts.student_messages("x", legal=False),
                 prompts.student_messages("x", examples=[{"claim": "y", "label": "OUT"}]), prompts.ft_messages("x")):
        t = _all_text(msgs)
        assert "{{" not in t and "<!--" not in t
        assert msgs[-1] == {"role": "user", "content": "CLAIM: x"}


def test_students_never_see_trigger_names():
    triggers = ["generic_green", "undefined_natural", "climate_neutral", "vague_comparison", "brand_eco_slogan",
                "vague_supply_chain", "recycled_recyclable", "defined_term", "named_endorsement", "out_of_scope"]
    for msgs in (prompts.student_messages("x"), prompts.ft_messages("x")):
        t = _all_text(msgs)
        assert not any(tr in t for tr in triggers)


def test_legal_block_only_where_intended():
    assert "asserzione ambientale generica" in _all_text(prompts.student_messages("x", legal=True))
    assert "asserzione ambientale generica" not in _all_text(prompts.student_messages("x", legal=False))
    assert "asserzione ambientale generica" in _all_text(prompts.teacher_messages("x"))
    assert "asserzione ambientale" not in _all_text(prompts.ft_messages("x"))


def test_fewshots_do_not_leak_test_or_dev():
    if DEFAULT_MANIFEST.exists():
        files = [prompts.PROMPTS / "fewshot_teacher.jsonl", prompts.PROMPTS / "fewshot_student.jsonl"]
        assert check_split(training_files=files)["ok"]


def test_teacher_fewshot_labels_follow_post_rule():
    IN_SCOPE_T = {"generic_green", "undefined_natural", "climate_neutral", "vague_comparison",
                  "brand_eco_slogan", "vague_supply_chain"}

    def label(tr):
        t = set(tr) - {"out_of_scope"}
        if not t:
            return "OUT"
        if "defined_term" in t:
            t.discard("undefined_natural")
        return "IN_SCOPE" if t & IN_SCOPE_T else "NEEDS_VERIFICATION"

    for fs in prompts.fewshots("fewshot_teacher.jsonl"):
        assert label(fs["triggers"]) == fs["label"], fs["claim"]


def test_no_prompt_example_reveals_a_test_or_dev_claim():
    """Examples quoted inside prompts must not equal, near-duplicate or (3+ words) be contained in a
    test or dev claim (teacher prompt iteration 3, 2026-11-07)."""
    if not DEFAULT_MANIFEST.exists():
        return
    from apprentice.check_split import load_manifest
    assert prompts.prompt_leaks(load_manifest()) == []
