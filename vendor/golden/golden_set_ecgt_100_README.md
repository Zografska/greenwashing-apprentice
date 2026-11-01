# ECGT gold set — 100 Carrefour Italy products

Gold evaluation set for a detector of claims under the EU ECGT rules (Directive 2024/825), built from `clean/carrefour.json`. Every claim is copied verbatim from the source `description`, and each label is derived mechanically from its triggers (only out_of_scope → DISCARDED; any group-A trigger → IN_SCOPE; otherwise group B → NEEDS_VERIFICATION; defined_term cancels undefined_natural). Existing annotation fields: none were present in this file, so nothing could have been copied.

Files: `golden_set_ecgt_100.json` (the 100 selected products), `golden_set_ecgt_reserve.json` (the other 174 usable products, labelled the same way), and this README.

## Amendments (2026-10-03, review of unannotated lines)

The counts further down are from the original build and are **not** updated. After these amendments
the selected 100 have: hard_yes 37 · in_between 35 · hard_no 28; 288 IN_SCOPE / NEEDS_VERIFICATION claims
(IN_SCOPE 179 · NEEDS_VERIFICATION 109); 489 DISCARDED, of which 1 is `needs_review`.

| EAN | product | change |
|---|---|---|
| 8022966510104 | Maniva Acqua Oligominerale | added «Non sprecare, ricicla.\nÈ per il bene del nostro pianeta.» → generic_green, IN_SCOPE (merged 2-unit span; «È» continues the previous line). hard_no → hard_yes |
| 8002200163136 | Kimbo Macinato Fresco | added «Cialde compostabili» → biodegradable, NV. hard_no → hard_yes |
| 8017331105108 | L'Angelica Senna e Carvi | added «A Villa Angelica: il cuore della natura» → out_of_scope, DISCARDED, `needs_review: true` (place storytelling, close to origin; no impact element). Exclude from scoring until reviewed |

Two conventions settled in the same review (apply to the reserve set and all future labelling):

- **Headings are never claims on their own.** A heading over disposal instructions («Per l'ambiente»,
  «Rispetta l'ambiente», «La nostra confezione e l'ambiente» followed by «Come smaltire:» / material
  codes) is dropped with them. A heading followed by an actual claim: label the claim, the heading is
  out_of_scope.
- **Recycling calls-to-action: the benefit clause decides.** A bare call-to-action («Riciclami!»,
  «Ricicla con Plasmon», «Pensa a riciclare») is out_of_scope. One that adds an environmental-benefit
  clause («per il pianeta», «per il bene del nostro pianeta») is generic_green → IN_SCOPE. This matches
  the anchor «Fai la differenziata per il pianeta».

- **Brand eco-slogans are exempt from the heading rule**: «Fiorentini per l'ambiente», «Latteria
  Soresina per l'ambiente» stay brand_eco_slogan claims even directly above a disposal block.

Reserve set, same day: «Rispettiamo l'ambiente» (cameo le Soffici Margherita, 8003000616105) relabelled
out_of_scope as a bare heading over the disposal block; that product moves hard_yes → hard_no.

A claim may carry `needs_review: true`: its label is provisional and evaluators must skip it.

## Pool size

The brief expected a pool of 150 records. `clean/carrefour.json` actually holds **300** records, so the accounting below is: 100 selected + 174 reserve + 26 unusable = 300.

## Field mapping (Carrefour)

| Output field | Source |
|---|---|
| product_id | `product_id` |
| ean | `ean` |
| name | `name` |
| category | `origin_file` (Carrefour aisle slug) |
| source_file | constant `clean/carrefour.json` |
| source_index | position in the JSON array |
| retailer | constant `Carrefour` |
| brand | derived from `name` and text (Carrefour private lines kept as written, e.g. "Carrefour Bio", "Simpl"; Milk / Milk Pro / Brescia merged as "Centrale del Latte di Brescia") |
| claims[].source_field | always `description`: the only text field. Carrefour folds features, producer info, certifications and lifestyle badges into it. |
| url | not used |

The file has no separate `recycling` field. Carrefour appends a packaging-disposal block to `description`, with lines such as «Bottiglia Plastica - Largamente riciclabile», «Confezione - PAP 21 - Raccolta carta» and «Verifica le disposizioni del tuo Comune». That block is treated as the `recycling` field and never extracted. Structured lines starting «Origine Altro Testo …» or «Luogo di provenienza …» are the retailer's origin fields, so they are not extracted either. The label «Metodo di Pesca» is dropped in front of fishing-method text. The product object also carries a product-level `triggers` list (the union of its claims' triggers), as the brief asked. The claim-level gray zone is recorded at the start of `note` («Gray zone: …»).

## Unusable records

26 records were set aside. Duplicates: none. All 300 EANs are unique and there is no repeated brand + name.

| idx | EAN | name | reason |
|---|---|---|---|
| 15 | 8012666060764 | Acqua frizzante 6 bottiglie 1,5L | description only repeats the product name (no marketing text) |
| 53 | 8005228092112 | Primitivo IGT Nostre Terre | description only repeats the product name (no marketing text) |
| 56 | 8000128060476 | Riesling DOC La Calenzana | description only repeats the product name (no marketing text) |
| 58 | 8000128060858 | Passerina IGT La Calenzana | description only repeats the product name (no marketing text) |
| 65 | 2100409000000 | Fesa di Tacchino a Fette x 4 | description only repeats the product name (no marketing text) |
| 67 | 8021580001401 | Hamburger Maxi della Maremma 200 g | description only repeats the product name (no marketing text) |
| 142 | 2084435000000 | Arrosto di Tacchino | description only repeats the product name (no marketing text) |
| 143 | 8030654000646 | Passatelli 250 gr | description only repeats the product name (no marketing text) |
| 158 | 4009044271342 | Borsa Shopper Surgelati Termica | empty description |
| 160 | 2583910000000 | Polpo eviscerato congelato | description only repeats the product name (no marketing text) |
| 161 | 8001186040028 | Code di gamberi argentini surgelate | description only repeats the product name (no marketing text) |
| 178 | 8026495512776 | Demi Baguette | description only repeats the product name (no marketing text) |
| 179 | 8006287868519 | Freselle Bianche | description only repeats the product name (no marketing text) |
| 181 | 8003890851716 | Filone Integrale Bio | description only repeats the product name (no marketing text) |
| 182 | 8006287868526 | Freselle Integrali | description only repeats the product name (no marketing text) |
| 217 | 8019500002218 | Polpa di riccio di mare 55g | description only repeats the product name (no marketing text) |
| 218 | 2126540000000 | Filetto di Merluzzo | description only repeats the product name (no marketing text) |
| 219 | 8032649651659 | Saku Tonno Marinato | description only repeats the product name (no marketing text) |
| 220 | 8032649655077 | Tartare di Pesce Spada Marinato | description only repeats the product name (no marketing text) |
| 221 | 8032649651390 | Pesce Spada Affumicato | empty description |
| 237 | 8412497131310 | Stor set piatto per bambini Disney Baby | empty description |
| 255 | 8010012001546 | Burrata di Bufala x2 | description only repeats the product name (no marketing text) |
| 256 | 2120564000000 | Salsa Tzatziki | description only repeats the product name (no marketing text) |
| 257 | 2415014000000 | Salame Campagnolo | description only repeats the product name (no marketing text) |
| 258 | 2044548000000 | Pancetta Con Aglio | description only repeats the product name (no marketing text) |
| 261 | 2611085000000 | Bresaola di Fassone da banco Terre d'Italia | empty description |

## Counts

### Usable pool (274)

- Products: 274. Buckets: hard_yes 80 · in_between 92 · hard_no 102, of which 37 hard_no products have DISCARDED decoy claims.
- Claims: 1475. IN_SCOPE 365 · NEEDS_VERIFICATION 189 · DISCARDED 921 · low confidence 256
- Macro category: food and drink 211 · personal care and household 63
- Product gray_zone tags: generic_plus_specific 32, natural_footnote 12, farming_vs_heritage 5, endorsement_named_vs_generic 9, risk_vs_performance 4, comparator_vague_vs_named 4, eco_in_health_heritage 13, senza_pollutant_vs_additive 6, split_slogan 10

| trigger | products | claims |
|---|---|---|
| generic_green | 110 | 213 |
| undefined_natural | 40 | 57 |
| climate_neutral | 9 | 10 |
| vague_comparison | 25 | 36 |
| brand_eco_slogan | 44 | 46 |
| vague_supply_chain | 55 | 84 |
| recycled_recyclable | 63 | 89 |
| biodegradable | 4 | 6 |
| certification | 49 | 80 |
| named_endorsement | 10 | 12 |
| vegan | 6 | 6 |
| farming_practice | 30 | 43 |
| defined_term | 8 | 9 |
| risk_reduction | 1 | 2 |
| named_comparison | 6 | 8 |
| pollutant_free | 8 | 11 |
| out_of_scope | 201 | 1036 |

| category | products |
|---|---|
| acqua-e-analcolici | 18 |
| articoli-per-la-casa | 20 |
| birra-vino-e-liquori | 17 |
| carne | 9 |
| condimenti-e-conserve | 19 |
| cura-della-casa | 19 |
| dolci-e-prima-colazione | 20 |
| gastronomia | 15 |
| gelati-e-surgelati | 16 |
| pane-e-snack-salati | 16 |
| pasta-riso-e-farina | 20 |
| pesce | 13 |
| prodotti-prima-infanzia | 19 |
| salumi-e-formaggi | 15 |
| salute-e-benessere | 19 |
| uova-latte-e-latticini | 19 |

### Selected 100

- Products: 100. Buckets: hard_yes 35 · in_between 35 · hard_no 30, of which 30 hard_no products have DISCARDED decoy claims.
- Claims: 774. IN_SCOPE 178 · NEEDS_VERIFICATION 108 · DISCARDED 488 · low confidence 134
- Macro category: food and drink 72 · personal care and household 28
- Product gray_zone tags: generic_plus_specific 8, natural_footnote 7, farming_vs_heritage 3, endorsement_named_vs_generic 3, risk_vs_performance 4, comparator_vague_vs_named 3, eco_in_health_heritage 4, senza_pollutant_vs_additive 3, split_slogan 3

| trigger | products | claims |
|---|---|---|
| generic_green | 48 | 102 |
| undefined_natural | 17 | 26 |
| climate_neutral | 6 | 6 |
| vague_comparison | 14 | 19 |
| brand_eco_slogan | 23 | 25 |
| vague_supply_chain | 25 | 40 |
| recycled_recyclable | 34 | 52 |
| biodegradable | 3 | 5 |
| certification | 22 | 38 |
| named_endorsement | 3 | 4 |
| vegan | 3 | 3 |
| farming_practice | 11 | 19 |
| defined_term | 5 | 6 |
| risk_reduction | 1 | 2 |
| named_comparison | 5 | 7 |
| pollutant_free | 6 | 7 |
| out_of_scope | 98 | 551 |

| category | products |
|---|---|
| acqua-e-analcolici | 7 |
| articoli-per-la-casa | 9 |
| birra-vino-e-liquori | 7 |
| carne | 2 |
| condimenti-e-conserve | 6 |
| cura-della-casa | 12 |
| dolci-e-prima-colazione | 7 |
| gastronomia | 6 |
| gelati-e-surgelati | 6 |
| pane-e-snack-salati | 6 |
| pasta-riso-e-farina | 4 |
| pesce | 6 |
| prodotti-prima-infanzia | 8 |
| salumi-e-formaggi | 4 |
| salute-e-benessere | 4 |
| uova-latte-e-latticini | 6 |

Retailers (selected): Carrefour 100 (100%). Source files: clean/carrefour.json 100.

Brands (selected, 99 distinct, max 2 per brand): L'Angelica 2, Aeternum 1, Amuchina 1, Antartika 1, Apoteke 1, Asiago Food 1, Astro 1, BRITA 1, Barilla 1, Ben Fatto 1, Bibanesi 1, Birrificio Angelo Poretti 1, Boario 1, Carrefour 1, Carrefour Bio 1, Carrefour Selection 1, Carrefour il Mercato 1, Cavit 1, Centrale del Latte di Brescia 1, Cif 1, Coccolino 1, Consorcio 1, Dixan 1, Durex 1, Equilibra 1, FRoSTA 1, Fattoria Scaldasole 1, Felicia 1, Feudi di San Gregorio 1, Filippo Berio 1, Fissan 1, Flora 1, Forchir 1, Fumara 1, Fuze Tea 1, Galbusera 1, Gastronomia Piccinini 1, Germinal Bio 1, Golden Lady 1, Handl 1, HiPP 1, Italpizza 1, Johnson's 1, Kimbo 1, Kioene 1, Knorr 1, La Molisana 1, Le Stagioni d'Italia 1, Lenor 1, Levissima 1, Lisciani 1, Lysoform 1, Maniva 1, Maped 1, Mastri Birrai Umbri 1, Mellin 1, Mila 1, Molino Rossetto 1, Moneta 1, Mowi 1, Mulino Bianco 1, Nestlé Nidina 1, Nutrifree 1, Oro Saiwa 1, Orogel 1, Orphea 1, Pampers 1, Parmareggio 1, Pentel 1, Perlana 1, Pezzullo 1, Philips 1, Pigna 1, Plasmon 1, Pomì 1, Rio Mare 1, Riso Scotti 1, River Steamer 1, Rizzoli 1, Roberto 1, S.Pellegrino 1, STABILO 1, Samurài 1, San Crispino 1, Santàl 1, Scala 1, Terre d'Italia 1, The Icelander 1, Tre Marie 1, UHU 1, Valfrutta 1, Vesmati 1, Viani 1, Vileda 1, Wettex 1, Wüber 1, Zymil 1, le Naturelle 1, unbranded 1

