# ECGT gold set — 100 Eurospin products

This is a gold evaluation set for a detector of claims under the EU ECGT rules (Directive 2024/825), built from `clean/eurospin.json`. It uses the same method as the Carrefour set (`golden_set_ecgt_100.json`), and the guide and project conventions from that set apply unchanged. Every claim is copied verbatim from its source field. Each label is derived mechanically from the claim's triggers: only out_of_scope gives DISCARDED; any group-A trigger gives IN_SCOPE; otherwise a group-B trigger gives NEEDS_VERIFICATION. defined_term cancels undefined_natural. The file contained no existing annotation fields.

Files: `golden_set_ecgt_eurospin_100.json` (selected), `golden_set_ecgt_eurospin_reserve.json` (the other 83 usable products, labelled the same way), and this README.

Accounting: 100 selected + 83 reserve + 17 unusable = 200 records in the file.

## Field mapping (Eurospin)

| Output field | Source |
|---|---|
| product_id | `product_id` |
| ean | `ean` (null for 11 bulk/fresh items) |
| name | `name` |
| category | `origin_file` |
| source_file | constant `clean/eurospin.json` |
| source_index | position in the JSON array |
| retailer | constant `Eurospin` |
| brand | inferred from the text. 73 selected products (and most of the reserve) name no brand and are "unbranded"; these are mainly Eurospin private label or fresh produce. |
| claims[].source_field | always `description`, the only text field. The first ALL-CAPS line is the legal sales name and is never extracted. |
| not extracted | `url`; packaging-disposal lines; the mandatory organic control-body codes («IT-BIO-007 Agricoltura UE», «Organismo di controllo autorizzato…», 25 lines) |

## Retailer-specific decisions

- Most listings are just the ALL-CAPS sales name. 120 of the 183 usable products have no IN_SCOPE or NEEDS_VERIFICATION claim.
- **Amo Essere Bio** (the private organic line) repeats the same two sentences on about 25 products: «pratiche ambientali sostenibili» and «… rispetto dell'ambiente». They are labelled generic_green + certification (generic_plus_specific), so these products are in_between. The 3-per-brand cap admits only 3 of them.
- **«unbranded»** products are not counted as one brand for the 3-per-brand cap. Each is a different unidentified product. Counting them as one brand would make 100 products impossible.
- **The mandatory organic control-body codes** (Reg. 2018/848) were removed as mandatory particulars, not marketing claims (25 lines).


## Unusable records

17 records were set aside.

| idx | EAN | name | reason |
|---|---|---|---|
| 91 | 8028815708005 | Ventilatore da pavimento | empty description |
| 93 | 8032764761752 | Filetto di orata | description only repeats the product name (no marketing text) |
| 119 | None | Set rasatura 6in1 HS0710 "Severin" | empty description |
| 126 | 2080011000000 | Pancetta a fette | description only repeats the product name (no marketing text) |
| 128 | 2070116000000 | Ananas | description only repeats the product name (no marketing text) |
| 137 | 8009867008718 | Pasta di acciughe | description only repeats the product name (no marketing text) |
| 140 | 2100428000000 | Capocollo stagionato | description only repeats the product name (no marketing text) |
| 144 | 8007509110720 | Zaino Shuttle 2 scomparti | empty description |
| 148 | 2080059000000 | Salsiccia norcina | description only repeats the product name (no marketing text) |
| 149 | 8017596103666 | Salsa messicana | description only repeats the product name (no marketing text) |
| 157 | 8024920199073 | Fave surgelate | description only repeats the product name (no marketing text) |
| 161 | 8018708959973 | Guacamole | description only repeats the product name (no marketing text) |
| 164 | 8017596103727 | Kefir | description only repeats the product name (no marketing text) |
| 172 | 2070345000000 | Limoni | description only repeats the product name (no marketing text) |
| 176 | 8016117015464 | Ciotola elettronica | empty description |
| 182 | 8017596006387 | Cioccolato bianco | description only repeats the product name (no marketing text) |
| 194 | 8013912260143 | Mirtilli | description only repeats the product name (no marketing text) |

## Counts

### Usable pool (183)

