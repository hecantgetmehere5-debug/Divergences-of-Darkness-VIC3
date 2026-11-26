# Divergences of Darkness → Vic3: content plan

Every Vic2 event file (`events/`) and decision file (`decisions/`) is sorted into one of three groups:

- **Keep**: alt-history content unique to DoD. Each group below becomes one Vic3 storyline: journal entries plus events, with decisions where Vic3 decisions fit.
- **Merge**: small files folded into a storyline listed next to them.
- **Drop**: Vic2 mechanics, or generic content Vic3 already covers (or does differently).

`(ev)` = event file, `(dec)` = decision file. The number is how many events or decisions the file has.

---

## KEEP: storylines to rebuild

### 1. Holy Roman Empire & Central Europe
- HRE - 410000 (ev 72): the Prague Proclamation, the Bohemian empire
- Hungary (ev 76, dec 35): Bohemian–Hungarian rivalry, the Crown of St Stephen
- FRA-CZH (ev 27, dec 4): the partition of Venice, the Italian question
- Liberal Kingdom of Germany (ev 33): the German councils and unification
- Grossdeutschland (dec 20), North Germany (dec 7), NGF (dec 1), SGF (dec 1): German formables
- **Merge:** Irredentism (dec 8), only the DoD-specific parts

### 2. Dual Monarchy, Burgundy, Valois & Britain
- DUAFlavor (ev 80), Dual Monarchy (dec 11): the Savoyard and Anglois dilemmas, the succession
- houseofvalois (dec 14), Valois (ev 32): only the parts about the Valois vs the Dual Monarchy. The Italian half (Etruria, Lucca, the Italian war, Transalpina) moved to storyline 3.
- BRGdecisions (dec 13), BRGAnversControl (ev 2)
- England (dec 15), Beornia (dec 4), European_revolutions (ev 33): Scottish and Irish revolutions
- Selon Treaty (ev 2), SelonTreaty (dec 2)
- Batavia (dec 2)
- **Merge:** FRAFlavor (ev 2)

### 3. Italy, Aragon-Italy & Venice-Greece
- Italy - 1242XX (ev 52), Italy (dec 14): Etruria, the Dorians
- CouncilITALY (ev 31)
- Kingdom of Aragon-Italy (ev 13), ARA-ITA (dec 6)
- Venice_GRE (ev 99), GRE (dec 24), Form Greece (dec 1): the flight to Greece, the Exarchates, Crete and Cyprus
- Moved here from storyline 2: the Italian half of Valois and houseofvalois (Etruria, Lucca, the Italian war, Transalpina), and the Etruria/Carbonari events from European_revolutions
- **Merge:** FlighttoSicily (ev 2)

### 4. Iberia
- Iberian Union (ev 10), IberianUnion (dec 7)
- Navarra (ev 17), Greater Euskadia (dec 1)

### 5. Balkans & the Ottoman Fall
- Ottoman Fall (ev 66), OttomanRevoltSetup (ev 1), TUR (dec 17): Illyria, Albania, the Tanzimat
- CROflavor (ev 15), Form Yugoslavia (dec 6): the Illyrian and Serbo-Croat union
- Macedonia (dec 4), Form Romania (dec 3)

### 6. Baltic, Scandinavia & Poland-Lithuania
- End of Kurland (dec 15): only abolishing/annexing Courland. The Neu-Kurland and Antilles purchase decisions moved to storyline 9.
- Rebel Islands - 3712XX (ev 80): the 56 'Rebellion Spreads/Calms Down' events are Vic2 rebel mechanics and are dropped; the 24 Curonian island-purchase events moved to storyline 9
- Baltic (dec 11), Livonia (dec 1), Lithuania (dec 1), PLC (ev 9)
- **Merge:** FlightfromSCA (ev 1)

### 7. Russia, the Steppe & the Caucasus
- RUS (ev 5, dec 14), Russian Borderlands (ev 10), Russian Expansion (ev 1), RussianClaims (dec 1)
- Tatars (ev 14), Tartaria (dec 4)
- Circassia (dec 5), Georgia (dec 10), Transcaucasia (dec 3)
- Turkestan (ev 1, dec 1)

