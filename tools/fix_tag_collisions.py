"""Make the DoD definitions win for every tag that vanilla also uses (BRG is Borgu in vanilla,
ARA is Arabia, ENG is England...).

1. Country definitions and flag definitions: each vanilla file is overridden by a mod file
   of the same name holding vanilla's content minus the tags DoD defines (flags only where
   DoD has its own flags), so the game sees one definition per tag.
2. Names: the DoD names (TAG and TAG_ADJ) of those tags go in localization/<lang>/replace/,
   which overrides vanilla.

Re-run after a Vic3 update. Usage: py tools/fix_tag_collisions.py <vic3_game_dir>
"""
import re, sys
from pathlib import Path

V3 = Path(sys.argv[1])
MOD = Path(__file__).resolve().parent.parent / "DoD_Vic3"
HEADER = "# DoD override of the vanilla file of the same name: vanilla content minus the tags DoD redefines.\n"


def blocks(text):
    """Yield (key, start, end) for every top-level `KEY = { ... }`."""
    i, n = 0, len(text)
    depth = 0
    while i < n:
        c = text[i]
        if c == "#":
            i = text.find("\n", i)
            if i < 0:
                break
            continue
        if depth == 0:
            m = re.compile(r"([A-Za-z0-9_]+)\s*=\s*\{").match(text, i)
            if m and (i == 0 or text[i - 1] in "\n\t "):
                j, d = m.end(), 1
                while d and j < n:
                    if text[j] == "#":
                        j = text.find("\n", j)
                        continue
                    d += {"{": 1, "}": -1}.get(text[j], 0)
                    j += 1
                yield m.group(1), i, j
                i = j
                continue
        i += 1


def keys_of(path):
    return {k for k, *_ in blocks(path.read_text(encoding="utf-8-sig"))}


def strip_file(src, dst, drop):
    text = src.read_text(encoding="utf-8-sig")
    out, pos, removed = [], 0, 0
    for k, s, e in blocks(text):
        if k in drop:
            out.append(text[pos:s])
            pos = e
            removed += 1
    out.append(text[pos:])
    if removed:
        dst.write_text(HEADER + "".join(out), encoding="utf-8-sig")
    return removed


mod_tags = set()
for f in (MOD / "common/country_definitions").glob("dod_*.txt"):
    mod_tags |= keys_of(f)
mod_flags = keys_of(MOD / "common/flag_definitions/dod_flags.txt")

for sub, drop in (("country_definitions", mod_tags), ("flag_definitions", mod_tags & mod_flags)):
    total = 0
    for f in sorted((V3 / "common" / sub).glob("*.txt")):
        total += strip_file(f, MOD / "common" / sub / f.name, drop)
    print(f"{sub}: removed {total} vanilla definitions of DoD tags")

# vanilla history for tags that are a different country in DoD (different capital): drop their
# c:TAG blocks so e.g. Burgundy (BRG) doesn't get Borgu's laws, techs, literacy and parties
dod_cap = {}
for f in (MOD / "common/country_definitions").glob("dod_*.txt"):
    for k, s, e in blocks(f.read_text(encoding="utf-8-sig")):
        c = re.search(r"^\s*capital\s*=\s*(STATE_\w+)", f.read_text(encoding="utf-8-sig")[s:e], re.M)
        if c:
            dod_cap[k] = c.group(1)
van_cap = {}
for f in (V3 / "common/country_definitions").glob("*.txt"):
    t = f.read_text(encoding="utf-8-sig")
    for k, s, e in blocks(t):
        c = re.search(r"capital\s*=\s*(STATE_\w+)", t[s:e])
        if c:
            van_cap[k] = c.group(1)
different = {t for t in mod_tags if t in van_cap and dod_cap.get(t) != van_cap[t]}
(MOD / "common/history/countries/dod_00_different_tags.txt").write_text(
    "# Tags that are a different country in DoD than in vanilla (written by tools/fix_tag_collisions.py).\n"
    "# Vanilla history for these is removed by the override files in this folder and its siblings.\n"
    "# " + " ".join(sorted(different)) + "\n", encoding="utf-8-sig")
TAGBLOCK = re.compile(r"c:([A-Z0-9]{3})\s*\??=\s*\{")
for sub in ("countries", "population", "governments", "government_setup", "ai"):
    removed = files = 0
    for f in sorted((V3 / "common/history" / sub).glob("*.txt")):
        text = f.read_text(encoding="utf-8-sig")
        out, pos, i, n = [], 0, 0, 0
        while True:
            m = TAGBLOCK.search(text, i)
            if not m:
                break
            j, d = m.end(), 1
            while d and j < len(text):
                if text[j] == "#":
                    j = text.find("\n", j)
                    continue
                d += {"{": 1, "}": -1}.get(text[j], 0)
                j += 1
            if m.group(1) in different:
                out.append(text[pos:m.start()])
                pos, n = j, n + 1
            i = j
        if n:
            out.append(text[pos:])
            dst = MOD / "common/history" / sub / f.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(HEADER + "".join(out), encoding="utf-8-sig")
            removed, files = removed + n, files + 1
    print(f"history/{sub}: removed {removed} blocks of {len(different)} different-country tags in {files} files")

# names
for lang in ("english", "french", "german", "spanish"):
    van = set()
    for f in (V3 / "localization" / lang).rglob("*.yml"):
        van |= set(re.findall(r"^\s*([A-Z][A-Z0-9]{2}(?:_ADJ)?):", f.read_text(encoding="utf-8-sig", errors="ignore"), re.M))
    names = {}
    for f in (MOD / "localization" / lang).glob("dod_*.yml"):
        for m in re.finditer(r'^\s*([A-Z][A-Z0-9]{2}(?:_ADJ)?):\d*\s*(".*")\s*$', f.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
            k = m.group(1)
            if k.split("_")[0] in mod_tags and k in van:
                names.setdefault(k, m.group(2))
    if names:
        d = MOD / "localization" / lang / "replace"
        d.mkdir(exist_ok=True)
        (d / f"dod_country_names_l_{lang}.yml").write_text(
            f"﻿l_{lang}:\n" + "".join(f" {k}: {v}\n" for k, v in sorted(names.items())), encoding="utf-8")
    print(f"{lang}: {len(names)} country names override vanilla")
