# ECGT_TWO_PASS_PROMPT.md

**Version 4** (2026-09-24). Replaces the single-pass `PRODUCT_CLASSIFIER_PROMPT.md` v3 for
local 3–8B models. **Not yet tested.** Calibrate token budgets with `--limit 2-3` before a full run.

> **Retriever redesign (2026-09-24):** Pass 1 is being replaced by deterministic segmentation
> plus an embedding + lexical candidate retriever (`retriever/`, see `ECGT_RETRIEVER_CHECKLIST.md`).
> Pass 2 and POST below stay the source of truth. The Pass 1 section is kept only as the
> baseline (A) for the Step 7 end-to-end comparison.

## What changed from v3, and why

| v3 | v4 | Why |
|---|---|---|
| One pass: extract + classify, ~5k-token system prompt, T1–T16 | Two short passes + deterministic Python between them | A small model can't hold 16 precedence rules; each pass now does one thing |
| DISCARD label with 5 reasons + notes | No DISCARD in output; out-of-scope spans are dropped | User requirement |
| Model picks the label | Model picks **triggers** (enum), Python maps triggers → label | Precedence ("a visible defect beats verification") becomes code, not a model judgment |
| UNCERTAIN label | Two labels + `confidence` | Small models overuse escape labels |
| Model joins footnotes, drops material codes, dedupes, reports `source_field` | Python does all four | Deterministic; removes ~40% of v3's rules |
| Italian instructions | English instructions, Italian examples verbatim | Llama-class small models follow English instructions more reliably; the examples keep the Italian surface forms. Worth an A/B test. |
| Specific recycled content with no base → IN_SCOPE (T8) | → NEEDS_VERIFICATION | Gray-zone decision, 2026-09-24 |
| Vegan → DISCARD | → NEEDS_VERIFICATION, always | Gray-zone decision |
| Only sustainability endorsements | Any **named** approval → NV (UCPD Annex I #2/#4, beyond ECGT) | Gray-zone decision |
| Production method ≠ environmental claim | Supply-chain claims (farms, animals, farmers, sourcing, traceability) are in scope; recipe/history are not | Gray-zone decision |
| — | "riduce il rischio di …" wording → NV | Gray-zone decision |

## Label semantics (the single idea both passes rest on)

- **IN_SCOPE**: problematic *as written*. Generic or vague green/natural/social wording with no
  definition, offset-based climate neutrality, a reduction or comparison with no identifiable
  comparator, or a brand eco-slogan.
- **NEEDS_VERIFICATION (NV)**: specific and checkable. Lawful if a third party can confirm it
  (recycled %, a named certification, a named endorsement, vegan, a concrete farming practice,
  a defined term).
- If a claim has both, **IN_SCOPE wins** (Python enforces this).

---

## Pipeline

```
record ─► [PRE]  strip annotation fields; drop `recycling` field; drop material-code lines,
                 "Raccolta differenziata", "Verifica le disposizioni del tuo Comune"
                 (reuse _MANDATORY_DISCLOSURE_PATTERNS)
       ─► [PASS 1] extract candidate spans (list of strings)
                 (retriever design: segment → footnote join → lexical OR margin > τ instead)
       ─► [MID]  verbatim check → strip bullets/trailing punctuation → dedupe →
                 locate source_field → join footnote by marker (*, **, ^, °)
       ─► [PASS 2] one call per claim → triggers[] + confidence
       ─► [POST] triggers → label; drop claims whose only trigger is out_of_scope
```

---

## PASS 1: extraction (baseline only)

Replaced by the retriever in `retriever/` (config: `retriever/ecgt_retriever.yaml`). Kept
unchanged so Step 7 of `ECGT_RETRIEVER_CHECKLIST.md` can run "A) original two-pass" as a baseline.

**Settings:** temperature 0 · Ollama `format` = schema below · `num_predict` ≈ 1024 (est. ~40
tok/claim × 25) · `num_ctx` sized to record + ~1.5k prompt.

### System prompt

```
You extract marketing claims from ONE Italian grocery or personal-care product record.
Return ONLY claims in the scope below. Copy each claim EXACTLY as written (same words, same
capitalization, same symbols such as *, ^, %). Never paraphrase or translate.

EXTRACT a sentence, line or bullet if it talks about ANY of these:
1. Environment, nature, climate, planet, CO2/emissions, eco, green, sustainable.
   «Coop per l'ambiente» «Il gusto di amare il pianeta» «Agricoltura sostenibile»
2. Packaging: plastic, recycled, recyclable, biodegradable, compostable, less packaging.
   «Etichetta in carta riciclata» «75% In meno di plastica» «Eco pack 100% riciclabile»
3. The product or its ingredients being natural.
   «100% Naturale» «94% Ingredienti di origine naturale»
4. Certifications, labels, organic/bio, or approval by a NAMED organization.
   «Le migliori pesche gialle bio» «Approvata da A.I.Nut. - Associazione Italiana Nutrizionisti»
5. Vegan or free from animal ingredients.  «VEGANO» «formula vegana**»
6. Farms, farmers, animals, animal feed, sourcing, traceability.
   «Agricoltori selezionati» «Tracciabilità e sicurezza»
   «Le nostre mucche vengono nutrite in modo tradizionale, con erba fresca, fieno e piante di campo. E si sente!»
7. Reducing a risk: «aiutano a ridurre il rischio di irritazione della pelle»

DO NOT EXTRACT:
- Health or nutrition: «Speziato e Antiossidante» «fonte di fibre» «Alta digeribilità»
- What the product does or how well: «Pulizia profonda» «Protegge dagli agenti esterni»
  «limita la formazione di cattivi odori» «Massima protezione e comfort»
- Tests and skin tolerance: «Clinicamente testate» «ipoallergenico»
- History, tradition, recipe, family, founding year:
  «Dal 1820 la famiglia Grondona garantisce» «le inimitabili ricette di famiglia»
- Patents and trademarks: «Brevetto internazionale»
- Product names, weights, ingredient lists, storage or cooking instructions, allergen warnings.
- Lines that start with a footnote marker (*, **, ^) that only explain another line.
  Extract the line that CARRIES the marker, not the explanation.

HOW TO CUT:
- Cut only at a sentence end, line break or bullet. Never cut at a comma.
- Remove a leading "-" or "•".
- Same text in two fields: return it once.
- If a sentence mixes an in-scope part with an out-of-scope part, return the whole sentence.
- If unsure whether a line is in scope, EXTRACT it.

Output JSON: {"claims": ["<exact text>", ...]}. No claims: {"claims": []}.
```

### Few-shot (one exchange, prepend as user/assistant turns)

User:
```
{"name":"Bagnoschiuma idratante","features":"Formula vegana & biodegradabile^\nClinicamente testato\nProtegge la pelle dagli agenti esterni\n^99,9% formula biodegradabile","producer_info":"Dal 1920 le ricette di famiglia. Flacone green 100%. Aiuta a ridurre il rischio di irritazione della pelle.","certifications":["VEGANO"]}
```
Assistant:
```
{"claims":["Formula vegana & biodegradabile^","Flacone green 100%.","Aiuta a ridurre il rischio di irritazione della pelle.","VEGANO"]}
```

### Schema
```json
{"type":"object","properties":{"claims":{"type":"array","items":{"type":"string","minLength":2}}},"required":["claims"]}
```

---

## MID: deterministic step (Python)

1. **Verbatim check:** keep the span if it is a substring of one field. If not, retry with
   whitespace/case normalized and map back to the original text. Otherwise drop it and log it.
2. Strip leading bullets and trailing `.`/`;`. Dedupe. Record `source_field`, preferring the
   most specific field: `features` > `producer_info` > `description` > `name`.
3. **Footnote join:** if the span contains a marker (`*`, `**`, `^`, `°`), find lines in the
   record that start with the same marker. Join as `claim ... body`. With several candidate
   bodies, pass all of them to Pass 2 as `FOOTNOTE:` lines and let the model use the relevant one.

---

## PASS 2: classification (one call per claim)

**Settings:** temperature 0 · `format` = schema below · `num_predict` ≈ 96 · `num_ctx` ≈ 3k.

### System prompt

```
You label ONE marketing claim from an Italian product under the EU rules on green and ethical
claims. List EVERY trigger below that applies to the claim. Judge only the words; do not
guess whether they are true.

A. PROBLEM AS WRITTEN
generic_green      vague green/impact words with no definition: eco, green, sostenibile,
                   amico dell'ambiente, per il pianeta, ridurre l'impatto, ho a cuore l'ambiente
                   «brik-eco sostenibile» «Flacone green 100%» «cannuccia di carta per ridurre l'impatto sull'ambiente»
undefined_natural  "natural"/"of natural origin"/"% natural" with no definition in CLAIM or FOOTNOTE
                   «100% Naturale» «94% Ingredienti di origine naturale»
climate_neutral    carbon/climate neutral, zero emissions, emissions offset or compensated,
                   EVEN IF explained  «CO2 100% prodotto a impatto climatico neutralizzato»
vague_comparison   a reduction or "more/less" with no comparator, or only "the previous pack"
                   «75% In meno di plastica» «-17% Plastica rispetto al pack precedente»
                   «Con cacao da coltivazione più sostenibile»
brand_eco_slogan   brand, line or slogan with eco content  «Coop per l'ambiente» «Vivi Verde»
                   «Gallo green» «Il Tuo Ciclo. Il Tuo Pianeta. Teniamo A Entrambi.»
vague_supply_chain vague claim about farmers, sourcing or traceability
                   «Agricoltori selezionati» «Tracciabilità e sicurezza» «Agricoltura sostenibile»

B. SPECIFIC, NEEDS CHECKING
recycled_recyclable  recycled or recyclable content of a named part  «Etichetta in carta riciclata»
                     «Qualità Pampers in cartoni 100% riciclati»
biodegradable        biodegradable or compostable  «99,9% formula biodegradabile»
certification        organic/bio, or a named or unnamed certification or label (FSC, Fairtrade, Ecolabel)
                     «Le migliori pesche gialle bio»
named_endorsement    approval by a named organization  «Approvata da A.I.Nut. - Associazione Italiana Nutrizionisti»
vegan                vegan, free from animal ingredients  «VEGANO»
farming_practice     a concrete practice with farms or animals  «mucche nutrite con erba fresca, fieno e piante di campo»
defined_term         a green or natural word that CLAIM or FOOTNOTE defines
                     «96% Natural origin* ... water and naturally sourced ingredients with limited processing»
risk_reduction       "riduce/aiuta a ridurre il rischio di ..."
named_comparison     compared with a named brand, product or standard  «rispetto alle precedenti confezioni Beretta»
pollutant_free       free from a pollutant  «Senza microplastiche» «Senza siliconi»

C. NONE OF THE ABOVE
out_of_scope       health or nutrition; what the product does (performance); tests or skin
                   tolerance; history, tradition, recipe; patents or trademarks; geographic
                   origin (country or region); quality schemes (DOP, IGP, STG); free from a
                   non-pollutant (senza conservanti, parabeni, glutine, lattosio, zuccheri);
                   sales rank; natural flavour or taste (aroma naturale, gusto naturale);
                   packaging function (salvafreschezza, richiudibile, apertura facilitata)

Output JSON: {"triggers": [...], "confidence": 0.0-1.0}
confidence = how sure you are that the trigger list is right.
```

### Few-shot (5 compact exchanges)

```
CLAIM: Eco pack 100% riciclabile - Con meno plastica
FOOTNOTE: none
→ {"triggers":["generic_green","recycled_recyclable","vague_comparison"],"confidence":0.9}

CLAIM: 96% Natural origin* ... water and naturally sourced ingredients with limited processing
FOOTNOTE: *water and naturally sourced ingredients with limited processing
→ {"triggers":["defined_term"],"confidence":0.8}

CLAIM: Emissioni zero / Questa confezione è Carbon Neutral: ciò significa che neutralizziamo le emissioni di CO2 generate dalla sua produzione
FOOTNOTE: none
→ {"triggers":["climate_neutral"],"confidence":0.95}

CLAIM: Clinicamente testate
FOOTNOTE: none
→ {"triggers":["out_of_scope"],"confidence":0.9}

CLAIM: Aroma naturale
FOOTNOTE: none
→ {"triggers":["out_of_scope"],"confidence":0.9}
```

### User message template
```
CLAIM: {{claim_text}}
FOOTNOTE: {{footnote_body_or_none}}
PRODUCT: {{name}} ({{brand}})
```

### Schema
```json
{"type":"object","properties":{
  "triggers":{"type":"array","minItems":1,"items":{"type":"string","enum":[
    "generic_green","undefined_natural","climate_neutral","vague_comparison","brand_eco_slogan","vague_supply_chain",
    "recycled_recyclable","biodegradable","certification","named_endorsement","vegan","farming_practice",
    "defined_term","risk_reduction","named_comparison","pollutant_free","out_of_scope"]}},
  "confidence":{"type":"number","minimum":0,"maximum":1}},
 "required":["triggers","confidence"]}
```

---

## POST: triggers → label (Python)

```python
IN_SCOPE_T = {"generic_green","undefined_natural","climate_neutral",
              "vague_comparison","brand_eco_slogan","vague_supply_chain"}

def label(triggers):
    t = set(triggers) - {"out_of_scope"}      # any in-scope trigger beats the exit
    if not t:
        return None                           # drop: not ECGT, never reported
    if "defined_term" in t:
        t.discard("undefined_natural")        # a definition cancels "undefined"
    return "IN_SCOPE" if t & IN_SCOPE_T else "NEEDS_VERIFICATION"
```

Final output per product:
```json
{"product_id":"…","claims":[{"claim_text":"…","source_field":"…","label":"IN_SCOPE|NEEDS_VERIFICATION","triggers":["…"],"confidence":0.0}]}
```
`triggers` doubles as the rationale. If v3's `verification.question` is still needed for NV
claims, generate it from a per-trigger template in code, not with the model.

---

## Resolved questions (2026-09-24, see the checklist's decisions log)

1. **Geographic origin** («100% Italiano», «Coltivati in Puglia»): **out_of_scope**. Negative
   anchor category `origin`.
2. **DOP/IGP/STG**: **out_of_scope** (a quality scheme, not an endorsement). Negative anchor
   category `quality_scheme`.
3. **«Senza microplastiche»**: **NV** (`pollutant_free`; v3 had IN_SCOPE). «Senza siliconi» is
   also NV. «Senza parabeni» / «Senza conservanti» stay out_of_scope (`free_from_non_pollutant`).
4. **Pass 1 recall vs. prefilter**: superseded. There is no `extraction.py` prefilter in the
   retriever design; the lexical half of the candidate rule is `lexical.include` in
   `retriever/ecgt_retriever.yaml`, checked with `retriever/lexical_coverage.py`.