### 8. Persia & the Middle East
- Iran (ev 112, dec 63), Persia (dec 3), IRQ (dec 2)
- Arabia (ev 11, dec 7): the Arab revolt, the House of Saud
- ArabiaUnite (dec 1), ALH (dec 1), UAR (dec 27)
- Caliphate (ev 4), caliphate (ev 5, dec 1), HolyCities (dec 1)
- oman (ev 1, dec 8)
- **Merge:** Druze (ev 2), Levant (ev 2)
- Moved from storyline 5: the Kurdish liberation and Assyrian events and the Nejd-Hejaz 'Question of Arabia' events from Ottoman Fall

### 9. Arcadia & Ameriga (North America)
- Arcadia (ev 35, dec 16): the Vinlander, Septiman and Plantagenian union
- Ameriga events (ev 44), Ameriga decisions (dec 32): Beornia and Lotharingia
- ManifestDestiny (dec 17), Divergences colonization (dec 26)
- Arcadian Native Events (ev 1), DIN-claims (dec 1), Rohnnst (dec 2)
- SPA (dec 1, purchase of the Spanish Pacific), moved from storyline 4
- ColonialNation (ev 21), moved from storyline 3: colonial purchases of Athesia, Cuba, the Caribbean islands and the Falklands

### 10. Gran Colombia, Mexico & the Andes
- CLMFlavor (ev 93), CLM (dec 9), Colombia (dec 15)
- CLM Controlled Dissolution (ev 5), ColombianUnity (ev 5), Congresses of Andagoya (ev 16)
- Mexico Crisis (ev 23), MEX (dec 8), Mesoamerica (dec 68), USCA (dec 1)
- IncaModernization (ev 7), Inca (dec 6)
- Amazonia (ev 40)
- **Merge:** SPACLMwar_end (ev 1); the Andagoya Canal from Canals (dec)
- Moved from storyline 4: Council of Granada (ev 4) and ReclaimGranada (dec 2), which are about the Granadan successor states

### 11. East & Southeast Asia
- Japanese_events (ev 51), japanese_decisions (dec 18), JCW (ev 6)
- China (ev 45, dec 32), china2 (dec 6), Treaty Ports (dec 20)
- Zhourao (dec 4), Indochina (dec 2)
- Nusantara (ev 2), Form Nusantara (dec 3), Nusantara_flavor (dec 1)
- India (ev 1, dec 5), Rajputana (dec 1)
- **Merge:** Goa_patnam (dec 2), New colonies (dec 7)

### 12. Africa & Oceania
- TheBoerWar (ev 27), BoerWar (dec 2), SAF (dec 3), GRQ (dec 2): Leuwin and the Burgundian Cape
- Kongo (ev 5, dec 5), Dahomey Decisions (dec 9), Sokoto (dec 1)
- EthiopiaUnite (dec 40), EthernalAmatsa (ev 7), Oromo_uprising (ev 1)
- Waitangi (dec 4), Polynesia (dec 3)
- **Merge:** African Uncivs (ev 1), Colonial Cores (ev 4), the DoD parts of Annexation in general (ev 19) and UncivFlavor (dec 42), civilising (dec 2)
- Moved from storyline 8: Arabia event (ev 16), the Maghreb caliphates and the Mauretanian/Numidian/Libyan colonies

### 13. Archaeology (unique flavour)
- GMU Koldewey (ev 36), GMU That belongs in a museum (dec 5), archaeology (ev 15, dec 5), TURFlavor (ev 2)

### 14. World history (lore)
- Short Stories (ev 119), Short_Stories (dec 15): the "History of …" texts. These become lore events available at game start.

