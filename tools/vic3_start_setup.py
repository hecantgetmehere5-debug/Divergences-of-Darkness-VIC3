"""Build the DoD 1836 map layer for Vic3 from the Vic2 start data.

Inputs:  start_data/provinces.csv, start_data/vic3_province_link.csv (tools/vic3_map_link.py),
         start_data/culture_map.json, the Vic3 game dir and the Vic2 mod dir.
Outputs (in DoD_Vic3/):
  common/history/states/00_dod_states.txt            ownership (split states allowed), homelands, claims
  common/history/pops/00_dod_pops.txt                pops by culture and religion
  common/history/buildings/00_dod_buildings.txt      administration, farms, ports
  common/history/military_formations/00_dod_armies.txt  one starting army per country
  common/country_definitions/dod_countries.txt       capital lines filled in
  start_data/vic3_state_owners.csv                   summary for review

Usage: py tools/vic3_start_setup.py <vic3_game_dir> <vic2_mod_dir>
"""
import collections, csv, json, re, sys
from pathlib import Path

V3, V2 = Path(sys.argv[1]), Path(sys.argv[2])
ROOT = Path(__file__).resolve().parent.parent
MOD, DATA = ROOT / "DoD_Vic3", ROOT / "start_data"
IGNORE_TAGS = {"", "CLN"}  # CLN = the Vic2 mod's cleanup dummy

# ---------- load ----------
cmap = json.loads((DATA / "culture_map.json").read_text(encoding="utf-8"))
CUL, REL = cmap["vic2_to_vic3_culture"], cmap["vic2_to_vic3_religion"]

v2 = {}
for r in csv.DictReader(open(DATA / "provinces.csv", encoding="utf-8")):
    pops = []
    for part in filter(None, r["cultures"].split("; ")):
        cr, n = part.rsplit(":", 1)
        c, rl = cr.split("/")
        pops.append((CUL.get(c, c), REL.get(rl, rl), int(n)))
    owner = r["owner"] if r["owner"] not in IGNORE_TAGS else ""
    v2[int(r["province"])] = dict(owner=owner, cores=r["cores"].split() if r["cores"] else [], pops=pops, name=r["name"])

link = collections.defaultdict(list)          # state -> [(vic3 prov, vic2 prov)]
hits = collections.Counter()                  # vic2 prov -> number of vic3 provinces
for r in csv.DictReader(open(DATA / "vic3_province_link.csv", encoding="utf-8")):
    p = int(r["vic2_province"])
    link[r["state"]].append((r["vic3_province"], p))
    if p:
        hits[p] += 1

region_text = "".join(f.read_text(encoding="utf-8-sig") for f in sorted((V3 / "map_data/state_regions").glob("*.txt")))
sinfo = {}
for m in re.finditer(r"^(STATE_\w+)\s*=\s*\{(.*?)^\}", region_text, re.S | re.M):
    b = m.group(2)
    ar = re.search(r"arable_resources\s*=\s*\{([^}]*)\}", b)
    al = re.search(r"arable_land\s*=\s*(\d+)", b)
    pt = re.search(r"\bport\s*=\s*\"?(x[0-9A-Fa-f]{6})", b)
    sinfo[m.group(1)] = dict(
        arable=[x.strip('"') for x in ar.group(1).split()] if ar else [],
        land=int(al.group(1)) if al else 0,
        port="x" + pt.group(1)[1:].upper() if pt else None)

strat = {}
for f in (V3 / "common/strategic_regions").glob("*.txt"):
    for m in re.finditer(r"^(region_\w+)\s*=\s*\{.*?states\s*=\s*\{([^}]*)\}", f.read_text(encoding="utf-8-sig"), re.S | re.M):
        for s in m.group(2).split():
            strat[s] = m.group(1)

# ---------- ownership per state ----------
frag = {}   # state -> {tag: [vic3 provs]}
for st, items in link.items():
    by = collections.defaultdict(list)
    for h, p in items:
        if p and v2[p]["owner"]:
            by[v2[p]["owner"]].append(h)
    frag[st] = by

total_by_tag = collections.Counter()
for by in frag.values():
    for t, ps in by.items():
        total_by_tag[t] += len(ps)

# fold tiny border slivers into the state's main owner (keeps one-state countries intact)
for st, by in frag.items():
    if len(by) < 2:
        continue
    n = sum(len(v) for v in by.values())
    main = max(by, key=lambda t: len(by[t]))
    for t in list(by):
        if t != main and len(by[t]) <= 2 and len(by[t]) / n < 0.2 and total_by_tag[t] > len(by[t]):
            by[main] += by.pop(t)

