import json
from collections import Counter

import pytest

from apprentice import train
from apprentice.check_split import DEFAULT_MANIFEST, load_manifest

pytestmark = pytest.mark.skipif(not DEFAULT_MANIFEST.exists(), reason="no manifest")


@pytest.fixture(scope="module")
def man():
    return load_manifest()


def test_curve_subsets_are_nested_stratified_and_seeded(man):
    o0, o1 = train.ordered_train(man, 0), train.ordered_train(man, 1)
    assert len(o0) == 551 and {r["suite"] for r in o0} == {"train"}
    assert [r["text_id"] for r in o0] != [r["text_id"] for r in o1]           # seeds redraw
    full = Counter(r["gold_label"] for r in o0)
    for n in (150, 300):
        sub = Counter(r["gold_label"] for r in o0[:n])
        for lab in full:                                                        # class mix kept (±1)
            assert abs(sub[lab] - full[lab] * n / 551) <= 1


def test_h_and_t_share_texts(man):
    h, hi = train.build_examples("H", 150, 3, man)
    t, ti = train.build_examples("T", 150, 3, man)
    assert hi["subset_ids"] == ti["subset_ids"]
    assert {e["text_id"] for e in t} <= set(hi["subset_ids"])
    assert all(e["target"] in train.LABELS for e in h + t)


def test_tr_targets_are_reasoning_first_json(man):
    ex, _ = train.build_examples("T+R", 150, 0, man)
    obj = json.loads(ex[0]["target"])
    assert list(obj) == ["reasoning", "label"] and obj["label"] in train.LABELS


def test_t_large_adds_extra_texts(man):
    _, info = train.build_examples("T-large", 551, 0, man)
    assert info["texts"] == 551 + 574


def test_oversampling():
    ex = [{"label": "OUT"}] * 100 + [{"label": "IN_SCOPE"}] * 10 + [{"label": "NEEDS_VERIFICATION"}] * 30
    c = Counter(e["label"] for e in train.oversample(ex, 0, 0.5, 4.0))
    assert c["OUT"] == 100 and c["IN_SCOPE"] == 40 and c["NEEDS_VERIFICATION"] == 50


def test_parse_tr():
    assert train.parse_tr('{"reasoning": "x", "label": "OUT"}') == ("OUT", "x")
    assert train.parse_tr("garbage")[0] is None
