"""Re-label a gold set (default: Carrefour 100) with another LLM on Groq, then analyse the discrepancies.

Every gold claim (same spans, same footnotes) is classified again, one call per claim, with
the per-claim classifier prompt read from golden/ECGT_CLAIM_CLASSIFIER_PROMPT.md (system prompt,
few-shots, user template). The model's label is recomputed from its triggers (POST rule) and
compared with the gold label.

  run       classify the claims; resumable (already-done claims are skipped), one JSONL line per claim
  analyze   agreement and discrepancy report for one or more run files vs. gold

Needs GROQ_API_KEY in the environment (never pass it on the command line).

Usage:
  python3 tools/groq_relabel.py run --list-models
  python3 tools/groq_relabel.py run --model <groq-model-id> [--with-conventions] [--limit 5] [--dry-run]
  python3 tools/groq_relabel.py run --model <id> --gold golden/labeled/golden_set_ecgt_coop_100.json
  python3 tools/groq_relabel.py analyze golden/labeled/relabel/<run>.jsonl [<run2>.jsonl ...]
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "golden/labeled/golden_set_ecgt_100.json"
PROMPT_DOC = ROOT / "golden/ECGT_CLAIM_CLASSIFIER_PROMPT.md"
OUT_DIR = ROOT / "golden/labeled/relabel"
API = "https://api.groq.com/openai/v1"

GROUP_A = {"generic_green", "undefined_natural", "climate_neutral",
           "vague_comparison", "brand_eco_slogan", "vague_supply_chain"}
GROUP_B = {"recycled_recyclable", "biodegradable", "certification", "named_endorsement", "vegan",
           "farming_practice", "defined_term", "risk_reduction", "named_comparison", "pollutant_free"}
TRIGGERS = GROUP_A | GROUP_B | {"out_of_scope"}
LABELS = ["IN_SCOPE", "NEEDS_VERIFICATION", "DISCARDED"]

# Conventions settled after the classifier prompt was written (checklist decisions log,
# gold README "Amendments"). Appended only with --with-conventions.
CONVENTIONS = """
ADDITIONAL RULES (they override the examples above when they conflict):
- «Senza microplastiche», «Senza siliconi», «Senza fosfati», «Privo di PFAS»: pollutant_free.
  «Senza parabeni», «Senza conservanti», «Senza glutine/lattosio/zuccheri aggiunti»: out_of_scope.
- Natural flavour or taste («Aroma naturale», «Gusto naturale») and packaging function
  («salvafreschezza», «richiudibile», «apertura facilitata»): out_of_scope.
- Geographic origin (country or region) and DOP/IGP/STG: out_of_scope.
- A recycling call-to-action on its own («Riciclami!», «Pensa a riciclare») is out_of_scope; one that
  adds an environmental-benefit clause («per il pianeta», «per il bene del nostro pianeta») is generic_green.
