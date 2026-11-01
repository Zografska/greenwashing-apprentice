# ECGT gold set — 100 NaturaSì products

This is a gold evaluation set for a detector of claims under the EU ECGT rules (Directive 2024/825), built from `clean/naturasi.json`. It uses the same method as the Carrefour set (`golden_set_ecgt_100.json`), and the guide and project conventions from that set apply unchanged. Every claim is copied verbatim from its source field. Each label is derived mechanically from the claim's triggers: only out_of_scope gives DISCARDED; any group-A trigger gives IN_SCOPE; otherwise a group-B trigger gives NEEDS_VERIFICATION. defined_term cancels undefined_natural. The file contained no existing annotation fields.

Files: `golden_set_ecgt_naturasi_100.json` (selected), `golden_set_ecgt_naturasi_reserve.json` (the other 97 usable products, labelled the same way), and this README.

Accounting: 100 selected + 97 reserve + 3 unusable = 200 records in the file.

## Field mapping (NaturaSì)

| Output field | Source |
|---|---|
| product_id | `product_id` |
| ean | `ean` (null for 20 bulk/fresh items) |
| name | `name` |
| category | `origin_file` |
| source_file | constant `clean/naturasi.json` |
| source_index | position in the JSON array |
| retailer | constant `NaturaSì` |
| brand | derived from the `url` slug (the part after the product-name slug), with 12 manual fixes |
| claims[].source_field | always `certifications` (the badge list). |
| not extracted | `description`, which holds only «Certificazioni: …» (a copy of the badge list), «Denominazione legale: …» (the sales name) and «Ricetta: …» (the ingredient list); `url` |

## Retailer-specific decisions

NaturaSì listings have no marketing prose: the only claims are the certification badges. Because the badges are a closed list of 60 values, every badge was labelled with **one fixed mapping**, so each badge gets the same triggers wherever it appears:

| badge | triggers → label | gray zone |
|---|---|---|
| Agricoltura biologica, Demeter, BDIH, BioCeq, Cosmebio, Detergenza Pulita AIAB | certification → NV | – |
| NaTrue, Natural Cosmetics Standard, Nature Care Product, BIOS - NaturCosmetics, Icea Incensi Naturali | certification → NV | natural_footnote (a natural claim defined by a named standard) |
| BIOS - EcoClean / BioClean, Bio Eco Cosmesi AIAB, ICEA Eco Bio Cosmesi, EcoBioControl, BioAgriCert | certification → NV | generic_plus_specific (eco/bio word in a named scheme; *not* generic_green) |
| Equosolidale, Slow Cosmetique | certification (low) → NV | – |
| Vegan OK, Vegan society | vegan, certification → NV | – |
| ricetta vegana | vegan → NV | – |
| prodotto da nostra filiera | vague_supply_chain → IN | – |
| coltivazione sostenibile | generic_green, vague_supply_chain → IN | – |
| con dolcificanti naturali | undefined_natural (low) → IN | – |
| Prodotto inserito nel Prontuario AIC… | named_endorsement (low) → NV | endorsement_named_vs_generic |
| Spiga barrata | out_of_scope (low) → DISC | endorsement_named_vs_generic |
| nutrition, free-from, Kosher, nichel tested, farina macinata a pietra, cereali antichi, con pasta madre, da latte crudo… | out_of_scope → DISC | – |
| corrosivo, pericolo_salute (hazard pictograms), grande formato (pack size) | not extracted | – |


One consequence: 181 of the 197 usable products carry «Agricoltura biologica», so almost the whole pool is hard_yes. The in_between and hard_no targets cannot be met (see below).


## Unusable records

3 records were set aside.

| idx | EAN | name | reason |
|---|---|---|---|
| 165 | 8020033000121 | Acqua frizzante in vetro | no marketing text: no certification badges, and description holds only the legal name |
| 40 | 4260183213673 | Latte di cocco 3,8% di grassi | duplicate of idx 25 (same brand + name «Latte di cocco 3,8% di grassi», EAN 4260183213673 vs 4260183213529); kept the record with more badges/longer text |
| 72 | 8019010424951 | Mais dolce lavorato dal fresco | duplicate of idx 31 (same brand + name «Mais dolce lavorato dal fresco», EAN 8019010424951 vs 8019010119291); kept the record with more badges/longer text |

## Counts

### Usable pool (197)

