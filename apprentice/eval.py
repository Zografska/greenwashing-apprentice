"""Evaluation harness (SPEC §6, D15, D18, D28).

Predictions: JSONL, one row per text: {"text_id": ..., "pred": "IN_SCOPE"|"NEEDS_VERIFICATION"|"OUT"|null}
(optional "probs": {label: p}). A missing or invalid prediction counts as wrong.

  python3 -m apprentice.eval preds.jsonl --condition T --seed 0 --train-size 571 \
      --model Qwen/Qwen3-4B --model-revision <sha> --prompt prompts/P_ft.md --append
  python3 -m apprentice.eval --self-test      # gold labels as predictions -> every metric 1.0

Gold for dev is `dev_reviewed_label` when present (D24); for test suites it is `gold_label`.
Headline = macro-F1 on the pooled test_ce + test_carrefour suites (D18); every suite is also
reported on its own.

Dev is balanced by construction (50 per class) while the test suites are about 65% OUT, so dev rewards models
that over-flag. `dev_w` re-weights dev to the headline test class mix (each claim weighted by
p_test(class) / p_dev(class), using gold labels only); use it for every decision taken on dev (D35).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import binomtest
from sklearn.metrics import cohen_kappa_score, f1_score, precision_recall_fscore_support

from apprentice.check_split import DEFAULT_MANIFEST, check_split, load_manifest, sha256
from apprentice.data import LABELS, ROOT

SUITES = ("test_ce", "test_carrefour", "test_naturasi", "dev")
HEADLINE = ("test_ce", "test_carrefour")
RESULTS = ROOT / "results" / "results.csv"
INVALID = "__INVALID__"


def gold_map(manifest: list[dict]) -> dict[str, dict[str, str]]:
    """suite -> {text_id: gold}."""
    out: dict[str, dict[str, str]] = {s: {} for s in SUITES}
    for r in manifest:
        if r["suite"] in out:
            g = r.get("dev_reviewed_label") if r["suite"] == "dev" else None
            out[r["suite"]][r["text_id"]] = g or r["gold_label"]
    return out


def load_preds(path: Path | str) -> dict[str, str]:
    preds = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                preds[r["text_id"]] = r.get("pred")
    return preds


def _clean(p) -> str:
    return p if p in LABELS else INVALID


def _present(g, p) -> list[str]:
    """Classes present in gold or (valid) predictions: a class absent from both is not averaged."""
    return [l for l in LABELS if l in set(g) | set(p)]


def macro_f1(g, p, w=None) -> float:
    return float(f1_score(g, p, labels=_present(g, p), average="macro", zero_division=0, sample_weight=w))


def metrics(gold: list[str], pred: list[str], weights=None) -> dict:
    """Core metrics for aligned gold/pred lists (pred may contain invalid values). Optional per-item weights."""
    pred = [_clean(p) for p in pred]
    g, p = np.array(gold), np.array(pred)
    w = np.ones(len(g)) if weights is None else np.asarray(weights, dtype=float)
    prec, rec, f1, sup = precision_recall_fscore_support(g, p, labels=list(LABELS), zero_division=0,
                                                         sample_weight=w)
    flagged_g, flagged_p = g != "OUT", np.isin(p, ["IN_SCOPE", "NEEDS_VERIFICATION"])
    out = {"n": len(g), "macro_f1": macro_f1(g, p, w), "accuracy": float(np.average(g == p, weights=w)),
           "valid_rate": float(np.average(p != INVALID, weights=w)),
           "in_scope_recall": float(rec[0]),
           "flagged_recall": float(np.average(flagged_p[flagged_g], weights=w[flagged_g])) if flagged_g.any()
           else float("nan")}
    for lab, pr, rc, f, s in zip(LABELS, prec, rec, f1, sup):
        k = {"IN_SCOPE": "is", "NEEDS_VERIFICATION": "nv", "OUT": "out"}[lab]
        out |= {f"{k}_precision": float(pr), f"{k}_recall": float(rc), f"{k}_f1": float(f),
                f"{k}_n": int(np.sum(g == lab))}
    return out


def bootstrap_ci(gold: list[str], pred: list[str], stat=None, n_boot: int = 1000, seed: int = 0,
                 alpha: float = 0.05, weights=None) -> tuple[float, float]:
    """Percentile bootstrap CI over texts (default statistic: macro-F1, weighted if weights are given)."""
    g, p = np.array(gold), np.array([_clean(x) for x in pred])
    w = np.ones(len(g)) if weights is None else np.asarray(weights, dtype=float)
    stat = stat or macro_f1
    rng = np.random.default_rng(seed)
    if weights is None:
        vals = [stat(g[idx], p[idx]) for idx in (rng.integers(0, len(g), len(g)) for _ in range(n_boot))]
    else:
        vals = [macro_f1(g[idx], p[idx], w[idx]) for idx in (rng.integers(0, len(g), len(g)) for _ in range(n_boot))]
    return float(np.quantile(vals, alpha / 2)), float(np.quantile(vals, 1 - alpha / 2))


def test_prior_weights(golds: dict[str, dict[str, str]], dev_gold: list[str]) -> list[float]:
    """Per-item weights that give dev the class mix of the headline test suites (gold labels only)."""
    test = [l for s in HEADLINE for l in golds[s].values()]
    pt = {l: test.count(l) / len(test) for l in LABELS}
    pd = {l: dev_gold.count(l) / len(dev_gold) for l in LABELS}
    return [pt[l] / pd[l] if pd[l] else 0.0 for l in dev_gold]


def evaluate(preds: dict[str, str], manifest: list[dict] | None = None, n_boot: int = 1000) -> dict:
    manifest = manifest or load_manifest()
    golds = gold_map(manifest)
    res = {}
    for suite, gm in golds.items():
        ids = sorted(gm)
        if not ids or not any(i in preds for i in ids):
            continue
        g, p = [gm[i] for i in ids], [preds.get(i) for i in ids]
        res[suite] = metrics(g, p)
        res[suite]["macro_f1_ci"] = bootstrap_ci(g, p, n_boot=n_boot)
        if suite == "dev":
            w = test_prior_weights(golds, g)
            res["dev_w"] = metrics(g, p, w) | {"macro_f1_ci": bootstrap_ci(g, p, n_boot=n_boot, weights=w)}
    hl = [i for s in HEADLINE for i in sorted(golds[s])]
    if any(i in preds for i in hl):
        gm = golds["test_ce"] | golds["test_carrefour"]
        g, p = [gm[i] for i in hl], [preds.get(i) for i in hl]
        res["headline"] = metrics(g, p) | {"macro_f1_ci": bootstrap_ci(g, p, n_boot=n_boot)}
    return res


# ---- comparisons (D15, RQ4) ----------------------------------------------------------

def mcnemar(gold: list[str], pred_a: list[str], pred_b: list[str]) -> dict:
    """Exact McNemar test on correctness of two systems over the same texts."""
    a = np.array([_clean(x) for x in pred_a]) == np.array(gold)
    b = np.array([_clean(x) for x in pred_b]) == np.array(gold)
    n01, n10 = int(np.sum(a & ~b)), int(np.sum(~a & b))
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return {"a_only_correct": n01, "b_only_correct": n10, "p_value": float(p)}


def holm(pvalues: dict[str, float], alpha: float = 0.05) -> dict[str, dict]:
    """Holm-Bonferroni step-down adjustment."""
    order = sorted(pvalues, key=pvalues.get)
    m, running, out = len(order), 0.0, {}
    for k, name in enumerate(order):
        adj = min(1.0, max(running, (m - k) * pvalues[name]))
        running = adj
        out[name] = {"p": pvalues[name], "p_holm": adj, "reject": adj < alpha}
    return out


def majority_vote(pred_runs: list[dict[str, str]]) -> dict[str, str]:
    """Per-text majority over seeds; ties broken by LABELS order (IN_SCOPE first: safety)."""
    out = {}
    for tid in set().union(*pred_runs):
        votes = [_clean(r.get(tid)) for r in pred_runs]
        out[tid] = max(LABELS + (INVALID,), key=lambda l: (votes.count(l), -(LABELS + (INVALID,)).index(l)))
    return out


def kappa(a: list[str], b: list[str]) -> float:
    return float(cohen_kappa_score([_clean(x) for x in a], [_clean(x) for x in b]))


def error_overlap(gold: list[str], pred_s: list[str], pred_t: list[str]) -> dict:
    """RQ4: share of the student's errors that the teacher also gets wrong (same wrong label too)."""
    g = np.array(gold)
    s, t = np.array([_clean(x) for x in pred_s]), np.array([_clean(x) for x in pred_t])
    err = s != g
    return {"student_errors": int(err.sum()),
            "teacher_also_wrong": float(np.mean(t[err] != g[err])) if err.any() else float("nan"),
            "same_wrong_label": float(np.mean(t[err] == s[err])) if err.any() else float("nan")}


