# ECGT gold set — 100 Coop products

This is a gold evaluation set for a detector of claims under the EU ECGT rules (Directive 2024/825), built from `clean/coop.json`. It uses the same method as the Carrefour set (`golden_set_ecgt_100.json`), and the guide and project conventions from that set apply unchanged. Every claim is copied verbatim from its source field. Each label is derived mechanically from the claim's triggers: only out_of_scope gives DISCARDED; any group-A trigger gives IN_SCOPE; otherwise a group-B trigger gives NEEDS_VERIFICATION. defined_term cancels undefined_natural. `coop_claims.json` / `coop_claims.jsonl` hold earlier annotations; they were never opened. The file contained no existing annotation fields.

Files: `golden_set_ecgt_coop_100.json` (selected), `golden_set_ecgt_coop_reserve.json` (the other 149 usable products, labelled the same way), and this README.

Accounting: 100 selected + 149 reserve + 1 unusable = 250 records in the file.

## Field mapping (Coop)

| Output field | Source |
|---|---|
| product_id | `product_id` |
| ean | `ean` |
| name | `name` |
| category | `origin_file` |
| source_file | constant `clean/coop.json` |
| source_index | position in the JSON array |
| retailer | constant `Coop` |
| brand | `brand`; 26 records have it null or empty, so the brand was inferred from name/text or set to "unbranded" |
| claims[].source_field | `features`, `producer_info`, `certifications` (badge list), or `description`. `description` = features + producer_info + extra text, so a claim is taken from the most specific field, and from `description` only when its text appears nowhere else. |
| not extracted | `denomination` (the legal sales name); `url` |

## Retailer-specific decisions

- **Badges** are mapped one fixed way across all products:
  - BIOLOGICO, FOREST STEWARDSHIP COUNCIL → certification
  - VIVI VERDE → brand_eco_slogan
  - VEGANO → vegan
  - SOLIDAL → certification (low)
  - Equalitas - Cantina Sostenibile → certification + generic_green
  - DOP / IGP / DOC / DOCG / IGT, SENZA LATTOSIO, SENZA GLUTINE, PROTEIN +, Prodotto Ligure, BENE SI' → out_of_scope
  - Not extracted: brand or line names (COOP, FIOR FIORE, CRESCENDO, GLI SPESOTTI, DAYTECH, «Diventa SocioCoop…») and tax/regulatory status (DISPOSITIVO MEDICO DETRAIBILE, ALIMENTI SPECIALI DETRAIBILI).
  - A badge is dropped when a text field already has the same claim with the same words (ignoring case). A badge with different wording, e.g. DOP next to «Denominazione d'Origine Protetta», is kept as its own claim. 9 badges that one labelling batch had dropped as semantic duplicates were restored, so all batches follow the same rule.
- **Nutrition comparisons** («-30% di zuccheri rispetto al latte», «65% di grassi in meno*») are out_of_scope. The comparison triggers cover environmental comparisons only.
- **«Riciclabile sì, ma dove?»** is dropped as a recycling call-to-action, the same as in the Carrefour set.


## Unusable records

1 records were set aside.

| idx | EAN | name | reason |
|---|---|---|---|
| 246 | 8020141101291 | Acqua naturale in vetro | no marketing text (description, features, producer_info and certifications all empty) |

## Counts

### Usable pool (249)

- Products: 249. Buckets: hard_yes 60 · in_between 58 · hard_no 131, of which 97 hard_no products have DISCARDED decoy claims.
- Claims: 1219. IN_SCOPE 156 · NEEDS_VERIFICATION 158 · DISCARDED 905 · low confidence 120
- Claims by source field: producer_info 622, features 481, certifications 95, description 21
- Macro category: food and drink 194 · personal care and household 55
- Product gray_zone tags: generic_plus_specific 23, natural_footnote 5, farming_vs_heritage 3, endorsement_named_vs_generic 6, risk_vs_performance 9, comparator_vague_vs_named 7, eco_in_health_heritage 6, senza_pollutant_vs_additive 5, split_slogan 2

| trigger | products | claims |
|---|---|---|
| generic_green | 35 | 55 |
| undefined_natural | 28 | 38 |
| climate_neutral | 5 | 6 |
| vague_comparison | 11 | 12 |
| brand_eco_slogan | 25 | 31 |
| vague_supply_chain | 22 | 33 |
| recycled_recyclable | 39 | 49 |
| biodegradable | 7 | 7 |
| certification | 53 | 88 |
| named_endorsement | 9 | 14 |
| vegan | 18 | 24 |
| farming_practice | 10 | 11 |
| defined_term | 4 | 4 |
| risk_reduction | 3 | 6 |
| named_comparison | 4 | 5 |
| pollutant_free | 6 | 7 |
| out_of_scope | 209 | 962 |

| category | products |
|---|---|
| acqua-e-bevande | 25 |
| colazione-dolci-e-snack-salati | 42 |
| condimenti-conserve-e-scatolame | 16 |
| cura-persona | 43 |
| gastronomia-salumi-e-formaggi | 35 |
| latte-yogurt-e-uova | 24 |
| pane-pasta-riso-e-farine | 27 |
| parafarmacia | 19 |
| prima-infanzia | 18 |

### Selected 100

- Products: 100. Buckets: hard_yes 35 · in_between 35 · hard_no 30, of which 30 hard_no products have DISCARDED decoy claims.
- Claims: 699. IN_SCOPE 93 · NEEDS_VERIFICATION 100 · DISCARDED 506 · low confidence 75
- Claims by source field: producer_info 384, features 270, certifications 26, description 19
- Macro category: food and drink 69 · personal care and household 31
- Product gray_zone tags: generic_plus_specific 9, natural_footnote 3, farming_vs_heritage 3, endorsement_named_vs_generic 5, risk_vs_performance 6, comparator_vague_vs_named 5, eco_in_health_heritage 3, senza_pollutant_vs_additive 4, split_slogan 2

| trigger | products | claims |
|---|---|---|
| generic_green | 22 | 40 |
| undefined_natural | 17 | 25 |
| climate_neutral | 4 | 5 |
| vague_comparison | 7 | 7 |
| brand_eco_slogan | 6 | 7 |
| vague_supply_chain | 15 | 24 |
| recycled_recyclable | 23 | 31 |
| biodegradable | 5 | 5 |
| certification | 24 | 40 |
| named_endorsement | 8 | 13 |
| vegan | 13 | 17 |
| farming_practice | 8 | 9 |
| defined_term | 3 | 3 |
| risk_reduction | 3 | 6 |
| named_comparison | 3 | 4 |
| pollutant_free | 5 | 6 |
| out_of_scope | 98 | 543 |

| category | products |
|---|---|
| acqua-e-bevande | 11 |
| colazione-dolci-e-snack-salati | 13 |
| condimenti-conserve-e-scatolame | 7 |
| cura-persona | 25 |
| gastronomia-salumi-e-formaggi | 7 |
| latte-yogurt-e-uova | 14 |
| pane-pasta-riso-e-farine | 8 |
| parafarmacia | 5 |
| prima-infanzia | 10 |