- Products: 197. Buckets: hard_yes 177 · in_between 18 · hard_no 2, of which 2 hard_no products have DISCARDED decoy claims.
- Claims: 577. IN_SCOPE 48 · NEEDS_VERIFICATION 290 · DISCARDED 239 · low confidence 63
- Claims by source field: certifications 577
- Macro category: food and drink 184 · personal care and household 13
- Product gray_zone tags: generic_plus_specific 3, natural_footnote 7, farming_vs_heritage 0, endorsement_named_vs_generic 8, risk_vs_performance 0, comparator_vague_vs_named 0, eco_in_health_heritage 0, senza_pollutant_vs_additive 0, split_slogan 0

| trigger | products | claims |
|---|---|---|
| generic_green | 1 | 1 |
| undefined_natural | 3 | 3 |
| climate_neutral | 0 | 0 |
| vague_comparison | 0 | 0 |
| brand_eco_slogan | 0 | 0 |
| vague_supply_chain | 45 | 45 |
| recycled_recyclable | 0 | 0 |
| biodegradable | 0 | 0 |
| certification | 192 | 242 |
| named_endorsement | 8 | 8 |
| vegan | 42 | 46 |
| farming_practice | 0 | 0 |
| defined_term | 0 | 0 |
| risk_reduction | 0 | 0 |
| named_comparison | 0 | 0 |
| pollutant_free | 0 | 0 |
| out_of_scope | 131 | 239 |

| category | products |
|---|---|
| bevande | 16 |
| bevande-vegetali | 7 |
| carne-pesce-e-salumi | 8 |
| casa-e-giardino | 7 |
| cereali-e-legumi | 13 |
| colazione-e-merende | 18 |
| cura-della-persona | 6 |
| dispensa-e-condimenti | 15 |
| gastronomia | 15 |
| latte-formaggi-e-uova | 15 |
| pasta-riso-e-farine | 22 |
| prodotti-da-forno | 25 |
| proteine-vegetali | 8 |
| surgelati-e-gelati | 6 |
| tisane-e-infusi | 6 |
| vino-e-birra | 5 |
| yogurt-e-kefir | 5 |

### Selected 100

- Products: 100. Buckets: hard_yes 80 · in_between 18 · hard_no 2, of which 2 hard_no products have DISCARDED decoy claims.
- Claims: 301. IN_SCOPE 7 · NEEDS_VERIFICATION 169 · DISCARDED 125 · low confidence 43
- Claims by source field: certifications 301
- Macro category: food and drink 87 · personal care and household 13
- Product gray_zone tags: generic_plus_specific 3, natural_footnote 7, farming_vs_heritage 0, endorsement_named_vs_generic 8, risk_vs_performance 0, comparator_vague_vs_named 0, eco_in_health_heritage 0, senza_pollutant_vs_additive 0, split_slogan 0

| trigger | products | claims |
|---|---|---|
| generic_green | 1 | 1 |
| undefined_natural | 3 | 3 |
| climate_neutral | 0 | 0 |
| vague_comparison | 0 | 0 |
| brand_eco_slogan | 0 | 0 |
| vague_supply_chain | 4 | 4 |
| recycled_recyclable | 0 | 0 |
| biodegradable | 0 | 0 |
| certification | 95 | 133 |
| named_endorsement | 8 | 8 |
| vegan | 30 | 34 |
| farming_practice | 0 | 0 |
| defined_term | 0 | 0 |
| risk_reduction | 0 | 0 |
| named_comparison | 0 | 0 |
| pollutant_free | 0 | 0 |
| out_of_scope | 67 | 125 |

| category | products |
|---|---|
| bevande | 5 |
| bevande-vegetali | 5 |
| carne-pesce-e-salumi | 7 |
| casa-e-giardino | 7 |
| colazione-e-merende | 9 |
| cura-della-persona | 6 |
| dispensa-e-condimenti | 7 |
| gastronomia | 4 |
| latte-formaggi-e-uova | 14 |
| pasta-riso-e-farine | 8 |
| prodotti-da-forno | 10 |
| proteine-vegetali | 4 |
| tisane-e-infusi | 5 |
| vino-e-birra | 5 |
| yogurt-e-kefir | 4 |

Retailer (selected): NaturaSì 100 (100%), all from one source file.

