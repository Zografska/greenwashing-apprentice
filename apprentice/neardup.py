"""Lexical near-duplicate detection (character n-gram TF-IDF cosine).

Used for the split (D25) and by check_split for new data. Lexical, not semantic, on purpose:
the leak we guard against is the same claim with small surface changes (product name,
number, punctuation), and it needs no model download, so it runs anywhere (Mac, Kaggle, CI).
"""
from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_THRESHOLD = 0.85


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, norm="l2")


def similarity(a: list[str], b: list[str] | None = None, fit_corpus: list[str] | None = None) -> np.ndarray:
    """Cosine similarity matrix between normalised texts a (rows) and b (cols; default a).
    IDF is fitted on `fit_corpus` if given (use the full manifest for reproducible checks)."""
    vec = _vectorizer().fit(fit_corpus if fit_corpus is not None else a + (b or []))
    A = vec.transform(a)
    B = A if b is None else vec.transform(b)
    return (A @ B.T).toarray().astype(np.float32)


def clusters(texts: list[str], threshold: float = DEFAULT_THRESHOLD) -> list[int]:
    """Union-find over pairs with cosine >= threshold. Returns a cluster index per text."""
    n = len(texts)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    S = similarity(texts, fit_corpus=texts)
    ii, jj = np.where(np.triu(S >= threshold, k=1))
    for i, j in zip(ii.tolist(), jj.tolist()):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)
    roots = [find(i) for i in range(n)]
    remap = {r: k for k, r in enumerate(sorted(set(roots)))}
    return [remap[r] for r in roots]


def near_dups(a: list[str], b: list[str], threshold: float = DEFAULT_THRESHOLD,
              fit_corpus: list[str] | None = None) -> list[tuple[int, int, float]]:
    """Pairs (i in a, j in b, sim) with cosine >= threshold."""
    if not a or not b:
        return []
    S = similarity(a, b, fit_corpus)
    ii, jj = np.where(S >= threshold)
    return [(int(i), int(j), float(S[i, j])) for i, j in zip(ii, jj)]
