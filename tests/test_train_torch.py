"""End-to-end training/scoring on a tiny random Qwen3 (no download). Skipped without torch + peft."""
import argparse
import json

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("peft")
pytest.importorskip("transformers")

from tests.test_score_lp import QWEN3_LIKE  # noqa: E402
from apprentice import train  # noqa: E402


def tiny():
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers
    from transformers import PreTrainedTokenizerFast, Qwen3Config, Qwen3ForCausalLM
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    corpus = ["CLAIM: Confezione 100% riciclabile IN_SCOPE NEEDS_VERIFICATION OUT reasoning label",
              "Classify the claim from an Italian product listing under Directive ECGT"] * 50
    tk.train_from_iterator(corpus, trainers.BpeTrainer(
        vocab_size=500, special_tokens=["[UNK]", "<|im_start|>", "<|im_end|>", "<think>", "</think>", "<pad>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    tok = PreTrainedTokenizerFast(tokenizer_object=tk, pad_token="<pad>", eos_token="<|im_end|>")
    tok.chat_template = QWEN3_LIKE
    torch.manual_seed(0)
    cfg = Qwen3Config(vocab_size=len(tok), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, head_dim=16, max_position_embeddings=1024)
    return Qwen3ForCausalLM(cfg), tok


def test_encode_masks_prompt_and_matches_scoring_format():
    _, tok = tiny()
    end = train.end_token_of(tok)
    e = train.encode(tok, {"text": "Confezione riciclabile", "target": "OUT"}, end, 384)
    n_ans = len(tok("OUT" + end, add_special_tokens=False)["input_ids"])
    assert e["labels"][-n_ans:] == e["input_ids"][-n_ans:]
    assert all(l == -100 for l in e["labels"][:-n_ans])


def test_training_reduces_loss():
    model, tok = tiny()
    m, tok, _ = train.load_model("x", 0, "auto", 384, model, tok)
    end = train.end_token_of(tok)
    data = [train.encode(tok, {"text": f"claim {i}", "target": lab}, end, 384)
            for i, lab in enumerate(["OUT", "IN_SCOPE", "NEEDS_VERIFICATION"] * 8)]
    hp = dict(train.HPARAMS, epochs=1, lr=1e-2, micro_batch=4, grad_accum=1)
    first = train.train_loop(m, tok, data, 0, hp, log=lambda *_: None)["final_loss"]
    later = train.train_loop(m, tok, data, 0, dict(hp, epochs=4), log=lambda *_: None)["final_loss"]
    assert later < first


def test_run_end_to_end(tmp_path, monkeypatch):
    model, tok = tiny()
    monkeypatch.setattr(train, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(train, "PREDS", tmp_path / "preds")
    monkeypatch.setitem(train.HPARAMS, "epochs", 1)
    rows = []
    import apprentice.baselines as b
    monkeypatch.setattr(b, "append_results", rows.append)
    a = argparse.Namespace(condition="H", n=150, seed=0, model="tiny", backend="auto", score_test=False,
                           overwrite_final=False, save_adapter=False)
    out = train.run(a, model=model, tokenizer=tok)
    preds = [json.loads(l) for l in open(tmp_path / "preds" / "H" / "n150-s0" / "dev.jsonl")]
    assert len(preds) == 150 and all(p["pred"] in train.LABELS for p in preds)
    assert rows and rows[0]["run_id"] == "H-n150-s0" and "dev_w.macro_f1" in rows[0]
    assert out["scored"] == {"dev": 150}


def test_generate_path_runs():
    model, tok = tiny()
    rows = [{"text_id": f"t{i}", "suite": "dev", "text": f"claim {i}"} for i in range(3)]
    out = train.score_generate(model, tok, rows, batch=2, max_new=8)
    assert len(out) == 3 and all("raw" in o for o in out)