- Products: 183. Buckets: hard_yes 21 · in_between 42 · hard_no 120, of which 52 hard_no products have DISCARDED decoy claims.
- Claims: 401. IN_SCOPE 87 · NEEDS_VERIFICATION 39 · DISCARDED 275 · low confidence 32
- Claims by source field: description 401
- Macro category: food and drink 122 · personal care and household 61
- Product gray_zone tags: generic_plus_specific 38, natural_footnote 0, farming_vs_heritage 0, endorsement_named_vs_generic 0, risk_vs_performance 3, comparator_vague_vs_named 1, eco_in_health_heritage 1, senza_pollutant_vs_additive 1, split_slogan 0

| trigger | products | claims |
|---|---|---|
| generic_green | 46 | 75 |
| undefined_natural | 7 | 8 |
| climate_neutral | 0 | 0 |
| vague_comparison | 1 | 2 |
| brand_eco_slogan | 2 | 3 |
| vague_supply_chain | 6 | 6 |
| recycled_recyclable | 9 | 13 |
| biodegradable | 1 | 1 |
| certification | 44 | 80 |
| named_endorsement | 0 | 0 |
| vegan | 9 | 10 |
| farming_practice | 2 | 2 |
| defined_term | 0 | 0 |
| risk_reduction | 1 | 1 |
| named_comparison | 0 | 0 |
| pollutant_free | 1 | 1 |
| out_of_scope | 97 | 287 |

| category | products |
|---|---|
| bevande | 25 |
| carne-e-pesce | 8 |
| dispensa | 25 |
| frutta-e-verdura | 19 |
| gastronomia-salumi-e-formaggi | 13 |
| igiene-e-cura-personale | 34 |
| latticini-e-uova | 11 |
| mondo-animali | 11 |
| mondo-bimbi | 18 |
| pane-e-pasticceria | 10 |
| surgelati-e-gelati | 9 |

### Selected 100

- Products: 100. Buckets: hard_yes 19 · in_between 21 · hard_no 60, of which 43 hard_no products have DISCARDED decoy claims.
- Claims: 272. IN_SCOPE 43 · NEEDS_VERIFICATION 37 · DISCARDED 192 · low confidence 30
- Claims by source field: description 272
- Macro category: food and drink 69 · personal care and household 31
- Product gray_zone tags: generic_plus_specific 17, natural_footnote 0, farming_vs_heritage 0, endorsement_named_vs_generic 0, risk_vs_performance 3, comparator_vague_vs_named 1, eco_in_health_heritage 1, senza_pollutant_vs_additive 1, split_slogan 0

| trigger | products | claims |
|---|---|---|
| generic_green | 24 | 32 |
| undefined_natural | 6 | 7 |
| climate_neutral | 0 | 0 |
| vague_comparison | 1 | 2 |
| brand_eco_slogan | 2 | 3 |
| vague_supply_chain | 5 | 5 |
| recycled_recyclable | 9 | 13 |
| biodegradable | 1 | 1 |
| certification | 23 | 37 |
| named_endorsement | 0 | 0 |
| vegan | 8 | 9 |
| farming_practice | 2 | 2 |
| defined_term | 0 | 0 |
| risk_reduction | 1 | 1 |
| named_comparison | 0 | 0 |
| pollutant_free | 1 | 1 |
| out_of_scope | 74 | 203 |

| category | products |
|---|---|
| bevande | 20 |
| carne-e-pesce | 2 |
| dispensa | 13 |
| frutta-e-verdura | 6 |
| gastronomia-salumi-e-formaggi | 6 |
| igiene-e-cura-personale | 19 |
| latticini-e-uova | 6 |
| mondo-animali | 4 |
| mondo-bimbi | 10 |
| pane-e-pasticceria | 8 |
| surgelati-e-gelati | 6 |

Retailer (selected): Eurospin 100 (100%), all from one source file.

Brands (selected, 21 named + 73 unbranded, max 3 per brand): unbranded 73, Amo Essere Bio 3, Fior di Magnolia 3, Eurospin 2, Hello Baby 2, Amo Essere Eco 1, Covim 1, Don Jerez 1, Emmentaler Switzerland 1, Erzherzog Leopold 1, Fortepasso 1, Isola del Sole 1, Italia Zuccheri 1, La Brassicola 1, McGarlet 1, Metropolitan 1, Natura Bella 1, Near 1, Ostro 1, Prime Pappe 1, Radames 1, Total Family 1

## Targets and shortfalls