# ---------- footholds for the starting wars ----------
# Wars with no shared border would have no front, so the attacker starts on the defender's
# coast where its Vic2 troops stand: (state, "all" or "port", tag)
FOOTHOLDS = [
    ("STATE_BUSAN", "all", "JAP"),       # Joseon Fight for Freedom
    ("STATE_TEXAS", "port", "SPA"),      # Colombian War of Independence: Galveston
    ("STATE_ZULIA", "port", "SPA"),      # Maracaibo
    ("STATE_MIRANDA", "port", "SPA"),    # Barcelona
]
for st, what, tag in FOOTHOLDS:
    by = frag.get(st)
    if not by:
        continue
    take = [h for ps in by.values() for h in ps] if what == "all" else [sinfo[st]["port"]]
    for t in list(by):
        by[t] = [h for h in by[t] if h not in take]
        if not by[t]:
            del by[t]
    by.setdefault(tag, [])
    by[tag] += take

# ---------- pops per state fragment ----------
owner_of = {h: t for by in frag.values() for t, ps in by.items() for h in ps}
fpops = collections.defaultdict(collections.Counter)  # (state, tag) -> (cul, rel) -> size
claims = collections.defaultdict(set)
for st, items in link.items():
    for h, p in items:
        t = owner_of.get(h)
        if not p or not t:
            continue
        share = 1 / hits[p]
        for c, r, n in v2[p]["pops"]:
            fpops[(st, t)][(c, r)] += n * share
        for core in v2[p]["cores"]:
            if core != t and core not in IGNORE_TAGS:
                claims[st].add(core)
# Vic2 provinces too small for any Vic3 province to land in: spread their pops over
# the same owner's states, weighted by population already there
lost = 0
for p, d in v2.items():
    if not d["owner"] or hits[p]:
        continue
    keys = [k for k in fpops if k[1] == d["owner"]]
    if not keys:
        lost += sum(n for *_, n in d["pops"])
        continue
    weights = {k: sum(fpops[k].values()) for k in keys}
    wsum = sum(weights.values()) or 1
    for c, r, n in d["pops"]:
        for k in keys:
            fpops[k][(c, r)] += n * weights[k] / wsum

# ---------- capitals ----------
v2cap = {}
for f in (V2 / "history/countries").glob("*.txt"):
    m = re.search(r"^\s*capital\s*=\s*(\d+)", f.read_text(encoding="latin-1"), re.M)
    if m:
        v2cap[f.name[:3]] = int(m.group(1))
tag_pop = collections.Counter()
for (st, t), d in fpops.items():
    tag_pop[t] += sum(d.values())
capital = {}
for t in total_by_tag:
    cands = collections.Counter()
    cp = v2cap.get(t)
    for st, items in link.items():
        if t in frag[st]:
            cands[st] += sum(1 for h, p in items if p == cp and owner_of.get(h) == t)
    best = cands.most_common(1)
    if best and best[0][1] > 0:
        capital[t] = best[0][0]
    else:
        sts = [st for st in frag if t in frag[st]]
        if sts:
            capital[t] = max(sts, key=lambda s: sum(fpops[(s, t)].values()))

# ---------- write states ----------
def hexlist(ps):
    return " ".join(sorted(ps))

out = ["# Generated by tools/vic3_start_setup.py from the Vic2 DoD 1836 start. Do not edit by hand.", "STATES = {"]
rows = []
for st in sorted(frag):
    by = frag[st]
    if not by:
        continue
    out.append(f"\ts:{st} = {{")
    for t in sorted(by, key=lambda t: -len(by[t])):
        out += ["\t\tcreate_state = {", f"\t\t\tcountry = c:{t}", f"\t\t\towned_provinces = {{ {hexlist(by[t])} }}", "\t\t}"]
    cul = collections.Counter()
    for t in by:
        for (c, r), n in fpops[(st, t)].items():
            cul[c] += n
    tot = sum(cul.values()) or 1
    for c, n in cul.most_common():
        if n / tot >= 0.1 or n >= 250000:
            out.append(f"\t\tadd_homeland = cu:{c}")
    for c in sorted(claims[st] - set(by)):
        out.append(f"\t\tadd_claim = c:{c}")
    out.append("\t}")
    rows.append([st, " ".join(f"{t}:{len(by[t])}" for t in by), int(tot)])
out.append("}")
d = MOD / "common/history/states"; d.mkdir(parents=True, exist_ok=True)
(d / "00_dod_states.txt").write_text("\n".join(out) + "\n", encoding="utf-8-sig")