## Targets and shortfalls

| target | status | actual |
|---|---|---|
| hard_yes 35 · in_between 35 · hard_no 30 | met | 35 / 35 / 30 |
| ≥ 20 hard_no with DISCARDED decoys | met | 30 |
| ≤ 3 products per brand | met | max 2 |
| ≤ 40% from one retailer or source file | **NOT MET** | 100% Carrefour, from one file. The input is a single retailer and file, so this cap cannot be met. |
| ≥ 25 personal care / household | met | 28 |
| ≥ 40 food and drink | met | 72 |
| ≥ 60 IN_SCOPE claims | met | 178 |
| ≥ 40 NEEDS_VERIFICATION claims | met | 108 |
| ≥ 60 DISCARDED claims | met | 488 |
| trigger generic_green in ≥ 3 products | met | 48 |
| trigger undefined_natural in ≥ 3 products | met | 17 |
| trigger climate_neutral in ≥ 3 products | met | 6 |
| trigger vague_comparison in ≥ 3 products | met | 14 |
| trigger brand_eco_slogan in ≥ 3 products | met | 23 |
| trigger vague_supply_chain in ≥ 3 products | met | 25 |
| trigger recycled_recyclable in ≥ 3 products | met | 34 |
| trigger biodegradable in ≥ 3 products | met | 3 |
| trigger certification in ≥ 3 products | met | 22 |
| trigger named_endorsement in ≥ 3 products | met | 3 |
| trigger vegan in ≥ 3 products | met | 3 |
| trigger farming_practice in ≥ 3 products | met | 11 |
| trigger defined_term in ≥ 3 products | met | 5 |
| trigger risk_reduction in ≥ 3 products | **NOT MET** | 1 (only 1 in the whole pool: Rio Mare Pescato a Canna, idx 74, which is selected) |
| trigger named_comparison in ≥ 3 products | met | 5 |
| trigger pollutant_free in ≥ 3 products | met | 6 |
| trigger out_of_scope in ≥ 3 products | met | 98 |

No product was relabelled to fit a quota.

## Selection method

`random.seed(42)`, then a greedy pass:

1. Triggers, rarest first: add products carrying the trigger until it appears in 3 selected products.
2. Gray zones, rarest first: at least 3 products tagged with each.
3. hard_no products that have DISCARDED decoys, up to 24.
4. Fill in_between, then hard_yes, then hard_no, up to their targets.

Each step picks the highest-scoring candidate within the per-brand cap and the bucket targets. The score rewards triggers still under 3, personal care / household products while that group is under 25, IN_SCOPE / NEEDS_VERIFICATION / DISCARDED claim mix, and decoys in hard_no. It penalises brands already selected. Random numbers break ties.

## Bucket rules as applied

- **hard_yes**: at least one IN_SCOPE or NEEDS_VERIFICATION claim, and none of those claims sits on a gray zone.
- **in_between**: at least one IN_SCOPE or NEEDS_VERIFICATION claim sits on a gray zone. The product `gray_zone` is that claim's zone; if there are several, the rarest zone is used.
- **hard_no**: no IN_SCOPE or NEEDS_VERIFICATION claim. Some hard_no products carry a `gray_zone` because a DISCARDED claim sits on one, e.g. risk_vs_performance. These are deliberate decoys, and they stay hard_no because the validation rule forbids positive claims in hard_no.

## Why each reserve product was left out