Brands (selected, 71 named, max 3 per brand): Isola Bio 3, Sonett 3, Albacara 2, Aries 2, Baule Volante 2, Berchtesgadener Land 2, Berici Infusi 2, Bionova 2, Capre Felici 2, Cupper 2, Formaggi Debbene 2, Girolomoni 2, I Genuini 2, Iasa 2, Il Cerreto 2, Karma 2, Lab Nat 2, NaturaSì 2, Piu Bene 2, Primavera 2, Prometeo 2, Rapunzel 2, Sojade 2, Sottolestelle 2, Terre e Tradizioni 2, The Bridge 2, We Are 2, A. Vogel 1, Altromercato 1, Amicucina 1, Antico Caseificio Pompeano 1, Antico Molino Rosso 1, Antico Podere Bernardi 1, Bio Busti 1, Bio Fattorie d'Italia 1, Bio Happy 1, Bioalleva 1, Bioearth 1, Biovida 1, Biovitagral 1, Ca Verde 1, Cascine Orsine 1, Castello Di Arcano 1, Castello Di Tassarolo 1, Dr. Antonio Martins 1, Eco Blu 1, Ecor Bodycare 1, Enolea 1, Fattoria di Vaira 1, Fior Di Loto 1, Fior di Loto 1, Flora 1, Gautschi 1, Isola Plus 1, L'Antica Cucina 1, La Buona Terra 1, La Decima 1, Le Biodelizie 1, Le Carline 1, Le Terre di Ecor 1, Mas Del Gnac 1, Molinet 1, Molinum 1, Natural Food 1, Pievalta 1, Si Essenziali 1, Tomarchio 1, Victor Collection 1, Voelkel 1, Yogi Tea 1, Zuger 1

## Targets and shortfalls

