"""Anchor retrieval for S1 and e5 embeddings for B0 (SPEC D6, D8).

e5 settings come from the vendored retriever config: intfloat/multilingual-e5-base at the pinned revision,
prefix "query: " on both sides, normalised embeddings. Needs sentence-transformers and Hugging Face access
(Kaggle with Internet on, or the Mac).

Leak guard (D8): anchors listed in splits/anchor_exclusions_v1.json (lexical overlap with test, verified by
check_split) are never retrieved, and at query time any anchor whose normalised text equals the claim or whose
cosine with it is >= 0.95 is skipped. Skips are counted.

  r = AnchorRetriever()
  r.top_k(["Confezione 100% riciclabile"], k=3)   # -> [[{"id","claim","label","cosine"}, ...]]
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from apprentice.check_split import EXCLUSIONS_FILE, check_split
from apprentice.data import ROOT, normalise

ANCHORS = ROOT / "vendor" / "retriever" / "anchors_v4.jsonl"
E5_MODEL = "intfloat/multilingual-e5-base"
E5_REVISION = "d128750597153bb5987e10b1c3493a34e5a4502a"   # vendor/retriever/ecgt_retriever.yaml
E5_PREFIX = "query: "
GUARD_COSINE = 0.95


class E5:
    def __init__(self, device: str | None = None, batch_size: int = 64):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(E5_MODEL, revision=E5_REVISION, device=device)
        self.batch_size = batch_size

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode([E5_PREFIX + t for t in texts], batch_size=self.batch_size,
                                 normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)


def anchor_label(a: dict) -> str:
    return a["label_hint"] if a["polarity"] == "pos" else "OUT"


class AnchorRetriever:
    def __init__(self, encoder=None, anchors_path: Path = ANCHORS, exclusions_path: Path = EXCLUSIONS_FILE,
                 verify: bool = True):
        """`encoder` needs .encode(list[str]) -> L2-normalised np.ndarray (default: E5)."""
        excluded = set(json.loads(Path(exclusions_path).read_text())) if Path(exclusions_path).exists() else set()
        if verify:   # the exclusion list must cover every anchor that overlaps test (SPEC §4.3 rule 2)
            check_split(anchors_path=anchors_path, anchor_exclusions=sorted(excluded))
        all_anchors = [json.loads(l) for l in open(anchors_path, encoding="utf-8") if l.strip()]
        self.anchors = [a for a in all_anchors if a["id"] not in excluded]
        self.n_excluded = len(all_anchors) - len(self.anchors)
        self.encoder = encoder or E5()
        self.A = self.encoder.encode([a["text"] for a in self.anchors])
        self.norms = [normalise(a["text"]) for a in self.anchors]
        self.guard_skips = 0

    def top_k(self, claims: list[str], k: int = 3) -> list[list[dict]]:
        Q = self.encoder.encode(claims)
        S = Q @ self.A.T
        out = []
        for claim, sims in zip(claims, S):
            n = normalise(claim)
            picked = []
            for j in np.argsort(-sims):
                if sims[j] >= GUARD_COSINE or self.norms[j] == n:
                    self.guard_skips += 1
                    continue
                a = self.anchors[j]
                picked.append({"id": a["id"], "claim": a["text"], "label": anchor_label(a), "cosine": float(sims[j])})
                if len(picked) == k:
                    break
            out.append(picked)
        return out
