"""Give the events written new for Vic3 a fitting vanilla event picture.

Those events were all set to one of five stock videos. This script reads each event's
English title and description, matches them against themed keyword rules, prefers a
picture from the storyline's region, and rotates between equal choices so neighbouring
events don't share one image. Events with a restored original picture (texture = ...)
are not touched.

Usage: py tools/pick_event_pictures.py
"""
import collections, re, zlib
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "DoD_Vic3"
STOCK = {"unspecific_politicians_arguing", "unspecific_signed_contract", "unspecific_military_parade",
         "europenorthamerica_springtime_of_nations", "europenorthamerica_political_extremism"}

REGION = {  # file prefix -> region tag used to choose between pictures
    "afr": "africa", "asi": "asia", "asf": "asia", "east": "asia", "per": "mideast", "clm": "samerica",
    "ame": "namerica", "amf": "namerica", "arc": "namerica", "rus": "russia",
}

# (keywords, {region: [videos], "any": [videos]}) - first matching rule wins
RULES = [
    (r"\b(battle|war|invasion|invade|siege|army|armies|troops|campaign|offensive|front|conquest|attack)\b",
     {"any": ["europenorthamerica_before_the_battle", "unspecific_military_parade", "southamerica_war_civilians"],
      "asia": ["ep2_japanese_artillery", "asia_sepoy_mutiny"], "mideast": ["middleeast_battlefield_trenches"],
      "namerica": ["europenorthamerica_american_civil_war"], "russia": ["ep1_cossacks"]}),
    (r"\b(fleet|navy|naval|admiral|ships?|harbou?r|sail)\b",
     {"any": ["unspecific_naval_battle", "unspecific_steam_ship", "ep2_active_shipyard"]}),
    (r"\b(revolt|revolution|uprising|rebels?|rebellion|riot|insurrection|barricades?|mutiny)\b",
     {"any": ["votp_barricade", "europenorthamerica_springtime_of_nations", "africa_public_protest"],
      "asia": ["asia_sepoy_mutiny", "ep1_donghak_rebellion"], "samerica": ["rp1_social_banditry"]}),
    (r"\b(conspir\w*|secret|plot|carbonari|society|spies|spy)\b",
     {"any": ["votp_conspiring", "ep1_clandestine_meeting", "votp_agitators_sneaking"]}),
    (r"\b(protest|strike|workers|labou?r|union)\b",
     {"any": ["africa_public_protest", "asia_union_leader", "votp_agitator_speaking"]}),
    (r"\b(king|queen|emperor|empress|crown|coronation|throne|succession|heir|regent|regency|dynasty|abdicat\w*|sultan|shah|tsar|khan)\b",
     {"any": ["votp_monarch_holding_court", "ip4_abdication", "unspecific_ruler_speaking_to_people"],
      "mideast": ["ep1_persian_court"], "asia": ["ep2_important_japanese_men_negotiating"]}),
    (r"\b(treaty|alliance|negotiat\w*|diplomat\w*|accord|pact|peace|congress|envoy)\b",
     {"any": ["unspecific_signed_contract", "ep1_power_blocs", "ep1_transfer_of_authority"],
      "africa": ["africa_diplomats_negotiating"], "asia": ["ep2_important_japanese_men_negotiating"]}),
    (r"\b(parliament|election|vote|assembly|constitution|reform|law|council|diet|senate)\b",
     {"any": ["unspecific_politicians_arguing", "asia_politician_parliament_motion", "southamerica_election"]}),
    (r"\b(church|pope|bishop|faith|relig\w*|holy|caliph\w*|mosque|temple|priest|saint)\b",
     {"any": ["southamerica_christianity", "middleeast_islam", "europenorthamerica_judaism"],
      "asia": ["asia_buddhism", "asia_confucianism_shinto", "asia_hinduism_sikhism"], "africa": ["africa_animism"],
      "mideast": ["middleeast_islam"]}),
    (r"\b(excavat\w*|ruins?|archaeolog\w*|expedition|explor\w*|museum|ancient|tomb)\b",
     {"any": ["africa_desert_expedition", "middleeast_jungle_expedition", "europenorthamerica_art_gallery"]}),
    (r"\b(colon\w*|settlers?|frontier|natives?)\b",
     {"any": ["africa_construction_colony", "asia_westerners_arriving", "ip4_colonial_exploitation_going_well"],
      "namerica": ["europenorthamerica_native_american"], "samerica": ["rp1_amazon_exploitation"]}),
    (r"\b(slave\w*|slavery|abolition\w*)\b",
     {"any": ["southamerica_slave_chains", "southamerica_slaves_night"]}),
    (r"\b(famine|harvest|plague|cholera|disease|epidemic|flood|drought|winter|earthquake)\b",
     {"any": ["asia_dead_cattle_poor_harvest", "unspecific_sick_in_hospital", "ip5_harsh_winter", "unspecific_devastation"]}),
    (r"\b(fire|burn\w*|destroy\w*|ruined|disaster)\b", {"any": ["unspecific_fire", "unspecific_devastation"]}),
    (r"\b(railway|railroad|train|canal|factory|industr\w*|mine|mining|steam)\b",
     {"any": ["unspecific_trains", "unspecific_gears_pistons", "ip4_mining_scene", "southamerica_factory_opening"]}),
    (r"\b(trade|merchant|market|bank\w*|company|companies|gold|money|debt)\b",
     {"any": ["europenorthamerica_capitalists_meeting", "asia_farmers_market", "europenorthamerica_gold_prospectors"]}),
    (r"\b(university|science|scholar|nobel|prize|art|opera|theat\w*|book|press|newspaper|history of)\b",
     {"any": ["ip4_university_lecture", "ep2_intellectual_writer", "ep1_printing_press", "ip5_theater"]}),
    (r"\b(olympic\w*|games|fair|exhibition|festival|sport\w*)\b",
     {"any": ["unspecific_world_fair", "ip2_cross_cultural_festival"]}),
    (r"\b(crime|prison|police|trial|court|bandit\w*|murder|assassin\w*)\b",
     {"any": ["votp_prison", "votp_hostile_court", "ip3_police_raid", "southamerica_public_figure_assassination"]}),
    (r"\b(nation\w*|unity|unif\w*|independen\w*|patriot\w*|freedom|liberty)\b",
     {"any": ["europenorthamerica_springtime_of_nations", "unspecific_ruler_speaking_to_people", "votp_garibaldi"]}),
]
FALLBACK = {"any": ["unspecific_politicians_arguing", "votp_realist_household", "unspecific_ruler_speaking_to_people",
                    "europenorthamerica_rich_and_poor"],
            "asia": ["ip2_india_urban_scene", "ep2_japanese_cityscape"], "africa": ["africa_city_center"],
            "mideast": ["ep1_central_asian_city", "middleeast_middleclass_cafe"], "samerica": ["rp1_brazilian_city"],
            "russia": ["europenorthamerica_russian_serfs"]}