| idx | brand | name | bucket | reason |
|---|---|---|---|---|
| 2 | Santàl | Santàl Dolce di Natura pera Senza Zuccheri Aggiunti 1000 ml | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, defined_term, generic_green, named_comparison, recycled_recyclable) are already covered by ≥ 3 selected products; brand Santàl already selected (1) |
| 5 | Fonte Essenziale | Fonte essenziale Acqua Minerale Naturale Termale 6 x 1 L | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_endorsement) are already covered by ≥ 3 selected products |
| 7 | Powerade | POWERADE Hydro Active Lemon Lime PET 500 ml | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products |
| 10 | Valfrutta | Valfrutta Bio Pera 6 x 125 ml | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand Valfrutta already selected (1) |
| 11 | Valfrutta | Valfrutta Bio Arancia Carota Limone 6 x 125 ml | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand Valfrutta already selected (1) |
| 12 | San Benedetto | San Benedetto Thè Le Specialità Verde Matcha 1,5L | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products |
| 13 | Estathé | Estathé zero pesca 3 x 200 ml | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 14 | Carrefour Bio | Carrefour Bio Frullato di frutta alla Prugna 120 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 16 | San Benedetto | San Benedetto My Soda 1,5 L | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 17 | Carrefour Classic | Carrefour Classic Tè al Limone 1,5 L | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 18 | Carrefour Classic | Carrefour Classic Tè Verde 1,5 L | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 19 | UHU | UHU stic 5 x 8,2 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, pollutant_free, recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products; brand UHU already selected (1) |
| 24 | Aeternum | Aeternum Casseruola 2 manici Madame Petravera 20 cm | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable, undefined_natural, vague_comparison) are already covered by ≥ 3 selected products; brand Aeternum already selected (1) |
| 28 | Pentel | Pentel Roller EnerGel slim a scatto Punta 0.7 mm A/B/C 3 pz | in_between | in_between target (35) filled by higher-scoring products; its triggers (pollutant_free) are already covered by ≥ 3 selected products; brand Pentel already selected (1) |
| 30 | Pentel | Pentel Penna a sfera Superb Punta 0.7 mm Blu 3 pz | hard_no | hard_no target (30) filled by higher-scoring products; brand Pentel already selected (1) |
| 32 | Simpl | Simpl LED Sferica 40W E27 CW | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 33 | Simpl | Simpl LED Candela 40W E14 WW | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 34 | Carrefour | Carrefour 10+10pz Pile AA stilo | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 35 | Simpl | Simpl LED Goccia 60W E27 WW | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 36 | Simpl | Simpl 2 Torcia LR20 | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 37 | Simpl | Simpl 8 pile ministilo AAA | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 38 | Simpl | Simpl LED Sferica 40W E14 WW | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 42 | Birrificio Angelo Poretti | Birrificio Angelo Poretti l'Originale 4 Luppoli 3 x 33 cl | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_comparison) are already covered by ≥ 3 selected products; brand Birrificio Angelo Poretti already selected (1) |
| 44 | San Crispino | San Crispino Carattere Antico Pinot bianco Chardonnay Rubicone I.G.T.  | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand San Crispino already selected (1) |
| 45 | Beck's | Beck's lattina 44cl | hard_no | hard_no target (30) filled by higher-scoring products |
| 47 | La Morosina | La Morosina Birra Agricola Ticinensis Weizen 75 cl | in_between | in_between target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 49 | La Morosina | Morosina Birra Agricola Weizen 33 cl | in_between | in_between target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 51 | Cavit | Cavit i Mastri Vernacoli Müller Thurgau Vigneti delle Dolomiti IGT Vin | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Cavit already selected (1) |
| 52 | Borgocolorato | Borgocolorato Chardonnay Brut | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 54 | Althaia | Althaia Bianco in Latta | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 55 | Bavaria | Bavaria Premium Beer 5.0% 660 mL | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 57 | Hill 354 | Birra Ipa Hill 354 33 cl | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 59 | Fileni | Fileni Bio Cordon Bleu Bio con Cotto di Pollo, Mozzarella e Formaggio  | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products |
| 60 | Fileni | Fileni Bio Cotolette di Petto di Pollo Bio 0,220 kg | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products |
| 63 | Formento | Formento Piemontese 2 Medaglioni 2 x 100 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products |
| 64 | Fileni | Fileni Pepitos Bocconcini di pollo piccanti 0,250 kg | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 66 | unbranded | Braciole di Suino Confezione Risparmio | hard_no | hard_no target (30) filled by higher-scoring products; brand unbranded already selected (1) |
| 68 | Spiedì | Spiedì gli Arrosticini 1,000 Kg | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 69 | Fileni | Fileni Chicken Stick Bastoncini di pollo panati 0,250 kg | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 70 | Bonduelle | Bonduelle Legumeria Fagioli Rossi 3 x 160 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green) are already covered by ≥ 3 selected products |
| 73 | Rio Mare | Rio mare Filetti di Sgombro all'Olio di Oliva con Olive Verdi e Nere G | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Rio Mare already selected (1) |
| 75 | Rio Mare | Rio mare Filetti di Sgombro all'Olio di Oliva con Peperoncino Piccante | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Rio Mare already selected (1) |
| 76 | Saclà | Saclà OlivOlì Verdi Snocciolate 375 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vague_supply_chain) are already covered by ≥ 3 selected products |
| 77 | Saclà | Saclà Sfiziolì Carciofini Tagliati 205 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green) are already covered by ≥ 3 selected products |
| 78 | I Toscanacci | i toscanacci Ragù di Cervo 180 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan) are already covered by ≥ 3 selected products |
| 79 | Bonduelle | Bonduelle Legumeria Borlotti 310 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green) are already covered by ≥ 3 selected products |
| 81 | Delicius | Delicius Filetti di Sgombro al naturale 90 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, undefined_natural) are already covered by ≥ 3 selected products |
| 83 | La Drogheria 1880 | La Drogheria 1880 Pepe Nero in Grani 95 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 84 | Simpl | Simpl Olio di semi Vari 1 L | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 85 | Carrefour Classic | Carrefour Classic Capperi in Aceto di Vino 210 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 87 | Carrefour Classic | Carrefour Classic Pepe Nero Grani con Macinino 30 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 88 | D'Amico | D'Amico le Specialità olive itrana 300 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 98 | Coccolino | Coccolino Profumo per Bucato Elixir bouquet estivo 342 ml | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (biodegradable) are already covered by ≥ 3 selected products; brand Coccolino already selected (1) |
| 102 | Simpl | Simpl 3 Panni Gialli Multisuperficie 38x38 cm | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 103 | Aristea | Aristea 5 PZ Insalatiere PAPER BIA 1300cc | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 104 | Glade | Glade Assorbiodori, Profumatore per la Casa e Armadi, Fragranza Relaxi | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 105 | Aristea | Aristea 50 Bicch. 4oz (115cc) PAPER CLASSIC | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 106 | Prym | Prym 20 Bottoni automatici 6-11 mm | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 107 | Glade | Glade Assorbiodori, Profumatore per la Casa e Armadi, Fragranza Lavand | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 108 | L'Angelica | L'Angelica Passioni d'inverno al Gusto di Pan di Zenzero 15 Filtri 28. | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, generic_green, undefined_natural, vague_comparison, vegan) are already covered by ≥ 3 selected products; brand L'Angelica already selected (2) |
| 114 | Poggio del Farro | Poggio del Farro Flakes di Farro Integrali Bio 300 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products |
| 115 | Mulino Bianco | Mulino Bianco Fette Biscottate Rustiche 315g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Mulino Bianco already selected (1) |
| 116 | Mulino Bianco | Mulino Bianco Alveari con Burro Salato e Miele 300g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Mulino Bianco already selected (1) |
| 119 | Perugina | PERUGINA NERO Fondente Extra 85% Tavoletta Cioccolato Fondente 85g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products |
| 120 | Carrefour Selection | Carrefour Selection Éclats Caramel & Fleur de Sel Noir 100 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_comparison, vague_supply_chain) are already covered by ≥ 3 selected products; brand Carrefour Selection already selected (1) |
| 121 | Kimbo | Kimbo Espresso Napoletano Formula Bar 15 Cialde Compostabili* 109.5 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, recycled_recyclable) are already covered by ≥ 3 selected products; brand Kimbo already selected (1) |
| 122 | Carrefour Original | Carrefour Original Savoiardi 4 x 100 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 123 | Carrefour Bio | Carrefour Bio Corn Flakes Fiocchi tostati a base di mais 300 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Carrefour Bio already selected (1) |
| 124 | Carrefour Dolci & Decori | Carrefour Dolci & Decori Scorze di cedro candite 70 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 125 | Carrefour Original | Carrefour Original Amaretti croccanti 200 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 126 | ristora Professional | ristora Professional Cacao Amaro 1 Kg | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 127 | Carrefour Classic | Carrefour Classic Zucchero di Canna 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 130 | Maffei | maffei Pasta Fresca di Semola di Grano Duro Strozzapreti 250 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, vague_comparison) are already covered by ≥ 3 selected products |
| 132 | Suzi Wan | Suzi Wan Salsa di Soia 143 ml | hard_no | hard_no target (30) filled by higher-scoring products |
| 133 | Cameo | cameo le Soffici Margherita 600 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products |
| 136 | Knorr | Knorr Minestra Arlecchino 84 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Knorr already selected (1) |
| 137 | Knorr | Knorr Minestrone di Legumi 545 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Knorr already selected (1) |
| 139 | MaySoy | MaySoy Salsa di Soia 250 ml | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 140 | Carrefour Bio | Carrefour Bio Tofu al naturale 2 x 125 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Carrefour Bio already selected (1) |
| 141 | Urbani Tartufi | Urbani Tartufi Filosofia Naturale Tartufi Estivi 70 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 144 | Tilda | Tilda Pure Original Basmati 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 146 | Mulan | Mulan Edamame con Gemme di Sale 300 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 147 | FRoSTA | FRoSTA i Croccanti 2 Filetti di Merluzzo agli Spinaci 220 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand FRoSTA already selected (1) |
| 152 | Lamb Weston | Lamb Weston Twister Fries Seasoned 600 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, vague_comparison) are already covered by ≥ 3 selected products |
| 153 | Carrefour Bio | Carrefour Bio Minestrone surgelato 450 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 154 | Le Stagioni d'Italia | Le Stagioni d'Italia Pizza ai Funghi Senatore varietà Cappelli 370 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable, vague_supply_chain) are already covered by ≥ 3 selected products; brand Le Stagioni d'Italia already selected (1) |
| 156 | Lamb Weston | Lamb Weston Twister Fries 600 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, vague_comparison) are already covered by ≥ 3 selected products |
| 157 | Bonduelle | Bonduelle Natura in Padella Taccole Surgelato 450 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green) are already covered by ≥ 3 selected products |
| 159 | Icemänner | Icemänner Ice³ Cup 130 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 162 | Carrefour Classic | Carrefour Classic Nocciola 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 163 | Calippo | Calippo Cola 5 x 105 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 165 | Fiorentini | Fiorentini l'Originale Crusca Avena 250 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products |
| 166 | L'Angelica | L'Angelica Aloe Vera Biologica 1 L | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green, recycled_recyclable, vague_supply_chain, vegan) are already covered by ≥ 3 selected products; brand L'Angelica already selected (2) |
| 168 | Morato | Morato Protein & Fiber 380 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, undefined_natural) are already covered by ≥ 3 selected products |
| 170 | Morato | Morato American Sandwich Grano Duro 14 x 39,3 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vague_comparison) are already covered by ≥ 3 selected products |
| 174 | Isostad | Isostad, High Protein 25 Sport Bar, Gusto Nocciola, 25% di proteine -  | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green) are already covered by ≥ 3 selected products |
| 175 | Carrefour Bio | Carrefour Bio Pane a Fette al farro con semi di lino, girasole e soia  | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Carrefour Bio already selected (1) |
| 176 | Sarchio | Sarchio Sfogliette alle verdure Biologico 55 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green, undefined_natural) are already covered by ≥ 3 selected products |
| 177 | Mulino Bianco | Mulino Bianco Pan Bauletto Bianco Pane Ideale per Panini 400g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, named_endorsement, vague_supply_chain) are already covered by ≥ 3 selected products; brand Mulino Bianco already selected (1) |
| 180 | Carrefour Classic | Carrefour Classic Schiacciatine Classiche 6 x 37,5 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 183 | Simpl | Simpl Crackers 2 x 100 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 186 | Riso Scotti | Riso Scotti Riso Integrale Venere 500 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan) are already covered by ≥ 3 selected products; brand Riso Scotti already selected (1) |
| 187 | Molino Filippini | Molino Filippini il mio Couscous Mais e Riso 375 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, recycled_recyclable, vague_comparison) are already covered by ≥ 3 selected products |
| 188 | Barilla | Barilla Emiliane Tagliatelle Pasta all'Uovo 250g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (farming_practice) are already covered by ≥ 3 selected products; brand Barilla already selected (1) |
| 190 | Felicia | felicia Mezze Penne Piselli Verdi Bio 250 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, vague_comparison, vague_supply_chain) are already covered by ≥ 3 selected products; brand Felicia already selected (1) |
| 191 | Moro | Moro Farina per Polenta Taragna 1000 g | hard_no | hard_no target (30) filled by higher-scoring products |
| 192 | Riso Scotti | Riso Scotti Basmati Integrale 500 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, undefined_natural) are already covered by ≥ 3 selected products; brand Riso Scotti already selected (1) |
| 193 | Molino Casillo | Molino Casillo la Pasta Semola 1000 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products |
| 194 | Carrefour Bio | Carrefour Bio Semi di Canapa 200 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Carrefour Bio already selected (1) |
| 196 | Moro | Moro Pizzoccheri della Valtellina I.G.P. 500 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, undefined_natural) are already covered by ≥ 3 selected products |
| 197 | Granoro | granoro i Classici N. 106 Mezze Penne Rigate 500 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products |
| 198 | Carrefour Classic | Carrefour Classic Farina di Grano Tenero Integrale 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 199 | Carrefour Classic | Carrefour Classic Farina di Avena 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 200 | Carrefour Classic | Carrefour Classic Farina di Ceci 500 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 201 | Carrefour Classic | Carrefour Classic Farina di Grano Duro 1 kg | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 202 | Riso Scotti | Riso Scotti Jasmine Profumato 500 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan) are already covered by ≥ 3 selected products; brand Riso Scotti already selected (1) |
| 203 | Carrefour Classic | Carrefour Classic Semolino di Grano Duro 250 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 206 | Rizzoli | Rizzoli le Dolci del Mar Cantabrico Filetti di Alici in Olio Bio 60 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Rizzoli already selected (1) |
| 208 | Rizzoli | Rizzoli le Marinate del Mar Cantabrico Filetti di Alici con Olio agli  | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products; brand Rizzoli already selected (1) |
| 210 | Labeyrie | Labeyrie Il Tradizionale Salmone Affumicato 75 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, generic_green) are already covered by ≥ 3 selected products |
| 211 | Labeyrie | Labeyrie l'Originale Salmone affumicato ASC, 100% Senza Antibiotici, g | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, generic_green) are already covered by ≥ 3 selected products |
| 212 | Labeyrie | Labeyrie il Selvaggio Salmone Affumicato MSC, gusto Naturale 75 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, generic_green) are already covered by ≥ 3 selected products |
| 214 | Mowi | Mowi Gourmet Deli Trancio di Salmone Affumicato a Caldo Aneto 125 g | hard_no | hard_no target (30) filled by higher-scoring products; brand Mowi already selected (1) |
| 216 | unbranded | Salmone selvaggio Sockeye affumicato 70 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 222 | Plasmon | Plasmon Legumi Verdi Omogeneizzato con Legumi e Verdure 2 x 80 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (defined_term, recycled_recyclable, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand Plasmon already selected (1) |
| 225 | Plasmon | Plasmon la Mini Pasta Maccheroncini 300 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, recycled_recyclable, vague_supply_chain) are already covered by ≥ 3 selected products; brand Plasmon already selected (1) |
| 227 | Plasmon | Plasmon semplicemente bio manzo con carote 2 x 80 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, generic_green, recycled_recyclable, vague_supply_chain) are already covered by ≥ 3 selected products; brand Plasmon already selected (1) |
| 228 | Plasmon | Plasmon Omogeneizzato Fagioli con carote 2 x 80 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (defined_term, generic_green, recycled_recyclable, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand Plasmon already selected (1) |
| 230 | Nipiol | nipiol verdure miste omogeneizzato 2 x 80 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vague_supply_chain) are already covered by ≥ 3 selected products |
| 233 | HiPP | HiPP Camomilla 200 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_endorsement, recycled_recyclable, undefined_natural) are already covered by ≥ 3 selected products; brand HiPP already selected (1) |
| 235 | Pampers | Pampers Progressi Maxi 102 pz | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Pampers already selected (1) |
| 236 | Disney Baby | Disney Baby Minnie tazza da viaggio | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 239 | VTech | VTech Baby Magica palla multiattività | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 240 | VTech | VTech Baby Super Primi Passi Parlante 2 in 1 | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 241 | VTech | VTech Vroom Vroom Go - veicoli sorpresa assortiti | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 242 | Centrale del Latte di Brescia | Milk Kefir Fiocchi di latte 150 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (climate_neutral, undefined_natural, vague_supply_chain) are already covered by ≥ 3 selected products; brand Centrale del Latte di Brescia already selected (1) |
| 243 | Casa Modena | Casa Modena Snack & Vai! Dischetti di Mortadella e Tarallini Gran Pave | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_endorsement) are already covered by ≥ 3 selected products |
| 244 | Golfera | Golfera Golfetta 100 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green) are already covered by ≥ 3 selected products |
| 245 | Gran Soresina | Gran Soresina Grana Padano DOP Grattugiato 100 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products |
| 246 | Fumagalli | fumagalli Maiale Nero della Lomellina Salame Campagnolo 70 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 247 | Igor | Igor Gorgonzola Dolce DOP 150 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, climate_neutral, generic_green, recycled_recyclable, vague_comparison, vague_supply_chain) are already covered by ≥ 3 selected products |
| 251 | unbranded | Lardo d'Arnad DOP Valle d'Aosta | hard_no | hard_no target (30) filled by higher-scoring products; brand unbranded already selected (1) |
| 252 | Negroni | Negroni Negronetto 60 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products |
| 253 | Aia | Aia aeQuilibrium Petto di Pollo 130 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_endorsement, recycled_recyclable) are already covered by ≥ 3 selected products |
| 254 | Negroni | Negroni Pancetta Dolce in cubetti 2 x 80 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products |
| 260 | Carrefour Classic | Carrefour Classic Strutto | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 262 | Durex | Durex SuperSottile Vestibilità Extra-Large Preservativi Sottili, 10 Pr | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Durex already selected (1) |
| 263 | Durex | Durex Settebello Jeans Preservativi, 27 Profilattici | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable, vague_supply_chain) are already covered by ≥ 3 selected products; brand Durex already selected (1) |
| 264 | Durex | Durex Preservativi Supersottile Vestibilità Regolare, 18 Preservativi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Durex already selected (1) |
| 266 | Durex | Durex SuperSottile Vestibilità Regolare Preservativi Sottili, 10 Profi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Durex already selected (1) |
| 267 | L'Angelica | L'Angelica Waterstick Té Matcha Antiox 12 x 2 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, named_endorsement, undefined_natural, vegan) are already covered by ≥ 3 selected products; brand L'Angelica already selected (2) |
| 268 | Equilibra | equilibra Re-Hydra Zero Vitality Gusto Pesca 12 Stick 24 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (generic_green) are already covered by ≥ 3 selected products; brand Equilibra already selected (1) |
| 271 | Laboratoires Vitarmonyl | Laboratoires Vitarmonyl Melatonina Express 60 Compresse Orosolubili 4, | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (vague_supply_chain) are already covered by ≥ 3 selected products |
| 272 | Durex | Durex Nude Sensation 10 Profilattici | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Durex already selected (1) |
| 273 | Demak'Up | Demak Up Cocoon Rotondo 85 pz | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (undefined_natural) are already covered by ≥ 3 selected products |
| 274 | Golden Lady | Golden Lady Calzino sporty nero taglia S/M | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 276 | Golden Lady | Golden Lady Calzino in morbida microfibra 50 denari Nero Taglia Unica | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 277 | Golden Lady | Golden Lady Calzino sporty grigio | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 278 | Golden Lady | Golden Lady Collant My Secret 20 Den daino S | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 279 | Golden Lady | Golden Lady Collant velato Bodyform 20den con corpino sgambato conteni | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 280 | Golden Lady | Golden Lady Collant supercoprente North Polar con interno felpato Nero | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 282 | Centrale del Latte di Brescia | Milk Yogurt da bere Banana 500 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, certification, climate_neutral, farming_practice, generic_green, vague_supply_chain) are already covered by ≥ 3 selected products; brand Centrale del Latte di Brescia already selected (1) |
| 283 | Centrale del Latte di Brescia | Brescia Latte di Centrale Parzialmente Scremato U.H.T. a lunga conserv | in_between | in_between target (35) filled by higher-scoring products; its triggers (brand_eco_slogan, generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand Centrale del Latte di Brescia already selected (1) |
| 284 | Meran | Meran Yogurt extra cremoso Fior di Latte 1 kg | in_between | in_between target (35) filled by higher-scoring products; its triggers (farming_practice, generic_green) are already covered by ≥ 3 selected products |
| 288 | Zymil | Zymil Alta Digeribilità Senza Lattosio Benefit Fibre 1000 ml | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Zymil already selected (1) |
| 289 | Danacol | DANACOL Yogurt da bere, Riduce il Colesterolo grazie agli Steroli Vege | in_between | in_between target (35) filled by higher-scoring products; its triggers (named_endorsement, undefined_natural) are already covered by ≥ 3 selected products |
| 291 | Zymil | Zymil Alta Digeribilità Senza Lattosio Benefit Proteine 1000 ml | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Zymil already selected (1) |
| 292 | Parmareggio | Parmareggio Burro 400 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (generic_green, recycled_recyclable) are already covered by ≥ 3 selected products; brand Parmareggio already selected (1) |
| 293 | Centrale del Latte di Brescia | Milk Pro High Protein 35g Caramello Salato 350 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (recycled_recyclable) are already covered by ≥ 3 selected products; brand Centrale del Latte di Brescia already selected (1) |
| 294 | Danette | DANETTE, budino gusto caramello, fresco dessert, Senza Conservanti, Se | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 295 | Oatly | Oatly! Bevanda Barista Edition 1 L | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 296 | Carnini | Carnini il Bunet 2 x 100 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 297 | Carrefour Classic | Carrefour Classic Crema al Gusto Vaniglia 4 x 125 g | hard_no | no claims at all; the 30 hard_no slots went to products with DISCARDED decoy claims |
| 298 | Carrefour Bio | Carrefour Bio Burro 200 g | in_between | in_between target (35) filled by higher-scoring products; its triggers (certification, farming_practice, generic_green) are already covered by ≥ 3 selected products; brand Carrefour Bio already selected (1) |

## Judgment calls (every low-confidence claim)

General conventions, applied across the whole pool:
- Renewable-energy claims («100% energia elettrica da fonti rinnovabili») → generic_green (low). No trigger names them, and the closest rule treats them as unsubstantiated environmental benefit claims.
- Bio-based / plant-sourced packaging → recycled_recyclable or certification (low). There is no bio-based trigger.
- Recycling calls-to-action («Riciclami!», «Ricicliamo insieme», «Rispetta l'ambiente» before the disposal block) are not extracted. First-person statements («Rispettiamo l'ambiente», «X per l'ambiente») are extracted.
- «naturalmente privo di lattosio» / «naturalmente ricco di fibre» → out_of_scope, as the natural-absence idiom. «lattice di gomma naturale» → out_of_scope, as a material name.
- Sales denominations that contain «bio» are not extracted (review removed 4 that had slipped in).
- «Benessere animale garantito» with no named scheme → vague_supply_chain.

| set | idx | claim | triggers → label | reasoning |
|---|---|---|---|---|
| 100 | 3 | «Agiamo per preservare le sue delicate bollicine per le generazioni future.» | generic_green → IN_SCOPE | Sustainability-flavoured 'future generations' wording, but the object is the product's bubbles; borderline puffery. |
| 100 | 4 | «Solo aromi naturali» | out_of_scope → DISCARDED | 'Aromi naturali' is a regulated flavouring term (Reg. 1334/2008), treated as out of scope rather than undefined_natural. |
| 100 | 4 | «Contiene naturalmente zuccheri della frutta» | out_of_scope → DISCARDED | Mandatory accompanying statement to 'senza zuccheri aggiunti'; natural-presence idiom, not an environmental naturalness claim. |
| 100 | 4 | «Il nostro impegno coinvolge anche le nostre confezioni, per un prodotto buono dentro e fuori.» | generic_green → IN_SCOPE | Vague environmental commitment under the 'Santal per l'ambiente' heading; no explicit eco word in the sentence itself. |
| 100 | 4 | «Certificato da Carbon Trust.» | certification → NEEDS_VERIFICATION | Named third-party certification of the CO2 figure; could also be read as named_endorsement. |
| 100 | 4 | «È rinnovabile» | generic_green → IN_SCOPE | Bare 'renewable' packaging headline with no own trigger; closest is generic_green (explained only in following line). |
| 100 | 4 | «L'83% della confezione proviene da fonti vegetali rinnovabili.» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based/renewable content percentage; no exact trigger, closest specific material-content trigger chosen. |
| 100 | 4 | «Parte della plastica e del tappo provengono da canna da zucchero.» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based plastic claim; no exact trigger, closest specific material-content trigger chosen. |
| 100 | 4 | «È economia circolare» | generic_green → IN_SCOPE | 'Circular economy' used as an undefined generic environmental label. |
| 100 | 6 | «Frutta Selezionata» | out_of_scope → DISCARDED | Quality selection of fruit, not a supply-chain goodness claim; could be argued vague_supply_chain. |
| 100 | 6 | «Frutta 100% Naturale» | defined_term → NEEDS_VERIFICATION | Gray zone: natural_footnote. Next line gives a partial definition (no flavourings, preservatives, colourings) which only covers additives. |
| 100 | 6 | «Utilizziamo energia eolica» | generic_green → IN_SCOPE | Renewable-energy claim with no scope/share; no specific trigger exists, closest is generic_green. |
| 100 | 6 | «la Natura di prima mano» | brand_eco_slogan, undefined_natural → IN_SCOPE | Brand slogan built on 'Natura'; nature-evoking rather than explicit environmental claim. |
| 100 | 8 | «Naturalmente equilibrata» | out_of_scope → DISCARDED | 'Naturalmente' as 'by nature' about mineral balance of a natural mineral water; read like the natural-absence idiom rather than undefined_natural. |
| 100 | 20 | «No Bisfenolo A, No Nickel e metalli pesanti, No PFOA.» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. PFOA/heavy metals read as pollutants, BPA leans pollutant; could also be read as food-contact safety (out of scope). |
| 100 | 20 | «Moneta utilizza alluminio per uso alimentare» | out_of_scope → DISCARDED | Food-contact compliance statement used as a selling point. |
| 100 | 21 | «Le collezioni Pigna, si distinguono per la ricerca sempre attuale delle grafiche, realizzate in collaborazione con professionisti, fotogr…» | generic_green, out_of_scope → IN_SCOPE | Long sentence cut only at the period; 'linea cartotecnica ecologica' plus sales-rank puffery; refers to the Pigna Nature line, not necessarily this product. |
| 100 | 22 | «Affidati all'innovativa filtrazione in 4 fasi di MAXTRA PRO con carbone attivo naturale proveniente da gusci di cocco e granuli a scambio…» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: natural_footnote. 'Carbone attivo naturale' is partly explained by its source (coconut shells); mainly a performance sentence. |
| 100 | 22 | «aiuta a risparmiare centinaia di bottiglie di plastica con un'impronta di carbonio fino a 25 volte più piccola rispetto all'acqua in bott…» | named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparator is the generic category 'acqua in bottiglia' with no source; between named and vague comparison. |
| 100 | 22 | «Sii parte del cambiamento. Perché ogni bottiglia di plastica conta.» | brand_eco_slogan, generic_green → IN_SCOPE | Environmental campaign slogan; two sentences kept together as one slogan. |
| 100 | 22 | «L'impronta di carbonio dell'acqua filtrata BRITA è già fino a 25 volte inferiore rispetto all'acqua in bottiglia, ma lavoriamo costanteme…» | named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparator is the generic category 'acqua in bottiglia' with no source; between named and vague comparison. |
| 100 | 23 | «Ricaricabile» | out_of_scope → DISCARDED | Refillability is a durability/reuse feature with no environmental wording; no fitting trigger. |
| 100 | 25 | «Piastra crepiere dotata di rivestimento antiaderente Petravera Pro, caratterizzato dalla presenza di particelle minerali naturali che con…» | undefined_natural, out_of_scope → IN_SCOPE | 'Particelle minerali naturali' describes a coating material; natural used as undefined attribute inside a performance sentence. |
| 100 | 25 | «Il rivestimento in Petravera Pro conferisce ancora più robustezza e antiaderenza, realizzato con particelle minerali naturali garantisce …» | undefined_natural, out_of_scope → IN_SCOPE | 'Particelle minerali naturali' used as an undefined attribute inside a health/performance sentence. |
| 100 | 26 | «Prodotto esente da cloruro di polivinile» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. PVC-free: material avoidance loosely read as pollutant_free. |
| 100 | 27 | «15 anni» | out_of_scope → DISCARDED | Lifetime bullet (durability); short standalone selling line. |
| 100 | 27 | «Consumano fino all'85% di energia in meno rispetto alle lampadine tradizionali, grazie alla più moderna tecnologia LED a risparmio energe…» | named_comparison, out_of_scope → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparator 'lampadine tradizionali' is a generic category, not a specific product; between named and vague comparison. |
| 100 | 29 | «La formulazione della colla è composta per il 98% da ingredienti naturali (acqua inclusa)» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. 'Ingredienti naturali' with only the partial qualifier '(acqua inclusa)'. |
| 100 | 29 | «Senza solventi ed eliminabile con acqua fredda» | pollutant_free, out_of_scope → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Solvents readable as pollutant or formulation attribute. |
| 100 | 29 | «Confezione senza PVC e realizzata con un minimo di 80% di materiale riciclato» | recycled_recyclable, pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. 'Senza PVC' loosely read as pollutant_free; recycled content is clear. |
| 100 | 29 | «98% Formulazione naturale» | undefined_natural → IN_SCOPE | Cut at inline ' - ' bullet; same text elsewhere carries '(acqua inclusa)' qualifier. |
| 100 | 39 | «Sancrispino Carattere Antico è espressione della cultura e della forte personalità dei nostri 5000 soci agricoltori che producono vini ca…» | out_of_scope → DISCARDED | Gray zone: farming_vs_heritage. Tradition of production methods that hints at (unspecified) practice; heritage claim. |
| 100 | 40 | «Birra speciale italian Pale Ale prodotta in Italia non filtrata non pastorizzata» | out_of_scope → DISCARDED | Denomination line but carries origin and 'non filtrata non pastorizzata' quality claims. |
| 100 | 43 | «Monitoriamo i nostri consumi per evitare sprechi d'acqua» | generic_green → IN_SCOPE | Vague water-saving commitment without figures; no specific trigger. |
| 100 | 43 | «Usiamo energia elettrica 100% rinnovabile» | generic_green → IN_SCOPE | Specific renewable-electricity claim; no dedicated trigger exists, closest is generic_green. |
| 100 | 46 | «Nel nostro territorio, ricco e autentico, i vigneti coesistono da sempre con alberi da frutto, boschi, erbe aromatiche.» | out_of_scope → DISCARDED | Terroir/origin prose that faintly hints at biodiversity; no environmental wording. |
| 100 | 48 | «Qualità Sostenibile» | generic_green → IN_SCOPE | Generic 'sustainable' label displayed next to the SQNPI certification lines. |
| 100 | 50 | «Pica è il sistema di viticoltura di precisione di Cavit.» | farming_practice → NEEDS_VERIFICATION | Named precision-viticulture system; a practice, but its environmental relevance is only implied by the slogan above. |
| 100 | 61 | «Antispreco» | generic_green → IN_SCOPE | Anti-food-waste label (single portions); environmental sense implied but undefined. |
| 100 | 61 | «lotta contro lo spreco consumo consapevole» | generic_green → IN_SCOPE | Vague responsible-consumption / anti-waste slogan. |
| 100 | 61 | «Con carne di scottona Filiera Qualità» | vague_supply_chain → IN_SCOPE | 'Filiera Qualità' is a Carrefour supply-chain programme named without detail. |
| 100 | 71 | «Una passata ricca e vellutata, dalla consistenza piena e avvolgente.» | out_of_scope → DISCARDED | Sensory line that borders on mere description; kept as short standalone taste/quality puffery. |
| 100 | 72 | «save the olives» | brand_eco_slogan → IN_SCOPE | Brand environmental programme name; eco meaning comes from the following line about protecting olive trees and biodiversity. |
| 100 | 72 | «Scopri come contribuiamo a proteggere gli ulivi secolari e la biodiversità su savetheolives.com» | generic_green → IN_SCOPE | Website invitation, but it asserts an unspecified biodiversity-protection contribution. |
| 100 | 72 | «Olio extra vergine di oliva 100% italiano» | out_of_scope → DISCARDED | Sales name plus '100% italiano' origin claim; extracted for the origin element. |
| 100 | 74 | «Da tempo infatti diversifichiamo le zone di pesca, i metodi e le specie pescate per rispettare e bilanciare i punti di forza e debolezza …» | vague_supply_chain → IN_SCOPE | Fishing-practice description too vague to verify; closer to asserted supply-chain goodness than a concrete practice. |
| 100 | 82 | «Solo pomodori italiani da filiera certificata» | certification, out_of_scope → NEEDS_VERIFICATION | Unnamed 'certificata' supply chain; sense (quality vs sustainability) unclear, could also be vague_supply_chain. |
| 100 | 82 | «Pomì trace ⏎ Segui la tracciabilità» | vague_supply_chain → IN_SCOPE | Traceability programme plus website invitation; kept as a traceability assertion. |
| 100 | 82 | «Pomì per l'ambiente» | brand_eco_slogan → IN_SCOPE | Probably the header of a removed disposal block, but as written it is a brand environmental slogan. |
| 100 | 86 | «Filetti di tonno in olio di oliva extra vergine biologico» | certification → NEEDS_VERIFICATION | Legal sales denomination, but it carries the organic (biologico) claim, so extracted. |
| 100 | 94 | «I Cerotti Dopopuntura Orphea Protezione Persona Bambini contribuiscono ad attenuare le sensazioni fastidiose di prurito causate da agenti…» | out_of_scope → DISCARDED | Gray zone: risk_vs_performance. 'impedisce ... ulteriore irritazione' is performance phrased close to risk reduction; no explicit 'rischio' wording. |
| 100 | 96 | «Per igienizzare e pulire a fondo tutta la casa, con agente pulente di origine naturale e una piacevole fragranza biodegradabile.» | undefined_natural, biodegradable, out_of_scope → IN_SCOPE | Gray zone: generic_plus_specific. Undefined 'di origine naturale' next to a specific biodegradability fact; gray zone choice is approximate. |
| 100 | 101 | «Grazie alle sue fibre resistenti e di origine vegetale, dura a lungo e non lascia pelucchi anche dopo numerosi utilizzi.» | out_of_scope → DISCARDED | 'di origine vegetale' is a material-origin fact rather than an undefined 'naturale' claim; could be read as undefined_natural. |
| 100 | 101 | «Wettex Magico è l'originale panno spugna svedese secco, composto al 100% da fibre naturali, cotone e cellulosa.» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. '100% fibre naturali' is immediately defined as cotton and cellulose, treated as defined_term. |
| 100 | 110 | «Harmony - Patto del grano buono» | brand_eco_slogan → IN_SCOPE | Programme name has no explicit eco word; its environmental meaning comes from the sustainable-agriculture lines below. |
| 100 | 110 | «Collaboriamo con agricoltori situati in Europa» | out_of_scope → DISCARDED | Origin statement about farmers; not framed as supply-chain goodness. |
| 100 | 110 | «Perché Abbiamo a Cuore i Nostri prodotti e la natura che ci Permette di Produrli» | generic_green → IN_SCOPE | Care for nature asserted generically; not a product naturalness claim. |
| 100 | 111 | «Le Stagioni d'Italia porta sulla vostra tavola una grande novità, il Gran Frollino con Antico Grano Senatore varietà Cappelli, un vero do…» | undefined_natural, out_of_scope → IN_SCOPE | 'un vero dono della natura' is poetic but presents the product/grain as natural without definition. |
| 100 | 111 | «Senza OGM» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. GMO-free ingredient claim, not a pollutant and not in feed context; treated as out_of_scope. |
| 100 | 111 | «Senza olio di palma» | out_of_scope → DISCARDED | Palm-oil-free is framed here as a nutrition choice, though the next line calls it 'etica e sostenibile'. |
| 100 | 111 | «Certificato SIS» | out_of_scope → DISCARDED | Seed-purity certification by SIS, not a sustainability/ethical certification. |
| 100 | 111 | «Una varietà antica che nasce da un seme certificato e garantito nella sua purezza da SIS Società Italiana Sementi.» | out_of_scope → DISCARDED | Named body certifies seed purity (quality/heritage), not a sustainability endorsement. |
| 100 | 112 | «L'Istituto Erboristico L'Angelica ha formulato la Tisana Senna e Carvi, coniugando natura e scienza con:» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'natura e scienza' evokes naturalness inside a health-formulation sentence; weak natural claim. |
| 100 | 112 | «Natura e scienza» | undefined_natural → IN_SCOPE | Heading that evokes naturalness as a selling point without defining it; could be seen as pure brand prose. |
| 100 | 112 | «Solo le migliori erbe e fiori per un benessere naturale» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'naturale' qualifies the wellbeing benefit rather than the product; still an undefined natural selling point. |
| 100 | 112 | «Sostenibilità» | generic_green → IN_SCOPE | Standalone section heading, treated as a generic sustainability claim. |
| 100 | 112 | «Senza cellophane con conseguente riduzione di 156 tonnellate di CO₂ nell'ambiente» | vague_comparison → IN_SCOPE | CO2 reduction with no stated baseline or method; a reduction claim, not climate neutrality. |
| 100 | 112 | «In collaborazione con: FISS - Fondazione Istituto Scienze della Salute» | out_of_scope → DISCARDED | Gray zone: endorsement_named_vs_generic. Collaboration with a named health foundation, not an endorsement of environmental characteristics. |
| 100 | 113 | «Nuovo astuccio, senza involucro per ridurre l'immissione nell'ambiente di 26 tonnellate di plastica ogni anno» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Quantified reduction with only an implicit comparator (the previous pack with wrapper). |
| 100 | 113 | «Naturalità garantita» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. Followed by a partial explanation ('Nessun aroma aggiunto'), which does not really define naturalness. |
| 100 | 113 | «Nessun aroma aggiunto, solo il meglio che la natura può offrire.» | undefined_natural, out_of_scope → IN_SCOPE | 'il meglio che la natura può offrire' is an undefined natural framing next to a no-added-flavour claim. |
| 100 | 113 | «Natura e scienza» | undefined_natural → IN_SCOPE | Heading that evokes naturalness as a selling point without defining it; could be seen as pure brand prose. |
| 100 | 113 | «Inoltre, abbiamo migliorato l'astuccio eliminando l'involucro trasparente, riducendo l'immissione di 26 tonnellate di plastica nell'ambie…» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Reduction versus an implicit previous pack ('abbiamo migliorato l'astuccio'); comparator not named. |
| 100 | 117 | «No ogm, olio di palma, conservanti e coloranti.» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. 'No OGM' (not in feed context) alongside additives and palm oil; read as additive/composition claim, not pollutant. |
| 100 | 117 | «Per il nostro grano seguiamo le nostre migliori pratiche agricole, non usiamo glifosato e operiamo nelle vicinanze dei centri di stoccaggio.» | vague_supply_chain, farming_practice → IN_SCOPE | Mixes vague 'migliori pratiche agricole' (vague supply chain) with a concrete practice (no glyphosate). |
| 100 | 117 | «Sosteniamo la Biodiversità creando oasi di fiori e api.» | farming_practice → NEEDS_VERIFICATION | Biodiversity claim tied to a concrete action (flower/bee oases); treated as farming practice rather than generic green. |
| 100 | 138 | «Scegliere Kioene è un passo concreto verso il cambiamento, attraverso un gesto semplice ed usuale come fare la spesa.» | generic_green → IN_SCOPE | Implicit environmental benefit ('cambiamento') following a planet-wellbeing sentence; no explicit eco word. |
| 100 | 145 | «Questo prodotto Tre Marie partecipa all'impegno di Sammontana Italia» | generic_green → IN_SCOPE | Refers to the environmental commitment described below without stating it; implicit generic eco claim. |
| 100 | 145 | «Prova la cottura in friggitrice ad aria: rispetto alla cottura in forno elettrico ti consente di ridurre tempo, consumo di energia ed emi…» | named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparison with a specific comparator (electric oven) but concerns the cooking method, not the product; no figures given. |
| 100 | 145 | «Sammontana è una società benefit» | certification → NEEDS_VERIFICATION | Legal benefit-corporation status: verifiable, closest to certification (ethical sense). |
| 100 | 148 | «Il mio impasto lievita naturalmente per oltre 24 ore» | out_of_scope → DISCARDED | 'lievita naturalmente' describes the leavening process (no added agents), not a natural product attribute. |
| 100 | 149 | «La nostra missione è portare sulla tua tavola il sapore autentico della natura, garantendo un'alimentazione varia e gustosa per te e la t…» | out_of_scope → DISCARDED | 'sapore autentico della natura' is taste puffery, not a natural attribute of the product. |
| 100 | 150 | «Questa busta è già di dimensioni e spessore ridotti al minimo» | vague_comparison → IN_SCOPE | Packaging reduction asserted with no comparator or figures. |
| 100 | 150 | «Il suo riciclo darà vita a nuovi oggetti» | recycled_recyclable → NEEDS_VERIFICATION | Recycling-outcome statement about the pack, borderline disposal info. |
| 100 | 150 | «Il meglio dai nostri agricoltori.» | vague_supply_chain → IN_SCOPE | Supply-chain goodness asserted without detail; could also be read as plain quality puffery. |
| 100 | 150 | «Selezioniamo i terreni più vocati.» | vague_supply_chain → IN_SCOPE | Vague sourcing-quality claim; closest is vague_supply_chain. |
| 100 | 150 | «Analizziamo e certifichiamo tutti i nostri prodotti per garantire elevata qualità e salubrità.» | out_of_scope → DISCARDED | 'certifichiamo' in quality/safety sense, not sustainability certification. |
| 100 | 164 | «Programma per la valutazione dell'impronta ambientale ⏎ Ministero della transizione ecologica» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Participation in the Ministry's environmental-footprint programme shown as an endorsement-style mark by a named public body; no results given. |
| 100 | 167 | «Inchiostro a base vegetale» | generic_green → IN_SCOPE | Listed as a reason the pack is 'amica dell'ambiente'; plant-based ink fits no specific trigger. |
| 100 | 167 | «Energia rinnovabile» | generic_green → IN_SCOPE | Renewable-energy claim listed under 'amica dell'ambiente'; no specific trigger covers energy sourcing. |
| 100 | 167 | «Scopri di più sul nostro impegno per la sostenibilità: www.germinalbio.it» | generic_green → IN_SCOPE | Website invitation, but it asserts a sustainability commitment. |
| 100 | 171 | «Filiera certificata» | vague_supply_chain, certification → IN_SCOPE | Unnamed 'certified supply chain'; both vague supply-chain and unnamed certification apply. |
| 100 | 171 | «Insieme per la sostenibilità» | brand_eco_slogan → IN_SCOPE | Brand sustainability slogan placed as the heading of the disposal line. |
| 100 | 172 | «Grissini gustosi e friabili preparati con ingredienti selezionati secondo la ricetta tradizionale perfetti per ogni momento da condividere» | out_of_scope → DISCARDED | 'Ingredienti selezionati' without a supply-chain reference read as quality puffery; the claim is mainly tradition/taste. |
| 100 | 173 | «Tutti i Pangrì di questa confezione contengono farina di grano tenero ottenuta nel rispetto della Carta del Mulino, il disciplinare di co…» | generic_green, named_endorsement, out_of_scope → IN_SCOPE | Gray zone: endorsement_named_vs_generic. Own sustainability charter co-written with WWF (named body) plus generic biodiversity benefit. |
| 100 | 173 | «La Carta del Mulino prevede il rispetto dei criteri di sostenibilità ISCC Plus ed è stata scritta insieme al WWF e al Dipartimento di Sci…» | certification, named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Names a scheme (ISCC Plus) and named co-authors; treated as specific, needing verification. |
| 100 | 173 | «Mulino Bianco acquista 100% energia elettrica da fonti rinnovabili» | generic_green → IN_SCOPE | Specific renewable-electricity claim; no specific trigger covers energy sourcing, so closest is generic_green. |
| 100 | 184 | «Per produrle utilizziamo esclusivamente cartone certificato FSC, cioè realizzato con materie prime da foreste gestite in maniera responsa…» | certification → NEEDS_VERIFICATION | 'gestite in maniera responsabile' is the FSC scheme's own definition, so generic_green was not added. |
| 100 | 185 | «La coltivazione di Ceci bio Felicia avviene principalmente in Puglia e Basilicata.» | certification, out_of_scope → NEEDS_VERIFICATION | Gray zone: eco_in_health_heritage. Origin statement; 'bio' appears only as part of the product name. |
| 100 | 189 | «Azienda 100% italiana da filiera integrata» | vague_supply_chain, out_of_scope → IN_SCOPE | 'filiera integrata' asserts supply-chain control without detail; mainly an Italian-origin claim. |
| 100 | 195 | «Piacere vegetale. Sorriso responsabile.» | generic_green, brand_eco_slogan → IN_SCOPE | Slogan; 'responsabile' in the environmental sense given the preceding sentence; 'vegetale' alone not treated as vegan. |
| 100 | 204 | «Pescate in primavera» | out_of_scope → DISCARDED | Seasonal catch; not a concrete sustainable-fishing practice as written. |
| 100 | 205 | «I nostri fishburger sono cotti al vapore perché amiamo il sapore ricco e naturale del pesce.» | undefined_natural, out_of_scope → IN_SCOPE | 'sapore naturale' is close to mere taste description; labelled as an undefined natural attribute. |
| 100 | 205 | «Metodo di cattura: ami e palangari» | farming_practice → NEEDS_VERIFICATION | Mandatory fishing-gear field, but states a concrete fishing method (hooks and longlines). |
| 100 | 207 | «Buona e nutriente, magra, tenera e ricca di Omega 3, perché cresce lentamente secondo i ritmi del clima montano.» | farming_practice, out_of_scope → NEEDS_VERIFICATION | Slow growth 'secondo i ritmi del clima montano' is a loose rearing claim inside a nutrition sentence. |
| 100 | 209 | «Scopri di più sulla pesca sostenibile e sulla provenienza di questo pesce.» | generic_green → IN_SCOPE | QR invitation that nonetheless asserts 'pesca sostenibile'. |
| 100 | 223 | «HiPP 1 Bio Combiotic è studiato per rispondere alle particolari esigenze nutrizionali dei lattanti.» | out_of_scope → DISCARDED | 'Bio' appears only as part of the product name; the sentence itself is a nutrition claim. |
| 100 | 223 | «HiPP 1 Bio Combiotic contiene unicamente lattosio» | out_of_scope → DISCARDED | 'Bio' appears only as part of the product name; the sentence itself is a nutrition claim. |
| 100 | 223 | «Scienza e natura insieme ⏎ 50 anni di ricerca in armonia con la natura.» | generic_green, out_of_scope → IN_SCOPE | Gray zone: split_slogan. 'In armonia con la natura' read as a vague environmental claim inside a research-heritage slogan. |
| 100 | 223 | «La qualità Bio Hipp supera i requisiti standard richiesti dal regolamento UE sui prodotti biologici.» | certification, named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Organic claim plus a comparison against the EU organic regulation as the stated comparator. |
| 100 | 223 | «CO₂ Ridotta ⏎ Emissione di CO₂-inferiore rispetto alle confezioni di latta» | named_comparison → NEEDS_VERIFICATION | Gray zone: comparator_vague_vs_named. Comparator is a packaging category (tin cans), specific but with no quantity or source. |
| 100 | 223 | «Stampa con colori a base di oli vegetali - sena oli minerali» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Mineral-oil-free inks read as a contaminant-free (MOSH/MOAH) claim. |
| 100 | 223 | «FSC- Cartone a sostegno della gestione forestale responsabile» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. FSC certification plus 'responsabile' environmental wording (FSC tagline). |
| 100 | 223 | «Il brand N°1 nei latti formulati biologici in Europa» | certification, out_of_scope → NEEDS_VERIFICATION | Sales-rank claim that also asserts the products are organic. |
| 100 | 223 | «Latte per lattanti in polvere bio» | certification → NEEDS_VERIFICATION | Sales denomination that carries the organic term; extracted because the organic claim needs verification. |
| 100 | 224 | «Filiera italiana certificata» | certification, out_of_scope → NEEDS_VERIFICATION | Unnamed supply-chain certification (quality/traceability sense) plus Italian origin. |
| 100 | 224 | «Filiera certificata - In collaborazione con il Ministero delle Politiche Agricole, Alimentari e Forestali» | certification → NEEDS_VERIFICATION | Unnamed supply-chain certification associated with a ministry; not clearly a sustainability certification. |
| 100 | 224 | «Solo quello che vedi ⏎ trasparenza dal campo al vasetto» | vague_supply_chain → IN_SCOPE | Field-to-jar transparency asserted without verifiable detail. |
| 100 | 224 | «Per Plasmon, l'alimentazione dei più piccoli ha bisogno delle attenzioni più grandi, e per questo gli Omogeneizzati alla Carne Plasmon so…» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. Defined via an in-text 'what does 100% natural mean' explanation, but the definition is partly circular (only natural ingredients). |
| 100 | 224 | «100% Naturale: 0% Amidi Aggiunti. 0% Sale Aggiunto.» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. '100% Naturale' followed by a partial definition (no added starch/salt). |
| 100 | 226 | «Dal vasetto di vetro si può vedere la nuova consistenza ancora più naturale della frutta, a cui i piccoli non resisteranno, la mangeranno…» | undefined_natural → IN_SCOPE | 'Più naturale' describes texture (sensory) but is still an undefined natural attribute. |
| 100 | 226 | «Ecco perché aderiamo al progetto Mosaico Verde e ci impegniamo a creare sempre più spazi verdi, piantando nuovi alberi per i nostri bambini.» | generic_green → IN_SCOPE | Tree-planting commitment tied to the offset programme; no measurable detail. |
| 100 | 232 | «Coperchio e Misurino in plastica, prodotti per almeno il 66% da fonti rinnovabili vegetali (canna da zucchero)°. ... °Coperchio e misurin…» | certification → NEEDS_VERIFICATION | Bio-based (renewable plant-source) plastic content with a named TÜV Austria certificate; no dedicated trigger for bio-based content, certification is closest. |
| 100 | 232 | «Energia Elettrica da Fonti Rinnovabili nella fabbrica dove NIDINA OPTIPRO 4 polvere viene prodotto.» | generic_green → IN_SCOPE | Specific renewable-electricity claim with no evidence and no fitting group-B trigger; generic_green chosen as closest. |
| 100 | 232 | «Coperchio e misurino in plastica - prodotti per almeno il 66% da Fonti Rinnovabili Vegetali° ... °Coperchio e misurino certificati da: TŪ…» | certification → NEEDS_VERIFICATION | Bio-based (renewable plant-source) plastic content with a named TÜV Austria certificate; no dedicated trigger for bio-based content, certification is closest. |
| 100 | 234 | «Senza solfati, coloranti e ftalati» | pollutant_free, out_of_scope → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Phthalates can be read as a pollutant/endocrine disruptor; sulfates and colourants are additives. |
| 100 | 248 | «Parmareggio, in collaborazione con l'esperto in nutrizione Dott. Giorgio Donegani, ha creato un minipasto completo e bilanciato che soddi…» | named_endorsement, out_of_scope → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Health/nutrition claim linked to a named nutrition expert (an individual, not a body); treated as a named endorsement. |
| 100 | 265 | «Lattice - Preservativi trasparenti in lattice di gomma naturale» | out_of_scope → DISCARDED | 'Lattice di gomma naturale' is the standard name of the material (natural rubber latex), not an undefined natural claim. |
| 100 | 269 | «I cerotti Apoteke utilizzano un adesivo di nuova tecnologia privo di solventi e ipoallergenico.» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. 'privo di solventi' could be read as a pollutant-free claim, but in an adhesive for skin it reads as a skin-tolerance/formulation claim. |
| 100 | 270 | «Rispetta la tua natura» | out_of_scope → DISCARDED | Brand slogan using 'natura' in the sense of one's own body/nature; not a claim that the product is natural or eco. |
| 100 | 281 | «Milk Pro High Protein Kefir combina tutti i benefici naturali del Kefir Milk ad un elevato contenuto proteico.» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'benefici naturali' is an undefined natural attribute inside a nutrition/health sentence. |
| 100 | 285 | «Grazie a questa alimentazione naturale, il Latte Fieno ha un sapore puro ed è ricco di preziose sostanze nutritive.» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. 'alimentazione naturale' is partially defined by the preceding feed list; could also be read as undefined_natural. |
| 100 | 286 | «Il sistema di controllo qualità prevede rigorose e frequenti verifiche su mangimi, acque di abbeverata e uova deposte.» | vague_supply_chain → IN_SCOPE | Supply-chain controls asserted without verifiable detail; mainly a quality/safety claim. |
| 100 | 287 | «Ispirati dalla natura» | brand_eco_slogan, undefined_natural → IN_SCOPE | Brand slogan evoking nature without any definition; implicit natural/eco positioning. |
| reserve | 2 | «Solo aromi naturali» | out_of_scope → DISCARDED | 'Aromi naturali' is a regulated flavouring term (Reg. 1334/2008), treated as out of scope rather than undefined_natural. |
| reserve | 2 | «Contiene naturalmente zuccheri della frutta» | out_of_scope → DISCARDED | Mandatory accompanying statement to 'senza zuccheri aggiunti'; natural-presence idiom, not an environmental naturalness claim. |
| reserve | 2 | «Il nostro impegno coinvolge anche le nostre confezioni, per un prodotto buono dentro e fuori.» | generic_green → IN_SCOPE | Vague environmental commitment under the 'Santal per l'ambiente' heading; no explicit eco word in the sentence itself. |
| reserve | 2 | «Certificato da Carbon Trust.» | certification → NEEDS_VERIFICATION | Named third-party certification of the CO2 figure; could also be read as named_endorsement. |
| reserve | 2 | «È rinnovabile» | generic_green → IN_SCOPE | Bare 'renewable' packaging headline with no own trigger; closest is generic_green (explained only in following line). |
| reserve | 2 | «L'83% della confezione proviene da fonti vegetali rinnovabili.» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based/renewable content percentage; no exact trigger, closest specific material-content trigger chosen. |
| reserve | 2 | «Parte della plastica e del tappo provengono da canna da zucchero.» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based plastic claim; no exact trigger, closest specific material-content trigger chosen. |
| reserve | 2 | «È economia circolare» | generic_green → IN_SCOPE | 'Circular economy' used as an undefined generic environmental label. |
| reserve | 5 | «La naturale azione dell'acqua termale, povera di sodio e ricca di solfati e magnesio, rende Fonte Essenziale particolarmente indicata com…» | out_of_scope → DISCARDED | 'Naturale azione' of a natural mineral water inside a health sentence; treated as health claim, not undefined_natural. |
| reserve | 12 | «Il thè verde matcha, ottenuto da foglie raccolte a mano e lasciate essiccare a bassa temperatura, regala una nuova esperienza di gusto in…» | out_of_scope → DISCARDED | Hand-picking/drying is a craft-quality processing claim, not an environmental farming practice. |
| reserve | 12 | «Il nuovo tappo che non disperdi nell'ambiente (Dir. UE 2019/904, art.6)» | generic_green → IN_SCOPE | Tethered cap is a legal requirement of the SUP Directive presented as an environmental feature; no specific trigger for 'legal requirement as distinctive'. |
| reserve | 19 | «Il famoso stick di colla "Made in Germany" con l'esclusivo tappo a vite che ne previene l'essiccazione ed una formulazione naturale al 98…» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: natural_footnote. 'Naturale al 98%' with only the partial qualifier '(acqua inclusa)'; naturalness itself undefined. |
| reserve | 19 | «Senza solventi.» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Solvents (VOC) readable as pollutant or as a formulation/safety attribute. |
| reserve | 19 | «La formulazione della colla è composta per il 98% da ingredienti naturali (acqua inclusa)» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. 'Ingredienti naturali' with only the partial qualifier '(acqua inclusa)'. |
| reserve | 19 | «Senza solventi ed eliminabile con acqua fredda» | pollutant_free, out_of_scope → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. Solvents readable as pollutant or formulation attribute. |
| reserve | 19 | «Confezione senza PVC, realizzata con un minimo di 80% di materiale riciclato» | recycled_recyclable, pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. 'Senza PVC' is a material-avoidance claim loosely read as pollutant_free; recycled content is clear. |
| reserve | 19 | «98% Formulazione naturale (acqua inclusa)» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. Cut at the inline ' - ' bullet; partial qualifier '(acqua inclusa)' only. |
| reserve | 24 | «Casseruola a due manici dotata di rivestimento antiaderente Petravera Pro, caratterizzato dalla presenza di particelle minerali naturali …» | undefined_natural, out_of_scope → IN_SCOPE | 'Particelle minerali naturali' describes a coating material; natural used as undefined attribute inside a performance sentence. |
| reserve | 24 | «Il rivestimento in Petravera Pro conferisce ancora più robustezza e antiaderenza, realizzato con particelle minerali naturali garantisce …» | undefined_natural, out_of_scope → IN_SCOPE | 'Particelle minerali naturali' used as an undefined attribute inside a health/performance sentence. |
| reserve | 28 | «Prodotto esente da cloruro di polivinile» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. PVC-free: material avoidance loosely read as pollutant_free. |
| reserve | 42 | «Monitoriamo i nostri consumi per evitare sprechi d'acqua» | generic_green → IN_SCOPE | Vague water-saving commitment without figures; no specific trigger. |
| reserve | 42 | «Usiamo energia elettrica 100% rinnovabile» | generic_green → IN_SCOPE | Specific renewable-electricity claim; no dedicated trigger exists, closest is generic_green. |
| reserve | 44 | «Sancrispino Carattere Antico è espressione della cultura e della forte personalità dei nostri 5000 soci agricoltori che producono vini ca…» | out_of_scope → DISCARDED | Gray zone: farming_vs_heritage. Tradition of production methods that hints at (unspecified) practice; heritage claim. |
| reserve | 47 | «Artigianale - Da filiera agricola italiana» | out_of_scope → DISCARDED | Artisanal + Italian farm supply chain; origin claim, arguably vague_supply_chain. |
| reserve | 47 | «Birra Agricola significa pensata, coltivata e trasformata entro i confini della nostra Cascina.» | out_of_scope → DISCARDED | Farm-origin/production-scope statement; concrete but not an environmental farming practice. |
| reserve | 47 | «Grazie a Birra Agricola Ticinensis portiamo avanti la tradizione contadina della nostra famiglia.» | out_of_scope → DISCARDED | Gray zone: farming_vs_heritage. Farming tradition framed as heritage. |
| reserve | 47 | «Coltivata in casa ⏎ naturalmente, dal campo alla bottiglia» | undefined_natural → IN_SCOPE | Gray zone: split_slogan. 'Naturalmente' may mean 'of course' rather than a naturalness attribute; slogan split over two lines. |
| reserve | 49 | «Dalla terra alla tavola» | out_of_scope → DISCARDED | Farm-to-table slogan; origin/supply-chain flavour without eco wording. |
| reserve | 49 | «Birra Agricola significa pensata, coltivata e trasformata entro i confini della nostra cascina.» | out_of_scope → DISCARDED | Farm-origin/production-scope statement; concrete but not an environmental farming practice. |
| reserve | 49 | «Grazie a Birra Agricola Morosina portiamo avanti la tradizione contadina della nostra famiglia.» | out_of_scope → DISCARDED | Gray zone: farming_vs_heritage. Farming tradition framed as heritage. |
| reserve | 49 | «Coltivata in Casa ⏎ naturalmente, dal campo alla bottiglia» | undefined_natural → IN_SCOPE | Gray zone: split_slogan. 'Naturalmente' may mean 'of course' rather than a naturalness attribute; slogan split over two lines. |
| reserve | 59 | «Scelta giusta» | out_of_scope → DISCARDED | Vague 'right choice' line slogan; no explicit environmental meaning in text. |
| reserve | 60 | «Scelta giusta» | out_of_scope → DISCARDED | Vague 'right choice' line slogan; no explicit environmental meaning in text. |
| reserve | 63 | «Garantisce l'ottimale conservazione della carne e la naturale frollatura che la rende così tenera e gustosa.» | out_of_scope → DISCARDED | 'Naturale frollatura' describes the ageing process, not a natural product attribute. |
| reserve | 63 | «Prodotto realizzato con energia rinnovabili» | generic_green → IN_SCOPE | Renewable-energy claim without scope/share; no dedicated trigger, closest is generic_green. |
| reserve | 70 | «Il Mondo Che Ci Piace ⏎ possiamo costruirlo ogni giorno insieme con semplici gesti: scelte sostenibili* e un'alimentazione ricca di prodo…» | brand_eco_slogan, generic_green, out_of_scope → IN_SCOPE | Gray zone: split_slogan. Brand slogan continued on next line with 'scelte sostenibili*'; the footnote only points to a QR code/website. |
| reserve | 73 | «Prova il gusto autentico dei Filetti di Sgombro Grigliati Rio Mare all'Olio di Oliva con Olive Verdi e Nere: filetti di sgombro lavorati …» | out_of_scope → DISCARDED | 'pesci selezionati' read as quality selection, not a supply-chain assertion. |
| reserve | 75 | «Prova il gusto autentico dei Filetti di Sgombro Grigliati Rio Mare all'Olio di Oliva con Peperoncino: filetti di sgombro lavorati a mano …» | out_of_scope → DISCARDED | 'pesci selezionati' read as quality selection, not a supply-chain assertion. |
| reserve | 76 | «Curiamo tutte le fasi di lavorazione dalla raccolta al confezionamento, per garantirti un prodotto di qualità.» | vague_supply_chain, out_of_scope → IN_SCOPE | Whole-chain control asserted without detail (akin to 'filiera controllata'), but framed as quality. |
| reserve | 78 | «I Toscanacci per l'ambiente» | brand_eco_slogan → IN_SCOPE | Probably the header of a removed disposal block, but as written it is a brand environmental slogan. |
| reserve | 81 | «Delicius, bontà 100% naturale.» | undefined_natural → IN_SCOPE | Gray zone: natural_footnote. Following sentences (open-sea fishing, no added additives) act as a partial justification, not a real definition of 'naturale'. |
| reserve | 81 | «Li lavoriamo a mano uno per uno e li prepariamo al naturale, per preservarne tutto il sapore e le proprietà nutrizionali.» | out_of_scope → DISCARDED | 'al naturale' is the culinary preparation term in the product name, not a natural attribute claim. |
| reserve | 98 | «La nostra innovativa formula trasparente, infusa di microperle e arricchita di fragranze preziose, per un extra profumo* che dura a lungo…» | out_of_scope → DISCARDED | Gray zone: comparator_vague_vs_named. Named comparator (Coccolino softeners) but the comparison is about fragrance performance, not environment, so out_of_scope rather than named_comparison. |
| reserve | 98 | «Aggiungi ai tuoi vestiti una nuova sensazione di extra freschezza, ispirata alla Natura» | out_of_scope → DISCARDED | 'ispirata alla Natura' describes fragrance inspiration, not a natural product attribute. |
| reserve | 108 | «Nuovo astuccio, senza involucro per ridurre l'immissione nell'ambiente di 26 tonnellate di plastica ogni anno» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Quantified reduction with only an implicit comparator (the previous pack with wrapper). |
| reserve | 108 | «Solo il meglio della natura» | undefined_natural → IN_SCOPE | Implies natural sourcing without definition; poetic phrasing. |
| reserve | 108 | «Natura e scienza» | undefined_natural → IN_SCOPE | Heading that evokes naturalness as a selling point without defining it; could be seen as pure brand prose. |
| reserve | 108 | «Inoltre, abbiamo migliorato l'astuccio eliminando l'involucro trasparente, riducendo l'immissione di 26 tonnellate di plastica nell'ambie…» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Reduction versus an implicit previous pack ('abbiamo migliorato l'astuccio'); comparator not named. |
| reserve | 114 | «Flakes di farro integrale bio» | certification → NEEDS_VERIFICATION | Sales denomination, but carries the organic claim, so extracted. |
| reserve | 115 | «Mulino Bianco acquista 100% energia elettrica da fonti rinnovabili» | generic_green → IN_SCOPE | Specific renewable-electricity claim with no fitting group-B trigger; generic_green is the closest available. |
| reserve | 115 | «Tutto il sapore rustico del farro, le virtù del grano integrale e una nota delicata data dallo zucchero di canna, per una colazione natur…» | out_of_scope → DISCARDED | 'naturalmente' used as an adverb idiom, not a natural product attribute. |
| reserve | 115 | «Le Fette Biscottate Rustiche sono preparate solo con materie prime accuratamente selezionate e controllate.» | vague_supply_chain → IN_SCOPE | Close to 'ingredienti selezionati da filiera controllata', but could be read as plain quality puffery. |
| reserve | 116 | «Mulino Bianco acquista 100% energia elettrica da fonti rinnovabili» | generic_green → IN_SCOPE | Renewable-electricity purchase claim at company level; no dedicated trigger, closest is generic_green (environmental performance claim without product-level substantiation). |
| reserve | 119 | «Passione e responsabilità, ingredienti che ci rendono orgogliosi» | generic_green → IN_SCOPE | 'responsabilità' heads the sustainability section; environmental sense is implied but not explicit. |
| reserve | 119 | «Con Nestlé Cocoa Plan sosteniamo oltre 150.000 famiglie di coltivatori di cacao (scopri di più su www.nestlecocoaplan.com).» | vague_supply_chain → IN_SCOPE | Social/ethical sourcing programme claim; quantified but programme content not verifiable from text. |
| reserve | 119 | «Siamo impegnati ad acquistare energia elettrica da fonti rinnovabili nei nostri stabilimenti e ad eliminare gli sprechi.» | generic_green → IN_SCOPE | Future commitment on renewable energy and waste; no dedicated trigger, closest is generic_green. |
| reserve | 133 | «Rispettiamo l'ambiente» | generic_green → IN_SCOPE | Placed as a heading of a recycling call-to-action; kept because it asserts the company respects the environment. |
| reserve | 146 | «Un piacere semplice e naturale» | undefined_natural → IN_SCOPE | Headline puffery; 'naturale' as undefined product attribute. |
| reserve | 147 | «La nostra missione è portare sulla tua tavola il sapore autentico della natura, garantendo un'alimentazione varia e gustosa per te e la t…» | out_of_scope → DISCARDED | 'sapore autentico della natura' is taste puffery, not a natural attribute of the product. |
| reserve | 152 | «Lasciamo la buccia: più gusto, meno spreco.» | vague_comparison, out_of_scope → IN_SCOPE | 'meno spreco' is a waste-reduction benefit with no comparator; environmental reading is implicit. |
| reserve | 152 | «La nostra confezione è realizzata al 60% in bioplastica, più sostenibile per l'ambiente.» | generic_green, vague_comparison → IN_SCOPE | Gray zone: generic_plus_specific. Bio-based content has no dedicated trigger; the claim is driven by 'più sostenibile' without comparator. |
| reserve | 154 | «Le Stagioni d'Italia porta sulla tua tavola una pizza straordinaria, preparata con questa antica varietà di grano duro: un vero dono dell…» | out_of_scope → DISCARDED | 'dono della natura' is heritage/quality puffery about an ancient grain variety, not a natural product attribute. |
| reserve | 154 | «Lenta lievitazione naturale» | out_of_scope → DISCARDED | Natural leavening = process term, not a natural product attribute. |
| reserve | 154 | «Certificato SIS» | out_of_scope → DISCARDED | Seed purity certification (SIS), not a sustainability/ethical certification. |
| reserve | 154 | «Una varietà antica che nasce da un seme certificato e garantito nella sua purezza da SIS, Società Italiana Sementi.» | out_of_scope → DISCARDED | Seed purity certification, not sustainability sense. |
| reserve | 156 | «Lasciamo la buccia: più gusto, meno spreco.» | vague_comparison, out_of_scope → IN_SCOPE | 'meno spreco' is a waste-reduction benefit with no comparator; environmental reading is implicit. |
| reserve | 156 | «La nostra confezione è realizzata al 60% in bioplastica, più sostenibile per l'ambiente.» | generic_green, vague_comparison → IN_SCOPE | Gray zone: generic_plus_specific. Bio-based content has no dedicated trigger; the claim is driven by 'più sostenibile' without comparator. |
| reserve | 157 | «Il Mondo Che Ci Piace ⏎ possiamo costruirlo ogni giorno insieme con semplici gesti: scelte sostenibili* e un'alimentazione ricca di prodo…» | generic_green, brand_eco_slogan → IN_SCOPE | Gray zone: split_slogan. Brand slogan continued on the next line; the footnote only points to a website, so 'scelte sostenibili' stays undefined. |
| reserve | 165 | «Fiorentini è una azienda familiare che produce specialità alimentari a base di cereali; prodotti volutamente semplici, naturali, leggeri …» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'naturali' as undefined product attribute inside a family-heritage sentence. |
| reserve | 166 | «L'Angelica seleziona solo le migliori materie prime, raccogliendole nel loro paese di origine.» | out_of_scope → DISCARDED | 'Selects the best raw materials' read as quality puffery rather than a supply-chain goodness claim. |
| reserve | 166 | «Il controllo diretto delle coltivazioni di aloe è sinonimo di qualità della materia prima.» | vague_supply_chain, out_of_scope → IN_SCOPE | Direct control of cultivation asserted without detail, akin to 'filiera controllata', but framed as quality. |
| reserve | 168 | «Più natura, più qualità» | undefined_natural, out_of_scope → IN_SCOPE | 'Più natura' as a heading over the environmental paragraph; read as an undefined natural claim. |
| reserve | 168 | «Hai tra le mani l'amore per la natura, riciclami!» | generic_green → IN_SCOPE | Recycling call-to-action, but it also casts the product as 'l'amore per la natura'. |
| reserve | 170 | «Meno plastica = risparmio CO₂ - Equivalente a 1500 nuovi alberi piantati» | vague_comparison → IN_SCOPE | 'Meno plastica' has no comparator (only the 'Nuovo pack' heading); the tree-planting equivalence is not an offset claim so climate_neutral was not added. |
| reserve | 177 | «La Carta del Mulino è il nostro disciplinare per la coltivazione sostenibile del grano tenero redatto insieme al WWF.» | generic_green, named_endorsement → IN_SCOPE | Gray zone: endorsement_named_vs_generic. Own sustainability charter co-written with WWF; generic 'sostenibile' plus a named body. |
| reserve | 177 | «La Carta del Mulino prevede il rispetto dei criteri di sostenibilità ISCC Plus ed è stata scritta insieme al WWF e al Dipartimento di Sci…» | certification, named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Names a scheme (ISCC Plus) and named co-authors; treated as specific, needing verification. |
| reserve | 177 | «Mulino Bianco acquista 100% energia elettrica da fonti rinnovabili» | generic_green → IN_SCOPE | Specific renewable-electricity claim; no specific trigger covers energy sourcing, so closest is generic_green. |
| reserve | 186 | «Insieme per la sostenibilità» | brand_eco_slogan → IN_SCOPE | Brand sustainability slogan used as heading of a disposal line (appears twice, extracted once). |
| reserve | 187 | «Meno spreco: l'acqua utilizzata viene interamente assorbita dal Cous Cous.» | vague_comparison → IN_SCOPE | 'Less waste' with no comparator, though an explanation follows. |
| reserve | 187 | «Meno energia: perché si prepara in soli 5 minuti.» | vague_comparison → IN_SCOPE | 'Less energy' with no comparator, justified only by short preparation time. |
| reserve | 190 | «La coltivazione di Piselli Verdi bio Felicia avviene principalmente in Puglia e Basilicata.» | certification, out_of_scope → NEEDS_VERIFICATION | Gray zone: eco_in_health_heritage. Origin statement; 'bio' appears only as part of the product name. |
| reserve | 192 | «La naturalezza, le proprietà nutritive e il leggero sapore di nocciola del Basmati Integrale vengono mantenute grazie ad una lavorazione …» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'La naturalezza' of the rice is an undefined natural attribute inside a nutrition/taste sentence. |
| reserve | 192 | «Insieme per la sostenibilità» | brand_eco_slogan → IN_SCOPE | Riso Scotti sustainability slogan used as heading of the disposal line. |
| reserve | 196 | «Ingredienti selezionati» | out_of_scope → DISCARDED | Bare 'selected ingredients' read as quality puffery rather than a supply-chain claim. |
| reserve | 202 | «Insieme per la sostenibilità» | brand_eco_slogan → IN_SCOPE | Riso Scotti sustainability slogan used as heading of the disposal line. |
| reserve | 206 | «Pescate in primavera» | out_of_scope → DISCARDED | Seasonal catch; not a concrete sustainable-fishing practice as written. |
| reserve | 208 | «Pescate in primavera» | out_of_scope → DISCARDED | Seasonal catch; not a concrete sustainable-fishing practice as written. |
| reserve | 222 | «L'Omogeneizzato Legumi Verdi Plasmon è prodotto con Ingredienti selezionati.» | out_of_scope → DISCARDED | 'Ingredienti selezionati' alone read as quality puffery rather than a supply-chain claim. |
| reserve | 222 | «Per Plasmon, l'alimentazione dei più piccoli ha bisogno delle attenzioni più grandi, e per questo gli Omogeneizzati ai Legumi Plasmon son…» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. Defined via an in-text 'what does 100% natural mean' explanation, but the definition is partly circular (only natural ingredients). |
| reserve | 225 | «Prodotto in Italia - Con ingredienti italiani - Filiera italiana certificata» | certification, out_of_scope → NEEDS_VERIFICATION | Unnamed supply-chain certification (quality/traceability sense) plus Italian origin. |
| reserve | 227 | «Alimento per l'infanzia biologico: omogeneizzato manzo con carote.» | certification → NEEDS_VERIFICATION | Sales denomination that carries the organic term; extracted because the organic claim needs verification. |
| reserve | 228 | «Solo quello che vedi ⏎ trasparenza dal campo al vasetto» | vague_supply_chain → IN_SCOPE | Field-to-jar transparency asserted without verifiable detail. |
| reserve | 228 | «L'Omogeneizzato Fagioli Borlotti con Carote Plasmon è prodotto con Ingredienti selezionati.» | out_of_scope → DISCARDED | 'Ingredienti selezionati' alone read as quality puffery rather than a supply-chain claim. |
| reserve | 228 | «Per Plasmon, l’alimentazione dei più piccoli ha bisogno delle attenzioni più grandi, e per questo gli Omogeneizzati ai Legumi Plasmon son…» | defined_term, out_of_scope → NEEDS_VERIFICATION | Gray zone: natural_footnote. Defined via an in-text 'what does 100% natural mean' explanation, but the definition is partly circular (only natural ingredients). |
| reserve | 233 | «La tisana alla Camomilla HiPP è una bevanda dolce e ben digeribile, preparata con estratto naturale di fiori di camomilla.» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'Estratto naturale' is close to an ingredient descriptor, but is an undefined natural attribute in a digestibility sentence. |
| reserve | 233 | «Questa bevanda è stata testata scientificamente dall'associazione no-profit Toothfriendly International e valutata non cariogena.» | named_endorsement, out_of_scope → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Dental-health test and rating by a named association; closer to a named endorsement than a generic test. |
| reserve | 233 | «I componenti della confezione sono riciclabili separatamente:» | recycled_recyclable → NEEDS_VERIFICATION | Header of disposal info, but it is a recyclability claim, and one listed component goes to unsorted waste. |
| reserve | 242 | «Milk Kefir Fiocchi di latte con i fermenti lattici vivi caratteristici del kefir, ti offre un piacere leggero e tutto il benessere natura…» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'Benessere naturale' is an undefined natural wording embedded in a wellbeing/tradition sentence. |
| reserve | 242 | «Benessere animale garantito» | vague_supply_chain → IN_SCOPE | Animal welfare 'guaranteed' with no named certification or practice; read as vague supply-chain goodness rather than certification. |
| reserve | 242 | «Latticino in fiocchi a base di formaggio fresco magro con kefir (30%) senza lattosio (inferiore a 0,1g per 100g)» | out_of_scope → DISCARDED | Sales denomination line that carries a lactose-free claim. |
| reserve | 243 | «Casa Modena, in collaborazione con l'esperto in nutrizione Dott. Giorgio Donegani, ha creato un minipasto completo e bilanciato che soddi…» | named_endorsement, out_of_scope → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Health/nutrition claim linked to a named nutrition expert (an individual, not a body); treated as a named endorsement. |
| reserve | 245 | «Benessere animale» | vague_supply_chain → IN_SCOPE | Bare animal-welfare line with no practice or certification named. |
| reserve | 245 | «Filiera certificata» | certification → NEEDS_VERIFICATION | Unnamed supply-chain certification. |
| reserve | 246 | «Le caratteristiche genetiche di questa razza, insieme ad una alimentazione naturale e di alta qualità, rendono le carni del Maiale Nero d…» | undefined_natural, out_of_scope → IN_SCOPE | 'Alimentazione naturale' of the pigs is a vague feed claim: undefined natural rather than a concrete farming practice. |
| reserve | 247 | «100% Benessere animale» | vague_supply_chain → IN_SCOPE | Animal-welfare claim with no practice or certification named. |
| reserve | 247 | «Eliminazione sprechi acqua» | generic_green → IN_SCOPE | Vague environmental water-saving claim with no measure. |
| reserve | 247 | «Energia da fonte 100% rinnovabile» | generic_green → IN_SCOPE | Specific renewable-energy claim with no evidence and no fitting group-B trigger; generic_green chosen as closest. |
| reserve | 253 | «Federazione Italiana Pallavolo - Prodotto ufficiale delle nazionali italiane di pallavolo» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Sports-federation sponsorship by a named body; not a sustainability or health endorsement, but fits named_endorsement closest. |
| reserve | 262 | «Lattice - Preservativi trasparenti in lattice di gomma naturale.» | out_of_scope → DISCARDED | 'Gomma naturale' is the material name (natural rubber latex), not a natural claim. |
| reserve | 263 | «Lattice - Preservativi trasparenti in lattice di gomma naturale.» | out_of_scope → DISCARDED | 'Lattice di gomma naturale' is the standard name of the material (natural rubber latex), not an undefined natural claim. |
| reserve | 264 | «Lattice - Preservativi trasparenti in lattice di gomma naturale.» | out_of_scope → DISCARDED | 'Lattice di gomma naturale' is the standard name of the material (natural rubber latex), not an undefined natural claim. |
| reserve | 266 | «Lattice - Preservativi trasparenti in lattice di gomma naturale.» | out_of_scope → DISCARDED | 'Lattice di gomma naturale' is the standard name of the material (natural rubber latex), not an undefined natural claim. |
| reserve | 267 | «Coltivato all'ombra, raccolto a mano e macinato lentamente a pietra, si distingue per il suo colore verde brillante, il gusto intenso e v…» | farming_practice, out_of_scope → NEEDS_VERIFICATION | Gray zone: farming_vs_heritage. Shade-growing and hand-picking are concrete cultivation practices but presented as traditional quality/heritage rather than environmental practice. |
| reserve | 267 | «Il Tè Matcha, oltre ad essere un tonico che contrasta la stanchezza fisica e mentale è anche un ottimo antiossidante naturale.» | undefined_natural, out_of_scope → IN_SCOPE | Gray zone: eco_in_health_heritage. 'antiossidante naturale' is an undefined natural attribute embedded in a health claim. |
| reserve | 267 | «In collaborazione con: FISS - Fondazione Istituto Scienze della Salute» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Collaboration with a named health foundation implies endorsement but is not stated as approval/recommendation. |
| reserve | 271 | «I prodotti dei Laboratoires Vitarmonyl sono il frutto di una selezione rigorosa degli ingredienti e rispondono ad elevati standard produt…» | vague_supply_chain, out_of_scope → IN_SCOPE | Rigorous ingredient selection asserted without detail (like 'ingredienti selezionati'), but framed as quality rather than sustainability. |
| reserve | 282 | «Benessere animale garantito» | vague_supply_chain → IN_SCOPE | Animal welfare 'guaranteed' with no named certification or scheme; closest to vague supply-chain goodness (not 'certificato'). |
| reserve | 283 | «100% Green A2A» | generic_green, brand_eco_slogan → IN_SCOPE | Refers to the energy supplier's green tariff; generic 'Green' with no detail. |
| reserve | 283 | «Usiamo solo energie rinnovabili» | generic_green → IN_SCOPE | Renewable-energy claim fits no specific trigger; treated as broad environmental claim without evidence. |
| reserve | 289 | «Danacol riduce il colesterolo grazie agli steroli vegetali⁽¹⁾ ... Il colesterolo in eccesso può causare problemi al cuore. L'effetto bene…» | out_of_scope → DISCARDED | Gray zone: risk_vs_performance. Authorised-style health claim on cholesterol with heart-risk footnote; no explicit 'riduce il rischio' wording, so kept out_of_scope. |
| reserve | 289 | «Danacol sostiene il Policlinico Gemelli nella prevenzione cardiovascolare.» | named_endorsement, out_of_scope → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Brand sponsors a named hospital; the co-branding ('Danacol & Gemelli') implies endorsement but no approval is stated. |
| reserve | 293 | «Fonte naturale di vitamina B2» | out_of_scope → DISCARDED | 'naturale' describes the natural occurrence of B2 in milk (nutrition claim), read as natural-occurrence idiom rather than an undefined natural product claim. |

## Validation

`validate.py` output (final run):

```
selected 100 reserve 174 unusable 26 total 300 of 300
claims checked 1475
buckets {'hard_yes': 35, 'hard_no': 30, 'in_between': 35}
max per brand ("L'Angelica", 2)
retailer share {'Carrefour': 1.0} (cap 40% NOT MET: single-retailer pool)
FAILURES: 0
```

Checks: exactly 100 selected; selected + reserve + unusable = 300; every claim_text (each part around " ... ") and every footnote is an exact substring of the source description; every label equals the label derived from its triggers; bucket consistency; no duplicate EAN or brand + name; brand cap respected. A second reviewer checked the 100 selected products and flagged 8 missed claims, 18 claims that should not have been extracted, 0 trigger errors and 0 boundary errors.

- **Fixed:** 7 missed claims were added. 16 structured origin/provenance lines and sales-name lines were removed, and the same rule was then applied across the whole pool: 3 more sales-name «bio» lines came out of the reserve.
- **Kept on purpose:** «Rispetta l'ambiente» (idx 110) stays out, as a recycling call-to-action placed just before the disposal block. The standalone badges «Biologico» (idx 167) and «Senza lieviti» (idx 281) stay in, because they are badges rather than sales names.
- **Reserve:** the 174 reserve products did not get this second review.