# ---------- write pops ----------
out = ["# Generated by tools/vic3_start_setup.py. Sizes come from the Vic2 DoD 1836 pops (x4).", "POPS = {"]
for st in sorted(frag):
    tags = [t for t in frag[st] if fpops[(st, t)]]
    if not tags:
        continue
    out.append(f"\ts:{st} = {{")
    for t in tags:
        out.append(f"\t\tregion_state:{t} = {{")
        for (c, r), n in fpops[(st, t)].most_common():
            if n >= 100:
                out.append(f"\t\t\tcreate_pop = {{ culture = {c} religion = {r} size = {int(n)} }}")
        out.append("\t\t}")
    out.append("\t}")
out.append("}")
d = MOD / "common/history/pops"; d.mkdir(parents=True, exist_ok=True)
(d / "00_dod_pops.txt").write_text("\n".join(out) + "\n", encoding="utf-8-sig")

# ---------- write buildings ----------
def bld(name, tag, levels):
    return [f"\t\t\tcreate_building = {{", f"\t\t\t\tbuilding = \"{name}\"",
            f"\t\t\t\tadd_ownership = {{ country = {{ country = \"c:{tag}\" levels = {levels} }} }}",
            "\t\t\t\treserves = 1", "\t\t\t}"]

out = ["# Generated by tools/vic3_start_setup.py: a basic economy (administration, farms, ports).", "BUILDINGS = {"]
for st in sorted(frag):
    tags = [t for t in frag[st] if fpops[(st, t)]]
    if not tags:
        continue
    out.append(f"\ts:{st} = {{")
    info = sinfo.get(st, {})
    for t in tags:
        out.append(f"\t\tregion_state:{t} = {{")
        pop = sum(fpops[(st, t)].values())
        if capital.get(t) == st:
            out += bld("building_government_administration", t, max(1, min(10, int(tag_pop[t] / 3e6) + 1)))
        if info.get("arable") and pop > 50000:
            out += bld(info["arable"][0], t, max(1, min(info["land"] or 1, int(pop / 150000))))
        if info.get("port") and owner_of.get(info["port"]) == t:
            out += bld("building_port", t, 1)
        out.append("\t\t}")
    out.append("\t}")
out.append("}")
d = MOD / "common/history/buildings"; d.mkdir(parents=True, exist_ok=True)
(d / "00_dod_buildings.txt").write_text("\n".join(out) + "\n", encoding="utf-8-sig")

# ---------- write armies ----------
out = ["# Generated by tools/vic3_start_setup.py: one army per country in its capital, sized by population.", "MILITARY_FORMATIONS = {"]
for t in sorted(capital):
    st = capital[t]
    if st not in strat:
        continue
    n = max(1, min(40, round(tag_pop[t] / 1.5e6)))
    out += [f"\tc:{t} ?= {{", "\t\tcreate_military_formation = {", "\t\t\ttype = army", f"\t\t\thq_region = sr:{strat[st]}",
            "\t\t\tcombat_unit = {", "\t\t\t\ttype = unit_type:combat_unit_type_line_infantry", f"\t\t\t\tstate_region = s:{st}",
            f"\t\t\t\tcount = {n}", "\t\t\t}", "\t\t}", "\t}"]
out.append("}")
d = MOD / "common/history/military_formations"; d.mkdir(parents=True, exist_ok=True)
(d / "00_dod_armies.txt").write_text("\n".join(out) + "\n", encoding="utf-8-sig")

# ---------- capitals into country definitions ----------
cd = MOD / "common/country_definitions/dod_countries.txt"
text = cd.read_text(encoding="utf-8-sig")
def fill(m):
    tag, body = m.group(1), m.group(2)
    if tag in capital:
        # first run: fill the commented TODO line; later runs: update the existing capital line
        body = re.sub(r"^(\s*)#\s*capital\s*=\s*STATE_TODO\s*(#[^\n]*)?", lambda k: f"{k.group(1)}capital = {capital[tag]}  {k.group(2) or ''}".rstrip(), body, flags=re.M)
        body = re.sub(r"^(\s*)capital\s*=\s*STATE_\w+", lambda k: f"{k.group(1)}capital = {capital[tag]}", body, flags=re.M)
    else:
        body = re.sub(r"^(\s*)capital\s*=\s*(STATE_\w+)", r"\1# capital = STATE_TODO  # was \2, no land after the map link", body, flags=re.M)
    return f"{tag} = {{{body}}}"
text = re.sub(r"^(\w{3}) = \{(.*?)^\}", fill, text, flags=re.S | re.M)
cd.write_text(text, encoding="utf-8-sig")

with open(DATA / "vic3_state_owners.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["state", "owners (tag:vic3 provinces)", "population"]); w.writerows(rows)

print(f"states: {len(rows)}  countries: {len(total_by_tag)}  capitals: {len(capital)}")
print(f"population placed: {int(sum(tag_pop.values())):,}  lost (Vic2 provinces no Vic3 province reached): {lost:,}")
missing = [t for t in total_by_tag if t not in capital]
print("no capital:", missing)
