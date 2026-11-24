#!/usr/bin/env python3
"""Extract the Vic2 mod's 1836 start (owners, cultures, religions, pops, subjects)
so it can be mapped onto Vic3 states once the Vic3 map files are available.

Usage: python vic2_start_data.py <vic2_mod_dir> <out_dir> <vic3_mod_dir>
Writes:
  <out_dir>/provinces.csv        one row per province: owner, cores, goods, pops by culture
  <out_dir>/country_summary.csv  per country: provinces, Vic3-scale population, culture shares
  <vic3_mod_dir>/common/history/diplomacy/dod_diplomacy.txt  starting subjects and alliances
Vic2 pop sizes count working men; they are multiplied by 4 for Vic3-scale totals.
"""
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path

SRC, OUT, V3 = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
rd = lambda p: p.read_bytes().decode("cp1252", "replace")

names = {}
for line in rd(SRC/"map/definition.csv").splitlines()[1:]:
    p = line.split(";")
    if len(p) > 4 and p[0].strip().isdigit():
        names[int(p[0])] = p[4].strip()

prov = {}
for f in (SRC/"history/provinces").rglob("*.txt"):
    m = re.match(r"\s*(\d+)", f.name)
    if not m:
        continue
    top = re.split(r"\n\d{4}\.\d+\.\d+\s*=", rd(f))[0]
    get = lambda k: re.findall(rf"^\s*{k}\s*=\s*([A-Za-z0-9_]+)", top, re.M)
    prov[int(m.group(1))] = {"owner": (get("owner") or [""])[0], "cores": " ".join(get("add_core")),
                             "goods": (get("trade_goods") or [""])[0]}

pops = defaultdict(Counter)      # province -> (culture, religion) -> size
for f in (SRC/"history/pops/1836.1.1").glob("*.txt"):
    for m in re.finditer(r"^(\d+)\s*=\s*\{(.*?)^\}", rd(f), re.S | re.M):
        pid = int(m.group(1))
        for pm in re.finditer(r"\w+\s*=\s*\{\s*culture\s*=\s*(\w+)\s*religion\s*=\s*(\w+)\s*size\s*=\s*(\d+)", m.group(2)):
            pops[pid][(pm.group(1), pm.group(2))] += int(pm.group(3)) * 4

with open(OUT/"provinces.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["province", "name", "owner", "cores", "trade_goods", "population", "cultures"])
    for pid in sorted(set(prov) | set(pops)):
        p = prov.get(pid, {"owner": "", "cores": "", "goods": ""})
        c = pops.get(pid, Counter())
        w.writerow([pid, names.get(pid, ""), p["owner"], p["cores"], p["goods"], sum(c.values()),
                    "; ".join(f"{cu}/{re_}:{n}" for (cu, re_), n in c.most_common())])

summary = defaultdict(lambda: {"provinces": 0, "pop": 0, "cultures": Counter(), "religions": Counter()})
for pid, p in prov.items():
    if not p["owner"]:
        continue
    s = summary[p["owner"]]; s["provinces"] += 1
    for (cu, re_), n in pops.get(pid, Counter()).items():
        s["pop"] += n; s["cultures"][cu] += n; s["religions"][re_] += n
with open(OUT/"country_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["tag", "provinces", "population", "top_cultures", "top_religions"])
    for tag, s in sorted(summary.items(), key=lambda kv: -kv[1]["pop"]):
        tot = max(s["pop"], 1)
        w.writerow([tag, s["provinces"], s["pop"],
                    "; ".join(f"{c} {100*n/tot:.1f}%" for c, n in s["cultures"].most_common(6)),
                    "; ".join(f"{r} {100*n/tot:.1f}%" for r, n in s["religions"].most_common(3))])

# diplomacy: Vic2 substates/vassals/unions/alliances -> Vic3 pacts
TYPES = {"substate": "puppet", "vassal": "puppet", "union": "personal_union", "alliance": "alliance"}
lines = ["# Starting subjects and alliances, converted from the Vic2 mod's history/diplomacy", "DIPLOMACY = {"]
n = 0
for f in sorted((SRC/"history/diplomacy").glob("*.txt")):
    for m in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}", rd(f), re.S):
        kind = m.group(1).lower()
        if kind not in TYPES:
            continue
        b = m.group(2)
        a = re.search(r'first\s*=\s*"?([A-Z0-9]{3})', b); c = re.search(r'second\s*=\s*"?([A-Z0-9]{3})', b)
        st = re.search(r'start_date\s*=\s*"?(\d+)', b)
        if not (a and c) or (st and int(st.group(1)) > 1836):
            continue
        lines.append(f"\tc:{a.group(1)} ?= {{\n\t\tcreate_diplomatic_pact = {{\n\t\t\tcountry = c:{c.group(1)}\n\t\t\ttype = {TYPES[kind]}\n\t\t}}\n\t}}")
        n += 1
lines.append("}")
d = V3/"common/history/diplomacy"; d.mkdir(parents=True, exist_ok=True)
(d/"dod_diplomacy.txt").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
print(f"{len(prov)} provinces, {sum(sum(c.values()) for c in pops.values()):,} people (Vic3 scale), "
      f"{len(summary)} countries, {n} pacts")
