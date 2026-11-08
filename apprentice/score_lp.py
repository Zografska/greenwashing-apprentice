"""Log-probability label scoring for causal LMs (SPEC D23). Used for S0-noLegal / S0 / S1 and for every
label-only fine-tuned student (Kaggle notebook), so all of them are scored identically.

For each claim the chat prompt is rendered with the model's own template (Qwen3: thinking disabled, so the
assistant turn starts with an empty <think></think> block), and the score of a label is the total
log-probability of the label string followed by the end-of-turn token. The highest of the three wins; the
softmax over the three is kept as `probs`. This always gives a valid label and needs no constrained decoding.

Speed: system prompt + few-shots are identical for every claim, so their KV cache is computed once and
reused (cache cropped back after each claim). Falls back to full-prompt scoring if the template does not
render the shared prefix identically.

  s = LabelScorer("Qwen/Qwen3-4B")
  s.score([messages_1, messages_2, ...])   # -> [{"pred":..., "logp": {...}, "probs": {...}}, ...]
"""
from __future__ import annotations

import math

import torch

from apprentice.data import LABELS


def render(tokenizer, messages, add_generation_prompt=True) -> str:
    kw = dict(tokenize=False, add_generation_prompt=add_generation_prompt)
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=False, **kw)
    except TypeError:                      # templates without the thinking switch
        return tokenizer.apply_chat_template(messages, **kw)


def crop_to(cache, length: int) -> None:
    """Truncate a KV cache to `length` tokens. Uses a negative crop, which means "remove N tokens" in both
    transformers 4.x and 5.x (5.x rejects positive values)."""
    extra = cache.get_seq_length() - length
    if extra > 0:
        cache.crop(-extra)


class LabelScorer:
    def __init__(self, model_name: str | None = None, model=None, tokenizer=None, revision: str | None = None,
                 dtype=None, device: str | None = None, end_token: str | None = None, labels=LABELS):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.device = device or ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        if dtype is None:
            dtype = torch.float32 if self.device == "cpu" else torch.float16   # T4: no bf16
        self.tok = tokenizer or AutoTokenizer.from_pretrained(model_name, revision=revision)
        self.model = model or AutoModelForCausalLM.from_pretrained(model_name, revision=revision, torch_dtype=dtype)
        self.model.to(self.device).eval()
        self.labels = tuple(labels)
        end = end_token or self._guess_end_token()
        self.label_ids = {l: self.tok(l + end, add_special_tokens=False)["input_ids"] for l in self.labels}
        self.model_revision = getattr(self.model.config, "_commit_hash", None) or revision
        if not self.model_revision and model_name:      # transformers 5 no longer sets _commit_hash
            try:
                from huggingface_hub import model_info
                self.model_revision = model_info(model_name, revision=revision).sha
            except Exception:
                self.model_revision = None
        self.prefix_hits = self.prefix_misses = 0

    def _guess_end_token(self) -> str:
        probe = render(self.tok, [{"role": "user", "content": "x"}, {"role": "assistant", "content": "LABEL"}],
                       add_generation_prompt=False)
        tail = probe.split("LABEL", 1)[1]
        return tail.rstrip("\n")           # e.g. "<|im_end|>"

    def _ids(self, text: str) -> list[int]:
        return self.tok(text, add_special_tokens=False)["input_ids"]

    @torch.no_grad()
    def _forward(self, ids: list[int], cache=None):
        x = torch.tensor([ids], device=self.device)
        out = self.model(input_ids=x, past_key_values=cache, use_cache=True)
        return out.logits[0].float(), out.past_key_values

    @torch.no_grad()
    def _score_from(self, last_logits, cache, cache_len: int) -> dict[str, float]:
        """Label log-probs given the logits at the last prompt position and the cache of the prompt."""
        first = torch.log_softmax(last_logits, -1)
        res = {}
        for lab, ids in self.label_ids.items():
            lp = float(first[ids[0]])
            if len(ids) > 1:
                logits, cache = self._forward(ids[:-1], cache)
                lps = torch.log_softmax(logits, -1)
                lp += float(sum(lps[i, t] for i, t in enumerate(ids[1:])))
                crop_to(cache, cache_len)
            res[lab] = lp
        return res

    SENTINEL = "\u2063\u2063SCORE_LP_SENTINEL\u2063\u2063"

    def _prefix(self, messages) -> str | None:
        """Everything the template renders before the final user message's content. Rendering a copy whose
        last content is a sentinel (instead of rendering messages[:-1]) keeps templates that treat the last
        assistant turn specially (Qwen3 adds an empty think block after the last user query) consistent."""
        if len(messages) < 2:
            return None
        probe = messages[:-1] + [{**messages[-1], "content": self.SENTINEL}]
        text = render(self.tok, probe)
        return text.split(self.SENTINEL, 1)[0] if self.SENTINEL in text else None

    @torch.no_grad()
    def score(self, batch_messages: list[list[dict]], progress: bool = False) -> list[dict]:
        out, pcache, pkey, plen = [], None, None, 0
        it = batch_messages
        if progress:
            try:
                from tqdm.auto import tqdm
                it = tqdm(batch_messages)
            except ImportError:
                pass
        for msgs in it:
            full = render(self.tok, msgs)
            prefix = self._prefix(msgs)
            ids = self._ids(full)
            usable = False
            if prefix and full.startswith(prefix):
                pids = self._ids(prefix)
                usable = ids[:len(pids)] == pids and len(pids) < len(ids)
            if usable:
                self.prefix_hits += 1
                if prefix != pkey:              # (re)build the shared prefix cache
                    _, pcache = self._forward(pids)
                    pkey, plen = prefix, len(pids)
                logits, cache = self._forward(ids[plen:], pcache)
                lp = self._score_from(logits[-1], cache, len(ids))
                crop_to(cache, plen)
            else:
                self.prefix_misses += 1
                logits, cache = self._forward(ids)
                lp = self._score_from(logits[-1], cache, len(ids))
            m = max(lp.values())
            z = sum(math.exp(v - m) for v in lp.values())
            out.append({"pred": max(lp, key=lp.get), "logp": lp,
                        "probs": {k: math.exp(v - m) / z for k, v in lp.items()}})
        return out
