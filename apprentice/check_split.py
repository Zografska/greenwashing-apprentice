"""Reusable split guard (SPEC §4.3 rule 2). Call it before every training and evaluation job.

    from apprentice.check_split import check_split
    check_split(training_files=["data/teacher/train_labels.jsonl"])

Raises SplitError on any violation; returns a report dict otherwise. Checks:
  1. manifest integrity: unique text_id, norm == normalise(text), frozen hash (splits/FROZEN)
  2. every near-dup cluster sits on one side (train / train_extra / dev / test; 'excluded' may co-occur)
  3. no lexical near-dup (>= threshold) between test and any non-test text in the manifest
  4. training files: not under data/teacher/test/, and no text equal or near-dup to a test or dev text
  5. anchors: every anchor equal or near-dup to a test text must be in the exclusion list
  6. curve subsets are subsets of train
Text matching uses the same normalisation as the split (apprentice.data.normalise).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from apprentice import neardup
from apprentice.data import ROOT, normalise

DEFAULT_MANIFEST = ROOT / "splits" / "split_v1.jsonl"
TEACHER_TEST_DIR = (ROOT / "data" / "teacher" / "test").resolve()
EXCLUSIONS_FILE = ROOT / "splits" / "anchor_exclusions_v1.json"


class SplitError(AssertionError):
    pass


def load_manifest(path: Path | str = DEFAULT_MANIFEST) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_trainable_path(path: Path | str) -> None:
    """Teacher outputs on test may never be read by a training loader (SPEC §4.3 rule 3)."""
    p = Path(path).resolve()
    if p == TEACHER_TEST_DIR or TEACHER_TEST_DIR in p.parents:
        raise SplitError(f"{path} is under data/teacher/test/: test-set outputs cannot be used for training")


def _read_texts(path: Path | str) -> list[str]:
    """Normalised texts from a JSONL training file (fields tried: norm, text, claim_text)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            t = r.get("norm") or normalise(r.get("text") or r.get("claim_text") or "")
            if t:
                out.append(t)
    return out


def anchor_test_overlaps(manifest: list[dict], anchors_path: Path | str,
                         threshold: float = neardup.DEFAULT_THRESHOLD) -> list[str]:
    """Anchor ids whose text equals or near-duplicates a test text (to exclude at retrieval)."""
    anchors = [json.loads(l) for l in open(anchors_path, encoding="utf-8") if l.strip()]
    a_norm = [normalise(a["text"]) for a in anchors]
    test = [r["norm"] for r in manifest if r["side"] == "test"]
    test_set = set(test)
    hit = {i for i, t in enumerate(a_norm) if t in test_set}
    corpus = [r["norm"] for r in manifest] + a_norm
    hit |= {i for i, _, _ in neardup.near_dups(a_norm, test, threshold, fit_corpus=corpus)}
    return sorted(anchors[i]["id"] for i in hit)


def check_split(manifest_path: Path | str = DEFAULT_MANIFEST, training_files=(), anchors_path=None,
                anchor_exclusions=None, curve_subsets: dict | None = None,
                threshold: float | None = None) -> dict:
    manifest = load_manifest(manifest_path)
    threshold = threshold or manifest[0].get("near_dup_threshold", neardup.DEFAULT_THRESHOLD)
    errors, report = [], {"manifest": str(manifest_path), "rows": len(manifest)}

    # 1. integrity
    ids = [r["text_id"] for r in manifest]
    if len(ids) != len(set(ids)):
        errors.append("duplicate text_id in manifest")
    bad_norm = [r["text_id"] for r in manifest if normalise(r["text"]) != r["norm"]]
    if bad_norm:
        errors.append(f"{len(bad_norm)} rows where norm != normalise(text), e.g. {bad_norm[:3]}")
    frozen = Path(manifest_path).parent / "FROZEN"
    if frozen.exists():
        for line in frozen.read_text().splitlines():
            name, _, digest = line.partition(" ")
            if name == Path(manifest_path).name and digest and digest != sha256(manifest_path):
                errors.append(f"{name} differs from its frozen hash in splits/FROZEN")
        report["frozen"] = True

    # 2. clusters on one side
    sides = defaultdict(set)
    for r in manifest:
        if r["side"] != "excluded":
            sides[r["near_dup_cluster"]].add(r["side"])
    straddle = [c for c, s in sides.items() if len(s) > 1]
    if straddle:
        errors.append(f"{len(straddle)} near-dup clusters on more than one side, e.g. {straddle[:5]}")

    # 3. no near-dup between test and other included texts
    corpus = [r["norm"] for r in manifest]
    test = [r["norm"] for r in manifest if r["side"] == "test"]
    other = [r["norm"] for r in manifest if r["side"] in ("train", "train_extra", "dev")]
    pairs = neardup.near_dups(test, other, threshold, fit_corpus=corpus)
    if pairs:
        i, j, s = pairs[0]
        errors.append(f"{len(pairs)} test/non-test near-dup pairs, e.g. {test[i]!r} ~ {other[j]!r} ({s:.2f})")

    # 4. training files
    guarded = [r["norm"] for r in manifest if r["side"] in ("test", "dev")]
    guarded_set = set(guarded)
    for tf in training_files:
        try:
            assert_trainable_path(tf)
        except SplitError as e:
            errors.append(str(e))
            continue
        texts = _read_texts(tf)
        exact = [t for t in texts if t in guarded_set]
        near = neardup.near_dups(texts, guarded, threshold, fit_corpus=corpus + texts)
        if exact or near:
            errors.append(f"{tf}: {len(exact)} exact and {len(near)} near-dup matches with test/dev texts")
        report.setdefault("training_files", {})[str(tf)] = len(texts)

    # 5. anchors
    if anchors_path:
        need = anchor_test_overlaps(manifest, anchors_path, threshold)
        report["anchor_exclusions_required"] = need
        if anchor_exclusions is not None and set(need) - set(anchor_exclusions):
            errors.append(f"anchors overlapping test not excluded: {sorted(set(need) - set(anchor_exclusions))}")

    # 6. curve subsets
    if curve_subsets:
        train_ids = {r["text_id"] for r in manifest if r["side"] == "train"}
        for name, sub in curve_subsets.items():
            extra = set(sub) - train_ids
            if extra:
                errors.append(f"curve subset {name}: {len(extra)} ids not in train")

    if errors:
        raise SplitError("check_split failed:\n  - " + "\n  - ".join(errors))
    report["ok"] = True
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    ap.add_argument("--train-file", action="append", default=[])
    ap.add_argument("--anchors", default=str(ROOT / "vendor" / "retriever" / "anchors_v4.jsonl"))
    ap.add_argument("--write-exclusions", action="store_true",
                    help=f"write the required anchor exclusions to {EXCLUSIONS_FILE.name}")
    args = ap.parse_args()
    excl = json.loads(EXCLUSIONS_FILE.read_text()) if EXCLUSIONS_FILE.exists() else None
    rep = check_split(args.manifest, args.train_file, args.anchors, excl)
    if args.write_exclusions:
        EXCLUSIONS_FILE.write_text(json.dumps(rep["anchor_exclusions_required"], indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
