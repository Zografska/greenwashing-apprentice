import numpy as np

from apprentice.retrieve import AnchorRetriever, anchor_label


class FakeEncoder:
    """Bag-of-characters embedding: deterministic, no download."""
    def encode(self, texts):
        M = np.zeros((len(texts), 128))
        for i, t in enumerate(texts):
            for ch in t.lower():
                M[i, ord(ch) % 128] += 1
        return M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-9)


def test_anchor_labels():
    assert anchor_label({"polarity": "neg", "label_hint": None}) == "OUT"
    assert anchor_label({"polarity": "pos", "label_hint": "IN_SCOPE"}) == "IN_SCOPE"


def test_retriever_excludes_and_guards():
    r = AnchorRetriever(encoder=FakeEncoder())
    assert r.n_excluded == 17 and len(r.anchors) == 121 - 17
    excluded_texts = {"Senza parabeni"}  # N-free_from_non_pollutant anchors are excluded (overlap test)
    # an anchor's own text as the query must never come back (exact/near guard)
    probe = r.anchors[0]["text"]
    res = r.top_k([probe, "Confezione 100% riciclabile"], k=3)
    assert all(e["claim"] != probe for e in res[0])
    assert len(res[1]) == 3 and all(set(e) == {"id", "claim", "label", "cosine"} for e in res[1])
    assert r.guard_skips >= 1
    assert not any(e["claim"] in excluded_texts for row in res for e in row)
