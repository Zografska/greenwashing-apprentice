import pytest
from sklearn.metrics import f1_score

from apprentice import eval as ev


def test_metrics_match_sklearn_and_invalid_is_wrong():
    gold = ["IN_SCOPE", "OUT", "NEEDS_VERIFICATION", "OUT", "IN_SCOPE"]
    pred = ["IN_SCOPE", "OUT", "OUT", None, "garbage"]
    m = ev.metrics(gold, pred)
    clean = ["IN_SCOPE", "OUT", "OUT", "__INVALID__", "__INVALID__"]
    assert m["macro_f1"] == pytest.approx(f1_score(gold, clean, labels=list(ev.LABELS), average="macro", zero_division=0))
    assert m["valid_rate"] == pytest.approx(0.6)
    assert m["in_scope_recall"] == pytest.approx(0.5)
    assert m["flagged_recall"] == pytest.approx(1 / 3)


def test_perfect_predictions():
    gold = ["IN_SCOPE", "OUT", "NEEDS_VERIFICATION"] * 5
    m = ev.metrics(gold, gold)
    assert m["macro_f1"] == m["accuracy"] == m["flagged_recall"] == 1.0
    assert ev.bootstrap_ci(gold, gold, n_boot=50) == (1.0, 1.0)


def test_mcnemar_and_holm():
    gold = ["OUT"] * 20
    a = ["OUT"] * 20
    b = ["IN_SCOPE"] * 10 + ["OUT"] * 10
    r = ev.mcnemar(gold, a, b)
    assert (r["a_only_correct"], r["b_only_correct"]) == (10, 0) and r["p_value"] < 0.01
    assert ev.mcnemar(gold, a, a)["p_value"] == 1.0
    h = ev.holm({"x": 0.01, "y": 0.04, "z": 0.03})
    assert h["x"]["p_holm"] == pytest.approx(0.03)
    assert h["z"]["p_holm"] == pytest.approx(0.06) and h["y"]["p_holm"] == pytest.approx(0.06)
    assert h["x"]["reject"] and not h["y"]["reject"]


def test_majority_vote_tie_prefers_in_scope():
    runs = [{"t": "OUT"}, {"t": "IN_SCOPE"}, {"t": "NEEDS_VERIFICATION"}]
    assert ev.majority_vote(runs)["t"] == "IN_SCOPE"
    assert ev.majority_vote([{"t": "OUT"}, {"t": "OUT"}, {"t": "IN_SCOPE"}])["t"] == "OUT"


def test_error_overlap():
    gold = ["OUT", "OUT", "IN_SCOPE", "IN_SCOPE"]
    s = ["IN_SCOPE", "OUT", "OUT", "IN_SCOPE"]
    t = ["IN_SCOPE", "OUT", "IN_SCOPE", "IN_SCOPE"]
    r = ev.error_overlap(gold, s, t)
    assert r["student_errors"] == 2 and r["teacher_also_wrong"] == 0.5 and r["same_wrong_label"] == 0.5


def test_self_test_on_real_manifest():
    from apprentice.check_split import DEFAULT_MANIFEST, load_manifest
    if not DEFAULT_MANIFEST.exists():
        pytest.skip("no manifest")
    man = load_manifest()
    preds = {r["text_id"]: (r.get("dev_reviewed_label") if r["suite"] == "dev" else None) or r["gold_label"] for r in man}
    res = ev.evaluate(preds, man, n_boot=20)
    assert set(res) >= {"test_ce", "test_carrefour", "test_naturasi", "dev", "headline"}
    assert all(m["macro_f1"] == 1.0 for m in res.values())
