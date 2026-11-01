"""Build the split manifest (SPEC §4, D5/D22/D24/D25).

Unit: unique normalised claim text. Near-duplicate clusters stay on one side.

Assignment, in order:
  1. a cluster with any Carrefour-gold or NaturaSì-gold text -> test side
  2. other clusters with Coop/Eurospin gold texts -> 70% train / 30% test_ce
     (cluster-level, stratified by cluster label, seeded)
  3. reserve texts in a cluster that already holds gold texts -> excluded_overlap
  4. reserve-only clusters -> dev (~50 texts per class, cluster-level) or t_large_extra
Suite of a test-side text = its own origin (test_carrefour > test_naturasi > test_ce).

Usage:
  python3 -m apprentice.split                # writes splits/split_v1.jsonl (+ report); refuses if frozen
  python3 -m apprentice.split --dry-run      # summary only
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from apprentice.data import LABELS, ROOT, SOURCE_GIT_SHA, load_unique_texts
from apprentice import neardup

SPLIT_VERSION = "v1"
TEST_SUITES = ("test_carrefour", "test_naturasi", "test_ce")
SIDE = {"train": "train", "dev": "dev", "t_large_extra": "train_extra",
        "test_carrefour": "test", "test_naturasi": "test", "test_ce": "test",
        "excluded_overlap": "excluded"}


def build(seed: int = 0, test_frac_ce: float = 0.30, threshold: float = neardup.DEFAULT_THRESHOLD,
          dev_per_class: int = 50):
    texts, load_stats = load_unique_texts()
    items = sorted(texts.values(), key=lambda t: t.text_id)          # deterministic order
    cl = neardup.clusters([t.norm for t in items], threshold)
    by_cluster: dict[int, list] = defaultdict(list)
    for t, c in zip(items, cl):
        by_cluster[c].append(t)

    suite: dict[str, str] = {}
    rng = random.Random(seed)

    def cluster_label(members) -> str:
        return Counter(m.label for m in members).most_common(1)[0][0]

    ce_clusters = defaultdict(list)      # label -> [cluster ids] for step 2
    reserve_clusters = defaultdict(list)  # label -> [cluster ids] for step 4
    for c, members in sorted(by_cluster.items()):
        gold = [m for m in members if m.label_source == "gold"]
        if any(m.has("carrefour", "gold") or m.has("naturasi", "gold") for m in gold):
            for m in members:
                if m.label_source != "gold":
                    suite[m.text_id] = "excluded_overlap"
                elif m.has("carrefour", "gold"):
                    suite[m.text_id] = "test_carrefour"
                elif m.has("naturasi", "gold"):
                    suite[m.text_id] = "test_naturasi"
                else:
                    suite[m.text_id] = "test_ce"
        elif gold:
            ce_clusters[cluster_label(gold)].append(c)
        else:
            reserve_clusters[cluster_label(members)].append(c)

    # step 2: Coop/Eurospin gold clusters, stratified 70/30 by cluster label
    for lab in LABELS:
        cs = ce_clusters[lab][:]
        rng.shuffle(cs)
        n_test = round(len(cs) * test_frac_ce)
        for k, c in enumerate(cs):
            side = "test_ce" if k < n_test else "train"
            for m in by_cluster[c]:
                suite[m.text_id] = side if m.label_source == "gold" else "excluded_overlap"

    # step 4: reserve-only clusters -> dev (~dev_per_class texts per class) / t_large_extra
    for lab in LABELS:
        cs = reserve_clusters[lab][:]
        rng.shuffle(cs)
        taken = 0
        for c in cs:
            members = by_cluster[c]
            to_dev = taken < dev_per_class
            for m in members:
                suite[m.text_id] = "dev" if to_dev else "t_large_extra"
            if to_dev:
                taken += len(members)

    suite_origin = {"test_carrefour": "carrefour", "test_naturasi": "naturasi"}
    res_file = ROOT / "splits" / f"label_resolutions_{SPLIT_VERSION}.json"
    resolutions = json.loads(res_file.read_text(encoding="utf-8"))["labels"] if res_file.exists() else {}
    git = _git_head()
    rows = []
    for t, c in zip(items, cl):
        s = suite[t.text_id]
        lab = t.label_for(suite_origin[s]) if s in suite_origin else t.label
        resolution = None
        if t.text_id in resolutions:
            lab, resolution = resolutions[t.text_id]["label"], f"{res_file.name} (author decision, D32)"
        rows.append({
            "text_id": t.text_id, "text": t.text, "footnote": t.footnote, "norm": t.norm,
            "suite": suite[t.text_id], "side": SIDE[suite[t.text_id]],
            "gold_label": lab, "gold_label_source": t.label_source,
            "gold_label_conflict": t.label_conflict, "gold_label_resolution": resolution,
            "gold_triggers": t.triggers,
            "dev_reviewed_label": None,
            "near_dup_cluster": c, "near_dup_cluster_size": len(by_cluster[c]),
            "occurrences": [{"source_file": o.source_file, "product_id": o.product_id,
                             "source_field": o.source_field, "label": o.label} for o in t.occurrences],
            "source_git_sha": SOURCE_GIT_SHA,
            "split_version": SPLIT_VERSION, "split_seed": seed, "test_frac_ce": test_frac_ce,
            "near_dup_threshold": threshold, "built_at_commit": git, "created": date.today().isoformat(),
        })
    multi = [m for m in by_cluster.values() if len(m) > 1]
    report = {
        "load": load_stats, "params": {"seed": seed, "test_frac_ce": test_frac_ce,
                                       "near_dup_threshold": threshold, "dev_per_class": dev_per_class},
        "clusters": {"total": len(by_cluster), "multi_text": len(multi),
                     "texts_in_multi": sum(len(m) for m in multi)},
        "suite_label_counts": _counts(rows),
        "label_conflicts": [{"text": r["text"], "suite": r["suite"],
                             "labels": sorted({o["label"] for o in r["occurrences"]}),
                             "label_used": r["gold_label"], "resolution": r["gold_label_resolution"]}
                            for r in rows if r["gold_label_conflict"]],
        "merged_examples": [[m.text for m in members][:4] for members in
                            sorted(multi, key=len, reverse=True)[:25]],
    }
    return rows, report


def _counts(rows):
    out = defaultdict(Counter)
    for r in rows:
        out[r["suite"]][r["gold_label"]] += 1
    return {s: dict(c) | {"total": sum(c.values())} for s, c in sorted(out.items())}


def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--test-frac-ce", type=float, default=0.30)
    ap.add_argument("--threshold", type=float, default=neardup.DEFAULT_THRESHOLD)
    ap.add_argument("--dev-per-class", type=int, default=50)
    ap.add_argument("--out", default=str(ROOT / "splits" / f"split_{SPLIT_VERSION}.jsonl"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    frozen = ROOT / "splits" / "FROZEN"
    if not args.dry_run and frozen.exists() and out.name in frozen.read_text():
        raise SystemExit(f"{out.name} is frozen (splits/FROZEN). Make a new split version instead.")

    rows, report = build(args.seed, args.test_frac_ce, args.threshold, args.dev_per_class)
    print(json.dumps({k: report[k] for k in ("load", "params", "clusters", "suite_label_counts")}, indent=1))
    print("label conflicts:", json.dumps(report["label_conflicts"], ensure_ascii=False, indent=1))
    if args.dry_run:
        return
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out.with_name(out.stem + "_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(rows)} rows) and {out.stem}_report.json")


if __name__ == "__main__":
    main()