| target | status | actual |
|---|---|---|
| hard_yes 35 · in_between 35 · hard_no 30 | **NOT MET** | 80 / 18 / 2 (pool has only 18 in_between and 2 hard_no; every eligible product within the brand cap was taken, and the rest of the 100 was filled from the other buckets) |
| ≥ 20 hard_no with DISCARDED decoys | **NOT MET** | 2 (only 2 in the pool) |
| ≤ 3 products per brand | met | max 3 |
| ≤ 40% from one retailer or source file | **NOT MET** | 100% NaturaSì. The input is one retailer in one file, so this cap cannot be met. |
| ≥ 25 personal care / household | **NOT MET** | 13 (pool has 13) |
| ≥ 40 food and drink | met | 87 |
| ≥ 60 IN_SCOPE claims | **NOT MET** | 7 (pool has 48) |
| ≥ 40 NEEDS_VERIFICATION claims | met | 169 |
| ≥ 60 DISCARDED claims | met | 125 |
| trigger generic_green in ≥ 3 products | **NOT MET** | 1 (pool has 1) |
| trigger undefined_natural in ≥ 3 products | met | 3 |
| trigger climate_neutral in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger vague_comparison in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger brand_eco_slogan in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger vague_supply_chain in ≥ 3 products | met | 4 |
| trigger recycled_recyclable in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger biodegradable in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger certification in ≥ 3 products | met | 95 |
| trigger named_endorsement in ≥ 3 products | met | 8 |
| trigger vegan in ≥ 3 products | met | 30 |
| trigger farming_practice in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger defined_term in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger risk_reduction in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger named_comparison in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger pollutant_free in ≥ 3 products | **NOT MET** | 0 (pool has 0) |
| trigger out_of_scope in ≥ 3 products | met | 67 |

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
| 1 | Baule Volante | Le Brioscine semintegrali al cioccolato | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 3 | NaturaSì | Riso Ribe semilavorato per risotti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 4 | NaturaSì | Riso Ribe | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 7 | NaturaSì | Farina di avena integrale italiana | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 8 | NaturaSì | Riso Ribe integrale per risotti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 9 | NaturaSì | Farina di ceci italiani | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 10 | Aries | Pane ciabatta con farina di Timilìa e olive a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 11 | Aries | Pane integrale con noci e curcuma a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 15 | Aries | Pane segale-backferment a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 16 | NaturaSì | Crackers semintegrali salati in superficie | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 17 | Aries | Pane integrale con semi di zucca a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 18 | Aries | Pane di farina di Russello con semi misti a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 19 | Aries | Panini integrali con semi misti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 21 | Aries | Pane di farro monococco e semi di zucca a lievitazione naturale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 22 | NaturaSì | Pane bauletto di grano Turanicum | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 28 | NaturaSì | Cicerchia decorticata spezzata | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 29 | NaturaSì | Orzo tostato solubile | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 31 | NaturaSì | Mais dolce lavorato dal fresco | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 32 | Aries | Pizza a pala con pomodoro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 34 | NaturaSì | Creste di gallo semintegrali di farro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 35 | I Genuini | Pangrattato di farro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 37 | NaturaSì | Gelato al caffè | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 39 | NaturaSì | Succo di mela e mirtillo | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 42 | NaturaSì | Quinoa bianca italiana 250 g | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 43 | We Are | Cinnamon rolls bio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 44 | NaturaSì | Sugo olive e capperi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 45 | Aries | Pizzetta Margherita | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 47 | NaturaSì | Farina di farro integrale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 48 | NaturaSì | Grissini semintegrali senza sale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 50 | NaturaSì | Gelato al cioccolato | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 51 | Karma | Kéfruit fiori di sambuco | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 52 | Il Cerreto | Farro monococco decorticato | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 54 | NaturaSì | Polpa di pomodoro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 59 | Sojade | Dessert cioccolato | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 60 | NaturaSì | Gelato alla vaniglia | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 61 | NaturaSì | Succo di mela e zenzero | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 62 | NaturaSì | Fagioli borlotti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 63 | NaturaSì | Novellini semintegrali latte e miele | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 65 | Aries | Pizzette con funghi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 67 | NaturaSì | Riso nero integrale italiano | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 68 | NaturaSì | Gallette Soffioni di riso integrale e cereali | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 69 | Karma | Limonata fermentata | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 70 | NaturaSì | Farro dicocco integrale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 71 | Baule Volante | Biscotti del Lagaccio con pasta madre | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 73 | Aries | Pizza margherita | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 75 | Terre e Tradizioni | Farina tipo 1 di grano maiorca | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 77 | NaturaSì | Succo di mela bag in box | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 78 | Il Cerreto | Zuppa di farro monococco miglio e lenticchie rosse | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 81 | Aries | Pinza | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 83 | NaturaSì | Farina integrale di grano tenero | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 85 | Karma | Kombucha Guava | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 86 | NaturaSì | Grano saraceno decorticato italiano | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 88 | NaturaSì | Pomodori pelati in lattina | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 89 | Aries | Torta al formaggio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 92 | Sottolestelle | Pane bauletto alla segale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 93 | NaturaSì | Succo e polpa di pera | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 94 | NaturaSì | Piselli spezzati | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 95 | NaturaSì | Frollini yogurt e nocciole | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 96 | NaturaSì | Passata di pomodoro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 97 | Aries | Pizza Senatore Cappelli alle verdure senza formaggio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 99 | Girolomoni | Rigatoni trafilatura ruvida | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 100 | Karma | Kombucha - melograno | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 101 | NaturaSì | Cacao 100 | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 102 | NaturaSì | Soia edamame lavorata dal fresco | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 103 | NaturaSì | Tagliatelle all'uovo | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 105 | NaturaSì | Fusilli semintegrali di farro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 107 | NaturaSì | Croissant vegani con crema di nocciole e cacao | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 108 | NaturaSì | Fagioli borlotti lavorati dal fresco | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 109 | NaturaSì | 6 uova fresche | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 110 | Girolomoni | Mezze maniche Senatore Cappelli | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 111 | NaturaSì | Succo di mela e bergamotto | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 112 | NaturaSì | Cioccolato extra fondente 85% con fave di cacao | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 113 | NaturaSì | Sugo all’arrabbiata | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vague_supply_chain) are already covered by ≥ 3 selected products; brand already selected (2) |
| 114 | We Are | Bevanda allo zenzero | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 118 | Baule Volante | Zuppa Rusticana | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 122 | Aries | Torta salata zucca e radicchio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 127 | We Are | Praline al cioccolato ripiene di gelato alla nocciola | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 128 | Yogi Tea | LA SELEZIONE DEI FAVORITI | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (1) |
| 132 | Isola Bio | Bevanda vegetale di avena zero zuccheri | hard_yes | brand cap: Isola Bio already has 3 selected products |
| 135 | Il Cerreto | Zuppa di piselli | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 144 | NaturaSì | Gelato al pistacchio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 148 | Baule Volante | Ginger multi pack | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 152 | NaturaSì | Orzo mondo | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 156 | Aries | Torta salata con carciofi | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 159 | NaturaSì | Crackers multicereali con semi di chia | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 160 | Baule Volante | Preparato per burger con lenticchie e semi misti | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 161 | We Are | Gelato fiordilatte senza lattosio | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 164 | Il Cerreto | Yogurt intero alla pesca | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 169 | NaturaSì | Miglio bruno integrale | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 176 | Baule Volante | Cracker di segale e farro - linea benessere | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 177 | Isola Bio | Crema di avena da cucina | hard_yes | brand cap: Isola Bio already has 3 selected products |
| 183 | Primavera | Antipasto - tris di affettati | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 185 | NaturaSì | Orzo perlato | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 189 | Aries | Torta salata porri e olive | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 191 | NaturaSì | Semola di grano duro | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification) are already covered by ≥ 3 selected products; brand already selected (2) |
| 192 | NaturaSì | Polpette al sugo plant based | hard_yes | hard_yes target (35) filled by higher-scoring products; its triggers (certification, vegan) are already covered by ≥ 3 selected products; brand already selected (2) |
| 197 | Isola Bio | Bevanda avena chai | hard_yes | brand cap: Isola Bio already has 3 selected products |

