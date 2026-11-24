#!/usr/bin/env python3
"""Give ported events the picture their Vic2 original used, matched by event title.
Usage: python port_event_pictures.py <vic2_mod_dir> <vic3_mod_dir>   (needs Pillow)"""
import re, sys, glob
from pathlib import Path
from PIL import Image
V2, V3 = Path(sys.argv[1]), Path(sys.argv[2])
rd = lambda p: p.read_bytes().decode("cp1252", "replace")
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower().replace("&", "and"))
loc = {}
for f in sorted((V2/"localisation").glob("*.csv")):
    for l in rd(f).splitlines():
        p = l.split(";")
        if len(p) > 1 and p[0].strip() and p[0].strip() not in loc: loc[p[0].strip()] = re.sub("§.", "", p[1])
title2pic = {}
for f in (V2/"events").glob("*.txt"):
    for b in re.findall(r"(?:country|province)_event\s*=\s*\{(.*?)\n\}", rd(f), re.S):
        t = re.search(r'title\s*=\s*"?([^"\n]+)', b); p = re.search(r'picture\s*=\s*"?([^"\s]+)', b)
        if t and p: title2pic.setdefault(norm(loc.get(t.group(1).strip(), t.group(1))), p.group(1).strip('"'))
v3loc = {}
for f in glob.glob(str(V3/"localization/english/dod_*.yml")):
    for k, v in re.findall(r'^ (dod_\w+\.\d+)\.t:0 "(.*)"', open(f, encoding="utf-8-sig").read(), re.M): v3loc[k] = v
out = V3/"gfx/event_pictures/dod"; out.mkdir(parents=True, exist_ok=True)
done = matched = 0; converted = set()
for f in glob.glob(str(V3/"events/dod_*.txt")):
    s = open(f).read()
    def repl(m):
        global matched
        eid = m.group(1); pic = title2pic.get(norm(v3loc.get(eid, "")))
        if not pic: return m.group(0)
        src = next((p for ext in (".tga", ".dds", ".png") for p in [V2/"gfx/pictures/events"/(pic + ext)] if p.exists()), None)
        if not src: return m.group(0)
        if pic not in converted:
            Image.open(src).convert("RGBA").save(out/f"{pic}.dds")  # original size, lossless; converted.add(pic)
        matched += 1
        return re.sub(r'event_image = \{ video = "[^"]+" \}', f'event_image = {{ texture = "gfx/event_pictures/dod/{pic}.dds" }}', m.group(0), count=1)
    s2 = re.sub(r"^(dod_\w+\.\d+) = \{.*?^\}", repl, s, flags=re.S | re.M)
    if s2 != s: open(f, "w").write(s2)
print(f"{matched} events now use their original picture; {len(converted)} pictures converted")