| target | status | actual |
|---|---|---|
| hard_yes 35 · in_between 35 · hard_no 30 | **NOT MET** | 19 / 21 / 60 (pool has only 42 in_between and 120 hard_no, and 21 hard_yes; every eligible product within the brand cap was taken, and the rest of the 100 was filled from the other buckets) |
| ≥ 20 hard_no with DISCARDED decoys | met | 43 |
| ≤ 3 products per brand | met | max 3 ("unbranded" not counted as a brand) |
| ≤ 40% from one retailer or source file | **NOT MET** | 100% Eurospin. The input is one retailer in one file, so this cap cannot be met. |
| ≥ 25 personal care / household | met | 31 |
| ≥ 40 food and drink | met | 69 |
| ≥ 60 IN_SCOPE claims | **NOT MET** | 43 (pool has 87) |
| ≥ 40 NEEDS_VERIFICATION claims | **NOT MET** | 37 (pool has 39) |
| ≥ 60 DISCARDED claims | met | 192 |
| trigger generic_green in ≥ 3 products | met | 24 |
| trigger undefined_natural in ≥ 3 products | met | 6 |
| trigger climate_neutral in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger vague_comparison in ≥ 3 products | **NOT MET** | 1 (pool has 1) |
| trigger brand_eco_slogan in ≥ 3 products | **NOT MET** | 2 (pool has 2) |
| trigger vague_supply_chain in ≥ 3 products | met | 5 |
| trigger recycled_recyclable in ≥ 3 products | met | 9 |
| trigger biodegradable in ≥ 3 products | **NOT MET** | 1 (pool has 1) |
| trigger certification in ≥ 3 products | met | 23 |
| trigger named_endorsement in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger vegan in ≥ 3 products | met | 8 |
| trigger farming_practice in ≥ 3 products | **NOT MET** | 2 (pool has 2) |
| trigger defined_term in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger risk_reduction in ≥ 3 products | **NOT MET** | 1 (pool has 1) |
| trigger named_comparison in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger pollutant_free in ≥ 3 products | **NOT MET** | 1 (pool has 1) |
| trigger out_of_scope in ≥ 3 products | met | 74 |

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
| 1 | La Brassicola | Birra artigianale italiana "La Rossa" | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 10 | Fior di Magnolia | Salviette struccanti 25 pezzi | hard_yes | brand cap: Fior di Magnolia already has 3 selected products |
| 12 | Fior di Magnolia | Proteggi slip ripiegato 40 pezzi | hard_yes | brand cap: Fior di Magnolia already has 3 selected products |
| 18 | Fior di Magnolia | Assorbente sottile notte senza ali | hard_no | brand cap: Fior di Magnolia already has 3 selected products |
| 20 | Fior di Magnolia | Scrub thalasso corpo | hard_no | brand cap: Fior di Magnolia already has 3 selected products |
| 23 | Near | Crema doposole idratante | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 28 | Hello Baby | Pannolini XL per bambini 16 pezzi | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (2) |
| 29 | Hello Baby | Pannolini maxi per bambini 20 pezzi | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (2) |
| 30 | Hello Baby | Pannolini mini per bambini 24 pezzi | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (2) |
| 31 | Hello Baby | Pannolini pacco doppio junior 36 pezzi | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (2) |
| 34 | Amo Essere Bio | Bevanda alla soia senza zuccheri bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 35 | Amo Essere Bio | Bevanda alle mandorle senza zuccheri bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 42 | Amo Essere Bio | Infuso di finocchio Bio 20 filtri | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 43 | Amo Essere Bio | Snack mini gallette di mais Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 44 | Amo Essere Bio | Snack mini gallette mais e legumi Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 45 | Amo Essere Bio | Spaghetti integrali bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 46 | Amo Essere Bio | Gallette di riso bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 47 | Amo Essere Bio | Farina tipo 00 di grano tenero Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 48 | Amo Essere Bio | Olio extra vergine di oliva biologico | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 49 | Amo Essere Bio | Caramelle zenzero e limone Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 50 | Amo Essere Bio | Biscotti frollini integrali ai 5 cereali bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 56 | Amo Essere Bio | Mix vitality Bio - Misto di frutta secca | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 57 | Amo Essere Bio | Zenzero bio a cubetti | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 58 | Amo Essere Bio | Semi di lino bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 59 | Amo Essere Bio | Mandorle sgusciate Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 60 | Amo Essere Bio | Mix di semi per insalate Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 61 | Amo Essere Bio | Insalata lattughino Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 63 | Amo Essere Bio | Noci sgusciate Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 64 | Amo Essere Bio | Semi di chia bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 65 | Amo Essere Bio | Mix activity Bio - Misto di frutta secca | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 67 | Amo Essere Bio | Tofu al naturale Bio | in_between | brand cap: Amo Essere Bio already has 3 selected products |
| 71 | Near | Crema solare viso e corpo protezione 10 | hard_no | hard_no target (30) filled by higher-scoring products; brand already selected (1) |
| 80 | Le Bricole | Vino rosso | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 81 | unbranded | Pollo a pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 85 | unbranded | Profumo donna eau de parfum "Secret Moon" | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 87 | unbranded | Bocconcini in salsa per gatti multibox mix | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 89 | unbranded | Muffin al lampone e limone | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 90 | unbranded | Pizza margherita 2 pezzi surgelate | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 92 | Best Bräu | Birra Best Bräu scura Premium | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 95 | unbranded | Ciliegie | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 96 | unbranded | Salsa tzatziki | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 97 | unbranded | Lima doppia per calli e duroni | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 99 | unbranded | Sacchetti igienici per cane 3 rotoli | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 102 | unbranded | Focacce tradizionali surgelate 3 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 106 | unbranded | Limoni | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 107 | unbranded | Salame ungherese a fette | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 108 | unbranded | Dentifricio whitening/complete action | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 109 | unbranded | Kefir bianco | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 110 | unbranded | Bocconcini in gelatina per gatti multibox pesce | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 115 | unbranded | Cozze | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 120 | unbranded | Bevanda latte espresso | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 121 | unbranded | Paté per cani al pollo/manzo | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 122 | unbranded | Palloncini bombe d'acqua 80 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 127 | unbranded | Alloro in foglie | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 130 | unbranded | Shampoo idratante/nutriente | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 131 | unbranded | Crema alla vaniglia | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 141 | unbranded | Crema viso | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 142 | unbranded | Yogurt intero bianco | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 150 | unbranded | Avocado | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 151 | unbranded | Lasagne fresche all'uovo | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 152 | unbranded | Profumo uomo eau de parfum "Silver Waterfall" | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 154 | unbranded | Dental stick per cani | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 155 | unbranded | Palloncini Punch Ball 3 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 159 | unbranded | Coniglio intero | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 163 | unbranded | Shampoo illuminante/purificante | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 167 | unbranded | Panino soffice 10 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 168 | unbranded | Zuppa di pesce surgelata | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 170 | unbranded | Salamella suino | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 171 | unbranded | Caramelle marshmallow | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 173 | unbranded | Formaggio Brie de France | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 175 | unbranded | Yogurt intero alla banana | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 177 | unbranded | Palloncini assortiti 14 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 181 | unbranded | Pancetta fina | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 183 | unbranded | Lamponi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 184 | unbranded | Stinco di maiale | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 185 | unbranded | Salviettine detergenti per occhiali | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 187 | unbranded | Patè multibox mix per gatti | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 188 | unbranded | Palloncini decorazione 30 pezzi | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 192 | unbranded | Filetto di suino | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 193 | unbranded | Tè verde | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 195 | unbranded | Mortadella a fette | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 196 | unbranded | Profumo donna eau de parfum "Fabulous Flower" | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |
| 198 | unbranded | Crocchette per cani adulti | hard_no | no claims; hard_no slots went to products with DISCARDED decoys |

