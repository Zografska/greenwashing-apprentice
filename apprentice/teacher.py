"""Teacher runner (SPEC D9, D21, D28, D30). Any OpenAI-compatible chat API: OpenRouter (default,
with one pinned provider and no fallbacks), Groq, Kaggle proxy or a local llama.cpp server.
Standard library only for HTTP, so it runs from a plain Mac terminal.

  python3 -m apprentice.teacher providers --model openai/gpt-oss-120b      # OpenRouter endpoints
  python3 -m apprentice.teacher check-cache --model openai/gpt-oss-120b --pin <provider>
  python3 -m apprentice.teacher run   --model openai/gpt-oss-20b --pin <provider> --suite dev
  python3 -m apprentice.teacher score --model openai/gpt-oss-20b --pin <provider> --suite dev

Outputs (append-only JSONL, one row per text, resumable; one folder per service+provider):
  data/teacher/<service_tag>/<model_slug>/<prompt_hash>/<suite>.jsonl        train, t_large_extra, dev
  data/teacher/test/<service_tag>/<model_slug>/<prompt_hash>/<suite>.jsonl   test suites (never trainable)
Keys from the environment or the repo's .env: OPEN_ROUTER_API_KEY (openrouter), GROQ_API_KEY (groq).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from apprentice import prompts
from apprentice.check_split import check_split, load_manifest
from apprentice.data import LABELS, ROOT

SERVICES = {"openrouter": ("https://openrouter.ai/api/v1", "OPEN_ROUTER_API_KEY"),
            "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY")}
IN_SCOPE_T = {"generic_green", "undefined_natural", "climate_neutral",
              "vague_comparison", "brand_eco_slogan", "vague_supply_chain"}
TRIGGERS = IN_SCOPE_T | {"recycled_recyclable", "biodegradable", "certification", "named_endorsement", "vegan",
                         "farming_practice", "defined_term", "risk_reduction", "named_comparison",
                         "pollutant_free", "out_of_scope"}
TEST_SUITES = {"test_ce", "test_carrefour", "test_naturasi"}
SUITE_GROUPS = {"test": sorted(TEST_SUITES)}


def post_label(triggers) -> str | None:
    """SPEC §5 POST rule. None if no valid trigger."""
    t = set(triggers or []) & TRIGGERS
    if not t:
        return None
    t -= {"out_of_scope"}
    if not t:
        return "OUT"
    if "defined_term" in t:
        t.discard("undefined_natural")
    return "IN_SCOPE" if t & IN_SCOPE_T else "NEEDS_VERIFICATION"


# ---- config ---------------------------------------------------------------------------

def load_env(path: Path = ROOT / ".env") -> None:
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", line)
            if m and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


def slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", model)


def teacher_prompt_hash() -> str:
    return prompts.prompt_hash(json.dumps(prompts.teacher_messages("{{CLAIM}}"), ensure_ascii=False))


def service_tag(args) -> str:
    return args.service + (f"-{slug(args.pin)}" if args.pin else "")


def out_path(model: str, suite: str, phash: str, tag: str = "openrouter") -> Path:
    base = ROOT / "data" / "teacher" / ("test" if suite in TEST_SUITES else "")
    return base / tag / slug(model) / phash / f"{suite}.jsonl"


# ---- HTTP -----------------------------------------------------------------------------

class DailyLimit(Exception):
    pass


def chat(base_url: str, key: str, body: dict, timeout: int = 120, max_retries: int = 8) -> tuple[dict, dict]:
    """POST /chat/completions with backoff on 429/5xx. Returns (json, rate-limit headers)."""
    req = urllib.request.Request(f"{base_url}/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "User-Agent": "greenwashing-apprentice/1.0"})
    net_errors = 0
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                hdr = {k.lower(): v for k, v in r.headers.items() if k.lower().startswith(("x-ratelimit", "retry"))}
                return json.loads(r.read()), hdr
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code == 429:
                if re.search(r"per day|TPD|RPD", msg, re.I):
                    raise DailyLimit(msg[:300])
                wait = float(e.headers.get("retry-after") or 0) or min(60, 2 ** attempt * 2)
                print(f"  429, waiting {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
            elif e.code >= 500:
                time.sleep(min(60, 2 ** attempt * 2))
            else:
                raise RuntimeError(f"HTTP {e.code}: {msg[:500]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            net_errors += 1
            if net_errors >= 3:
                raise RuntimeError(f"cannot reach {base_url} ({e}). Check your connection / that the site "
                                   "isn't blocked; run this from your own Mac terminal.") from None
            print(f"  network error {e}, retrying", file=sys.stderr)
            time.sleep(5 * net_errors)
    raise RuntimeError("too many retries")


def request_body(model: str, claim: str, args) -> dict:
    body = {"model": model, "messages": prompts.teacher_messages(claim), "temperature": 0,
            "response_format": {"type": "json_object"}, "max_tokens": args.max_tokens}
    if args.service == "openrouter":
        body["reasoning"] = {"effort": args.reasoning_effort}
        body["usage"] = {"include": True}                       # returns cost per call
        if args.pin:
            body["provider"] = {"order": [args.pin], "allow_fallbacks": False, "require_parameters": True}
    elif "gpt-oss" in model:
        body["reasoning_effort"] = args.reasoning_effort
    return body


def parse(content: str) -> dict:
    try:
        obj = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        m = re.search(r"\{.*\}", content or "", re.S)
        try:
            obj = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            obj = {}
    triggers = [t for t in obj.get("triggers", []) if isinstance(t, str)] if isinstance(obj, dict) else []
    stated = obj.get("label") if isinstance(obj, dict) else None
    stated = "OUT" if stated == "DISCARDED" else stated
    post = post_label(triggers)
    return {"reasoning": obj.get("reasoning") if isinstance(obj, dict) else None, "triggers": triggers,
            "unknown_triggers": sorted(set(triggers) - TRIGGERS), "stated_label": stated,
            "post_label": post, "valid": post is not None,
            "consistent": post is not None and stated == post}


# ---- commands -------------------------------------------------------------------------

def cmd_check_cache(args, key):
    claim = "Confezione 100% riciclabile"
    rows = []
    for i in range(2):
        t0 = time.time()
        resp, hdr = chat(args.base_url, key, request_body(args.model, claim, args))
        u = resp.get("usage", {})
        cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
        rows.append((u.get("prompt_tokens"), cached, u.get("completion_tokens")))
        print(f"call {i + 1}: prompt_tokens={u.get('prompt_tokens')} cached_tokens={cached} "
              f"completion_tokens={u.get('completion_tokens')} cost={u.get('cost')} "
              f"served_by={resp.get('provider')} latency={time.time() - t0:.1f}s")
        time.sleep(2)
    print("rate-limit headers:", json.dumps(hdr, indent=1))
    print("answer:", resp["choices"][0]["message"].get("content"))
    pt, cached, _ = rows[1]
    if cached and pt and cached / pt > 0.5:
        print(f"\nCACHING WORKS: {cached}/{pt} prompt tokens cached on the repeat call.")
    else:
        print("\nNo cache hit reported on the repeat call. Fine on a paid provider (cost is what matters); "
              "on a free tier it means every call counts in full against the token limits.")


def cmd_providers(args, key):
    """List OpenRouter endpoints for a model; saves the raw list for the record."""
    req = urllib.request.Request(f"{args.base_url}/models/{args.model}/endpoints",
                                 headers={"Authorization": f"Bearer {key}", "User-Agent": "greenwashing-apprentice/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    out = ROOT / "data" / "teacher" / f"openrouter_endpoints_{slug(args.model)}.json"
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    eps = data.get("data", {}).get("endpoints", [])
    print(f"{args.model}: {len(eps)} endpoints (saved to {out.relative_to(ROOT)})")
    print(f"{'pin with':28s} {'quant':8s} {'$in/M':>7s} {'$out/M':>7s} {'json':>5s} {'reason':>6s} {'up30m':>6s}")
    for e in sorted(eps, key=lambda e: float(e.get("pricing", {}).get("prompt") or 9)):
        sp = set(e.get("supported_parameters") or [])
        price = e.get("pricing", {})
        pin = e.get("tag") or e.get("provider_name")
        up = e.get("uptime_last_30m")
        print(f"{str(pin):28s} {str(e.get('quantization')):8s} {float(price.get('prompt') or 0) * 1e6:7.3f} "
              f"{float(price.get('completion') or 0) * 1e6:7.3f} {'yes' if 'response_format' in sp else 'no':>5s} "
              f"{'yes' if 'reasoning' in sp else 'no':>6s} {('%.0f%%' % up) if isinstance(up, (int, float)) else '-':>6s}")


def suites_of(name: str) -> list[str]:
    return SUITE_GROUPS.get(name, [name])


def cmd_run(args, key):
    if args.service == "openrouter" and not args.pin:
        sys.exit("--pin <provider> is required on OpenRouter (D9: one provider per run). "
                 "List them with: python3 -m apprentice.teacher providers --model " + args.model)
    check_split()
    manifest = load_manifest()
    phash = teacher_prompt_hash()
    for suite in suites_of(args.suite):
        todo_rows = [r for r in manifest if r["suite"] == suite]
        path = out_path(args.model, suite, phash, service_tag(args))
        path.parent.mkdir(parents=True, exist_ok=True)
        done = set()
        if path.exists():
            done = {json.loads(l)["text_id"] for l in path.open(encoding="utf-8") if l.strip()}
        todo = [r for r in todo_rows if r["text_id"] not in done][: args.limit or None]
        print(f"{suite}: {len(done)} done, {len(todo)} to go -> {path.relative_to(ROOT)}")
        spent = 0.0
        with path.open("a", encoding="utf-8") as f:
            for k, r in enumerate(todo, 1):
                t0 = time.time()
                try:
                    resp, hdr = chat(args.base_url, key, request_body(args.model, r["text"], args))
                except DailyLimit as e:
                    print(f"\nDaily limit reached after {k - 1} calls; rerun the same command tomorrow to resume.\n{e}")
                    return
                msg = resp["choices"][0]["message"]
                u = resp.get("usage", {})
                row = {"text_id": r["text_id"], "suite": suite, "text": r["text"],
                       **parse(msg.get("content") or ""), "raw": msg.get("content"),
                       "model": args.model, "served_model": resp.get("model"), "service": args.service,
                       "base_url": args.base_url, "pinned": args.pin, "served_by": resp.get("provider"),
                       "prompt_hash": phash, "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       "usage": {"prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens"),
                                 "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                                 "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                 "cost_usd": u.get("cost")},
                       "latency_s": round(time.time() - t0, 2),
                       "settings": {"temperature": 0, "reasoning_effort": args.reasoning_effort,
                                    "max_tokens": args.max_tokens}}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                spent += u.get("cost") or 0
                if k % 10 == 0 or k == len(todo):
                    print(f"  {k}/{len(todo)}  cost so far ${spent:.4f}  served by {resp.get('provider')}")
                time.sleep(args.sleep)


def load_outputs(model: str, suite: str, phash: str | None = None, tag: str = "openrouter") -> list[dict]:
    path = out_path(model, suite, phash or teacher_prompt_hash(), tag)
    if not path.exists():
        sys.exit(f"no outputs at {path.relative_to(ROOT)}")
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def cmd_score(args, _key=None):
    from apprentice.eval import metrics
    manifest = {r["text_id"]: r for r in load_manifest()}
    for suite in suites_of(args.suite):
        rows = load_outputs(args.model, suite, args.prompt_hash, service_tag(args))
        gold = [(manifest[r["text_id"]].get("dev_reviewed_label") if suite == "dev" else None)
                or manifest[r["text_id"]]["gold_label"] for r in rows]
        pred = [r["post_label"] for r in rows]
        m = metrics(gold, pred)
        cons = sum(r["consistent"] for r in rows) / len(rows)
        print(f"{args.model} on {suite} (n={len(rows)}, prompt {rows[0]['prompt_hash']}):")
        print(f"  macro-F1 {m['macro_f1']:.3f}  accuracy {m['accuracy']:.3f}  valid {m['valid_rate']:.3f}  "
              f"consistency (stated == POST) {cons:.3f}")
        print(f"  F1  IN_SCOPE {m['is_f1']:.3f}  NV {m['nv_f1']:.3f}  OUT {m['out_f1']:.3f}   "
              f"IN_SCOPE recall {m['in_scope_recall']:.3f}")
        conf = Counter(zip(gold, [p or "INVALID" for p in pred]))
        print("  confusion (gold -> pred):", {f"{g}->{p}": n for (g, p), n in sorted(conf.items()) if g != p})
        unk = Counter(t for r in rows for t in r["unknown_triggers"])
        if unk:
            print("  unknown triggers:", dict(unk))
        tok = [r["usage"] for r in rows]
        cost = sum((r["usage"].get("cost_usd") or 0) for r in rows)
        print(f"  served by: {dict(Counter(r.get('served_by') for r in rows))}   total cost ${cost:.4f}")
        print(f"  tokens/call: prompt {sum(t['prompt_tokens'] or 0 for t in tok) / len(tok):.0f} "
              f"(cached {sum(t['cached_tokens'] or 0 for t in tok) / len(tok):.0f}), "
              f"completion {sum(t['completion_tokens'] or 0 for t in tok) / len(tok):.0f}")
        if args.show_errors:
            for r, g in zip(rows, gold):
                if r["post_label"] != g:
                    print(f"   [{g} -> {r['post_label']}] {r['text'][:90]}\n      {r['triggers']} | {r['reasoning']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["providers", "check-cache", "run", "score"])
    ap.add_argument("--model", default="openai/gpt-oss-20b")
    ap.add_argument("--suite", default="dev", help="dev | train | t_large_extra | test | test_ce | ...")
    ap.add_argument("--service", choices=sorted(SERVICES), default="openrouter")
    ap.add_argument("--pin", help="OpenRouter provider to pin (no fallbacks), e.g. a name from `providers`")
    ap.add_argument("--base-url", help="override the service URL (e.g. Kaggle proxy, llama.cpp server)")
    ap.add_argument("--key-env", help="override the API key variable")
    ap.add_argument("--reasoning-effort", default="low")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--sleep", type=float, default=0.2, help="pause between calls (s)")
    ap.add_argument("--limit", type=int, default=0, help="max new calls this run (0 = all)")
    ap.add_argument("--prompt-hash", help="score outputs of an earlier prompt version")
    ap.add_argument("--show-errors", action="store_true")
    args = ap.parse_args()
    url, key_env = SERVICES[args.service]
    args.base_url, args.key_env = args.base_url or url, args.key_env or key_env
    if args.command == "score":
        return cmd_score(args)
    load_env()
    key = os.environ.get(args.key_env)
    if not key:
        sys.exit(f"{args.key_env} not set (put it in .env)")
    {"providers": cmd_providers, "check-cache": cmd_check_cache, "run": cmd_run}[args.command](args, key)


if __name__ == "__main__":
    main()
