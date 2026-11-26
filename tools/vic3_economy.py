"""Build the DoD 1836 economy from vanilla's 1836 buildings, re-owned and rescaled.

Vanilla's building history captures where 1836 industry, mines, plantations and
infrastructure sit. For every Vic3 state this script takes vanilla's building levels,
scales them by DoD population / vanilla population (clamped 0.5-1.5x), splits them
between the state's DoD owners by population, and rewrites ownership for the new
owners. Construction sectors are rebuilt per country at its capital, and every
capital gets enough barracks for its starting army.

Run after tools/vic3_start_setup.py. Usage: py tools/vic3_economy.py <vic3_game_dir>
Writes DoD_Vic3/common/history/buildings/00_dod_buildings.txt
"""
import collections, re, sys
from pathlib import Path

V3 = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "DoD_Vic3"


# ---------- tiny Paradox script parser ----------
TOK = re.compile(r'"[^"]*"|[{}=]|[^\s{}="#]+|#[^\n]*')


def parse(text):
    toks = [t for t in TOK.findall(text) if not t.startswith("#")]
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks):
            t = toks[pos]
            if t == "}":
                pos += 1
                return out
            pos += 1
            if pos < len(toks) and toks[pos] == "=":
                pos += 1
                if toks[pos] == "{":
                    pos += 1
                    out.append((t.strip('"'), block()))
                else:
                    out.append((t.strip('"'), toks[pos].strip('"')))
                    pos += 1
            elif t == "{":
                out.append((None, block()))
            else:
                out.append((None, t.strip('"')))
        return out

    return block()


def get(node, key):
    return [v for k, v in node if k == key]


# ---------- vanilla data ----------
vb = collections.defaultdict(lambda: collections.defaultdict(lambda: {"levels": 0, "own": None, "pms": None}))
for f in sorted((V3 / "common/history/buildings").glob("*.txt")):
    for _, states in parse(f.read_text(encoding="utf-8-sig")):
        if not isinstance(states, list):
            continue
        for skey, regions in states:
            if not skey or not skey.startswith("s:"):
                continue
            st = skey[2:]
            for rkey, blds in regions:
                if not isinstance(blds, list):
                    continue
                for k, b in blds:
                    if k != "create_building" or not isinstance(b, list):
                        continue
                    name = get(b, "building")[0]
                    e = vb[st][name]
                    for own in get(b, "add_ownership"):
                        for kind, o in own:
                            lv = int(float((get(o, "levels") or ["1"])[0]))
                            e["levels"] += lv
                            if e["own"] is None:
                                e["own"] = (kind, (get(o, "type") or [None])[0])
                    if not get(b, "add_ownership"):
                        e["levels"] += int(float((get(b, "level") or ["1"])[0]))
                    pm = get(b, "activate_production_methods")
                    if pm and e["pms"] is None:
                        e["pms"] = [v for _, v in pm[0]]

vpop = collections.Counter()
for f in (V3 / "common/history/pops").glob("*.txt"):
    t = f.read_text(encoding="utf-8-sig")
    for m in re.finditer(r"s:(STATE_\w+)\s*=\s*\{(.*?)\n\t\}", t, re.S):
        vpop[m.group(1)] += sum(int(x) for x in re.findall(r"size\s*=\s*(\d+)", m.group(2)))

caps = {}
for f in (V3 / "map_data/state_regions").glob("*.txt"):
    for m in re.finditer(r"^(STATE_\w+)\s*=\s*\{(.*?)^\}", f.read_text(encoding="utf-8-sig"), re.S | re.M):
        cr = re.search(r"capped_resources\s*=\s*\{([^}]*)\}", m.group(2))
        al = re.search(r"arable_land\s*=\s*(\d+)", m.group(2))
        c = dict((k, int(v)) for k, v in re.findall(r"(building_\w+)\s*=\s*(\d+)", cr.group(1))) if cr else {}
        c["_arable"] = int(al.group(1)) if al else 0
        caps[m.group(1)] = c

# ---------- DoD data ----------
dpop = collections.defaultdict(dict)  # state -> tag -> pop
t = (MOD / "common/history/pops/00_dod_pops.txt").read_text(encoding="utf-8-sig")
for m in re.finditer(r"s:(STATE_\w+) = \{(.*?)\n\t\}", t, re.S):
    for r in re.finditer(r"region_state:(\w+) = \{(.*?)\n\t\t\}", m.group(2), re.S):
        dpop[m.group(1)][r.group(1)] = sum(int(x) for x in re.findall(r"size = (\d+)", r.group(2)))
cd = (MOD / "common/country_definitions/dod_countries.txt").read_text(encoding="utf-8-sig")
capital = {m.group(1): c.group(1) for m in re.finditer(r"^(\w{3}) = \{(.*?)^\}", cd, re.S | re.M)
           if (c := re.search(r"^\s*capital = (STATE_\w+)", m.group(2), re.M))}
