import json

import pytest

from apprentice import neardup
from apprentice.check_split import SplitError, assert_trainable_path, check_split, TEACHER_TEST_DIR
from apprentice.data import normalise, text_id


def row(text, side, cluster, suite=None):
    n = normalise(text)
    return {"text_id": text_id(n), "text": text, "norm": n, "side": side,
            "suite": suite or side, "near_dup_cluster": cluster, "near_dup_threshold": 0.9}


def write(tmp_path, rows, name="m.jsonl"):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows))
    return p


BASE = [row("Confezione 100% riciclabile", "test", 0),
        row("Senza glutine", "train", 1),
        row("Prodotto da agricoltura biologica certificata", "dev", 2),
        row("Il nostro impegno per il pianeta", "train", 3)]


def test_normalise():
    assert normalise("  Eco-Pack: 100% RICICLABILE!! ") == "eco pack 100 riciclabile"


def test_clusters_group_template_variants():
    texts = [normalise(t) for t in ["Dermatologicamente testato su pelli sensibili",
                                    "Dermatologicamente testata su pelli sensibili",
                                    "Senza glutine"]]
    c = neardup.clusters(texts, 0.9)
    assert c[0] == c[1] != c[2]


def test_clean_manifest_passes(tmp_path):
    assert check_split(write(tmp_path, BASE))["ok"]


def test_cluster_on_two_sides_fails(tmp_path):
    rows = BASE + [row("Confezione 100% riciclabile!", "train", 0)]
    with pytest.raises(SplitError, match="more than one side"):
        check_split(write(tmp_path, rows))


def test_near_dup_across_sides_fails(tmp_path):
    rows = BASE + [row("Confezione riciclabile al 100%", "train", 9)]
    rows[-1]["text"] = rows[-1]["norm"] = normalise("confezione 100 riciclabile x")
    with pytest.raises(SplitError, match="near-dup"):
        check_split(write(tmp_path, rows))


def test_training_file_with_test_text_fails(tmp_path):
    m = write(tmp_path, BASE)
    tf = tmp_path / "train.jsonl"
    tf.write_text(json.dumps({"text": "CONFEZIONE 100% riciclabile"}) + "\n")
    with pytest.raises(SplitError, match="exact"):
        check_split(m, training_files=[tf])


def test_training_file_with_dev_text_fails(tmp_path):
    m = write(tmp_path, BASE)
    tf = tmp_path / "train.jsonl"
    tf.write_text(json.dumps({"text": "Prodotto da agricoltura biologica certificata"}) + "\n")
    with pytest.raises(SplitError):
        check_split(m, training_files=[tf])


def test_teacher_test_dir_is_not_trainable():
    with pytest.raises(SplitError):
        assert_trainable_path(TEACHER_TEST_DIR / "teacher_test.jsonl")
    assert_trainable_path(TEACHER_TEST_DIR.parent / "train.jsonl")  # fine


def test_anchor_overlap_must_be_excluded(tmp_path):
    m = write(tmp_path, BASE)
    a = tmp_path / "anchors.jsonl"
    a.write_text(json.dumps({"id": "A1", "text": "Confezione 100% riciclabile"}) + "\n" +
                 json.dumps({"id": "A2", "text": "Clinicamente testato"}) + "\n")
    with pytest.raises(SplitError, match="A1"):
        check_split(m, anchors_path=a, anchor_exclusions=[])
    assert check_split(m, anchors_path=a, anchor_exclusions=["A1"])["anchor_exclusions_required"] == ["A1"]


def test_curve_subset_outside_train_fails(tmp_path):
    m = write(tmp_path, BASE)
    with pytest.raises(SplitError, match="curve subset"):
        check_split(m, curve_subsets={"n150": [BASE[0]["text_id"]]})


def test_frozen_hash_detects_edits(tmp_path):
    m = write(tmp_path, BASE)
    from apprentice.check_split import sha256
    (tmp_path / "FROZEN").write_text(f"m.jsonl {sha256(m)}\n")
    assert check_split(m)["frozen"]
    m.write_text(m.read_text().replace("riciclabile", "riciclata"))
    with pytest.raises(SplitError, match="frozen"):
        check_split(m)


def test_real_manifest_passes():
    from apprentice.check_split import DEFAULT_MANIFEST
    if not DEFAULT_MANIFEST.exists():
        pytest.skip("no manifest built yet")
    assert check_split(DEFAULT_MANIFEST)["ok"]
