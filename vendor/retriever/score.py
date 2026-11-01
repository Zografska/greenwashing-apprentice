"""Step 4: candidate scoring.

A span from segment.py becomes a candidate if `lexical_hit OR margin > τ`, where
margin = agg(sim to positive anchors) − agg(sim to negative anchors), agg = max or top-3 mean.
The span's margin is the max over its scored texts: the full text (with any joined footnote)
and its comma clauses. Each candidate keeps its top-k nearest positive anchors (id, text,
triggers) as Pass 2 few-shot. The retriever only decides *whether* a span is a candidate;
labels come from Pass 2 + POST.

Settings: `anchors`, `embedding`, `lexical` and `scoring` in ecgt_retriever.yaml. While
`scoring.tau.<model>` is null (before Step 5), only the lexical rule selects candidates, but every
span still gets its margin so Step 5 can sweep τ.

Usage:
  from retriever.score import Retriever
  r = Retriever(load_config())
  scored = r.score_record(record)          # every span with margin, lexical hits, candidate flag
  python3 retriever/score.py golden/clean/carrefour.json --index 1 [--model mpnet] [--all]
"""
import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from lexical_coverage import lexical_hit  # noqa: E402
from segment import Segmenter, Span, load_config  # noqa: E402


@dataclass
class Scored:
    span: Span
    margin: float                   # max over the span's scored texts
    best_text: str                  # the text (full span or a clause) that gave the margin
    lexical: list                   # keyword patterns that fired on the full text
    candidate: bool
    anchors: list = field(default_factory=list)   # top-k positive anchors: id, text, triggers, sim


class Retriever:
    def __init__(self, cfg, model=None):
        self.cfg = cfg
        emb = cfg["embedding"]
        self.model_key = model or emb["active"]
        self.mcfg = emb["models"][self.model_key]
        sc = cfg["scoring"]
        if sc["method"] != "margin" or sc["candidate_rule"] != "lexical_or_margin":
            raise ValueError("only method=margin, candidate_rule=lexical_or_margin are implemented")
        self.aggregation = sc["aggregation"]
        self.tau = (sc.get("tau") or {}).get(self.model_key)
        self.k = sc["fewshot_k"]
        self.segmenter = Segmenter(cfg)
        self.inc, self.exc = _patterns(cfg)

        path = ROOT / cfg["anchors"]["path"]
        raw = path.read_bytes()
        self.anchors_sha = hashlib.sha256(raw).hexdigest()
        want = cfg["anchors"].get("sha256")
        if want and want != self.anchors_sha:
            raise ValueError(f"anchors sha256 mismatch: config {want}, file {self.anchors_sha}")
        self.anchors = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
        self.is_pos = np.array([a["polarity"] == "pos" for a in self.anchors])
        self._model = None
        self._memo = {}
        self.A = self._anchor_matrix()

    # ---- embeddings ---------------------------------------------------------------------

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            device = self.cfg["embedding"].get("device", "auto")
            self._model = SentenceTransformer(self.mcfg["name"], revision=self.mcfg.get("revision"),
                                              device=None if device == "auto" else device)
        return self._model

    def embed(self, texts):
        prefix = self.mcfg.get("prefix") or ""
        return np.asarray(self._load_model().encode(
            [prefix + t for t in texts], batch_size=self.cfg["embedding"]["batch_size"],
            normalize_embeddings=self.mcfg.get("normalize", True), show_progress_bar=False),
            dtype=np.float32)

    def _embed_cached(self, texts):
        """embed() with an in-memory cache, so rescoring (e.g. another aggregation) is free."""
        new = [t for t in dict.fromkeys(texts) if t not in self._memo]
        if new:
            self._memo.update(zip(new, self.embed(new)))
        return np.stack([self._memo[t] for t in texts])

    def _anchor_matrix(self):
        """Anchor embeddings, cached by model name + revision + anchors sha256."""
        key = hashlib.sha256(f"{self.mcfg['name']}|{self.mcfg.get('revision')}|{self.mcfg.get('prefix')}|"
                             f"{self.anchors_sha}".encode()).hexdigest()[:16]
        cache = ROOT / self.cfg["embedding"]["cache_dir"] / f"{self.model_key}-{key}.npy"
        if cache.exists():
            return np.load(cache)
        A = self.embed([a["text"] for a in self.anchors])
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, A)
        return A

    # ---- scoring ------------------------------------------------------------------------

    def _agg(self, S):
        """Row-wise aggregate of a similarity block: max or mean of the top 3."""
        if self.aggregation == "max":
            return S.max(axis=1)
        k = min(3, S.shape[1])
        return np.sort(S, axis=1)[:, -k:].mean(axis=1)

    def score_spans(self, spans):
        texts, owner = [], []
        for i, sp in enumerate(spans):
            for t in dict.fromkeys([sp.text, *sp.clauses]):
                texts.append(t)
                owner.append(i)
        if not texts:
            return []
        S = self._embed_cached(texts) @ self.A.T
        margins = self._agg(S[:, self.is_pos]) - self._agg(S[:, ~self.is_pos])
        pos_idx = np.flatnonzero(self.is_pos)

        out = []
        owner = np.array(owner)
        for i, sp in enumerate(spans):
            rows = np.flatnonzero(owner == i)
            best = rows[np.argmax(margins[rows])]
            lex = lexical_hit(sp.text, self.inc, self.exc)
            m = float(margins[best])
            cand = bool(lex) or (self.tau is not None and m > self.tau)
            # Few-shot anchors: nearest positives to the full span text (its first row).
            sims = S[rows[0], pos_idx]
            top = pos_idx[np.argsort(-sims)[:self.k]]
            anchors = [dict(id=self.anchors[j]["id"], text=self.anchors[j]["text"],
                            triggers=self.anchors[j]["triggers"], sim=round(float(S[rows[0], j]), 4))
                       for j in top]
            out.append(Scored(sp, m, texts[best], lex, cand, anchors))
        return out

    def score_record(self, record):
        return self.score_spans(self.segmenter.segment(record))

    def candidates(self, record):
        return [s for s in self.score_record(record) if s.candidate]


def _patterns(cfg):
    lx = cfg["lexical"]
    flags = 0
    for name in lx.get("flags", []):
        flags |= getattr(re, name)
    return ([re.compile(p, flags) for p in lx.get("include", [])],
            [re.compile(p, flags) for p in lx.get("exclude", [])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", help="JSON list of product records")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--model", help="key into embedding.models (default: embedding.active)")
    ap.add_argument("--all", action="store_true", help="print every span, not only candidates")
    args = ap.parse_args()
    r = Retriever(load_config(), model=args.model)
    rec = json.load(open(args.records, encoding="utf-8"))[args.index]
    scored = r.score_record(rec)
    print(f"model={r.model_key} tau={r.tau} spans={len(scored)} "
          f"candidates={sum(s.candidate for s in scored)}")
    for s in sorted(scored, key=lambda s: -s.margin):
        if args.all or s.candidate:
            flag = "C" if s.candidate else " "
            lex = "L" if s.lexical else " "
            print(f"{flag}{lex} {s.margin:+.3f}  {s.span.text[:90]!r}  → {s.anchors[0]['id']}")


if __name__ == "__main__":
    main()