### 15. World flavour (adapted to Vic3)
Generic flavour events, rewritten to fit Vic3 systems (pops, interest groups, buildings, laws, movements) and to draw on DoD's alt-history setting where it fits.
- **Culture & society:** NobelPrize (ev 176), Olympics (ev 42), Sports (ev 3), WorldFairs (ev 6)
- **Monarchy & politics:** Monarchy (ev 15), SuffragetteMovements (ev 18), TemperanceLeague (ev 12), LiberalRevolutions (ev 29), NationalistMovements (ev 33)
- **Society & labour:** CrimeAndPunishment (ev 10), WorkPlaceEvents (ev 29), AssimilationTroubles (ev 14), Segregation (dec 5)
- **Disasters & economy:** Diseases (ev 7), NaturalDisasters (ev 6), Building Destruction (ev 3), EconomicalEvents (ev 13)
- **Oddities:** MostlyHarmless (ev 3), Monument_destruction (ev 2), Monuments Destruction Decisions (dec 2)

The Nobel Prize chain (176 events) gets condensed to a recurring yearly event plus a few milestone events.

---

## DROP

| Files | Why |
|---|---|
| Canals, Canals Construction, Canals (dec) | Vic3 builds canals natively (Andagoya Canal kept, see 10) |
| Goods, RGOChangeEvents, RGOSpreadEvents | Vic2 resource (RGO) mechanics; Vic3 uses resource discovery |
| PoliticalEvents, Political Scandals, ElectionEvents, UpperHouse, IssueSuggestion | Vic2 party and upper house mechanics |
| CBGeneration, CBsAndCores, InfamyWar_Events, GreatWar_Events, GreatPowers (ev) | Vic2 war and casus belli system; Vic3 uses diplomatic plays |
| GreatPowers (dec) | **Merge** the Scandinavia/Burgundy treaties into storylines 2 and 6 |
| CivilizationAndGunBoats, Scramble for Africa, ColonialUprisings, Exploration, New Colonies (ev) | Vic2 "uncivilized" and colonial mechanics; Vic3 has recognition, colonization and expeditions |
| Revolution_Event, Revolution_Nationalism_Event, Revolution_Relations_Event, Revolution_Spread_Event, Socialism_Facism, Dictatorship, Military Coups, crises, ReformJealousy, extra_decisions (ev+dec), IdeologyEnabling, PanNationalists | Vic2 rebels and ideologies; Vic3 uses movements, interest groups and revolutions |
| NationalValues, NV_Changes, Tech_School_Changes, Law Changes, Economy, Political, Government_flavor, GovernmentFlavor, The Public Demand | Vic2 national value, tech school and reform systems |
| NationalUnification (ev+dec), Independence, VassalRebellion, Force Satellite Release (ev+dec) | Vic3 has formables and subject independence natively |
| CleanUp (ev+dec), V2ME Cleanup, Debug_events, EventIDs, tech_fix, OnAction, setup, russiaAI, Fall of Chinese Dynasties (empty) | Technical/AI helpers, not content |

---

## Rough size

| | Event files | Events | Decision files | Decisions |
|---|---|---|---|---|
| Keep / merge | 90 | ~2,100 | 86 | ~700 |
| Drop | 38 | ~620 | 17 | ~60 |

Counts are approximate. Each kept storyline also gets cut down during the rebuild: Vic2 often used chains of 5–10 events where Vic3 would use one journal entry with a few events.

**Not yet placed:** the 14 'Congress of ...' balance-of-power events in European_revolutions. They react to big formations across several storylines and will be done once those storylines exist.

## Suggested order
Pilot: **1. HRE**, then 2 → 3 → 5 (the European core), then the Americas (9, 10), then the rest, with world flavour (15) last.

---

## Start setup notes (from the DoD fan wiki)

