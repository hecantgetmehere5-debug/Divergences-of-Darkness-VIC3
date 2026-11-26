"""Print a compact, readable summary of Vic2 event or decision files (for porting by hand).

Usage: py tools/vic2_dump.py <vic2_mod_dir> events|decisions <file name> [<file name> ...]
For each event: id, title, start of the description, options, tags it mentions, and whether it
fires by itself (mean_time_to_happen) or only when triggered. For each decision: key, title,
start of the description and tags.
"""
import re, sys
from pathlib import Path

V2, KIND, NAMES = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
rd = lambda p: p.read_bytes().decode("cp1252", "replace")
loc = {}
for f in sorted((V2 / "localisation").glob("*.csv")):
    for l in rd(f).splitlines():
        p = l.split(";")
        if len(p) > 1 and p[0].strip() and p[0].strip() not in loc:
            loc[p[0].strip()] = re.sub("§.", "", p[1]).strip().replace("\\n", " ")
L = lambda k, n=200: loc.get(k.strip().strip('"'), k.strip().strip('"'))[:n]


def find(name):
    for f in sorted((V2 / KIND).glob("*.txt")):
        if f.stem == name or f.stem.startswith(name + " ") or f.stem.startswith(name + "-"):
            return f
    sys.exit(f"not found: {name}")


for name in NAMES:
    f = find(name)
    print(f"##### {f.name}")
    t = re.sub(r"#[^\n]*", "", rd(f))
    if KIND == "events":
        for b in re.findall(r"(?:country|province)_event\s*=\s*\{(.*?)\n\}", t, re.S):
            i = re.search(r"\bid\s*=\s*(\d+)", b)
            ti = re.search(r'title\s*=\s*"?([^"\n]+)', b)
            d = re.search(r'desc\s*=\s*"?([^"\n]+)', b)
            opts = [L(o, 45) for o in re.findall(r'option\s*=\s*\{\s*name\s*=\s*"?([^"\n]+)', b)]
            tags = sorted(set(re.findall(r"\b(?:tag|owner|exists|civilized)\s*=\s*([A-Z]{3})\b", b)))
            how = "mtth" if "mean_time_to_happen" in b else "triggered"
            print(f"{i.group(1) if i else '?'} [{how}] {L(ti.group(1), 70) if ti else ''} | {L(d.group(1)) if d else ''} | opts {opts} | {tags}")
    else:
        depth, cur, start = 0, None, 0
        for m in re.finditer(r"([\w.]+)\s*=\s*\{|\{|\}", t):
            if m.group(0) == "}":
                depth -= 1
                if depth == 1 and cur:
                    b = t[start:m.end()]
                    tags = sorted(set(re.findall(r"\b(?:tag|owner|exists)\s*=\s*([A-Z]{3})\b", b)))
                    print(f"{cur} | {L(cur + '_title', 60)} | {L(cur + '_desc', 220)} | {tags}")
                    cur = None
            else:
                if m.group(1) and depth == 1:
                    cur, start = m.group(1), m.start()
                depth += 1