loc = {}
for f in (MOD / "localization/english").glob("dod_*.yml"):
    for line in f.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        m = re.match(r'\s*([\w.]+):\d*\s*"(.*)"\s*$', line)
        if m:
            loc[m.group(1)] = m.group(2).lower()

changed, used = 0, collections.Counter()
for f in sorted((MOD / "events").glob("dod_*.txt")):
    region = REGION.get(f.stem.split("_")[1], "europe")
    text = f.read_text(encoding="utf-8-sig")

    def repl(m):
        global changed
        ev, body = m.group(1), m.group(2)
        cur = re.search(r'event_image = \{ video = "(\w+)" \}', body)
        if not cur or cur.group(1) not in STOCK:
            return m.group(0)
        words = " ".join(loc.get(k, "") for k in re.findall(r"(?:title|desc)\s*=\s*([\w.]+)", body))
        table = next((t for pat, t in RULES if re.search(pat, words)), FALLBACK)
        choices = table.get(region) or table["any"]
        pick = choices[zlib.crc32(ev.encode()) % len(choices)]
        used[pick] += 1
        if pick != cur.group(1):
            changed += 1
        return m.group(0).replace(cur.group(0), f'event_image = {{ video = "{pick}" }}')

    new = re.sub(r"^([\w.]+\.\d+) = \{(.*?)^\}", repl, text, flags=re.S | re.M)
    if new != text:
        f.write_text(new, encoding="utf-8-sig")
print(f"events re-pictured: {changed}; distinct pictures now used: {len(used)}")
print(used.most_common(8))