Source: [Victoria 2 Divergences Wiki](https://victoria2divergences.fandom.com/wiki/Victoria_2_Divergences_Wiki) (History and Tag List pages). Things the 1836 Vic3 setup must reproduce for the storylines to work:

- **Gran Colombia (CLM)** starts **at war with Spain**, not as a subject (Spanish counter-invasion after Havana, 1835). Spain still holds Cuba.
- **Egypt (EGY)** independent since 1833 under Muhammad I; the Ottomans and the Hafsids (TUN) are at war with it.
- **Albania (ALB) and Macedonia (MAC)** exist as rebel states (Macedonian revolt 1835) for the Ottoman Civil War journal entry.
- **Hungary (HUN)** independent since 1820.
- **Greece** under Venetian protection since 1827; Venice holds most of Greece except Thrace.
- **HRE (HLR)** ruled from Prague by the young Zsigmond (Sigismund) V, after the Great German War left Central Europe in an uneasy status quo; Austria and Bavaria independent kingdoms.
- **Arcadia:** Vinland, Plantagenia and the Belgian Confederacy at uneasy peace after the War of the Double Alliance (Treaty of Løfby, 1831).

## Tag notes

- **India is HND (Hindustan).** "Form Hindustan" targets HND.
- **IND** is the colonial Indonesia release; its Vic2 culture (Marathi) was an HPM leftover and is now Javan.
- The wiki warns that many tags in the country list are HPM leftovers with no content (e.g. Belgium). They should be pruned during the map setup, once it is clear which ones own nothing.
- A **Vic3 version of DoD** already exists on the Steam Workshop (team project, "tweaked lore"). The port stays independent of it (decided 2026-11-24).

## Gaps and open questions

**Needs the Vic3 game files:** states and capitals for every country, starting pops/armies/history, Vic3 culture definitions for the mod's own cultures (Arcadia and two others have none yet), religion names, map-specific content left out of the storylines (capital moves, renamings, resource discoveries, Crete/Cyprus, Qeshm/Gorgan, Gibraltar, Equinoxia secession, Curonian collapse, Batavia).

**Not ported yet:** the mod's event, decision and leader pictures (stock Vic3 pictures are used); the 14 "Congress of ..." events; the Japanese–Chinese Regency War, "Operation Tsunami", the Mad Baron, the Druze revolt.

**Open decisions:** whether the history decisions should be repeatable; whether `TUR_fascist_dictatorship` stays "Turkey"; all balance numbers are first estimates.

**To verify in game:** `create_country`, `create_character`, `set_state_religion`, diplomatic pact types (puppet, protectorate, dominion, tributary, personal_union), play types (`dp_make_protectorate`, `dp_humiliation`, `dp_open_market`, `dp_independence`), `global_var:` scopes, `clamp_variable`, `change_relations`, `add_claim`, `state_mortality_mult`, on_action merging, flag variant triggers, flag texture size (~730 MB uncompressed), leftover Vic2 `$VARS$` in 3,239 converted text lines.

## Start setup progress

- **Done:** culture definitions for the 33 DoD-specific cultures (`common/cultures/dod_cultures.txt`, format to verify), starting laws for 23 major countries (`common/history/countries/dod_laws.txt`), 37 starting subjects and alliances from the Vic2 diplomacy history (`common/history/diplomacy/dod_diplomacy.txt`).
- **Prepared:** `start_data/provinces.csv` and `start_data/country_summary.csv`, extracted by `tools/vic2_start_data.py`: every Vic2 province's 1836 owner, cores, goods and population by culture and religion (Vic3 scale, x4).
- **Map layer (first pass, built from the Vic3 1.13 game files):** `tools/vic3_map_link.py` links each of the ~40,700 Vic3 land provinces to the Vic2 province on the same ground (fitted from ~900 matching place names, median error ~8 px). `tools/vic3_start_setup.py` then writes `history/states` (split states, homelands, claims from Vic2 cores), `history/pops` (cultures through `start_data/culture_map.json`, ~1.09 billion people), basic `history/buildings` (administration, one farm type, ports), one starting army per country, and the `capital =` lines in `dod_countries.txt`. `.metadata/metadata.json` replaces vanilla's map-tied history folders.
- **Starting wars:** `history/diplomatic_plays/00_dod_starting_wars.txt` sets up the nine wars running on 1836.1.1 in the Vic2 mod's `history/wars`: Spain vs Gran Colombia, the Ottomans and Hafsids vs Egypt, the Albanian and Macedonian revolts, the three-way Ethiopian civil war, Japan vs Korea (Manchu China backing Korea) and Tungning vs the Ming.
- **Economy:** `tools/vic3_economy.py` (run after `vic3_start_setup.py`, it overwrites the basic buildings) rebuilds `history/buildings` from vanilla's 1836 buildings: each state's levels are scaled by DoD/vanilla population (0.5–1.5x, capped by the state's resources and arable land), split between the DoD owners by population and re-owned (manor houses and financial districts included). Every country gets a construction sector and enough barracks for its army at its capital; populated states vanilla left bare get a farm. About 10,500 levels in total (vanilla: ~8,700).
- **Technology, armies and navies:** `tools/vic3_military.py` gives the 100 DoD countries that vanilla has no history for the vanilla tech tier of whoever owned their capital in 1836 (`history/countries/dod_01_technology.txt`). It rebuilds `history/military_formations`: one army per country at its capital with a tier-based mix (line infantry, dragoons and cannon for tiers 1–3; irregulars and hussars below), and 33 fleets (317 ships, ships of the line only for tiers 1–2) based at each naval power's largest naval administration.
- **Rulers and characters:** the mod now replaces vanilla's `history/characters`. `tools/vic3_characters.py` keeps vanilla characters only for the 74 tags whose DoD capital matches vanilla's (Spain, Japan, Austria, Bavaria, Siam, …) and never for the 13 countries with hand-written DoD rulers; every other country gets game-generated rulers. It also ports the Vic2 mod's starting leaders as 242 generals and 38 admirals, with their Vic2 personality and background turned into Vic3 traits.
- **Footholds and fronts:** wars with no shared border would have no front, so the attacker starts on the defender's coast (`FOOTHOLDS` in `vic3_start_setup.py`): Japan holds all of Busan; Spain holds the ports of Texas (Galveston), Zulia (Maracaibo) and Miranda (Barcelona). The defenders get war goals to retake them. `tools/vic3_deployments.py` starts the attackers' armies mobilised on the front of their war (Spain at Maracaibo, Japan at Busan, the Ottomans, Amatsa and Tungning on their borders).
- **Tag collisions:** 295 DoD tags also exist in vanilla, 146 of them as a different country (BRG = Borgu, ARA = Arabia, ENG = England...). `tools/fix_tag_collisions.py` overrides vanilla's country and flag definition files with copies minus the DoD tags, and puts the DoD names in `localization/<lang>/replace/`. For the 211 tags whose DoD capital differs from vanilla's, it also strips their blocks from vanilla's `history/countries`, `population`, `governments` and `ai` (so Burgundy no longer gets Borgu's laws, techs and literacy); `vic3_military.py` then gives them a DoD tech tier. Re-run it after a Vic3 update, then `vic3_military.py`.
- **Recommended countries:** `tools/dod_recommended.py` sets the game-setup screen's recommended countries to DoD ones with lore blurbs: Economic Dominance (Dual Monarchy, Burgundy, Belgian Confederacy, Venice), Hegemony (Scandinavia, Ottomans, Japan, Bohemia), Egalitarian Society (Poland-Lithuania, Gran Colombia, Taiping, Tawantinsuyu), Tutorial (Hungary, Plantagenia, Vietnam, Aragon).
- **Map link at the Bering Strait:** the two maps cut the world at different places. The link now clamps at the map edge, adds hand-picked reference points for Alaska and the Russian Far East (used only for the local correction, so the rest of the world is unchanged), and pulls Asian provinces that land on Vic2 Alaska back to their own state.
- **Generator order:** `vic3_map_link.py` → `vic3_start_setup.py` → `vic3_economy.py` → `vic3_military.py` → `vic3_economy.py` again (fleets need the naval bases, barracks need the armies) → `vic3_deployments.py`; `vic3_characters.py` any time after the capitals exist.
- **Still to do:** an economy that reflects DoD's own history rather than vanilla's geography ; OLD and ANB own no Vic3 province after the link; vanilla `history/countries` still loads for vanilla tags (laws and techs). Untested in game.
