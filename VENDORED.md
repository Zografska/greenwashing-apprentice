# VENDORED.md: frozen snapshot from `greenwashing-claim-detector`

Everything under `vendor/` is a **read-only copy** of committed files from the main repo,
taken with `git show <commit>:<path>` on 2026-11-01. **Never edit these files.** If the source
changes (e.g. the professors relabel something), re-vendor deliberately, bump the split
version (`split_v2`), and add a new section below. Do not sync silently. See SPEC §4.3.

Commits:

- `0d0081a7e6eb02279f4b9792dc5466e2c6b67086`: main repo HEAD (branch `website-dashboard`, clean tree)
- `69b008a84bc73bbbccc9385b3c30c62085e6b9ef` (= `f0f1b57~1`): last commit with `src/knowledge/` (legal chunks)
- `9811ae59a96838af8c9fa4d899979c86bf37eebc` (= `0f7ff41~1`): last commit with `rag/docs/consolidated.pdf`

| vendored file | source commit | source path | sha256 (first 16) |
|---|---|---|---|
| `vendor/golden/golden_set_ecgt_100.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_100.json` | `b22b7c31baab3a45` |
| `vendor/golden/golden_set_ecgt_reserve.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_reserve.json` | `526540db9910a0e3` |
| `vendor/golden/golden_set_ecgt_coop_100.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_coop_100.json` | `a530137a9c08d0c6` |
| `vendor/golden/golden_set_ecgt_coop_reserve.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_coop_reserve.json` | `ea74a8d21c3686f1` |
| `vendor/golden/golden_set_ecgt_eurospin_100.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_eurospin_100.json` | `d7d4a7875b38ac8a` |
| `vendor/golden/golden_set_ecgt_eurospin_reserve.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_eurospin_reserve.json` | `8567a14ed409e43f` |
| `vendor/golden/golden_set_ecgt_naturasi_100.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_naturasi_100.json` | `3b7983803686862a` |
| `vendor/golden/golden_set_ecgt_naturasi_reserve.json` | `0d0081a` | `golden/labeled/golden_set_ecgt_naturasi_reserve.json` | `c2347aafeef3d343` |
| `vendor/golden/golden_set_ecgt_100_README.md` | `0d0081a` | `golden/labeled/golden_set_ecgt_100_README.md` | `870701904722dd02` |
| `vendor/golden/golden_set_ecgt_coop_100_README.md` | `0d0081a` | `golden/labeled/golden_set_ecgt_coop_100_README.md` | `32baf8cbc3274532` |
| `vendor/golden/golden_set_ecgt_eurospin_100_README.md` | `0d0081a` | `golden/labeled/golden_set_ecgt_eurospin_100_README.md` | `6b7d768ecc2806a9` |
| `vendor/golden/golden_set_ecgt_naturasi_100_README.md` | `0d0081a` | `golden/labeled/golden_set_ecgt_naturasi_100_README.md` | `8fa2fb8ad6bd82e7` |
| `vendor/retriever/anchors_v4.jsonl` | `0d0081a` | `retriever/knowledge/anchors_v4.jsonl` | `4dfcb5549f8230bd` |
| `vendor/retriever/ecgt_retriever.yaml` | `0d0081a` | `retriever/ecgt_retriever.yaml` | `76f327e8c38b56aa` |
| `vendor/retriever/score.py` | `0d0081a` | `retriever/score.py` | `bea74b0f0ae7fad7` |
| `vendor/retriever/segment.py` | `0d0081a` | `retriever/segment.py` | `a531a461042a9dad` |
| `vendor/retriever/lexical_coverage.py` | `0d0081a` | `retriever/lexical_coverage.py` | `36dcd6ea5ca5c70e` |
| `vendor/prompts/ECGT_CLAIM_CLASSIFIER_PROMPT.md` | `0d0081a` | `classifier/ECGT_CLAIM_CLASSIFIER_PROMPT.md` | `500a008e8c6f136e` |
| `vendor/prompts/ECGT_TWO_PASS_PROMPT.md` | `0d0081a` | `golden/ECGT_TWO_PASS_PROMPT.md` | `e58381e0b7bfbd37` |
| `vendor/tools/groq_relabel.py` | `0d0081a` | `tools/groq_relabel.py` | `f5b748e87973803b` |
| `vendor/tools/jsonl_viewer.html` | `0d0081a` | `tools/jsonl_viewer.html` | `9c534f5cafb2fc93` |
| `vendor/tools/json_viewer.html` | `0d0081a` | `tools/json_viewer.html` | `35b8521a96da0e83` |
| `vendor/legal/ecgt_chunks_it.json` | `69b008a` | `src/knowledge/chunks/ecgt.json` | `5597b64a3de367d8` |
| `vendor/legal/ucpd_chunks_it.json` | `69b008a` | `src/knowledge/chunks/ucpd.json` | `d51f4f59404e2a1f` |
| `vendor/legal/chunker.py` | `69b008a` | `src/knowledge/chunker.py` | `f34b5c1d0b107335` |
| `vendor/legal/ucpd_ecgt_consolidated_it.pdf` | `9811ae5` | `rag/docs/consolidated.pdf` | `2abe868aa7a129d5` |

Notes:

- `vendor/retriever/*.py` and `vendor/tools/groq_relabel.py` are **reference code** (not imported as is).
  `score.py` depends on `segment.py`, `lexical_coverage.py` and the YAML config; the apprentice only needs
  the e5 embedding settings (model `intfloat/multilingual-e5-base`, revision `d128750597153bb5987e10b1c3493a34e5a4502a`,
  prefix `query: ` on both sides, normalised) and the anchor file.
- `groq_relabel.py` was never run in the main repo.
- `vendor/legal/*_chunks_it.json` and the PDF are the **EU directive text (Italian OJ edition)**, not Italy's
  D.Lgs. 30/2026. See the claude.ai project doc `claude/legal-framework-ecgt-ucpd.md`.
- `docs/SPEC.md` is not vendored: it is this repo's own document (originally drafted in the main repo).