## Judgment calls (every low-confidence claim)

| set | idx | claim | triggers → label | reasoning |
|---|---|---|---|---|
| 100 | 5 | «100% italiano - Filiera certificata* ... La filiera di produzione ITALIA ZUCCHERI - CO.PRO.B. sca è certificata secondo lo standard ISO22…» | certification, out_of_scope → NEEDS_VERIFICATION | ISO 22005 is a named traceability (not sustainability) standard; treated as certification of the supply chain, with origin claim out_of_scope. |
| 100 | 5 | «CO.PRO.B. sca è una cooperativa di agricoltori italiani che costituiscono l'unia VERA filiera corta dello zucchero 100% ITALIANO» | vague_supply_chain, out_of_scope → IN_SCOPE | 'VERA filiera corta' asserts supply-chain goodness without verifiable detail; origin part out_of_scope. |
| 100 | 6 | «Ha un gusto forte e naturale.» | undefined_natural, out_of_scope → IN_SCOPE | 'naturale' qualifies the taste rather than the product composition; borderline undefined natural. |
| 100 | 7 | «100% agricoltura integrata» | farming_practice → NEEDS_VERIFICATION | Integrated farming is a concrete practice (and a regional scheme) but no scheme or certifier is named. |
| 100 | 9 | «Questo prodotto è realizzato con materia prima da foreste gestite in maniera sostenibile e da fonti controllate» | generic_green, vague_supply_chain → IN_SCOPE | FSC-style wording with no certifier named: generic 'sostenibile' plus unverified 'fonti controllate'. |
| 100 | 11 | «Questa ricarica corrisponde a 2 confezioni da 500 ml: acquistandola, non solo risparmi i costi dei flaconi, ma contribuisci anche a ridur…» | vague_comparison, out_of_scope → IN_SCOPE | Reduction in plastic/waste with only an implicit comparator (buying two bottles); cost saving part out_of_scope. |
| 100 | 11 | «Ricarica 75% di plastica in meno* ... *75% di plastica in meno rispetto ad un flacone di capacità equivalente» | vague_comparison → IN_SCOPE | Gray zone: comparator_vague_vs_named. Comparator is a generic 'flacone di capacità equivalente', not a named product; treated as vague. |
| 100 | 14 | «Le fibre naturali li rendono ipoallergenici a contatto con la pelle.» | out_of_scope → DISCARDED | 'fibre naturali' is a material description (cotton), like 'lattice di gomma naturale'; hypoallergenic claim is out_of_scope. |
| 100 | 17 | «Questo prodotto è realizzato con materia prima da foreste gestite in maniera sostenibile e da fonti controllate» | generic_green, vague_supply_chain → IN_SCOPE | FSC-style wording with no certifier named: generic 'sostenibile' plus unverified 'fonti controllate'. |
| 100 | 22 | «Privo di solventi» | out_of_scope → DISCARDED | Gray zone: senza_pollutant_vs_additive. Solvent-free refers to the adhesive formulation; read as a product-safety/additive claim rather than a pollutant claim. |
| 100 | 22 | «Non contengono pvc» | pollutant_free → NEEDS_VERIFICATION | Gray zone: senza_pollutant_vs_additive. PVC-free is an environmentally-motivated material exclusion; closest trigger pollutant_free. |
| 100 | 26 | «Crema con ossido di zinco che aiuta a proteggere la pelle del bambino dallo sviluppo di batteri mettendo così la cute al riparo dall'aggr…» | out_of_scope → DISCARDED | Gray zone: risk_vs_performance. Protective/preventive performance phrasing close to risk reduction but no explicit 'riduce il rischio'. |
| 100 | 27 | «ASCIUTTO IMMEDIATO E LUNGA DURATA - Il nucleo a canali permette una maggiore distribuzione del liquido riducendo il rischio di fuoriuscit…» | out_of_scope → DISCARDED | Gray zone: risk_vs_performance. 'riducendo il rischio di fuoriuscite' is risk wording but about leaks (product performance), not health/environment. |
| 100 | 40 | «Consorzio vini di Romagna - Cantina sostenibile» | certification, generic_green → IN_SCOPE | Gray zone: generic_plus_specific. 'Cantina sostenibile' with the Consorzio named but no scheme (e.g. Equalitas) stated; applied the project convention certification + generic_green. |
| 100 | 66 | «Questo prodotto deriva da una filiera corta dove raccolta, selezione e lavaggio rispettano un rigido disciplinare di controllo a tutela d…» | vague_supply_chain, out_of_scope → IN_SCOPE | Unnamed 'rigido disciplinare di controllo' on a short supply chain, framed around quality/freshness. |
| 100 | 77 | «Il Latte Intero Amo Essere Biologico ha una confezione ottenuta da fonti rinnovabili.» | recycled_recyclable → NEEDS_VERIFICATION | Renewable-source (bio-based) packaging with no further detail in this sentence; project convention recycled_recyclable, low. |
| 100 | 77 | «Il tappo e gli strati di plastica della confezione sono ottenuti da fonti rinnovabili, ricavate dalla canna da zucchero invece che da fon…» | recycled_recyclable → NEEDS_VERIFICATION | Bio-based (sugar cane) packaging; project convention maps it to recycled_recyclable, low. |
| 100 | 84 | «Realizzati con filetti di pesce selvaggio!» | farming_practice → NEEDS_VERIFICATION | 'pesce selvaggio' (wild-caught) is a sourcing/fishing-method claim; no rule fits exactly, closest farming_practice. |
| 100 | 116 | «Naturalmente ricchi di acidi grassi omega-3*» | out_of_scope → DISCARDED | Natural-presence idiom (out_of_scope); the * marker has no note body in text, so footnote is null. |
| 100 | 123 | «Senza olio di palma» | out_of_scope → DISCARDED | Palm-oil-free can carry a deforestation connotation but no environmental wording is used; treated as a free-from claim. |
| 100 | 132 | «Questa pallina può comodamente essere raccolta con la paletta senza sbriciolarsi.» | out_of_scope → DISCARDED | Performance/convenience description; borderline between descriptive prose and selling claim. |
| 100 | 132 | «Si può smaltire nel WC domestico o nella raccolta dei rifiuti organici.» | recycled_recyclable → NEEDS_VERIFICATION | Product (not packaging) disposal in organic waste implies compostability; closest trigger recycled_recyclable. |
| 100 | 132 | «1,5 kg di lettiera 100% vegetale assorbono 3 litri di urina.» | vegan, out_of_scope → NEEDS_VERIFICATION | '100% vegetale' on a cat litter is a plant-based material claim; mapped to vegan per the guide's literal list, with absorption performance as out_of_scope. |
| 100 | 132 | «100% vegetale» | vegan → NEEDS_VERIFICATION | Plant-based litter material; mapped to vegan per the guide's literal '100% vegetale' example, though it is not a food/vegan-lifestyle claim. |
| 100 | 132 | «Efficace controllo degli odori - Smaltibile nell'organico e nel WC» | recycled_recyclable, out_of_scope → NEEDS_VERIFICATION | Odour-control performance plus disposal in organic waste (implied compostability); kept whole as the ' - ' joins two badges in one line. |
| 100 | 133 | «Made in Italy» | out_of_scope → DISCARDED | Line split at the inline ' - ' separator, which Eurospin uses between independent badge lines. '+8 anni' is an age warning and is excluded. |
| 100 | 160 | «100% compostabile» | recycled_recyclable → NEEDS_VERIFICATION | Line split at the inline ' - ' separator, which Eurospin uses between independent badge lines. The following '*' note is a trademark disclaimer for the name, not a footnote of this claim. |
| 100 | 174 | «Gocce di luce» | out_of_scope → DISCARDED | Could be a line name rather than a claim; read as shine/performance puffery. |
| 100 | 189 | «Senza olio di palma» | out_of_scope → DISCARDED | Palm-oil-free can carry a deforestation connotation but no environmental wording is used; treated as a free-from claim. |
| 100 | 191 | «VIVA LA SOSTENIBILITA' NELLE VITIVINICOLTURA IN ITALIA» | generic_green, certification → IN_SCOPE | Gray zone: generic_plus_specific. Headline of the VIVA ministerial sustainability programme: the scheme name plus a generic sustainability slogan. |
| reserve | 12 | «Questo prodotto è realizzato con materia prima da foreste gestite in maniera sostenibile e da fonti controllate» | generic_green, vague_supply_chain → IN_SCOPE | FSC-style wording with no certifier named: generic 'sostenibile' plus unverified 'fonti controllate'. |
| reserve | 31 | «Taglia 5 - 11-25 kg - Confezione risparmio» | out_of_scope → DISCARDED | Only 'Confezione risparmio' (value pack) is a selling point; line kept whole since cuts are only at bullets/lines. |

## Validation

`validate2.py` output (final run):

```
[eurospin] selected 100 reserve 83 unusable 17 total 200 of 200
[eurospin] claims checked 401; buckets {'hard_no': 60, 'hard_yes': 19, 'in_between': 21}; max per named brand ('Fior di Magnolia', 3); unbranded selected 73
[eurospin] retailer share 100% Eurospin (40% cap not achievable: single-retailer file)
[eurospin] FAILURES: 0
```

Checks: exactly 100 selected; selected + reserve + unusable = file size; every claim_text part and footnote is an exact substring of its `source_field` (or exactly one element of `certifications`); every label equals the label derived from its triggers; bucket consistency; no duplicate non-null EAN or brand + name; brand cap respected.

Review: A reviewer checked the 100 products selected at that point and found 3 missed out-of-scope sentences and 1 claim taken from a sales-name line. All 4 were fixed. After the re-run, one newly selected product (idx 104, no claims) was checked by hand. The reserve did not get this second review.