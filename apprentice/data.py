"""Load the vendored gold and reserve sets as unique claim texts.

The student sees only the claim text (footnotes are already joined into `claim_text`
as "claim ... footnote" by the labelling conventions), so the unit of everything
downstream (split, training, evaluation) is the *normalised claim text*.

Rules (SPEC §4.1):
- gold label DISCARDED -> OUT
- claims with needs_review: true are skipped everywhere
- a text seen in a fully reviewed gold-100 set takes its label from there;
  reserve sets (lighter review) only label texts that appear nowhere in a gold-100
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = ROOT / "vendor" / "golden"
SOURCE_GIT_SHA = "0d0081a7e6eb02279f4b9792dc5466e2c6b67086"  # see VENDORED.md

LABELS = ("IN_SCOPE", "NEEDS_VERIFICATION", "OUT")
LABEL_MAP = {"IN_SCOPE": "IN_SCOPE", "NEEDS_VERIFICATION": "NEEDS_VERIFICATION",
             "DISCARDED": "OUT", "OUT": "OUT"}

# file stem -> (origin, review level). origin decides the test suite a text can belong to.
SOURCES = {
    "golden_set_ecgt_100":              ("carrefour", "gold"),
    "golden_set_ecgt_coop_100":         ("coop",      "gold"),
    "golden_set_ecgt_eurospin_100":     ("eurospin",  "gold"),
    "golden_set_ecgt_naturasi_100":     ("naturasi",  "gold"),
    "golden_set_ecgt_reserve":          ("carrefour", "reserve"),
    "golden_set_ecgt_coop_reserve":     ("coop",      "reserve"),
    "golden_set_ecgt_eurospin_reserve": ("eurospin",  "reserve"),
    "golden_set_ecgt_naturasi_reserve": ("naturasi",  "reserve"),
}


def normalise(text: str) -> str:
    """Lowercase, NFKC, collapse every run of non-word characters to one space, trim."""
    t = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"\W+", " ", t).strip()


def text_id(norm: str) -> str:
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


@dataclass
class Occurrence:
    source_file: str
    origin: str
    review: str          # "gold" | "reserve"
    product_id: str
    source_field: str
    label: str           # mapped label in this occurrence
    triggers: list[str]


@dataclass
class UniqueText:
    text_id: str
    norm: str
    text: str                      # verbatim claim_text of the first gold occurrence (else first)
    footnote: str | None
    occurrences: list[Occurrence] = field(default_factory=list)

    @property
    def gold_occ(self) -> list[Occurrence]:
        return [o for o in self.occurrences if o.review == "gold"]

    @property
    def label_source(self) -> str:
        return "gold" if self.gold_occ else "reserve"

    def _label_pool(self) -> list[Occurrence]:
        return self.gold_occ or self.occurrences

    @property
    def label(self) -> str:
        """Majority label over the authoritative occurrences (gold if any, else reserve)."""
        return Counter(o.label for o in self._label_pool()).most_common(1)[0][0]

    def label_for(self, origin: str) -> str:
        """Label from this origin's gold occurrences (used for test suites: the suite's own
        frozen gold wins over other sets' labels for the same text). Falls back to `label`."""
        occ = [o for o in self.gold_occ if o.origin == origin]
        return Counter(o.label for o in occ).most_common(1)[0][0] if occ else self.label

    @property
    def label_conflict(self) -> bool:
        return len({o.label for o in self._label_pool()}) > 1

    @property
    def triggers(self) -> list[str]:
        for o in self._label_pool():
            if o.label == self.label:
                return o.triggers
        return []

    @property
    def origins(self) -> set[str]:
        return {o.origin for o in self.occurrences}

    def has(self, origin: str, review: str) -> bool:
        return any(o.origin == origin and o.review == review for o in self.occurrences)


def load_unique_texts(golden_dir: Path = GOLDEN_DIR) -> tuple[dict[str, UniqueText], dict]:
    """Return {text_id: UniqueText} plus load statistics."""
    texts: dict[str, UniqueText] = {}
    stats = Counter()
    for stem, (origin, review) in SOURCES.items():
        records = json.loads((golden_dir / f"{stem}.json").read_text(encoding="utf-8"))
        for rec in records:
            for c in rec.get("claims", []):
                stats["claims_total"] += 1
                if c.get("needs_review"):
                    stats["skipped_needs_review"] += 1
                    continue
                norm = normalise(c["claim_text"])
                if not norm:
                    stats["skipped_empty"] += 1
                    continue
                tid = text_id(norm)
                occ = Occurrence(
                    source_file=f"vendor/golden/{stem}.json", origin=origin, review=review,
                    product_id=str(rec.get("product_id") or rec.get("ean") or ""),
                    source_field=c.get("source_field") or "",
                    label=LABEL_MAP[c["label"]], triggers=list(c.get("triggers") or []))
                ut = texts.get(tid)
                if ut is None:
                    ut = texts[tid] = UniqueText(tid, norm, c["claim_text"], c.get("footnote"))
                elif review == "gold" and not ut.gold_occ:
                    ut.text, ut.footnote = c["claim_text"], c.get("footnote")  # prefer gold wording
                ut.occurrences.append(occ)
    stats["unique_texts"] = len(texts)
    stats["label_conflicts"] = sum(t.label_conflict for t in texts.values())
    return texts, dict(stats)


if __name__ == "__main__":
    texts, stats = load_unique_texts()
    print(json.dumps(stats, indent=2))
    print(Counter((t.label_source, t.label) for t in texts.values()))
    for t in [t for t in texts.values() if t.label_conflict][:10]:
        print("CONFLICT", t.text[:70], [(o.source_file.split('/')[-1], o.label) for o in t._label_pool()])
