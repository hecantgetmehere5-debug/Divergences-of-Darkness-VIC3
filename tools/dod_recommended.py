"""Recommend DoD countries on the game-setup screen, with DoD descriptions.

The recommended countries come from each objective's `recommended_tags`. This overrides
vanilla's two objective files with copies that list DoD countries, and writes each
country's name and lore blurb for every objective it appears under.

Usage: py tools/dod_recommended.py <vic3_game_dir>
"""
import re, sys
from pathlib import Path

V3 = Path(sys.argv[1])
MOD = Path(__file__).resolve().parent.parent / "DoD_Vic3"

RECOMMENDED = {
    "objective_economic_dominance": ["DUA", "BRG", "NBG", "VEN"],
    "objective_hegemon": ["SCA", "TUR", "JAP", "BOH"],
    "objective_egalitarian_society": ["PLC", "CLM", "TAI", "INC"],
    "objective_tutorial": ["HUN", "PLA", "DAI", "ARA"],
}

LORE = {
    "DUA": "Since the Treaty of Rome the crowns of England and France have rested on one head. King Henri X rules from Paris over Anglois, English, French, Provencal and Irish subjects who agree on little but their distrust of each other. Can the Dual Monarchy forge a single Anglois people, or will the Channel split it in two?",
    "BRG": "From Antwerp, the Protestant kingdom of Burgundy commands the richest ports of the Low Countries, a sphere of German princes along the Rhine, Java and the Cape. Its people are the most literate in Europe and its merchants the boldest. Will Burgundy build a Rhine Confederacy, claim the crown of France, or rule the seas through trade?",
    "NBG": "Victorious in the War of the Double Alliance, the Belgian Confederacy is the heart of Arcadianism: the dream of one free Union for all the peoples of eastern Arcadia. Chancellor Louise Geloes-Randwijck must turn a fragile peace into a continent. Can the Confederacy unite Arcadia before Vinland and Plantagenia recover?",
    "VEN": "The Most Serene Republic never fell. Venice protects Greece, holds the Aegean and trades from the Adriatic to the Levant, while the Ottoman Empire tears itself apart next door. Will the Lion of Saint Mark carve out a Greek empire, or drown in the politics of Italy?",
    "SCA": "The Kalmar Union endures. From Copenhagen, Scandinavia rules the Nordic lands, Finland, Scotland, Estonia and Pomerania, with colonies from Hispaniola to the Philippines. Its ambition is the Dominium Maris Baltici, but Bohemia and Poland-Lithuania stand in the way. Will the Baltic become a Scandinavian lake?",
    "TUR": "Thirty years of civil war between the reformer Suleiman II and the reactionary Mustafa IV have bled the Sublime Porte dry. Egypt, Albania and Macedonia are in open revolt and Hungary, Illyria and Venice circle like vultures. Can the Ottomans survive the century, or will the empire fall apart for good?",
    "JAP": "Japan has looked outward. Its settlers hold Kita Kaigan across the northern ocean, and its armies have landed at Busan to bring Joseon to heel, with Manchu China behind Korea. Will Japan build an empire around the Pacific rim, or overreach on the Asian mainland?",
    "BOH": "After the Great German War the Bohemian crown kept Bohemia, Silesia, Brandenburg and Saxony, and Prague is the seat of the Kingdom of the Germans. The child-king Sigismund V inherits the legacy of the Stone Emperor. Will Bohemia proclaim a Thousand Year Reich and unite the German lands?",
    "PLC": "The Polish-Lithuanian Commonwealth still stands, a noble republic stretching from the Baltic towards Ruthenia, squeezed between Scandinavia and the Russian successor states. Its Sejm can reform or let the Commonwealth crumble. Will Poland-Lithuania renew the Golden Liberty for a modern age?",
    "CLM": "Born from the wars of independence, Gran Colombia reaches from Mexico to the Andes. Since the Havana disaster of 1835 a Spanish army has landed on its shores. Can the Congress hold the republic together through war, the Caste War and its own ambitions?",
    "TAI": "The Taiping Heavenly Kingdom has torn southern China from the Manchu throne, preaching a new faith and the equality of all under Heaven. Its rivals in Beijing and Nanjing want it destroyed. Will the Heavenly Kingdom remake China, or fall like every dynasty before it?",
    "INC": "Tawantinsuyu lives. The Inca empire survived the conquistadors and now faces the modern world under Pachacuti II, who wants to modernise without losing the sun faith of the Inti. Can the Sapa Inca build a new Andean power?",
    "HUN": "Hungary won its independence from the Ottomans in 1820 and now governs itself for the first time in centuries. Its Magyar nobility, its many minorities and its hungry neighbours will test the young kingdom. A good first country for learning the game.",
    "PLA": "Plantagenia, the Anglo-French kingdom of eastern Arcadia, lost lands to the Belgian Confederacy at the Treaty of Lofby and must rebuild. A manageable size, clear rivals and the Arcadian question make it a good start.",
    "DAI": "Vietnam rules the eastern shore of Indochina, between the Chinese successor states and the colonial powers arriving by sea. A compact country with room to grow, and a good first country.",
    "ARA": "Aragon governs Catalonia, Valencia and southern Italy, and its princes sit on foreign thrones, Macedonia among them. Its fleets and the Council of Italy give it a hand in every Mediterranean quarrel. A rich, approachable start.",
}

out = []
for name in ("00_objective_tutorial.txt", "01_player_objectives.txt"):
    t = (V3 / "common/objectives" / name).read_text(encoding="utf-8-sig")
    for obj, tags in RECOMMENDED.items():
        t = re.sub(rf"(^{obj}\s*=\s*\{{.*?recommended_tags\s*=\s*\{{)[^}}]*\}}",
                   lambda m: m.group(1) + " " + " ".join(tags) + " }", t, count=1, flags=re.S | re.M)
    (MOD / "common/objectives").mkdir(parents=True, exist_ok=True)
    (MOD / "common/objectives" / name).write_text(
        "# DoD override of the vanilla file: the recommended countries are DoD countries (tools/dod_recommended.py).\n" + t,
        encoding="utf-8-sig")

loc = ["﻿l_english:"]
for tag, text in LORE.items():
    loc.append(f' {tag}_FLAVOR_TEXT: "{text}"')
for obj, tags in RECOMMENDED.items():
    for tag in tags:
        loc.append(f' {obj}_name_{tag}: "#v ${tag}$#!"')
        loc.append(f' {obj}_desc_{tag}: "#lore ${tag}_FLAVOR_TEXT$#!"')
d = MOD / "localization/english/replace"
d.mkdir(parents=True, exist_ok=True)
(d / "dod_recommended_l_english.yml").write_text("\n".join(loc) + "\n", encoding="utf-8")
print("recommended:", {k: " ".join(v) for k, v in RECOMMENDED.items()})
