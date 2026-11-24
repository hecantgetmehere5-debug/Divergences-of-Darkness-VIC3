#!/usr/bin/env python3
"""Static audit of the DoD Vic3 mod script. Run from the DoD_Vic3 folder."""
import re, glob, csv
from collections import Counter, defaultdict
src = {f: open(f, encoding="utf-8-sig").read() for f in glob.glob("events/*.txt") + glob.glob("common/**/*.txt", recursive=True)}
dod = {f: s for f, s in src.items() if "dod_" in f}
alltxt = "\n".join(dod.values())
defs = open("common/country_definitions/dod_countries.txt", encoding="utf-8-sig").read()
tags = set(re.findall(r"^([A-Z0-9]{3}) = \{", defs, re.M))
issues = defaultdict(list)

# 1. country tags used but not defined
for f, s in dod.items():
    if "country_definitions" in f or "coat_of_arms" in f or "flag_definitions" in f: continue
    for t in set(re.findall(r"\bc:([A-Z0-9]{3})\b", s)) | set(re.findall(r"change_tag = ([A-Z0-9]{3})\b", s)) | set(re.findall(r"TAG = ([A-Z0-9]{3})\b", s)):
        if t not in tags: issues["undefined tag"].append(f"{t} in {f}")

# 2. cultures used vs known (DoD cultures + every culture in the Vic2 start pops / country defs)
known = set(re.findall(r"^(\w+) = \{", open("common/cultures/dod_cultures.txt", encoding="utf-8-sig").read(), re.M))
for r in csv.DictReader(open("../start_data/provinces.csv")):
    known |= {p.split("/")[0] for p in r["cultures"].split("; ") if p}
known |= set(re.findall(r"cultures = \{ ([\w ]+) \}", defs) and " ".join(re.findall(r"cultures = \{ ([\w ]+) \}", defs)).split())
for c in sorted(set(re.findall(r"cu:(\w+)", alltxt)) | set(re.findall(r"CULTURE = (\w+)", alltxt))):
    if c not in known: issues["unknown culture"].append(c)

# 3. variables read but never set (anywhere)
setv = set(re.findall(r"set_variable = (\w+)", alltxt)) | set(re.findall(r"set_variable = \{ name = (\w+)", alltxt)) \
     | set(re.findall(r"change_variable = \{ name = (\w+)", alltxt))
setg = set(re.findall(r"set_global_variable = (\w+)", alltxt)) | set(re.findall(r"set_global_variable = \{ name = (\w+)", alltxt))
readv = set(re.findall(r"has_variable = (\w+)", alltxt)) | set(re.findall(r"(?<!global_)var:(\w+)", alltxt))
readg = set(re.findall(r"has_global_variable = (\w+)", alltxt)) | set(re.findall(r"global_var:(\w+)", alltxt))
for v in sorted(readv - setv): issues["variable read, never set"].append(v)
for v in sorted(readg - setg): issues["global variable read, never set"].append(v)

# 4. saved scopes used but never saved
saved = set(re.findall(r"save_scope_as = (\w+)", alltxt))
for sc in sorted(set(re.findall(r"scope:(\w+)", alltxt)) - saved - {"from"}): issues["scope used, never saved"].append(sc)

# 5. events whose every option has a trigger (risk: no valid option)
for f, s in dod.items():
    if not f.startswith("events/"): continue
    for m in re.finditer(r"^(dod_\w+\.\d+) = \{(.*?)^\}", s, re.S | re.M):
        opts = re.findall(r"\toption = \{(.*?)\n\t\}", m.group(2), re.S)
        if opts and all(re.search(r"^\t\ttrigger = \{", o, re.M) for o in opts):
            issues["all options conditional"].append(m.group(1))

# 6. duplicate event ids, decisions, JEs, modifiers, loc keys
def dups(name, items):
    c = Counter(items)
    for k, n in c.items():
        if n > 1: issues[name].append(f"{k} x{n}")
dups("duplicate event id", re.findall(r"^(dod_\w+\.\d+) = \{", alltxt, re.M))
for folder, label in [("decisions", "duplicate decision"), ("journal_entries", "duplicate journal entry"), ("modifiers", "duplicate modifier")]:
    dups(label, re.findall(r"^(\w+) = \{", "\n".join(s for f, s in dod.items() if folder in f), re.M))
lockeys = []
for f in glob.glob("localization/english/*.yml"):
    for l in open(f, encoding="utf-8-sig").read().splitlines()[1:]:
        m = re.match(r" (\S+):0 ", l)
        if m: lockeys.append(m.group(1))
        if l.strip() and not l.lstrip().startswith("#") and l.count('"') != 2: issues["bad quotes in loc"].append(f"{f}: {l[:50]}")
dups("duplicate loc key", lockeys)

# 7. on_action entries listed twice
for f, s in dod.items():
    if "on_actions" in f: dups(f"duplicate on_action entry ({f})", re.findall(r"(dod_\w+\.\d+)", s))

# 8. inventory of engine names to verify against the game
inv = {"laws": set(re.findall(r"law_type:(\w+)", alltxt)), "play types": set(re.findall(r"type = (dp_\w+)", alltxt)),
       "pact types": set(re.findall(r"create_diplomatic_pact = \{[^}]*type = (\w+)", alltxt)),
       "modifier keys": set(re.findall(r"^\t(\w+) = -?[\d.]+$", "\n".join(s for f, s in dod.items() if "modifiers" in f), re.M)),
       "religions": set(re.findall(r"rel:(\w+)", alltxt)), "interest groups": set(re.findall(r"ig:(\w+)", alltxt))}
for k, v in issues.items():
    print(f"\n== {k} ({len(v)})"); print("   " + "\n   ".join(v[:25]) + ("\n   ..." if len(v) > 25 else ""))
print("\n== ENGINE NAMES TO VERIFY")
for k, v in inv.items(): print(f"{k}: {', '.join(sorted(v))}")