Retailer (selected): Coop 100 (100%), all from one source file.

Brands (selected, 96 named + 1 unbranded, max 2 per brand): Granarolo 2, Nivea 2, Pantene Pro-V 2, Actimel 1, Alce Nero 1, Alpro 1, BERNARD JARNOUX 1, Bonomelli 1, Brescia 1, Brimi 1, Bìobì 1, Carnini 1, Chicco 1, Chilly 1, Citterio 1, Colgate 1, Coop 1, Curasept 1, Céréal 1, Energade 1, Equilibra 1, Fabbri 1, Fattorie Osella 1, Fior di Riso 1, Fiordovo 1, Fiorentini 1, Francesco Capetta 1, Frantoio Anfosso Davide & Figli 1, Fratelli Beretta 1, FuzeTea 1, Gallo 1, Garnier 1, Geomar 1, Glysolid 1, Hawaiian Tropic 1, Head & Shoulders 1, HiPP Biologico 1, Huggies 1, Kaloderma 1, Kativa 1, Knorr 1, Kukident 1, L'Angelica 1, L'Oréal Paris 1, La Fiammante 1, Labello 1, Laboratoires Vitarmonyl 1, Latteria Soresina 1, Le Farine Magiche 1, Lenti 1, Lete 1, Libera Terra 1, Loacker 1, Matt 1, Mellin 1, Mentadent 1, Merano 1, Mezzacorona 1, Milk 1, Molino Spadoni 1, Montello 1, Mukki 1, Mulino Bianco 1, Mustela 1, Nesquik 1, Nobili Principato di Puglia 1, Nonno Nanni 1, Nuvenia 1, Olitalia 1, PANEANGELI 1, PROBIOS 1, Palette 1, Palmolive 1, Pampers 1, Parmalat 1, Pasta del Capitano 1, Plasmon 1, Pompadour 1, Ricola 1, Rigoni di Asiago 1, Rio Mare 1, San Carlo 1, Santàl 1, Satin Care 1, Sauber 1, Sensodyne 1, Silver Care 1, Star 1, Twinings 1, Uliveto 1, Vincenzi 1, Viva la Mamma 1, Yoga 1, Zucchi 1, Zuegg 1, acquafarina 1, unbranded 1

## Targets and shortfalls

| target | status | actual |
|---|---|---|
| hard_yes 35 · in_between 35 · hard_no 30 | met | 35 / 35 / 30 |
| ≥ 20 hard_no with DISCARDED decoys | met | 30 |
| ≤ 3 products per brand | met | max 2 ("unbranded" not counted as a brand) |
| ≤ 40% from one retailer or source file | **NOT MET** | 100% Coop. The input is one retailer in one file, so this cap cannot be met. |
| ≥ 25 personal care / household | met | 31 |
| ≥ 40 food and drink | met | 69 |
| ≥ 60 IN_SCOPE claims | met | 93 |
| ≥ 40 NEEDS_VERIFICATION claims | met | 100 |
| ≥ 60 DISCARDED claims | met | 506 |
| trigger generic_green in ≥ 3 products | met | 22 |
| trigger undefined_natural in ≥ 3 products | met | 17 |
| trigger climate_neutral in ≥ 3 products | met | 4 |
| trigger vague_comparison in ≥ 3 products | met | 7 |
| trigger brand_eco_slogan in ≥ 3 products | met | 6 |
| trigger vague_supply_chain in ≥ 3 products | met | 15 |
| trigger recycled_recyclable in ≥ 3 products | met | 23 |
| trigger biodegradable in ≥ 3 products | met | 5 |
| trigger certification in ≥ 3 products | met | 24 |
| trigger named_endorsement in ≥ 3 products | met | 8 |
| trigger vegan in ≥ 3 products | met | 13 |
| trigger farming_practice in ≥ 3 products | met | 8 |
| trigger defined_term in ≥ 3 products | met | 3 |
| trigger risk_reduction in ≥ 3 products | met | 3 |
| trigger named_comparison in ≥ 3 products | met | 3 |
| trigger pollutant_free in ≥ 3 products | met | 5 |
| trigger out_of_scope in ≥ 3 products | met | 98 |

No product was relabelled to fit a quota.

## Selection method

The selection uses the same greedy pass as the Carrefour set, with `random.seed(42)`:

1. Triggers, rarest first, until each appears in 3 selected products.
2. Gray zones, rarest first, until each has 3 products.
3. hard_no products that have decoys, up to 24.
4. Fill in_between, then hard_yes, then hard_no, up to their targets.
5. If a bucket ran out, fill the rest of the 100 from the other buckets (hard_no first, then in_between, then hard_yes).

The brand cap of 3 is never relaxed. The score rewards rare triggers, personal care / household products while that group is under 25, the claim-label mix and hard_no decoys. It penalises repeated brands.

## Bucket rules as applied

- **hard_yes**: at least one IN_SCOPE or NEEDS_VERIFICATION claim, and none of those claims sits on a gray zone.
- **in_between**: at least one IN_SCOPE or NEEDS_VERIFICATION claim sits on a gray zone. The product `gray_zone` is that claim's zone; if there are several, the rarest zone is used.
- **hard_no**: no IN_SCOPE or NEEDS_VERIFICATION claim. A hard_no product can carry a `gray_zone` when a DISCARDED decoy sits on one.

The claim-level gray zone is written at the start of `note` («Gray zone: …»).

## Why each reserve product was left out