- A section heading is never a claim on its own; a brand eco-slogan («<Brand> per l'ambiente») is
  brand_eco_slogan.
"""


def label_from(triggers):
    t = set(triggers) - {"out_of_scope"}
    if not t:
        return "DISCARDED"
    if "defined_term" in t:
        t.discard("undefined_natural")
    return "IN_SCOPE" if t & GROUP_A else "NEEDS_VERIFICATION"


# ---- prompt ------------------------------------------------------------------------------

def _block_after(text, heading):
    """First ``` fenced block after a markdown heading."""
    i = text.index(heading)
    m = re.search(r"```[a-z]*\n(.*?)```", text[i:], re.S)
    return m.group(1).strip("\n")


def load_prompt(with_conventions):
    doc = PROMPT_DOC.read_text(encoding="utf-8")
    system = _block_after(doc, "## System prompt")
    if with_conventions:
        system = system.replace("Output ONLY JSON:", CONVENTIONS.strip() + "\n\nOutput ONLY JSON:", 1)
    shots = []
    for block in _block_after(doc, "## Few-shot").split("\n\n"):
        user, _, answer = block.partition("\n→ ")
        if answer:
            shots += [{"role": "user", "content": user.strip()},
                      {"role": "assistant", "content": answer.strip()}]
    template = _block_after(doc, "## User message template")
    return system, shots, template


def quoted_in_prompt(with_conventions):
    """Claim texts that appear verbatim as examples in the prompt (they leak the expected answer)."""
    system, shots, _ = load_prompt(with_conventions)
    quoted = set(re.findall(r"«([^»]+)»", system))
    quoted |= {m["content"].split("\n")[0].removeprefix("CLAIM: ") for m in shots if m["role"] == "user"}
    return quoted


def user_message(template, claim, product):
    return (template.replace("{{claim_text}}", claim["claim_text"])
            .replace("{{footnote_body_or_none}}", claim.get("footnote") or "none")
            .replace("{{name}}", product.get("name") or "")
            .replace("{{brand}}", product.get("brand") or ""))


def gold_claims(gold=GOLD):
    for p in json.load(open(gold, encoding="utf-8")):
        for i, c in enumerate(p["claims"]):
            yield p, i, c


# ---- Groq --------------------------------------------------------------------------------

class Groq:
    def __init__(self, model, temperature, max_retries=8):
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            sys.exit("GROQ_API_KEY is not set")
        self.model, self.temperature, self.max_retries = model, temperature, max_retries
        self.http = httpx.Client(base_url=API, timeout=60,
                                 headers={"Authorization": f"Bearer {key}"})

    def models(self):
        r = self.http.get("/models")
        r.raise_for_status()
        return sorted(m["id"] for m in r.json()["data"])

    def chat(self, messages):
        body = {"model": self.model, "messages": messages, "temperature": self.temperature,
                "response_format": {"type": "json_object"}, "max_tokens": 200}
        for attempt in range(self.max_retries):
            r = self.http.post("/chat/completions", json=body)
            if r.status_code == 429 or r.status_code >= 500:
                wait = float(r.headers.get("retry-after") or 2 ** attempt)
                time.sleep(min(wait, 60))
                continue
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        raise RuntimeError(f"gave up after {self.max_retries} retries (last status {r.status_code})")


def parse(raw):
    """Validate the model's JSON. Unknown triggers are dropped and reported, never guessed."""
    data = json.loads(raw)
    trig = data.get("triggers") or []
    if isinstance(trig, str):
        trig = [trig]
    valid = [t for t in dict.fromkeys(trig) if t in TRIGGERS]
    unknown = [t for t in trig if t not in TRIGGERS]
    if not valid:
        raise ValueError(f"no valid triggers in {trig!r}")
    conf = data.get("confidence")
    return dict(triggers=valid, unknown_triggers=unknown, label_model=data.get("label"),
                label=label_from(valid), confidence=float(conf) if conf is not None else None)


# ---- run ---------------------------------------------------------------------------------

def run(args):
    if args.list_models:
        print("\n".join(Groq("", 0).models()))
        return
    if not args.model:
        sys.exit("--model is required (see --list-models)")
    system, shots, template = load_prompt(args.with_conventions)
    prompt_sha = hashlib.sha256(json.dumps([system, shots, template]).encode()).hexdigest()[:12]
    tag = "conv" if args.with_conventions else "base"
    gold = Path(args.gold).resolve()
    set_name = gold.stem.removeprefix("golden_set_ecgt_").replace("_100", "100") or "gold"
    if set_name == "100":
        set_name = "carrefour100"
    out = Path(args.out) if args.out else OUT_DIR / f"{set_name}__{re.sub(r'[^\w.-]+', '-', args.model)}__{tag}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    done = set()
    if out.exists():
        for line in open(out, encoding="utf-8"):
            rec = json.loads(line)
            if not rec.get("error"):
                done.add(rec["claim_id"])
    todo = [(p, i, c) for p, i, c in gold_claims(gold) if f"{p['product_id']}#{i}" not in done]
    if args.limit:
        todo = todo[:args.limit]

    if args.dry_run:
        p, i, c = todo[0]
        msgs = [{"role": "system", "content": system}, *shots,
                {"role": "user", "content": user_message(template, c, p)}]
        print(json.dumps(msgs, ensure_ascii=False, indent=1))
        print(f"\n{len(todo)} claims to do, {len(done)} already done → {out}  (prompt {prompt_sha})")
        return

    client = Groq(args.model, args.temperature)

    def work(item):
        p, i, c = item
        msgs = [{"role": "system", "content": system}, *shots,
                {"role": "user", "content": user_message(template, c, p)}]
        rec = dict(claim_id=f"{p['product_id']}#{i}", product_id=p["product_id"], claim_index=i,
                   claim_text=c["claim_text"], footnote=c.get("footnote"),
                   gold_triggers=c["triggers"], gold_label=c["label"], gold_confidence=c.get("confidence"),
                   gold_note=c.get("note"), needs_review=c.get("needs_review", False),
                   golden_bucket=p["golden_bucket"], gray_zone=p.get("gray_zone"),
                   gold_file=str(gold.relative_to(ROOT)), model=args.model, prompt=tag, prompt_sha=prompt_sha, temperature=args.temperature,
                   ts=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        t0 = time.time()
        raw = None
        try:
            raw = client.chat(msgs)
            rec.update(parse(raw), raw=raw, error=None)
        except Exception as e:  # recorded and retried on the next run
            rec.update(raw=raw, error=f"{type(e).__name__}: {e}")
        rec["latency_s"] = round(time.time() - t0, 2)
        if args.rpm:
            time.sleep(60 / args.rpm * args.workers)
        return rec

    n_err = 0
    with open(out, "a", encoding="utf-8") as f, ThreadPoolExecutor(args.workers) as pool:
        futures = [pool.submit(work, it) for it in todo]
        for k, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            n_err += bool(rec["error"])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if k % 25 == 0 or k == len(todo):
                print(f"  {k}/{len(todo)} done, {n_err} errors", flush=True)
    print(f"→ {out}" + (f"  ({n_err} errors: rerun the same command to retry them)" if n_err else ""))


# ---- analyze -----------------------------------------------------------------------------

def load_run(path):
    """Latest successful record per claim (a rerun may append a retry after an error)."""
    recs = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if not r.get("error"):
            recs[r["claim_id"]] = r
    return recs


def kappa(pairs, cats):
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in cats) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def binary(label):
    return "ECGT" if label in ("IN_SCOPE", "NEEDS_VERIFICATION") else "DISCARDED"


def severity(gold, model):
    """3 = ECGT vs not, 2 = IN_SCOPE vs NV, 1 = same label but different triggers, 0 = identical."""
    if binary(gold["gold_label"]) != binary(model["label"]):
        return 3
    if gold["gold_label"] != model["label"]:
        return 2
    gt = set(gold["gold_triggers"]) - {"out_of_scope"}
    mt = set(model["triggers"]) - {"out_of_scope"}
    return 1 if gt != mt else 0


def pct(a, b):
    return f"{a}/{b} = {a / b:.1%}" if b else "n/a"


def report_one(name, recs, lines):
    rows = [r for r in recs.values() if not r["needs_review"]]
    n_all = sum(1 for _ in gold_claims(ROOT / rows[0].get("gold_file", GOLD.relative_to(ROOT))))
    lines += [f"## {name}", "",
              f"- model `{rows[0]['model']}`, prompt `{rows[0]['prompt']}` ({rows[0]['prompt_sha']}), "
              f"temperature {rows[0]['temperature']}",
              f"- coverage: {len(recs)}/{n_all} claims classified; {len(rows)} scored (needs_review skipped)", ""]

    # labels
    pairs = [(r["gold_label"], r["label"]) for r in rows]
    agree = sum(a == b for a, b in pairs)
    bpairs = [(binary(a), binary(b)) for a, b in pairs]
    lines += ["### Label agreement", "",
              f"- 3-class: {pct(agree, len(pairs))}, Cohen's κ = {kappa(pairs, LABELS):.3f}",
              f"- ECGT vs DISCARDED: {pct(sum(a == b for a, b in bpairs), len(bpairs))}, "
              f"κ = {kappa(bpairs, ['ECGT', 'DISCARDED']):.3f}"]
    both_pos = [(a, b) for a, b in pairs if binary(a) == binary(b) == "ECGT"]
    lines += [f"- IN_SCOPE vs NV, among claims both call ECGT: {pct(sum(a == b for a, b in both_pos), len(both_pos))}",
              "", "Confusion (rows = gold, columns = model):", "",
              "| gold \\ model | " + " | ".join(LABELS) + " | total |", "|---|" + "---|" * (len(LABELS) + 1)]
    conf = collections.Counter(pairs)
    for g in LABELS:
        lines.append(f"| {g} | " + " | ".join(str(conf[(g, m)]) for m in LABELS)
                     + f" | {sum(conf[(g, m)] for m in LABELS)} |")
    flips_down = sum(1 for a, b in bpairs if a == "ECGT" and b == "DISCARDED")
    flips_up = sum(1 for a, b in bpairs if a == "DISCARDED" and b == "ECGT")
    self_incons = sum(1 for r in rows if r.get("label_model") and r["label_model"] != r["label"])
    unknown = sum(1 for r in rows if r.get("unknown_triggers"))
    lines += ["", f"- gold ECGT → model DISCARDED: {flips_down}; gold DISCARDED → model ECGT: {flips_up}",
              f"- model's own label contradicts its triggers (POST recomputed): {self_incons}",
              f"- responses with unknown trigger names (dropped): {unknown}", ""]

    # triggers
    lines += ["### Trigger agreement (gold as reference)", "",
              "| trigger | gold | model | both | precision | recall | F1 |", "|---|---|---|---|---|---|---|"]
    exact = jac = 0.0
    for r in rows:
        g, m = set(r["gold_triggers"]), set(r["triggers"])
        exact += g == m
        jac += len(g & m) / len(g | m)
    for t in sorted(TRIGGERS, key=lambda t: -sum(t in r["gold_triggers"] for r in rows)):
        g = sum(t in r["gold_triggers"] for r in rows)
        m = sum(t in r["triggers"] for r in rows)
        b = sum(t in r["gold_triggers"] and t in r["triggers"] for r in rows)
        if not (g or m):
            continue
        p_, r_ = (b / m if m else 0), (b / g if g else 0)
        f1 = 2 * p_ * r_ / (p_ + r_) if p_ + r_ else 0
        lines.append(f"| {t} | {g} | {m} | {b} | {p_:.0%} | {r_:.0%} | {f1:.2f} |")
    lines += ["", f"- exact trigger-set match: {pct(int(exact), len(rows))}; mean Jaccard {jac / len(rows):.3f}", ""]

    # slices
    lines += ["### Agreement by slice (3-class label)", "", "| slice | agree | n |", "|---|---|---|"]

    def sl(name, pred):
        sub = [r for r in rows if pred(r)]
        if sub:
            a = sum(r["gold_label"] == r["label"] for r in sub)
            lines.append(f"| {name} | {a / len(sub):.0%} | {len(sub)} |")
    sl("gold confidence high", lambda r: r["gold_confidence"] == "high")
    sl("gold confidence low", lambda r: r["gold_confidence"] == "low")
    sl("gold note mentions a gray zone", lambda r: (r["gold_note"] or "").startswith("Gray zone"))
    sl("amended in review (2026-10-03)", lambda r: "Amended" in (r["gold_note"] or ""))
    sl("footnoted claim", lambda r: bool(r["footnote"]))
    quoted = quoted_in_prompt(rows[0]["prompt"] == "conv")
    sl("claim quoted verbatim in the prompt (leaks the answer)",
       lambda r: r["claim_text"] in quoted or r["claim_text"].rstrip(".") in quoted)
    for b in ["hard_yes", "in_between", "hard_no"]:
        sl(f"bucket {b}", lambda r, b=b: r["golden_bucket"] == b)
    for g in LABELS:
        sl(f"gold {g}", lambda r, g=g: r["gold_label"] == g)
    bins = [(0, .7), (.7, .85), (.85, .95), (.95, 1.01)]
    for lo, hi in bins:
        sl(f"model confidence [{lo:.2f}, {min(hi, 1):.2f}{']' if hi > 1 else ')'}",
           lambda r, lo=lo, hi=hi: r.get("confidence") is not None and lo <= r["confidence"] < hi)
    lines.append("")

    # gold-confidence vs severity
    sev = collections.Counter(severity(r, r) for r in rows)
    lines += ["### Discrepancy severity", "",
              f"- 3 ECGT ↔ DISCARDED: {sev[3]} · 2 IN_SCOPE ↔ NV: {sev[2]} · "
              f"1 same label, different triggers: {sev[1]} · 0 identical: {sev[0]}", ""]
    return rows


def analyze(args):
    runs = {Path(p).stem: load_run(p) for p in args.runs}
    lines = [f"# Gold-set re-label: discrepancy analysis", "",
             f"Gold: {', '.join(sorted({f'`{r.get("gold_file", GOLD.relative_to(ROOT))}`' for recs in runs.values() for r in recs.values()}))}. Generated {datetime.now().isoformat(timespec='minutes')}.",
             "Gold labels were themselves produced by an LLM (Claude, GOLDEN_SET_CURATION_PROMPT.md) with a "
             "partial human review, so agreement measures consistency between two labellers, not accuracy.", ""]
    for name, recs in runs.items():
        report_one(name, recs, lines)

    # cross-model view: claims where every run disagrees with gold on ECGT vs not
    names = list(runs)
    if len(names) > 1:
        common = set.intersection(*(set(r) for r in runs.values()))
        rows = [[runs[n][cid] for n in names] for cid in sorted(common)]
        rows = [rs for rs in rows if not rs[0]["needs_review"]]
        pair = lambda a, b: kappa([(x["label"], y["label"]) for x, y in zip(a, b)], LABELS)
        lines += ["## Across runs", ""]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = [rs[i] for rs in rows]
                b = [rs[j] for rs in rows]
                agree = sum(x["label"] == y["label"] for x, y in zip(a, b))
                lines.append(f"- `{names[i]}` vs `{names[j]}`: {pct(agree, len(rows))}, κ = {pair(a, b):.3f}")
        unanimous = [rs for rs in rows if all(binary(r["label"]) != binary(r["gold_label"]) for r in rs)]
        lines += ["", f"- claims where **every** run disagrees with gold on ECGT vs DISCARDED: {len(unanimous)} "
                  "(strongest candidates for a gold-label error; listed first in the CSV)", ""]

    out_md = Path(args.out or OUT_DIR / "discrepancy_report.md")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # CSV for manual review: every claim with a discrepancy in any run, most severe first
    out_csv = out_md.with_suffix(".csv")
    cids = sorted(set().union(*(set(r) for r in runs.values())))
    table = []
    for cid in cids:
        recs = [runs[n].get(cid) for n in names]
        base = next(r for r in recs if r)
        sevs = [severity(r, r) if r else None for r in recs]
        if not any(sevs):
            continue
        n_disagree_bin = sum(1 for r in recs if r and binary(r["label"]) != binary(r["gold_label"]))
        row = dict(max_severity=max(s for s in sevs if s is not None), runs_disagree_ecgt=n_disagree_bin,
                   claim_id=cid, claim_text=base["claim_text"], footnote=base["footnote"] or "",
                   gold_label=base["gold_label"], gold_triggers=" ".join(base["gold_triggers"]),
                   gold_confidence=base["gold_confidence"], gold_note=base["gold_note"] or "",
                   needs_review=base["needs_review"], golden_bucket=base["golden_bucket"])
        for n, r in zip(names, recs):
            row[f"{n}:label"] = r["label"] if r else ""
            row[f"{n}:triggers"] = " ".join(r["triggers"]) if r else ""
            row[f"{n}:confidence"] = r.get("confidence") if r else ""
        row["review_verdict"] = ""          # fill in by hand: gold_ok | model_ok | both_defensible | rule_gap
        table.append(row)
    table.sort(key=lambda r: (-r["max_severity"], -r["runs_disagree_ecgt"], r["claim_id"]))
    if table:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)
    print(out_md.read_text(encoding="utf-8"))
    print(f"→ {out_md}\n→ {out_csv} ({len(table)} claims with a discrepancy, most severe first)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--model", help="Groq model id")
    r.add_argument("--list-models", action="store_true")
    r.add_argument("--gold", default=str(GOLD), help="gold set JSON (default: Carrefour 100)")
    r.add_argument("--with-conventions", action="store_true",
                   help="append the conventions settled after the classifier prompt was written")
    r.add_argument("--temperature", type=float, default=0.0)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--rpm", type=float, help="throttle to about this many requests per minute")
    r.add_argument("--limit", type=int, help="only the first N remaining claims (smoke test)")
    r.add_argument("--dry-run", action="store_true", help="print the first request, call nothing")
    r.add_argument("--out", help="output JSONL (default: golden/labeled/relabel/<set>__<model>__<prompt>.jsonl)")
    a = sub.add_parser("analyze")
    a.add_argument("runs", nargs="+")
    a.add_argument("--out", help="report path (default: golden/labeled/relabel/discrepancy_report.md)")
    args = ap.parse_args()
    (run if args.cmd == "run" else analyze)(args)


if __name__ == "__main__":
    main()
