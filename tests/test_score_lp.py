"""Prefix-cached label scoring must equal naive full-sequence scoring. Uses a tiny random Qwen3 model and a
locally trained tokenizer (no download). Skipped where torch/transformers are not installed (e.g. the Mac
core env); runs on Kaggle."""
import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from tokenizers import Tokenizer, models, pre_tokenizers, trainers  # noqa: E402

from apprentice.score_lp import LabelScorer, render  # noqa: E402

QWEN3_LIKE = ("{% set ns = namespace(lq=-1) %}{% for m in messages %}{% if m['role']=='user' %}"
              "{% set ns.lq = loop.index0 %}{% endif %}{% endfor %}"
              "{% for m in messages %}<|im_start|>{{ m['role'] }}\n{% if m['role']=='assistant' and loop.index0 > ns.lq %}"
              "<think>\n\n</think>\n\n{% endif %}{{ m['content'] }}<|im_end|>\n{% endfor %}"
              "{% if add_generation_prompt %}<|im_start|>assistant\n{% if enable_thinking is defined and "
              "enable_thinking is false %}<think>\n\n</think>\n\n{% endif %}{% endif %}")


@pytest.fixture(scope="module")
def scorer():
    from transformers import PreTrainedTokenizerFast, Qwen3Config, Qwen3ForCausalLM
    tk = Tokenizer(models.BPE(unk_token="[UNK]"))
    tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    corpus = ["CLAIM: Confezione 100% riciclabile IN_SCOPE NEEDS_VERIFICATION OUT system user assistant",
              "Legal context asserzione ambientale generica eco green natura Similar labelled examples"] * 50
    tk.train_from_iterator(corpus, trainers.BpeTrainer(
        vocab_size=400, special_tokens=["[UNK]", "<|im_start|>", "<|im_end|>", "<think>", "</think>", "<pad>"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    tok = PreTrainedTokenizerFast(tokenizer_object=tk, pad_token="<pad>", eos_token="<|im_end|>")
    tok.chat_template = QWEN3_LIKE
    torch.manual_seed(0)
    cfg = Qwen3Config(vocab_size=len(tok), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, head_dim=16, max_position_embeddings=512)
    return LabelScorer(model=Qwen3ForCausalLM(cfg), tokenizer=tok, device="cpu")


def naive(s, msgs):
    ids = s.tok(render(s.tok, msgs), add_special_tokens=False)["input_ids"]
    out = {}
    with torch.no_grad():
        for lab, lids in s.label_ids.items():
            lp = torch.log_softmax(s.model(torch.tensor([ids + lids])).logits[0].float(), -1)
            out[lab] = float(sum(lp[len(ids) - 1 + i, t] for i, t in enumerate(lids)))
    return out


def test_end_token_is_im_end(scorer):
    assert scorer._guess_end_token() == "<|im_end|>"


def test_prefix_cache_matches_naive(scorer):
    sys_ = {"role": "system", "content": "Legal context asserzione ambientale generica"}
    fs = [{"role": "user", "content": "CLAIM: eco"}, {"role": "assistant", "content": "OUT"}]
    batch = [[sys_, *fs, {"role": "user", "content": c}] for c in
             ["CLAIM: Confezione 100% riciclabile", "CLAIM: green",
              "Similar labelled examples:\nCLAIM: natura -> IN_SCOPE\n\nCLAIM: eco green"]]
    before = scorer.prefix_hits
    out = scorer.score(batch)
    assert scorer.prefix_hits - before == 3
    for m, o in zip(batch, out):
        n = naive(scorer, m)
        assert max(abs(n[k] - o["logp"][k]) for k in n) < 1e-3
        assert o["pred"] == max(n, key=n.get) and abs(sum(o["probs"].values()) - 1) < 1e-6


def test_no_prefix_path(scorer):
    m = [{"role": "user", "content": "CLAIM: eco"}]
    o = scorer.score([m])[0]
    n = naive(scorer, m)
    assert max(abs(n[k] - o["logp"][k]) for k in n) < 1e-3