# ---- results.csv (D28) ---------------------------------------------------------------

def _hash_file(path) -> str | None:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16] if path else None


def results_row(res: dict, meta: dict) -> dict:
    row = dict(meta)
    for suite, m in res.items():
        for k, v in m.items():
            if k == "macro_f1_ci":
                row[f"{suite}.macro_f1_lo"], row[f"{suite}.macro_f1_hi"] = v
            else:
                row[f"{suite}.{k}"] = v
    return row


def append_results(row: dict, path: Path = RESULTS) -> None:
    path.parent.mkdir(exist_ok=True)
    rows, fields = [], list(row)
    if path.exists() and path.stat().st_size:
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            rows, fields = list(r), r.fieldnames + [k for k in row if k not in r.fieldnames]
    rows.append(row)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("preds", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    for k in ("condition", "model", "model-revision", "run-id", "libs", "lora", "provider", "notes"):
        ap.add_argument(f"--{k}")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--train-size", type=int)
    ap.add_argument("--prompt", help="prompt file (its hash is logged)")
    ap.add_argument("--append", action="store_true", help=f"append a row to {RESULTS.relative_to(ROOT)}")
    ap.add_argument("--n-boot", type=int, default=1000)
    a = ap.parse_args()

    check_split(a.manifest)
    manifest = load_manifest(a.manifest)
    if a.self_test:
        preds = {r["text_id"]: (r.get("dev_reviewed_label") if r["suite"] == "dev" else None) or r["gold_label"]
                 for r in manifest}
    else:
        preds = load_preds(a.preds)
    res = evaluate(preds, manifest, a.n_boot)
    for s, m in res.items():
        lo, hi = m["macro_f1_ci"]
        print(f"{s:15s} n={m['n']:4d}  macro-F1 {m['macro_f1']:.3f} [{lo:.3f}, {hi:.3f}]  "
              f"IS-rec {m['in_scope_recall']:.3f}  flag-rec {m['flagged_recall']:.3f}  valid {m['valid_rate']:.3f}")
    if a.self_test:
        bad = {s: m["macro_f1"] for s, m in res.items() if m["macro_f1"] < 1.0}
        if bad:
            raise SystemExit(f"SELF-TEST FAILED: {bad}")
        print("self-test OK: gold as predictions -> 1.0")
        return
    if a.append:
        meta = {"run_id": a.run_id or f"{a.condition}-s{a.seed}-n{a.train_size}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}",
                "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "condition": a.condition, "seed": a.seed, "train_size": a.train_size,
                "model": a.model, "model_revision": a.model_revision, "provider": a.provider,
                "prompt_file": a.prompt, "prompt_hash": _hash_file(a.prompt),
                "manifest": Path(a.manifest).name, "manifest_sha256": sha256(a.manifest)[:16],
                "preds_file": a.preds, "preds_hash": _hash_file(a.preds),
                "libs": a.libs or f"python {platform.python_version()}", "lora": a.lora, "notes": a.notes}
        append_results(results_row(res, meta))
        print(f"appended to {RESULTS}")


if __name__ == "__main__":
    main()