| idx | brand | name | bucket | reason |
|---|---|---|---|---|
| 1 | Pompadour | Tisana digestiva plus con finocchio e camomilla | in_between | in_between target (35) filled by higher-scoring products; its triggers (biodegradable, certification, climate_neutral, generic_green, pollutant_free, recycled_recyclable, vegan) are already covered by ≥ 3 selected products; brand already selected (1) |
| 2 | PRETI | Pandolce antico | hard_no | hard_no target (30) filled by higher-scoring products |
| 3 | Rigoni di Asiago | Confettura di pesche gialle natù no zuccheri aggiu | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, named_endorsement, undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 5 | Coop | Tavoletta cioccolato extra fondente 70% | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (1) |
| 6 | Coop | Miele di castagno | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 7 | Biscottificio Grondona | Pasticcini lunette | hard_no | hard_no target (30) filled by higher-scoring products |
| 11 | Coop | Tavoletta cioccolato extra fondente | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (1) |
| 13 | Eat Natural | Barretta morbida fetta alla frutta arachidi | in_between | in_between target (35) filled by higher-scoring products; its triggers (defined_term) are already covered by ≥ 3 selected products |
| 14 | Elah | Preparato per crema al cioccolato | hard_no | hard_no target (30) filled by higher-scoring products |
| 15 | La Sfoglia Della Nonna | Vol au vent | hard_no | hard_no target (30) filled by higher-scoring products |
| 16 | Orlando Grondona | Pandolce antica genova | in_between | in_between target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 20 | Coop | Wafer con crema alla nocciola | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 21 | Pick Up! | Biscotti con tavoletta cioccolato pick up mini x12 | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 22 | Pernigotti | Cioccolatini gianduiotto nero | hard_no | hard_no target (30) filled by higher-scoring products |
| 23 | Coop | Cialde caffè espresso bar | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 24 | Misura | Biscotti dolcesenza allo yogurt | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products |
| 25 | Saila | Caramelle alla liquirizia purissima | hard_no | hard_no target (30) filled by higher-scoring products |
| 26 | Mautino | Torta alla mela | hard_no | hard_no target (30) filled by higher-scoring products |
| 28 | Frisk | Caramelle peppermint | hard_no | hard_no target (30) filled by higher-scoring products |
| 30 | Coop | Confettura di ciliegia di vignola igp | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 31 | F.lli Rebecchi Valtrebbia | Decorazioni gel per dolci rosso | hard_no | hard_no target (30) filled by higher-scoring products |
| 32 | Haribo | Caramelle gommose liquirizia kimono | hard_no | hard_no target (30) filled by higher-scoring products |
| 33 | Misura | Fette biscottate proteiche | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products |
| 34 | Farmo | Muffin choco | hard_no | hard_no target (30) filled by higher-scoring products |
| 37 | Garnier | Colorazione capelli permanente 5.3 castano dorato | in_between | in_between target (35) filled by higher-scoring products; its triggers (undefined_natural, vague_comparison, vegan) are already covered by ≥ 3 selected products; brand already selected (1) |
| 40 | Nivea | Siero anti macchie luminosità | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (2) |
| 41 | Coop | Shampoo per capelli spenti delicato illuminante | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 42 | Coop | Sapone liquido idratante ricarica | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, generic_green, undefined_natural, vague_comparison) are already covered by ≥ 3 selected products; brand already selected (1) |
| 45 | Equilibra | Corpo crema idratante 48h rosa ialuronica | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 47 | Coop | Olio detergente struccante per pelli mature | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 49 | Vape | Dopopuntura penna gel derm herbal | hard_no | hard_no target (30) filled by higher-scoring products |
| 50 | Pampers | Salviettine igieniche baby fresh x70 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 54 | Garnier | Solare viso fluido anti imperfezioni niacinamide s | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 59 | Garnier | Maschera tessuto patch occhi vitamina c | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (biodegradable, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 60 | Coop | Dentifricio con microgranuli | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 66 | Coop | Assorbenti normali ripiegati x12 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 70 | Lines | Assorbenti lunghi con ali a incastro x88 | hard_no | hard_no target (30) filled by higher-scoring products |
| 73 | Coop | Asiago fresco DOP | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 74 | Coop | Parmigiano reggiano DOP 20 mesi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 79 | Fratelli Beretta | Pancetta affumicata a fette | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 80 | Fratelli Beretta | Salamini con bresaola | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 81 | Rovagnati | Prosciutto cotto snello grancotto | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_comparison, recycled_recyclable) are already covered by ≥ 3 selected products |
| 83 | Viva la Mamma | Noodles di pollo e verdure | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 84 | Citterio | Prosciutto toscano dop taglio fresco | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 85 | Coop | Seitan alla piastra | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, vegan) are already covered by ≥ 3 selected products; brand already selected (1) |
| 86 | Granarolo | Formaggio grattugiato italiano | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 87 | Coop | Burrata burratina senza lattosio | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 88 | Coop | Feta DOP | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 89 | Artigiani di Bottega | Capocollo di martina franca | hard_no | hard_no target (30) filled by higher-scoring products |
| 90 | Caseificio Pezzana | Tomini aromatici | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable, vague_comparison) are already covered by ≥ 3 selected products |
| 91 | Coop | Gorgonzola DOP dolce al cucchiaio | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 93 | unbranded | Olive verdi dolci greche | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 94 | unbranded | Caciocavallo silano DOP | hard_no | hard_no target (30) filled by higher-scoring products |
| 95 | de Angelis | Pasta sfoglia rotonda arrotolata | hard_no | hard_no target (30) filled by higher-scoring products |
| 96 | SAN MICHELE | Prosciutto crudo val del cinghio disossato | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 97 | Oro Latini | Gorgonzola DOP | hard_no | hard_no target (30) filled by higher-scoring products |
| 101 | Coop | Albume d'uovo | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, farming_practice, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 105 | Centrale del Latte di Torino | Burro | hard_no | hard_no target (30) filled by higher-scoring products |
| 107 | Tapporosso | Latte al cacao x3 | hard_no | hard_no target (30) filled by higher-scoring products |
| 109 | Latteria Soresina | Latte uht intero | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (1) |
| 111 | Bella Vita | Yogurt mango/maracuja bella vita | hard_no | hard_no target (30) filled by higher-scoring products |
| 116 | Fantolino | Uova fresche xl x4 | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 119 | Knorr | Zuppa tradizionale con orzo/farro e legumi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 120 | Coop | Panetti pane di kamut stirati a mano | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 121 | Coop | Grissini integrali | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 123 | Gallo | Riso basmati parboiled | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 124 | Coop | Gallette di grano saraceno | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 125 | LUCCHI & GUASTALLI | Trofie artigianali | hard_no | hard_no target (30) filled by higher-scoring products |
| 128 | Coop | Zuppa campagnola | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 130 | Forno Piero | Crostini speziati | hard_no | hard_no target (30) filled by higher-scoring products |
| 131 | Musso | Riso arborio | hard_no | hard_no target (30) filled by higher-scoring products |
| 133 | FRAGRANZE | Pane a legna arabo | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 134 | Garofalo | Penne mezze ziti rigate n.60 di gragnano igp | hard_no | hard_no target (30) filled by higher-scoring products |
| 136 | Fornai del Gusto | Grissini stirati alla barbabietola | hard_no | hard_no target (30) filled by higher-scoring products |
| 137 | Equilibra | Integratore alimentare sonno&relax gommose x30 | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vegan) are already covered by ≥ 3 selected products; brand already selected (1) |
| 138 | Equilibra | Integratore alimentare per sistema immunitario | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 140 | Equilibra | Integratore alimentare collagene anti aging x14 | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products; brand already selected (1) |
| 141 | Equilibra | Integratore alimentare potassio/magnesio x12 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 142 | Equilibra | Integratore alimentare collagene q10 ialuronico | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 144 | Equilibra | Integratore melatonina x75 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 145 | Equilibra | Integratore biofoltil forte vegicaps x32 | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 146 | Equilibra | Integratore alimentare potassio e magnesio x20 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 148 | Matt | Integratore magnesio | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 149 | Bonomelli | Integratore alimentare immunity pronto da bere | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 153 | Pampers | Pannolini progressi xl tg.6 +16kg x84 | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 154 | Pampers | Pannolini più asciutto tg.6 xl 15-30 kg x34 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 157 | Huggies | Mutandina 10 pyjama pants 4-7 anni maschio | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 158 | Coop | Pastina gemmine | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 159 | Plasmon | Pasta mini pennette | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, recycled_recyclable, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (1) |
| 163 | Infiore | Guaina per gestante inferiore tg.5 | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 165 | Alce Nero | Omogeneizzato legumi e verdure | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 167 | Yoga | Succo ace optimum | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, recycled_recyclable, vague_comparison) are already covered by ≥ 3 selected products; brand already selected (1) |
| 168 | Coop | Succo nettare alla pesca | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand already selected (1) |
| 170 | BOCCHINO | Grappa tradizione barricata | hard_no | hard_no target (30) filled by higher-scoring products |
| 174 | Civ&Civ | Vino rosso lambrusco di castelvetro DOC amabile | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, generic_green) are already covered by ≥ 3 selected products |
| 175 | Pasqua | Vino rosso amarone della valpolicella DOCG | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green) are already covered by ≥ 3 selected products |
| 176 | Monster | Bevanda energetica energy drink punch pacific | hard_no | hard_no target (30) filled by higher-scoring products |
| 180 | Coop | Frullato di mela 100% frutta | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 182 | Coop | Bevanda di frutta pesca e mango | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 183 | Pellegrino | Vino liquoroso moscato igt | hard_no | hard_no target (30) filled by higher-scoring products |
| 186 | Casaceto | Aceto bianco di alcol | in_between | in_between target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 190 | Coop | Fagioli borlotti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 191 | Montello | Fagioli corona giganti lessati | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vegan) are already covered by ≥ 3 selected products; brand already selected (1) |
| 194 | Coop | Funghi trifolati in olio girasole | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 195 | Zarotti | Alici filetti | hard_no | hard_no target (30) filled by higher-scoring products |
| 198 | SANTAGATA | Olio extravergine d'oliva | hard_no | hard_no target (30) filled by higher-scoring products |
| 199 | Coop | Pomodori secchi con pecorino sardo DOP | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 201 | unbranded | Biscotti krumiri | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 202 | unbranded | Torta sacher | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 203 | unbranded | Torta alla gianduia | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 204 | Gecchele | Pasticcini sigari e ventagli | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 205 | unbranded | Pastiera napoletana | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 207 | elison | Elastici per capelli fascia chic hair stylist | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 208 | Franck Provost | Pinza per capelli moda modello grande | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 209 | elison | Cuffia doccia gabbiano | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 210 | RIMMEL | Mascara wonderluxe 001 nero | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 211 | BIONSEN | Bagnodoccia dermo idratante | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 212 | Gusto Qui | Paella | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 213 | unbranded | Ricotta | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 214 | VAL D'AVETO | Formaggio morbidezza san ste | hard_no | hard_no target (30) filled by higher-scoring products |
| 215 | unbranded | Fontina DOP | hard_no | hard_no target (30) filled by higher-scoring products |
| 216 | unbranded | Formaggio montasio DOP oltre 90 giorni | hard_no | hard_no target (30) filled by higher-scoring products |
| 217 | Neogal | Yogurt greco intero 10% grassi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 218 | Bassi | Gorgonzola dop | hard_no | hard_no target (30) filled by higher-scoring products |
| 219 | SENFTER | Speck di montagna | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 220 | DEL ZOPPO | Bresaola equina | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 221 | FANTOLINO | Uova sfuse allevamento a terra x4 | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 223 | Lactis | Panna fresca | hard_no | hard_no target (30) filled by higher-scoring products |
| 224 | Valli Genovesi | Burro | hard_no | hard_no target (30) filled by higher-scoring products |
| 226 | alplí | Yogurt da bere alla banana | hard_no | hard_no target (30) filled by higher-scoring products |
| 227 | unbranded | Pane pagnotta | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 228 | Luna blu | Fusilli | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 229 | CURTIRISO | CURTIRISO RISO LUNGO B 5 KG | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 230 | unbranded | Pizza wurstel | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 231 | Riso Ceriotti | Riso carnaroli | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 232 | unbranded | Focaccia romana | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 233 | Alemanni | Grissini | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 234 | Coop | Sciroppo balsamico | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 235 | unbranded | Strisce reattive per misurazione glicemica x25 | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 236 | Matt | Integratore alimentare difesa vit. C arancia x20 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 238 | Coop | Integratore alimentare stick vitamine d k ossa x20 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 239 | HiPP | Latte per lattanti combiotic | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products |
| 242 | Lagavulin | Whisky single malt 8 yo | hard_no | hard_no target (30) filled by higher-scoring products |
| 243 | CONFINE | Birra bionda doppio malto | hard_no | hard_no target (30) filled by higher-scoring products |
| 244 | Busnel | Cognac calvados pays d'auge fine 40 gradi | hard_no | hard_no target (30) filled by higher-scoring products |
| 245 | Espolón | Tequila blanco | hard_no | hard_no target (30) filled by higher-scoring products |
| 247 | Vialla Raiano | Vino bianco fiano di avellino DOCG | hard_no | hard_no target (30) filled by higher-scoring products |
| 248 | Perelli | Zafferano 4 buste | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 249 | Casale dei pozzi | Ragù di maremmana | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |

