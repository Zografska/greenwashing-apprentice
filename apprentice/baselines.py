"""Baselines (SPEC §5): prompted students S0-noLegal / S0 / S1 and the classic baseline B0.

  python3 -m apprentice.baselines prompted --condition S0 --suite dev
  python3 -m apprentice.baselines prompted --condition S1 --suite test --final --append
  python3 -m apprentice.baselines b0 --labels teacher --suite dev

Predictions go to results/preds/<condition>/<suite>.jsonl (suite "test" = the three test suites together).
Test predictions need --final and are written once (a second run refuses unless --overwrite-final, which is
logged). --append adds a row to results/results.csv via apprentice.eval. Runs on Kaggle (GPU, Internet on)
or the Mac; needs transformers + torch (prompted) or sentence-transformers (S1, B0).
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from apprentice import prompts
from apprentice.check_split import assert_trainable_path, check_split, load_manifest, sha256
from apprentice.data import LABELS, ROOT
from apprentice.eval import append_results, evaluate, results_row

PREDS = ROOT / "results" / "preds"
TEACHER_TRAIN = (ROOT / "data" / "teacher" / "openrouter-coreweave_fp4" / "openai_gpt-oss-120b" /
                 "2ef529403276b34b" / "train.jsonl")
TEST_SUITES = ("test_ce", "test_carrefour", "test_naturasi")
DEFAULT_MODEL = "Qwen/Qwen3-4B"


def suite_rows(manifest, suite):
    wanted = TEST_SUITES if suite == "test" else (suite,)
    return [r for r in manifest if r["suite"] in wanted]


def out_file(condition: str, suite: str, final: bool, overwrite: bool) -> Path:
    if suite == "test" and not final:
        sys.exit("Test predictions are made once per final model: add --final (SPEC §7).")
    p = PREDS / condition / f"{suite}.jsonl"
    if suite == "test" and p.exists() and not overwrite:
        sys.exit(f"{p.relative_to(ROOT)} already exists: test is scored once. Use --overwrite-final only for a "
                 "broken run, and note why in results.csv.")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_and_eval(path, rows, condition, meta, manifest, append):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    res = evaluate({r["text_id"]: r["pred"] for r in rows}, manifest)
    for s, m in res.items():
        lo, hi = m["macro_f1_ci"]
        print(f"{condition:11s} {s:15s} n={m['n']:4d} macro-F1 {m['macro_f1']:.3f} [{lo:.3f},{hi:.3f}] "
              f"IS-rec {m['in_scope_recall']:.3f} acc {m['accuracy']:.3f}")
    if append:
        meta = {"run_id": f"{condition}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}",
                "date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "condition": condition,
                "manifest": "split_v1.jsonl", "manifest_sha256": sha256(ROOT / "splits" / "split_v1.jsonl")[:16],
                "preds_file": str(path.relative_to(ROOT)), **meta}
        append_results(results_row(res, meta))
        print("appended to results/results.csv")


def libs() -> str:
    out = [f"python {platform.python_version()}"]
    for mod in ("torch", "transformers", "sentence_transformers", "sklearn"):
        try:
            out.append(f"{mod} {__import__(mod).__version__}")
        except Exception:
            pass
    return "; ".join(out)


def cmd_prompted(a):
    path = out_file(a.condition, a.suite, a.final, a.overwrite_final)
    from apprentice.score_lp import LabelScorer
    check_split()
    manifest = load_manifest()
    rows_in = suite_rows(manifest, a.suite)
    legal = a.condition != "S0-noLegal"
    examples = [None] * len(rows_in)
    retr = None
    if a.condition == "S1":
        from apprentice.retrieve import AnchorRetriever
        retr = AnchorRetriever()
        examples = retr.top_k([r["text"] for r in rows_in], k=3)
    msgs = [prompts.student_messages(r["text"], legal=legal, examples=ex) for r, ex in zip(rows_in, examples)]
    scorer = LabelScorer(a.model, revision=a.revision)
    t0 = time.time()
    scored = scorer.score(msgs, progress=True)
    dt = time.time() - t0
    rows = [{"text_id": r["text_id"], "suite": r["suite"], "pred": s["pred"], "probs": s["probs"],
             **({"anchors": [e["id"] for e in ex]} if ex else {})} for r, s, ex in zip(rows_in, scored, examples)]
    print(f"{len(rows)} claims in {dt:.0f}s ({1000 * dt / len(rows):.0f} ms/claim); prefix cache hits "
          f"{scorer.prefix_hits}, misses {scorer.prefix_misses}" +
          (f"; anchors excluded {retr.n_excluded}, guard skips {retr.guard_skips}" if retr else ""))
    phash = prompts.prompt_hash(json.dumps(prompts.student_messages("{{CLAIM}}", legal=legal), ensure_ascii=False),
                                a.condition)
    write_and_eval(path, rows, a.condition,
                   {"model": a.model, "model_revision": scorer.model_revision, "prompt_hash": phash,
                    "libs": libs(), "notes": f"ms/claim {1000 * dt / len(rows):.0f} on {scorer.device}"},
                   manifest, a.append)


def cmd_b0(a):
    path = out_file(f"B0-{'T' if a.labels == 'teacher' else 'H'}", a.suite, a.final, a.overwrite_final)
    from sklearn.linear_model import LogisticRegression
    from apprentice.retrieve import E5
    manifest = load_manifest()
    train = [r for r in manifest if r["suite"] == "train"]
    if a.labels == "teacher":
        assert_trainable_path(TEACHER_TRAIN)
        check_split(training_files=[TEACHER_TRAIN])
        tl = {json.loads(l)["text_id"]: json.loads(l)["post_label"] for l in open(TEACHER_TRAIN, encoding="utf-8")}
        pairs = [(r["text"], tl.get(r["text_id"])) for r in train]
    else:
        check_split()
        pairs = [(r["text"], r["gold_label"]) for r in train]
    pairs = [(t, y) for t, y in pairs if y in LABELS]
    condition = f"B0-{'T' if a.labels == 'teacher' else 'H'}"
    rows_in = suite_rows(manifest, a.suite)
    enc = E5()
    clf = LogisticRegression(class_weight="balanced", max_iter=5000, C=1.0)
    clf.fit(enc.encode([t for t, _ in pairs]), [y for _, y in pairs])
    P = clf.predict_proba(enc.encode([r["text"] for r in rows_in]))
    rows = [{"text_id": r["text_id"], "suite": r["suite"], "pred": str(clf.classes_[p.argmax()]),
             "probs": {str(c): float(v) for c, v in zip(clf.classes_, p)}} for r, p in zip(rows_in, P)]
    write_and_eval(path, rows, condition,
                   {"model": "intfloat/multilingual-e5-base + LogisticRegression(balanced, C=1)",
                    "train_size": len(pairs), "libs": libs()}, manifest, a.append)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompted")
    p.add_argument("--condition", choices=["S0-noLegal", "S0", "S1"], required=True)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--revision")
    b = sub.add_parser("b0")
    b.add_argument("--labels", choices=["teacher", "gold"], required=True)
    for x in (p, b):
        x.add_argument("--suite", choices=["dev", "test"], default="dev")
        x.add_argument("--final", action="store_true", help="required for test")
        x.add_argument("--overwrite-final", action="store_true")
        x.add_argument("--append", action="store_true", help="add a row to results/results.csv")
    a = ap.parse_args()
    {"prompted": cmd_prompted, "b0": cmd_b0}[a.cmd](a)


if __name__ == "__main__":
    main()
