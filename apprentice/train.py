"""Fine-tune a student with LoRA and score it (SPEC §5, D7, D16, D23, D28, D35).

  python3 -m apprentice.train --condition T --n 551 --seed 0              # dev only (smoke test)
  python3 -m apprentice.train --condition H --n 150 --seed 2 --score-test # grid run: dev + test, once

Conditions (all use P_ft: one instruction line + the claim; no legal text, no examples, no categories):
  H        expert-reviewed gold labels, train texts (n in 150/300/551)
  T        teacher labels (gpt-oss-120b, frozen prompt), same texts as H for a given seed and n
  T+R      teacher reasoning then label, as JSON {"reasoning": ..., "label": ...}; scored by generation
  T-large  teacher labels on train + t_large_extra (≈1,125 texts)
  T-1.7B   as T, with --model unsloth/Qwen3-1.7B
Subsets: for each seed the train texts are shuffled within gold-label strata and the n=150/300 subsets are
prefixes of the 551 ordering, so they are nested and identical for H and T (D16).
Imbalance: minority classes are oversampled (with replacement) up to half the majority class, from the label
source's own distribution, capped at 4x.
Training: fixed hyperparameters (HPARAMS), loss on the answer tokens only, no early stopping. Test is scored
only with --score-test, and refused if that run's test predictions already exist.
Backends: Unsloth 4-bit QLoRA when installed (Kaggle), otherwise transformers + PEFT (+ bitsandbytes on CUDA).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from apprentice import prompts
from apprentice.check_split import assert_trainable_path, check_split, load_manifest
from apprentice.data import LABELS, ROOT

TEACHER_DIR = ROOT / "data" / "teacher" / "openrouter-coreweave_fp4" / "openai_gpt-oss-120b" / "2ef529403276b34b"
RUNS = ROOT / "runs"
PREDS = ROOT / "results" / "preds"
TEST_SUITES = ("test_ce", "test_carrefour", "test_naturasi")
CONDITIONS = ("H", "T", "T+R", "T-large", "T-1.7B")
DEFAULT_MODEL = {"T-1.7B": "unsloth/Qwen3-1.7B"}
BASE_MODEL = "unsloth/Qwen3-4B"
HPARAMS = {"lora_r": 16, "lora_alpha": 16, "lora_dropout": 0.0,
           "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
           "lr": 2e-4, "epochs": 3, "micro_batch": 8, "grad_accum": 2, "warmup_ratio": 0.05,
           "weight_decay": 0.0, "max_len": 384, "oversample_to": 0.5, "oversample_cap": 4.0}


# ---- data ---------------------------------------------------------------------------------

def teacher_rows(suite: str) -> dict[str, dict]:
    path = TEACHER_DIR / f"{suite}.jsonl"
    assert_trainable_path(path)
    return {r["text_id"]: r for r in map(json.loads, open(path, encoding="utf-8")) if r.get("post_label")}


def ordered_train(manifest: list[dict], seed: int) -> list[dict]:
    """Train texts in a seed-specific order, interleaved across gold strata so every prefix keeps the
    class mix (nested curve subsets, shared by H and T)."""
    rng = random.Random(seed)
    strata = {l: [r for r in manifest if r["suite"] == "train" and r["gold_label"] == l] for l in LABELS}
    for l in LABELS:
        strata[l].sort(key=lambda r: r["text_id"])
        rng.shuffle(strata[l])
    total = sum(map(len, strata.values()))
    order, taken = [], {l: 0 for l in LABELS}
    for k in range(1, total + 1):    # largest-deficit-first interleave (proportional at every prefix)
        l = max(LABELS, key=lambda c: (len(strata[c]) * k / total - taken[c], -LABELS.index(c)))
        order.append(strata[l][taken[l]])
        taken[l] += 1
    return order


def oversample(examples: list[dict], seed: int, to: float, cap: float) -> list[dict]:
    rng = random.Random(seed + 1000)
    by = {l: [e for e in examples if e["label"] == l] for l in LABELS}
    top = max(len(v) for v in by.values())
    out = list(examples)
    for l, items in by.items():
        if not items:
            continue
        want = min(int(round(top * to)), int(len(items) * cap))
        out += [rng.choice(items) for _ in range(max(0, want - len(items)))]
    rng.shuffle(out)
    return out


def build_examples(condition: str, n: int, seed: int, manifest: list[dict]) -> tuple[list[dict], dict]:
    order = ordered_train(manifest, seed)
    if condition != "T-large":
        if n not in (150, 300, 551):
            sys.exit("--n must be 150, 300 or 551")
        order = order[:n]
    rows = list(order)
    if condition == "T-large":
        rows += sorted((r for r in manifest if r["suite"] == "t_large_extra"), key=lambda r: r["text_id"])
    ids = [r["text_id"] for r in rows]
    if condition == "H":
        ex = [{"text_id": r["text_id"], "text": r["text"], "label": r["gold_label"], "target": r["gold_label"]}
              for r in rows]
    else:
        tl = teacher_rows("train")
        if condition == "T-large":
            tl |= teacher_rows("t_large_extra")
        ex = []
        for r in rows:
            t = tl.get(r["text_id"])
            if not t:
                continue                                         # teacher output invalid: skip
            target = (json.dumps({"reasoning": t["reasoning"] or "", "label": t["post_label"]}, ensure_ascii=False)
                      if condition == "T+R" else t["post_label"])
            ex.append({"text_id": r["text_id"], "text": r["text"], "label": t["post_label"], "target": target})
    info = {"texts": len(ids), "examples_before_oversampling": len(ex),
            "label_counts": dict(Counter(e["label"] for e in ex)), "subset_ids": ids}
    return ex, info


# ---- tokenisation (same format as score_lp: generation prompt, then answer + end-of-turn) ----

def encode(tok, ex: dict, end_token: str, max_len: int) -> dict:
    from apprentice.score_lp import render
    p_ids = tok(render(tok, prompts.ft_messages(ex["text"])), add_special_tokens=False)["input_ids"]
    a_ids = tok(ex["target"] + end_token, add_special_tokens=False)["input_ids"]
    ids = (p_ids + a_ids)[:max_len]
    labels = ([-100] * len(p_ids) + a_ids)[:max_len]
    return {"input_ids": ids, "labels": labels}


def end_token_of(tok) -> str:
    from apprentice.score_lp import render
    probe = render(tok, [{"role": "user", "content": "x"}, {"role": "assistant", "content": "LABEL"}],
                   add_generation_prompt=False)
    return probe.split("LABEL", 1)[1].rstrip("\n")


# ---- model --------------------------------------------------------------------------------

def load_model(name: str, seed: int, backend: str, max_len: int, model=None, tokenizer=None):
    import torch
    if model is not None:                                        # tests: pre-built tiny model
        from peft import LoraConfig, get_peft_model
        cfg = LoraConfig(r=HPARAMS["lora_r"], lora_alpha=HPARAMS["lora_alpha"], lora_dropout=0.0,
                         target_modules=HPARAMS["target_modules"], task_type="CAUSAL_LM")
        return get_peft_model(model, cfg), tokenizer, "test"
    if backend in ("auto", "unsloth"):
        try:
            from unsloth import FastLanguageModel
            m, t = FastLanguageModel.from_pretrained(name, max_seq_length=max_len, load_in_4bit=True, dtype=None)
            m = FastLanguageModel.get_peft_model(
                m, r=HPARAMS["lora_r"], lora_alpha=HPARAMS["lora_alpha"], lora_dropout=HPARAMS["lora_dropout"],
                target_modules=HPARAMS["target_modules"], bias="none", use_gradient_checkpointing="unsloth",
                random_state=seed)
            return m, t, "unsloth"
        except ImportError:
            if backend == "unsloth":
                raise
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer
    t = AutoTokenizer.from_pretrained(name)
    kw = {}
    if torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.float16)
        kw["device_map"] = {"": 0}
    m = AutoModelForCausalLM.from_pretrained(name, **kw)
    if kw:
        m = prepare_model_for_kbit_training(m, use_gradient_checkpointing=True)
    cfg = LoraConfig(r=HPARAMS["lora_r"], lora_alpha=HPARAMS["lora_alpha"], lora_dropout=HPARAMS["lora_dropout"],
                     target_modules=HPARAMS["target_modules"], task_type="CAUSAL_LM")
    return get_peft_model(m, cfg), t, "hf"


def train_loop(model, tok, data: list[dict], seed: int, hp: dict, log=print) -> dict:
    import torch
    torch.manual_seed(seed)
    dev = next(model.parameters()).device
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=hp["lr"], weight_decay=hp["weight_decay"])
    steps_per_epoch = math.ceil(len(data) / (hp["micro_batch"] * hp["grad_accum"]))
    total = steps_per_epoch * hp["epochs"]
    warm = max(1, int(total * hp["warmup_ratio"]))
    def lr_lambda(s: int) -> float:      # linear warm-up, then linear decay to 0
        return (s + 1) / warm if s < warm else max(0.0, (total - s) / max(1, total - warm))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    use_amp = dev.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    rng = random.Random(seed)
    model.train()
    step, losses, t0 = 0, [], time.time()
    for epoch in range(hp["epochs"]):
        order = list(range(len(data)))
        rng.shuffle(order)
        batches = [order[i:i + hp["micro_batch"]] for i in range(0, len(order), hp["micro_batch"])]
        for bi, b in enumerate(batches):
            L = max(len(data[i]["input_ids"]) for i in b)
            ids = torch.full((len(b), L), pad, dtype=torch.long)
            lab = torch.full((len(b), L), -100, dtype=torch.long)
            att = torch.zeros((len(b), L), dtype=torch.long)
            for j, i in enumerate(b):
                n = len(data[i]["input_ids"])
                ids[j, :n] = torch.tensor(data[i]["input_ids"])
                lab[j, :n] = torch.tensor(data[i]["labels"])
                att[j, :n] = 1
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                loss = model(input_ids=ids.to(dev), attention_mask=att.to(dev), labels=lab.to(dev)).loss
            scaler.scale(loss / hp["grad_accum"]).backward()
            losses.append(loss.item())
            if (bi + 1) % hp["grad_accum"] == 0 or bi == len(batches) - 1:
                scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)
                sched.step()
                step += 1
                if step % 20 == 0 or step == total:
                    log(f"  step {step}/{total}  epoch {epoch + 1}  loss {sum(losses[-20:]) / len(losses[-20:]):.4f}")
    model.eval()
    return {"steps": step, "final_loss": sum(losses[-20:]) / max(1, len(losses[-20:])),
            "train_seconds": round(time.time() - t0, 1)}


# ---- scoring ------------------------------------------------------------------------------

def score_labels(model, tok, rows: list[dict]) -> list[dict]:
    from apprentice.score_lp import LabelScorer
    s = LabelScorer(model=model, tokenizer=tok, device=str(next(model.parameters()).device))
    # P_ft prompts are short, so no prefix cache: plain forwards work with every backend (Unsloth included)
    out = s.score([prompts.ft_messages(r["text"]) for r in rows], progress=True, use_cache=False)
    return [{"text_id": r["text_id"], "suite": r["suite"], "pred": o["pred"], "probs": o["probs"]}
            for r, o in zip(rows, out)]


def parse_tr(text: str) -> tuple[str | None, str | None]:
    import re
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        obj = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        obj = {}
    lab = obj.get("label") if isinstance(obj, dict) else None
    return (lab if lab in LABELS else None), (obj.get("reasoning") if isinstance(obj, dict) else None)


def score_generate(model, tok, rows: list[dict], batch: int = 16, max_new: int = 256) -> list[dict]:
    import torch
    from apprentice.score_lp import render
    side = tok.padding_side
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    dev = next(model.parameters()).device
    out = []
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        texts = [render(tok, prompts.ft_messages(r["text"])) for r in chunk]
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.pad_token_id)
        for r, g in zip(chunk, gen[:, enc["input_ids"].shape[1]:]):
            txt = tok.decode(g, skip_special_tokens=True)
            lab, why = parse_tr(txt)
            out.append({"text_id": r["text_id"], "suite": r["suite"], "pred": lab, "reasoning": why, "raw": txt})
        print(f"  generated {min(i + batch, len(rows))}/{len(rows)}")
    tok.padding_side = side
    return out


# ---- main ---------------------------------------------------------------------------------

def libs() -> str:
    out = []
    for mod in ("torch", "transformers", "peft", "unsloth", "bitsandbytes"):
        try:
            out.append(f"{mod} {__import__(mod).__version__}")
        except Exception:
            pass
    return "; ".join(out)


def run(a, model=None, tokenizer=None) -> dict:
    from apprentice.baselines import write_and_eval
    manifest = load_manifest()
    name = a.model or DEFAULT_MODEL.get(a.condition, BASE_MODEL)
    run_id = f"{a.condition}-n{a.n if a.condition != 'T-large' else 'all'}-s{a.seed}"
    pred_dir = PREDS / a.condition / f"n{a.n if a.condition != 'T-large' else 'all'}-s{a.seed}"
    if a.score_test and (pred_dir / "test.jsonl").exists() and not a.overwrite_final:
        sys.exit(f"{(pred_dir / 'test.jsonl').relative_to(ROOT)} exists: test is scored once per run.")
    ex, info = build_examples(a.condition, a.n, a.seed, manifest)
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "train.jsonl", "w", encoding="utf-8") as f:
        for e in ex:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    curve = {run_id: info["subset_ids"]} if a.condition != "T-large" else None
    check_split(training_files=[run_dir / "train.jsonl"], curve_subsets=curve)
    data = oversample(ex, a.seed, HPARAMS["oversample_to"], HPARAMS["oversample_cap"])
    print(f"{run_id}: {info['texts']} texts, {len(ex)} examples {info['label_counts']} -> {len(data)} after "
          f"oversampling {dict(Counter(e['label'] for e in data))}")
    m, tok, backend = load_model(name, a.seed, a.backend, HPARAMS["max_len"], model, tokenizer)
    end = end_token_of(tok)
    enc = [encode(tok, e, end, HPARAMS["max_len"]) for e in data]
    stats = train_loop(m, tok, enc, a.seed, HPARAMS)
    print(f"trained: {stats}")
    if backend == "unsloth" and a.condition == "T+R":      # fast generation; label scoring uses plain forwards
        from unsloth import FastLanguageModel
        FastLanguageModel.for_inference(m)
    if a.save_adapter:
        m.save_pretrained(run_dir / "adapter")
    pred_dir.mkdir(parents=True, exist_ok=True)
    suites = [("dev", [r for r in manifest if r["suite"] == "dev"])]
    if a.score_test:
        suites.append(("test", [r for r in manifest if r["suite"] in TEST_SUITES]))
    meta_base = {"run_id": run_id, "seed": a.seed, "train_size": info["texts"], "model": name, "backend": backend,
                 "lora": json.dumps({k: v for k, v in HPARAMS.items() if k != "target_modules"}),
                 "libs": libs(), "prompt_hash": prompts.prompt_hash(json.dumps(prompts.ft_messages("{{CLAIM}}"))),
                 "notes": (f"[{a.tag}] " if getattr(a, "tag", None) else "") +
                          f"examples {len(data)} (oversampled); steps {stats['steps']}; "
                          f"train {stats['train_seconds']}s; loss {stats['final_loss']:.4f}"}
    try:
        from huggingface_hub import model_info
        meta_base["model_revision"] = model_info(name).sha
    except Exception:
        meta_base["model_revision"] = None
    results = {}
    for suite, rows in suites:
        t0 = time.time()
        preds = score_generate(m, tok, rows) if a.condition == "T+R" else score_labels(m, tok, rows)
        dt = time.time() - t0
        if a.condition == "T+R":
            print(f"  valid JSON {sum(p['pred'] is not None for p in preds) / len(preds):.3f}")
        meta = dict(meta_base, notes=meta_base["notes"] + f"; scoring {1000 * dt / len(rows):.0f} ms/claim")
        write_and_eval(pred_dir / f"{suite}.jsonl", preds, a.condition, meta, manifest, append=True)
        results[suite] = len(preds)
    (run_dir / "run.json").write_text(json.dumps({"run_id": run_id, "condition": a.condition, **meta_base,
                                                  "stats": stats, "info": {k: v for k, v in info.items() if k != "subset_ids"},
                                                  "hparams": HPARAMS, "scored": results,
                                                  "date": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                                                 indent=1))
    return {"run_id": run_id, "stats": stats, "scored": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", choices=CONDITIONS, required=True)
    ap.add_argument("--n", type=int, default=551)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--model", help=f"default {BASE_MODEL} ({DEFAULT_MODEL['T-1.7B']} for T-1.7B)")
    ap.add_argument("--backend", choices=["auto", "unsloth", "hf"], default="auto")
    ap.add_argument("--score-test", action="store_true", help="also score test (once per run)")
    ap.add_argument("--overwrite-final", action="store_true")
    ap.add_argument("--save-adapter", action="store_true")
    ap.add_argument("--tag", help="free-text tag written to results.csv notes (e.g. smoke)")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