## Judgment calls (every low-confidence claim)

| set | idx | claim | triggers → label | reasoning |
|---|---|---|---|---|
| 100 | 0 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 5 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 6 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 14 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 20 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 23 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 24 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 25 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 27 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 30 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 30 | «Slow Cosmetique» | certification → NEEDS_VERIFICATION | Slow Cosmétique is an association label rather than a third-party certification; closest trigger is certification. |
| 100 | 33 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 36 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 38 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 49 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 58 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 64 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 66 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 80 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 87 | «con dolcificanti naturali» | undefined_natural → IN_SCOPE | Undefined 'natural' attribute of the sweeteners; not a regulated term like 'aromi naturali'. |
| 100 | 87 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 90 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 98 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 104 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 106 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| 100 | 116 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 116 | «Spiga barrata» | out_of_scope → DISCARDED | Gray zone: endorsement_named_vs_generic. AIC licensed gluten-free mark: a health/composition certification, not a sustainability one. |
| 100 | 119 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 123 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 124 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 124 | «Spiga barrata» | out_of_scope → DISCARDED | Gray zone: endorsement_named_vs_generic. AIC licensed gluten-free mark: a health/composition certification, not a sustainability one. |
| 100 | 125 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 126 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 140 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 143 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 149 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 150 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 153 | «con dolcificanti naturali» | undefined_natural → IN_SCOPE | Undefined 'natural' attribute of the sweeteners; not a regulated term like 'aromi naturali'. |
| 100 | 153 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| 100 | 157 | «senza caglio animale» | out_of_scope → DISCARDED | Vegetarian-type composition claim; not a vegan claim (milk is still used). |
| 100 | 170 | «con dolcificanti naturali» | undefined_natural → IN_SCOPE | Undefined 'natural' attribute of the sweeteners; not a regulated term like 'aromi naturali'. |
| 100 | 182 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| 100 | 198 | «Prodotto inserito nel Prontuario AIC degli Alimenti, ed. 2024/25» | named_endorsement → NEEDS_VERIFICATION | Gray zone: endorsement_named_vs_generic. Listing by a named body (Associazione Italiana Celiachia) in a health context; handled like the A.I.Nut. example. |
| reserve | 1 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 3 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 4 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 8 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 35 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 51 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 59 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 65 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 69 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 71 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 81 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 85 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 95 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 99 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 100 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 110 | «Equosolidale» | certification → NEEDS_VERIFICATION | Fair-trade badge with no named scheme; treated as an unnamed fair-trade certification. |
| reserve | 122 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 156 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 160 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |
| reserve | 189 | «senza olio di palma» | out_of_scope → DISCARDED | Composition claim; no environmental wording (project convention). |

## Validation

`validate2.py` output (final run):

```
[naturasi] selected 100 reserve 97 unusable 3 total 200 of 200
[naturasi] claims checked 577; buckets {'hard_yes': 80, 'in_between': 18, 'hard_no': 2}; max per named brand ('Sonett', 3); unbranded selected 0
[naturasi] retailer share 100% NaturaSì (40% cap not achievable: single-retailer file)
[naturasi] FAILURES: 0
```

Checks: exactly 100 selected; selected + reserve + unusable = file size; every claim_text part and footnote is an exact substring of its `source_field` (or exactly one element of `certifications`); every label equals the label derived from its triggers; bucket consistency; no duplicate non-null EAN or brand + name; brand cap respected.

Review: The labels come from a fixed badge mapping, so there is no per-product judgment to review. The mapping table above is the full rule set, and all in_between and hard_no selections were checked by hand. The reserve did not get this second review.