armies = dict(re.findall(r"c:(\w+) \?= \{.*?count = (\d+)", (MOD / "common/history/military_formations/00_dod_armies.txt").read_text(encoding="utf-8-sig"), re.S))
tag_pop = collections.Counter()
for st, d in dpop.items():
    for tg, n in d.items():
        tag_pop[tg] += n

ARABLE = re.compile(r"_(farm|ranch|plantation|vineyard)$")
SKIP = {"building_construction_sector", "building_subsistence_farm", "building_subsistence_pasture",
        "building_subsistence_rice_paddy", "building_subsistence_orchard", "building_subsistence_fishing_village"}

plan = collections.defaultdict(lambda: collections.defaultdict(dict))  # st -> tag -> building -> (levels, own, pms)
for st, tags in dpop.items():
    tot = sum(tags.values())
    if not tot:
        continue
    scale = min(1.5, max(0.5, tot / vpop[st])) if vpop.get(st) else 1.0
    cap = caps.get(st, {})
    arable_left = {tg: cap.get("_arable", 0) * n / tot for tg, n in tags.items()}
    for name, e in vb.get(st, {}).items():
        if name in SKIP:
            continue
        total = e["levels"] * scale
        if name in cap:
            total = min(total, cap[name])
        for tg, n in tags.items():
            lv = total * n / tot
            if ARABLE.search(name):
                lv = min(lv, arable_left[tg])
                arable_left[tg] -= lv
            lv = round(lv)
            unique = not re.search(r"_(farm|ranch|plantation|vineyard|mine|camp|wharf|station|mill|works|industry|manufactory|workshop|foundry|plant|factory|shipyard|port|barrack|administration|center|university|academy|railway|fortification)$", name)
            if unique:  # monuments: only the main owner, one level
                lv = 1 if n == max(tags.values()) else 0
            if lv >= 1:
                plan[st][tg][name] = [lv, e["own"], e["pms"]]

arable_res = {}
for f in (V3 / "map_data/state_regions").glob("*.txt"):
    for m in re.finditer(r"^(STATE_\w+)\s*=\s*\{(.*?)^\}", f.read_text(encoding="utf-8-sig"), re.S | re.M):
        ar = re.search(r"arable_resources\s*=\s*\{([^}]*)\}", m.group(2))
        if ar and ar.group(1).split():
            arable_res[m.group(1)] = ar.group(1).split()[0].strip('"')
# states vanilla left bare but DoD populated: at least one farm
for st, tags in dpop.items():
    for tg, n in tags.items():
        if n > 50000 and not plan[st][tg] and st in arable_res:
            lv = max(1, min(caps.get(st, {}).get("_arable", 1) or 1, int(n / 150000)))
            plan[st][tg][arable_res[st]] = [lv, ("building", "building_manor_house"), None]

for tg, st in capital.items():
    if tg not in dpop.get(st, {}):
        continue
    b = plan[st][tg]
    b["building_construction_sector"] = [max(1, min(10, round(tag_pop[tg] / 5e6))), ("country", None), None]
    need = int(armies.get(tg, 0))
    if need:
        cur = b.get("building_barrack", [0, ("country", None), None])
        cur[0] = max(cur[0], need)
        b["building_barrack"] = cur
    if "building_government_administration" not in b:
        b["building_government_administration"] = [max(1, min(10, int(tag_pop[tg] / 3e6) + 1)), ("country", None), None]


def ownership(name, st, tg, lv, own):
    kind, typ = own or ("country", None)
    if kind == "building" and typ:
        region = capital.get(tg, st) if typ == "building_financial_district" else st
        return f'add_ownership = {{ building = {{ type = "{typ}" country = "c:{tg}" levels = {lv} region = "{region}" }} }}'
    return f'add_ownership = {{ country = {{ country = "c:{tg}" levels = {lv} }} }}'


out = ["# Generated by tools/vic3_economy.py: vanilla 1836 buildings, rescaled to the DoD population and re-owned.", "BUILDINGS = {"]
count = collections.Counter()
for st in sorted(plan):
    out.append(f"\ts:{st} = {{")
    for tg in sorted(plan[st]):
        out.append(f"\t\tregion_state:{tg} = {{")
        for name, (lv, own, pms) in sorted(plan[st][tg].items()):
            out += ["\t\t\tcreate_building = {", f'\t\t\t\tbuilding = "{name}"', "\t\t\t\t" + ownership(name, st, tg, lv, own), "\t\t\t\treserves = 1"]
            if pms:
                out.append("\t\t\t\tactivate_production_methods = { " + " ".join(f'"{p}"' for p in pms) + " }")
            out.append("\t\t\t}")
            count[name] += lv
        out.append("\t\t}")
    out.append("\t}")
out.append("}")
(MOD / "common/history/buildings/00_dod_buildings.txt").write_text("\n".join(out) + "\n", encoding="utf-8-sig")
print("states with buildings:", len(plan), " total levels:", sum(count.values()))
print("top:", count.most_common(15))