## Judgment calls (every low-confidence claim)

| set | idx | claim | triggers → label | reasoning |
|---|---|---|---|---|
| 100 | 0 | «50% di zenzero» | out_of_scope → DISCARDED | Ingredient percentage used as a selling bullet; treated as out-of-scope quality claim. |
| 100 | 0 | «Imballi certificati FSC per salvaguardare le foreste» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. FSC certification plus a generic forest-protection benefit phrase; generic part treated as generic_green. |
| 100 | 0 | «Filo in puro cotone» | out_of_scope → DISCARDED | Material-quality bullet inside a sustainability list; no environmental wording. |
| 100 | 0 | «Scritta in Braille» | out_of_scope → DISCARDED | Accessibility feature, not environmental. |
| 100 | 8 | «100% Elettrica rinnovabile» | generic_green → IN_SCOPE | Renewable-energy claim: project convention generic_green, low. |
| 100 | 8 | «Le chips 1936 sono prodotte con energia elettrica proveniente esclusivamente da fonti rinnovabili.» | generic_green → IN_SCOPE | Renewable-energy claim: project convention generic_green, low. |
| 100 | 9 | «65% di Grassi in Meno* ... *Rispetto alla media degli snack analoghi più venduti (fonte IRI vedi www.fiorentinialimentari.it)» | out_of_scope → DISCARDED | Nutritional comparison with a named source; comparison triggers are for environmental claims, so out_of_scope. |
| 100 | 12 | «Miele Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade claim with no named scheme; treated like an unnamed ethical certification. |
| 100 | 27 | «-50% di grassi saturi* ... *Rispetto alla media dei frollini più venduti. Fonte Unione Italiana Food Mercato Italia. Per maggiori informa…» | out_of_scope → DISCARDED | Nutritional comparison with a named source; comparison triggers are for environmental claims, so out_of_scope. |
| 100 | 29 | «FETTE BISCOTTATE SENZA SALE senza zuccheri aggiunti» | out_of_scope → DISCARDED | Line mixes the sales name with free-from claims. |
| 100 | 35 | «0% Allergeni comuni* - Profumi - Coloranti» | out_of_scope → DISCARDED | Footnote body is in producer_info, not features, so no footnote attached here. |
| 100 | 35 | «Il nostro obiettivo è ridurre l'impronta di carbonio dei nostri articoli per l'igiene intima femminile del 30% entro il 2030 con prodotti…» | generic_green, vague_comparison, recycled_recyclable → IN_SCOPE | Gray zone: generic_plus_specific. Future carbon-reduction commitment with no baseline plus generic 'sostenibili'; no trigger for future performance. |
| 100 | 35 | «Energia rinnovabile certificata» | generic_green, certification → IN_SCOPE | Renewable-energy claim: project convention generic_green, low. Unnamed 'certificata' added as certification. |
| 100 | 36 | «Burro di karité & oli naturali arricchiti con vitamine» | undefined_natural, out_of_scope → IN_SCOPE | 'oli naturali' is an ingredient descriptor, read as an undefined natural attribute. |
| 100 | 36 | «Con burro di karité da coltivazione etiche* ... *Commercio equo e solidale degli agricoltori dell'Africa Occidentale» | vague_supply_chain, certification → IN_SCOPE | 'coltivazione etiche' is vague; footnote claims fair trade with no named scheme. |
| 100 | 36 | «Senza oli minerali» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Mineral oils read as a cosmetic ingredient (additive side), not a pollutant. |
| 100 | 38 | «45% di plastica in meno ⏎ Rispetto al kit precedente» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Comparison and its comparator sit on two consecutive lines; kept as one claim with the line break. |
| 100 | 39 | «Fino a 100% protezione dalla forfora* ... **con uso regolare, forfora visibile eliminata al 100% in 66 casi su 100 (test clinico)» | out_of_scope → DISCARDED | Marker is '*' but the matching clinical note is labelled '**' in the text; attached the '**' note as the intended body. |
| 100 | 43 | «L'utente sperimenta un significativo aumento del comfort orale, riducendo l'attrito e l'irritazione causati dal movimento della protesi, …» | out_of_scope → DISCARDED | Gray zone: risk_vs_performance. Performance claim phrased close to irritation reduction, but no explicit 'rischio' wording. |
| 100 | 43 | «Inoltre, la stabilità offerta dalla crema riduce il rischio di movimenti imprevisti della dentiera, migliorando la fiducia in sé stessi e…» | risk_reduction → NEEDS_VERIFICATION | Gray zone: risk_vs_performance. Explicit 'riduce il rischio' wording, but the risk is denture movement (product performance), not a health/environmental risk. |
| 100 | 44 | «I minerali di origine naturale aiutano a rimuovere le macchie superficiali per Denti Bianchi a Lungo*** ... ***Clinicamente provato su 58…» | undefined_natural, out_of_scope → IN_SCOPE | 'minerali di origine naturale' is an undefined natural attribute inside a whitening performance claim. |
| 100 | 44 | «L'A.N.D.I. riconosce che un dentifricio al fluoro aiuta a prevenire la formazione della placca proteggendo la salute di denti e gengive.» | named_endorsement, out_of_scope → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Named body's statement about fluoride toothpaste in general; endorsement in a health context. |
| 100 | 44 | «Mentadent White Now soddisfa questi requisiti ed è quindi di significativa utilità, unito ad una sostituzione regolare dello spazzolino e…» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Continuation of the ANDI recognition; the endorsement is implicit in this sentence. |
| 100 | 51 | «Manico realizzato con plastica di origine biologica» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based plastic in the product handle; mapped to recycled_recyclable per the bio-based packaging convention, though this is the product itself. |
| 100 | 61 | «Senza olio minerale» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Mineral oil (petrolatum-type) free-from in a cosmetic; read as ingredient/additive rather than pollutant. |
| 100 | 61 | «Testato dell'Istituto Svizzero della Vitamina» | out_of_scope → DISCARDED | Test by a named institute; treated as a test claim (out_of_scope), not a named endorsement. |
| 100 | 64 | «Il balsamo Contiene Olio d'Argan nutriente e prodotto secondo i principi del commercio equo e solidale, noto per rendere i capelli morbid…» | vague_supply_chain, out_of_scope → IN_SCOPE | Fair-trade sourcing asserted ('secondo i principi del commercio equo e solidale') with no named scheme; treated as vague supply-chain rather than certification. |
| 100 | 67 | «Senza olio minerale» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Mineral oil (petrolatum-type) free-from in a cosmetic; read as ingredient/additive rather than pollutant. |
| 100 | 67 | «Testato dell'Istituto Svizzero della Vitamina» | out_of_scope → DISCARDED | Test by a named institute; treated as a test claim (out_of_scope), not a named endorsement. |
| 100 | 71 | «Propoli - Dalle molteplici proprietà naturali, aiuta a ridurre la fermentazione batterica, contribuendo a una migliore Igiene Orale.» | out_of_scope → DISCARDED | 'proprietà naturali' describes the propolis ingredient, not the product; kept out_of_scope (oral-hygiene performance). |
| 100 | 71 | «Pasta Del Capitano Spray Fresco Antialitosi Fresco Spray Antialitosi con una formula che svolge un’azione antibatterica naturale grazie a…» | undefined_natural, out_of_scope → IN_SCOPE | 'azione antibatterica naturale' attributes a natural character to the product's action without definition; could also be read as describing the propolis only. |
| 100 | 72 | «Bio-active complex H.A.F.» | out_of_scope → DISCARDED | 'Bio-active' is a technical ingredient name, not an organic claim. |
| 100 | 76 | «Dal latte fieno STG, la bontà Brimi.» | out_of_scope → DISCARDED | 'Latte fieno STG' is an EU traditional-speciality scheme that implies hay-feeding rules; treated as a quality scheme (like DOP) rather than a farming-practice claim. |
| 100 | 92 | «Cottura lenta materie prime selezionate» | vague_supply_chain, out_of_scope → IN_SCOPE | 'materie prime selezionate' is close to 'ingredienti selezionati' (vague supply chain) but may be read as plain quality puffery. |
| 100 | 92 | «No ingredienti OGM» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Non-GMO ingredients (not a feed/farming context); kept out_of_scope. |
| 100 | 99 | «Questo latte nasce qui, in Toscana, da allevamenti prevalentemente piccoli e a conduzione familiare dove le mucche rappresentato il bene …» | vague_supply_chain, out_of_scope → IN_SCOPE | Small family farms asserted as a quality/ethics point without verifiable practice; borderline between origin story and vague supply-chain claim. |
| 100 | 99 | «Tutto è controllato nei dettagli, delle condizioni ambientali, agli spazi e giacigli, fino alla cura dell'igiene e dell'alimentazione.» | vague_supply_chain → IN_SCOPE | 'Tutto è controllato' is a controlled-supply-chain assertion; partly backed by the ClassyFarm certification named in the preceding sentence. |
| 100 | 99 | «Il tappo e la plastica sono ricavati dalla canna da zucchero, una risorsa che opportunamente gestita ricresce all'infinito.» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based (sugarcane) packaging; recycled_recyclable per project convention. |
| 100 | 99 | «La carta utilizzata è certificata e proviene da foreste gestite nel rispetto di rigorosi standard ambientali sociali ed economici.» | certification → NEEDS_VERIFICATION | Unnamed forest certification (FSC-type wording); no certifier named. |
| 100 | 102 | «Questo yogurt viene prodotto nella nostra azienda agricola situata nel cuore delle colline Ovadesi, dove, a ciclo chiuso, coltiviamo la t…» | farming_practice, out_of_scope → NEEDS_VERIFICATION | 'a ciclo chiuso' closed-cycle farming is a farming practice but only loosely specified; also origin prose. |
| 100 | 103 | «Latte Fieno» | out_of_scope → DISCARDED | Hay-milk (STG scheme) term as a standalone selling line; treated as a quality scheme like DOP, though it implies feeding rules. |
| 100 | 104 | «#Bontàresponsabile» | brand_eco_slogan → IN_SCOPE | Brand CSR programme hashtag; 'responsabile' only implicitly environmental here. |
| 100 | 104 | «Questo è uno dei progetti che compongono #Bontà Responsabile, il nostro impegno per un futuro più buono.» | brand_eco_slogan → IN_SCOPE | CSR programme slogan with vague 'impegno per un futuro più buono'; environmental sense inferred from the packaging context. |
| 100 | 104 | «Questa confezione è composta per l'88% da materie prime rinnovabili ⏎ perché tappo e strati protettivi sono fatti con plastica provenient…» | recycled_recyclable → NEEDS_VERIFICATION | Renewable/bio-based (sugarcane) packaging share; recycled_recyclable per bio-based packaging convention. Review: sentence continues past the line break; extended to the full sentence. |
| 100 | 104 | «-18% di CO2eq verso la stessa confezione fatta con materiali convenzionali.» | named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparator is stated ('stessa confezione con materiali convenzionali') but not a named product or source; could be vague_comparison. |
| 100 | 104 | «Mentre cresce la canna da zucchero assorbe CO2eq; la produzione della plastica da canna da zucchero emette meno CO2eq rispetto a quella d…» | recycled_recyclable, named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Bio-based plastic CO2 comparison against fossil plastic in general; comparator stated but generic. |
| 100 | 106 | «Vegetale con fermenti vivi» | vegan, out_of_scope → NEEDS_VERIFICATION | 'Vegetale' (plant-based) is close to '100% vegetale' but not explicit; paired with a live-cultures health point. |
| 100 | 108 | «Cacao e zucchero di canna altromercato» | certification → NEEDS_VERIFICATION | Altromercato is a named fair-trade organisation; treated as certification by analogy with Fairtrade. |
| 100 | 108 | «Una combinazione unica di cacao e zucchero di canna provenienti da produttori equo solidali altromercato» | certification, out_of_scope → NEEDS_VERIFICATION | Named fair-trade organisation (Altromercato) treated as certification. |
| 100 | 113 | «Questo latte proviene esclusivamente da mucche selezionate e controllate negli allevamenti della nostra filiera, che hanno conservato il …» | vague_supply_chain, out_of_scope → IN_SCOPE | Gray zone: farming_vs_heritage. Selected/controlled herds in 'our supply chain' = vague supply chain; framed as heritage genetics ('mucche di un tempo'). |
| 100 | 115 | «Benessere animale» | vague_supply_chain → IN_SCOPE | Animal-welfare assertion with no named scheme (project convention: vague_supply_chain, low). |
| 100 | 115 | «Filiera certificata» | vague_supply_chain, certification → IN_SCOPE | Unnamed 'certified' supply chain: vague supply-chain assertion plus unnamed certification. |
| 100 | 118 | «La Carta del Mulino è il nostro disciplinare per la coltivazione sostenibile del grano tenero redatto insieme al WWF.» | generic_green, named_endorsement → IN_SCOPE | Own sustainability charter co-written with WWF: generic 'sostenibile' plus a named NGO partner (closest to named_endorsement). |
| 100 | 126 | «Dedicata a tutti coloro che onorano il ricordo delle vittime delle mafie attraverso il proprio impegno quotidiano.» | out_of_scope → DISCARDED | Social/anti-mafia ethical message, not environmental; kept as an out-of-scope selling line. |
| 100 | 129 | «Ecologico! ⏎ Un sacchetto di carta facilmente richiudibile come tradizione consiglia contiene questa preziosa miscela senza costose ed in…» | generic_green → IN_SCOPE | Gray zone: split_slogan. 'Ecologico!' header kept together with its explanatory line (paper bag, no boxes); the explanation does not substantiate the generic claim. |
| 100 | 135 | «Le castagne scelte per questa farina vengono raccolte manualmente, appena cadute dall'albero o sul punto di farlo, e provengono da boschi…» | out_of_scope → DISCARDED | Hand harvesting and Italian woods origin: a harvesting practice with no environmental framing, treated as quality/origin. |
| 100 | 139 | «Ecoswell» | generic_green → IN_SCOPE | Eco-prefixed name under the sustainability header, apparently the bottle/packaging programme; no content given. |
| 100 | 155 | «Formula vegana & biodegradabile^, senza parabeni, solfati, silicone, talco e microplastiche^^. ... ^99,8% formula biodegradabile» | vegan, biodegradable, pollutant_free, out_of_scope → NEEDS_VERIFICATION | Sentence carries two markers (^ and ^^); only one footnote allowed, so the ^ biodegradability note was attached (^^ = 'secondo la definizione dell'UNEP'). |
| 100 | 156 | «100% Ingredienti controllati rigorosamente ⏎ che soddisfano i nostri elevati standard qualitativi.» | out_of_scope → DISCARDED | Ingredient quality control rather than a supply-chain sustainability assertion; could be read as vague_supply_chain. |
| 100 | 162 | «Caratteristiche: mele biologiche raccolte al giusto grado di maturazione e lavorate fresche.» | certification, out_of_scope → NEEDS_VERIFICATION | Gray zone: eco_in_health_heritage. Organic word embedded in a quality/freshness description sentence. |
| 100 | 162 | «Tipo di coltivazione: nei meleti biologici ogni albero ha più spazio per la crescita e la maturazione dei suoi frutti.» | certification, farming_practice → NEEDS_VERIFICATION | Organic orchards plus a farming-practice claim; 'più spazio' is an implicit comparison with no comparator, but read as practice rather than vague_comparison. |
| 100 | 169 | «Solo aromi naturali» | out_of_scope → DISCARDED | Regulated flavouring term per project convention. |
| 100 | 171 | «La mia confezione è fatta per più dell'80% da materiali vegetali» | recycled_recyclable → NEEDS_VERIFICATION | Plant-sourced packaging mapped to recycled_recyclable per project convention. |
| 100 | 171 | «Il mio Tappo è di Origine Vegetale Derivato dalla Canna da Zucchero ed è ottenuto da un processo di fermentazione, evitando l'utilizzo di…» | recycled_recyclable → NEEDS_VERIFICATION | Sugar-cane bio-based cap mapped to recycled_recyclable per project convention. |
| 100 | 173 | «Raccolto a mano» | out_of_scope → DISCARDED | Hand harvesting read as quality/tradition, not an environmental farming practice. |
| 100 | 177 | «L'acqua ricca di preziosi minerali quali bicarbonati, magnesio e solfati costituisce un aiuto naturale per il miglior svolgimento dei pro…» | out_of_scope → DISCARDED | Gray zone: eco_in_health_heritage. 'aiuto naturale' in a health sentence about natural mineral water; read as a health claim, not an undefined natural product attribute. |
| 100 | 188 | «Azienda con sistema di gestione per la qualità UNI EN ISO 9001:2015 cert. CSQA nº 2; di gestione ambientale UNI EN ISO 14001:2015 cert. C…» | certification, out_of_scope → NEEDS_VERIFICATION | Company management-system certifications (incl. ISO 14001 environmental) with named certifier, not a product-level certification. |
| 100 | 189 | «Bottiglia in plastica 100% riciclata** e riciclabile ... **Da filiera alimentare controllata italiana ⏎ **Escluso tappo ed etichetta» | recycled_recyclable, vague_supply_chain → IN_SCOPE | Two '**' notes follow; both taken as the footnote. 'filiera alimentare controllata' in the note adds vague_supply_chain. |
| 100 | 193 | «100% Italiano - Solo pomodoro fresco - Da filiera corta» | vague_supply_chain, out_of_scope → IN_SCOPE | 'Filiera corta' is explained elsewhere (direct agreements) but not verifiable from the claim itself. |
| 100 | 193 | «Stringiamo accordi diretti con gli agricoltori (filiera corta) e riconosciamo loro il giusto compenso contro ogni sfruttamento della mano…» | vague_supply_chain → IN_SCOPE | Social/fair-pay supply-chain assertion with no named scheme or verification. |
| 100 | 222 | «FIORDOVO ALLEVAMENTO ALL'APERTO X4» | farming_practice → NEEDS_VERIFICATION | Product-name-like line, but 'allevamento all'aperto' is a concrete rearing-practice claim; it also contradicts the listing name ('allevamento a terra'). |
| 100 | 225 | «Bontà Leggera» | out_of_scope → DISCARDED | Likely a product-line name; kept as a short standalone taste/lightness selling line. |
| 100 | 237 | «La Vitamina C contribuisce: ⏎ - alla normale funzione del sistema immunitario ⏎ - alla riduzione della stanchezza e dell'affaticamento ⏎ …» | out_of_scope → DISCARDED | Single health-claim sentence split into bullets; extracted whole because the bullets are not meaningful alone. |
| 100 | 240 | «0% BPA» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. BPA-free leans pollutant per guide, low confidence. |
| 100 | 241 | «senza OGM*» | farming_practice → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. GMO-free fits no rule cleanly; closest is farming_practice (non-OGM). The * markers have no note body in the text. |
| reserve | 1 | «Imballi certificati FSC per salvaguardare le foreste» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. FSC certification plus a generic forest-protection benefit phrase; generic part treated as generic_green. |
| reserve | 1 | «Filo in puro cotone senza graffetta in alluminio» | out_of_scope → DISCARDED | Absence of an aluminium staple may imply a waste benefit but none is stated. |
| reserve | 1 | «Scritta in Braille per aiutare ciechi e ipovedenti» | out_of_scope → DISCARDED | Accessibility feature, not environmental. |
| reserve | 1 | «Conosciuto come uno dei migliori rimedi naturali per sconfiggere il gonfiore addominale e tutti i disturbi che colpiscono la digestione.» | out_of_scope → DISCARDED | Gray zone: eco_in_health_heritage. 'rimedi naturali' describes fennel inside a health claim, not a product-attribute natural claim. |
| reserve | 5 | «Acquistando questa tavoletta di cioccolato contribuisci a sostenere e promuovere lo sviluppo economico e sociale delle comunità in cui op…» | vague_supply_chain → IN_SCOPE | Social/fair-trade sourcing statement without a named scheme; closest is vague_supply_chain. |
| reserve | 6 | «Il miele di castagno vivi verde Coop è ottenuto dal nettare dei fiori di castagno provenienti principalmente dalle regioni italiane più v…» | brand_eco_slogan, out_of_scope → IN_SCOPE | Origin sentence that embeds the Vivi Verde eco line name. |
| reserve | 11 | «I prodotti Solidal Coop rendono concreto il sostegno alle cooperative, alle piccole comunità di produttori e ai lavoratori del Sud del mo…» | certification → NEEDS_VERIFICATION | Solidal is Coop's fair-trade line (project convention: certification, low). |
| reserve | 11 | «Fairtrade significa condizioni commerciali più eque e opportunità, per i produttori dei paesi in via di sviluppo, di investire nelle loro…» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. Named Fairtrade scheme plus 'futuro sostenibile' (social/economic sense, kept as written). |
| reserve | 11 | «Acquistando questa tavoletta di cioccolato contribuisci a sostenere e promuovere lo sviluppo economico e sociale delle comunità in cui op…» | vague_supply_chain → IN_SCOPE | Social/fair-trade sourcing statement without a named scheme; closest is vague_supply_chain. |
| reserve | 11 | «SOLIDAL» | certification → NEEDS_VERIFICATION | Coop's fair-trade product line badge; no third-party scheme named on the listing. |
| reserve | 14 | «Solo aromi naturali» | out_of_scope → DISCARDED | Regulated flavouring term (project convention). |
| reserve | 16 | «Ricette che nel tempo verranno custodite e tramandate grazie al quadernetto delle cose buone, non segrete, ma semplici perché naturali, q…» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'naturali' describes the recipes inside heritage prose; undefined. |
| reserve | 20 | «5 Monoporzioni salvafreschezza» | out_of_scope → DISCARDED | Piece count plus a freshness-preserving pack claim; kept for the 'salvafreschezza' selling point. |
| reserve | 24 | «Farina di tipo 2 da Filiera Italiana» | out_of_scope → DISCARDED | 'Filiera Italiana' is mainly an origin statement; no supply-chain quality wording. |
| reserve | 24 | «Confezione con carta certificata FSC per una gestione responsabile delle foreste» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. FSC certification plus 'gestione responsabile' wording; generic part treated as generic_green. |
| reserve | 33 | «Farina da Filiera Italiana» | out_of_scope → DISCARDED | 'Filiera Italiana' is mainly an origin statement; no supply-chain quality wording. |
| reserve | 33 | «Confezione con carta certificata FSC per una gestione responsabile delle foreste» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. FSC certification plus 'gestione responsabile' wording; generic part treated as generic_green. |
| reserve | 37 | «45% di plastica in meno ⏎ Rispetto al kit precedente» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Comparison and its comparator sit on two consecutive lines; kept as one claim with the line break. |
| reserve | 41 | «Cosmetico Certificato 100% naturale» | undefined_natural, certification → IN_SCOPE | 'Cosmetico Certificato 100% naturale': certified but no certifier or definition given in this line; natural part kept as undefined_natural. |
| reserve | 42 | «Cosmetico Certificato 100% naturale» | undefined_natural, certification → IN_SCOPE | 'Cosmetico Certificato 100% naturale': certified but no certifier or definition given in this line; natural part kept as undefined_natural. |
| reserve | 45 | «0% Petrolati, PEG» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Petrolatum/PEG read as cosmetic ingredients (additive side) rather than pollutants. |
| reserve | 45 | «Utilizzata con regolarità, grazie all'azione degli attivi naturali contenuti in formula, conferisce alla pelle un'idratazione completa (i…» | undefined_natural, out_of_scope → IN_SCOPE | 'attivi naturali' is an undefined natural attribute inside a performance sentence. |
| reserve | 45 | «Senza: parabeni - petrolati - siliconi - PEG» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Petrolatum/PEG read as cosmetic ingredients (additive side) rather than pollutants. |
| reserve | 47 | «Cosmetico Certificato 100% naturale» | undefined_natural, certification → IN_SCOPE | 'Cosmetico Certificato 100% naturale': certified but no certifier or definition given in this line; natural part kept as undefined_natural. |
| reserve | 47 | «Senza oli minerali - siliconi - coloranti e profumi sintetici - PEG - polimeri sintetici - Come previsto dal disciplinare NaTrue» | certification, out_of_scope → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Free-from list tied to the named NaTrue standard; synthetic polymers/mineral oils read as ingredients rather than pollutants. |
| reserve | 59 | «50% Paper-based sachet» | recycled_recyclable → NEEDS_VERIFICATION | Paper-based (plant-sourced) packaging share; mapped to recycled_recyclable per the bio-based packaging convention. |
| reserve | 85 | «Il prodotto non contiene proteine di origine animale» | vegan → NEEDS_VERIFICATION | States absence of animal proteins only (not of all animal ingredients); closest to the vegan trigger. |
| reserve | 86 | «Fatto con latte della nostra filiera» | vague_supply_chain → IN_SCOPE | Own supply chain asserted as a selling point with no verifiable detail; could also be read as neutral origin. |
| reserve | 86 | «Ogni forma è fatta con oltre 400 litri di latte italiano della nostra filiera Granarolo e viene prodotto con metodo tradizionale in calda…» | vague_supply_chain, out_of_scope → IN_SCOPE | 'della nostra filiera' supply-chain assertion inside a heritage/origin sentence. |
| reserve | 87 | «BENE SI'» | out_of_scope → DISCARDED | Coop free-from line badge; composition claim. |
| reserve | 109 | «Solo dal latte delle nostre mucche» | out_of_scope → DISCARDED | Own-herd origin statement; could be read as a vague supply-chain claim. |
| reserve | 109 | «Benessere animale» | vague_supply_chain → IN_SCOPE | Animal welfare asserted with no named scheme (convention for 'Benessere animale garantito'). |
| reserve | 123 | «Grazie al naturale trattamento al vapore, Riso Gallo Blond non scuoce mai e consente una cottura veloce che si adatta a tante modalità di…» | undefined_natural, out_of_scope → IN_SCOPE | 'naturale' qualifies the steam process rather than the product; read as an undefined natural claim inside a performance sentence. |
| reserve | 130 | «Senza olio di palma / senza conservanti aggiunti.» | out_of_scope → DISCARDED | 'Senza olio di palma' can carry an environmental connotation but is not a listed pollutant; treated as free-from. |
| reserve | 131 | «Questo Riso viene coltivato esclusivamente nell'Azienda Agricola Musso e deriva da sementi certificate, questo garantisce che il Caranaro…» | out_of_scope → DISCARDED | 'sementi certificate' refers to seed/variety authenticity, not a sustainability certification. |
| reserve | 137 | «Sonno & Relax Low Sugar Gummies Equilibra è un integratore alimentare in gummies masticabili dall'ottimo sapore fruttato, grazie all'arom…» | out_of_scope → DISCARDED | 'aroma naturale' is the regulated flavouring term (project convention: out_of_scope, low). |
| reserve | 140 | «Collagene Anti-Aging Equilibra contiene solo aromi, coloranti ed edulcoranti di origine naturale.» | undefined_natural → IN_SCOPE | 'di origine naturale' for additives with no definition; close to the regulated 'aromi naturali' convention but extends to colours and sweeteners. |
| reserve | 141 | «Aroma naturale arancia» | out_of_scope → DISCARDED | Regulated flavouring term (project convention: out_of_scope, low). |
| reserve | 159 | «Prodotto in Italia - Con ingredienti italiani - Filiera italiana certificata» | certification, out_of_scope → NEEDS_VERIFICATION | Unnamed 'filiera certificata' is a supply-chain/origin certification with no certifier named; could also be read as vague_supply_chain. |
| reserve | 159 | «Tracciabilità e sicurezza garantite da Oasi nella crescita» | vague_supply_chain → IN_SCOPE | 'Oasi nella crescita' is Plasmon's own programme, not an independent verifiable scheme, so kept as vague supply-chain. |
| reserve | 168 | «Ogni ape conta - Difendiamo la biodiversità» | generic_green, brand_eco_slogan → IN_SCOPE | Coop biodiversity campaign slogan; first-person environmental statement. |
| reserve | 168 | «Brick 86% da materie di origine vegetale» | recycled_recyclable → NEEDS_VERIFICATION | Plant-sourced packaging mapped to recycled_recyclable per project convention. |
| reserve | 186 | «Casaceto è l'aceto bianco di alcol per uso alimentare 100% naturale, ottenuto dalla fermentazione degli zuccheri contenuti in frutta e ce…» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. '100% naturale' followed by a production description (fermentation) that only partially explains it; not treated as a full definition. |
| reserve | 194 | «Un saporito contorno preparato con funghi tagliati a fettine e trifolati secondo la tradizionale ricetta, ottimo da consumare così com'è …» | out_of_scope → DISCARDED | Mostly descriptive sentence; extracted for the 'tradizionale ricetta' heritage element. |
| reserve | 239 | «HiPP Bio Combiotic con fermenti lattici vivi» | certification, out_of_scope → NEEDS_VERIFICATION | Gray zone: eco_in_health_heritage. Brand/product-name line combining 'Bio' with a probiotic health selling point; the following 'Latte per lattanti Bio' line was treated as the legal denomination and not extracted. |

## Validation

`validate2.py` output (final run):

```
[coop] selected 100 reserve 149 unusable 1 total 250 of 250
[coop] claims checked 1219; buckets {'in_between': 35, 'hard_yes': 35, 'hard_no': 30}; max per named brand ('Pantene Pro-V', 2); unbranded selected 1
[coop] retailer share 100% Coop (40% cap not achievable: single-retailer file)
[coop] FAILURES: 0
```

Checks: exactly 100 selected; selected + reserve + unusable = file size; every claim_text part and footnote is an exact substring of its `source_field` (or exactly one element of `certifications`); every label equals the label derived from its triggers; bucket consistency; no duplicate non-null EAN or brand + name; brand cap respected.

Review: Two reviewers checked the 100 selected products and found 1 boundary error (idx 104: a sentence continued past a line break) and 1 missed named endorsement (idx 189). Both were fixed. The reserve did not get this second review.