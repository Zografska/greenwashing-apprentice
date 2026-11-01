"""Coverage check for the lexical half of the candidate rule (`lexical_hit OR margin > τ`).

Runs the `lexical.include` / `lexical.exclude` patterns from ecgt_retriever.yaml over:
  - the anchor set: every positive anchor should hit (misses depend on the embedding alone);
    negative hits are reported as a cost (each one is an extra Pass 2 call, no gate)
  - optionally, a claims file (coop_claims.json or golden_set_ecgt_*.json format): IN_SCOPE/NV
    claims play the role of positives, DISCARD/DISCARDED claims of negatives; claims with
    `needs_review: true` are skipped. Tune keywords on the reserve set, never on the gold 100.

Usage:
  python3 retriever/lexical_coverage.py
  python3 retriever/lexical_coverage.py --claims golden/clean/coop_claims.json
  add --loo retriever/loo_results_v3.csv to cross-check against LOO embedding misses.
"""
import argparse
import csv
import json
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


def load_patterns(config_path):
    cfg = yaml.safe_load(open(config_path, encoding="utf-8"))["lexical"]
    flags = 0
    for name in cfg.get("flags", []):
        flags |= getattr(re, name)
    inc = [re.compile(p, flags) for p in cfg.get("include", [])]
    exc = [re.compile(p, flags) for p in cfg.get("exclude", [])]
    return inc, exc


def lexical_hit(text, inc, exc):
    """Return the patterns that fire on text, or [] if none does or an exclude matches."""
    if any(p.search(text) for p in exc):
        return []
    return [p.pattern for p in inc if p.search(text)]


def report(name, items, inc, exc):
    """items: list of (text, is_pos, tag)."""
    pos = [(t, g) for t, p, g in items if p]
    neg = [(t, g) for t, p, g in items if not p]
    pos_miss = [(t, g) for t, g in pos if not lexical_hit(t, inc, exc)]
    neg_hit = [(t, g, lexical_hit(t, inc, exc)) for t, g in neg if lexical_hit(t, inc, exc)]
    print(f"\n=== {name} ===")
    print(f"positives hit:  {len(pos) - len(pos_miss)}/{len(pos)}")
    print(f"negatives hit:  {len(neg_hit)}/{len(neg)}   (cost metric, no gate)")
    if pos_miss:
        print("\npositives with no lexical hit (depend on the embedding alone):")
        for t, g in pos_miss:
            print(f"  [{g}] {t!r}")
    if neg_hit:
        print("\nnegatives with a lexical hit:")
        for t, g, pats in neg_hit:
            print(f"  [{g}] {t!r}  <- {', '.join(pats)}")
    return {t for t, _ in pos_miss}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=HERE / "ecgt_retriever.yaml")
    ap.add_argument("--anchors", help="default: anchors.path from the config")
    ap.add_argument("--claims", help="coop_claims.json-style file")
    ap.add_argument("--loo", help="loo_check.py CSV; lists positives missed by both")
    args = ap.parse_args()

    inc, exc = load_patterns(args.config)
    anchors_path = args.anchors or yaml.safe_load(open(args.config))["anchors"]["path"]
    anchors = [json.loads(l) for l in open(anchors_path, encoding="utf-8") if l.strip()]
    lex_miss = report(f"anchors ({anchors_path})",
                      [(a["text"], a["polarity"] == "pos", a["category"]) for a in anchors], inc, exc)

    if args.loo:
        rows = list(csv.DictReader(open(args.loo, encoding="utf-8")))
        text_of = {a["id"]: a["text"] for a in anchors}
        print("\npositives missed by BOTH the embedding (LOO) and the lexical rule:")
        for model in dict.fromkeys(r["model"] for r in rows):
            both = [text_of[r["id"]] for r in rows
                    if r["model"] == model and r["polarity"] == "pos"
                    and r["polarity_ok"] == "False" and text_of.get(r["id"]) in lex_miss]
            print(f"  {model}: {len(both)}" + "".join(f"\n      {t!r}" for t in both))

    if args.claims:
        products = json.load(open(args.claims, encoding="utf-8"))
        items = [(c["claim_text"], c.get("label") not in ("DISCARD", "DISCARDED"), c.get("label"))
                 for p in products for c in p.get("claims", []) if not c.get("needs_review")]
        report(f"claims ({args.claims})", items, inc, exc)


if __name__ == "__main__":
    main()
