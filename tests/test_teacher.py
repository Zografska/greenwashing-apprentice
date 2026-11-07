from apprentice import teacher


def test_post_label():
    assert teacher.post_label(["out_of_scope"]) == "OUT"
    assert teacher.post_label(["certification", "generic_green"]) == "IN_SCOPE"
    assert teacher.post_label(["defined_term", "undefined_natural"]) == "NEEDS_VERIFICATION"
    assert teacher.post_label(["vegan", "out_of_scope"]) == "NEEDS_VERIFICATION"
    assert teacher.post_label(["made_up"]) is None and teacher.post_label([]) is None


def test_parse_handles_json_and_noise():
    p = teacher.parse('{"reasoning": "x", "triggers": ["generic_green"], "label": "IN_SCOPE"}')
    assert p["post_label"] == "IN_SCOPE" and p["consistent"] and p["valid"]
    p = teacher.parse('text before {"reasoning": "y", "triggers": ["vegan"], "label": "OUT"} after')
    assert p["post_label"] == "NEEDS_VERIFICATION" and not p["consistent"]
    p = teacher.parse("not json")
    assert not p["valid"] and p["post_label"] is None
    assert teacher.parse('{"triggers": ["oops"], "label": "OUT"}')["unknown_triggers"] == ["oops"]


def test_test_suites_go_to_isolated_dir():
    from apprentice.check_split import TEACHER_TEST_DIR
    p = teacher.out_path("openai/gpt-oss-20b", "test_carrefour", "abc", "openrouter-x")
    assert TEACHER_TEST_DIR in p.resolve().parents
    p = teacher.out_path("openai/gpt-oss-20b", "train", "abc", "openrouter-x")
    assert TEACHER_TEST_DIR not in p.resolve().parents


def test_prompt_hash_is_stable():
    assert teacher.teacher_prompt_hash() == teacher.teacher_prompt_hash()


def test_openrouter_body_pins_provider():
    import argparse
    a = argparse.Namespace(service="openrouter", pin="deepinfra", reasoning_effort="low", max_tokens=512)
    b = teacher.request_body("openai/gpt-oss-120b", "x", a)
    assert b["provider"] == {"order": ["deepinfra"], "allow_fallbacks": False, "require_parameters": True}
    assert b["reasoning"] == {"effort": "low"} and "reasoning_effort" not in b
    a.service = "groq"
    assert teacher.request_body("openai/gpt-oss-120b", "x", a)["reasoning_effort"] == "low"
