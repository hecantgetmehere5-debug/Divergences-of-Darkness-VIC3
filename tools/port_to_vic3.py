#!/usr/bin/env python3
"""Convert the Vic2 'Divergences of Darkness' mod into a Victoria 3 mod skeleton.

Converts what can be converted without the Vic3 game files:
  - mod metadata
  - localisation (CSV -> YAML)
  - country definitions (tags, colours, cultures, religion; capitals left TODO)
  - flags (.tga -> textured-emblem coats of arms + flag definitions)

Usage:  python port_to_vic3.py <vic2_mod_dir> <output_dir>
Needs Pillow for the flag conversion.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
REPORT = []

# ---------------------------------------------------------------- helpers

def read_text(p: Path) -> str:
    data = p.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def write_bom(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

# ---------------------------------------------------------------- metadata

def metadata():
    meta = {
        "name": "Divergences of Darkness",
        "id": "divergences_of_darkness",
        "version": "0.1.0",
        "supported_game_version": "",
        "short_description": "Port of the Victoria 2 mod Divergences of Darkness.",
        "tags": ["Alternative History"],
        "relationships": [],
        "game_custom_data": {"multiplayer_synchronized": True},
    }
    p = OUT / ".metadata" / "metadata.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, indent=2))

# ---------------------------------------------------------------- localisation

COLOR_CODE = re.compile("§.")  # Vic2 colour codes like §Y ... §W
VALID_KEY = re.compile(r"^[A-Za-z0-9_.\-']+$")


def localisation():
    seen = set()
    total = dupes = bad = vars_ = 0
    for csv in sorted((SRC / "localisation").glob("*.csv")):
        lines = []
        for raw in read_text(csv).splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            parts = raw.split(";")
            if len(parts) < 2:
                continue
            key, text = parts[0].strip(), parts[1]
            if not key:
                continue
            if not VALID_KEY.match(key):
                bad += 1
                continue
            if key in seen:  # Vic2: first loaded definition wins
                dupes += 1
                continue
            seen.add(key)
            text = COLOR_CODE.sub("", text).replace("§", "")
            text = text.replace('"', "'").strip()
            if "$" in text:
                vars_ += 1
            lines.append(f' {key}:0 "{text}"')
            total += 1
        if lines:
            out = OUT / "localization" / "english" / f"dod_{slug(csv.stem)}_l_english.yml"
            write_bom(out, "l_english:\n" + "\n".join(lines) + "\n")
    REPORT.append(f"Localisation: {total} keys written, {dupes} duplicates skipped, "
                  f"{bad} invalid keys skipped, {vars_} lines use Vic2 $VARS$ (need rewriting).")

# ---------------------------------------------------------------- countries

TOP_KV = re.compile(r"^(\w+)\s*=\s*\"?([^\"#\n{]+?)\"?\s*(#.*)?$")


def parse_top_level(text: str) -> dict:
    """Key = value pairs at brace depth 0 (ignores dated history blocks)."""
    out, depth = {}, 0
    for line in text.splitlines():
        if depth == 0:
            m = TOP_KV.match(line.strip())
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2).strip()
        depth += line.count("{") - line.count("}")
    return out


def parse_color(text: str):
    m = re.search(r"color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)", text)
    return tuple(int(x) for x in m.groups()) if m else (128, 128, 128)


def tier_for(name: str) -> str:
    n = name.lower()
    if "empire" in n or "raj" in n:
        return "empire"
    if any(w in n for w in ("duchy", "emirate", "sultanate", "principality", "free city",
                            "city", "khanate", "sheikhdom", "county", "bishopric")):
        return "principality"
    return "kingdom"


def countries():
    tag_files = {}
    for line in read_text(SRC / "common" / "countries.txt").splitlines():
        m = re.match(r'\s*([A-Z0-9]{3})\s*=\s*"([^"]+)"', line)
        if m and m.group(1) not in ("REB", "CLN"):
            tag_files[m.group(1)] = m.group(2)

    history = {}
    for f in (SRC / "history" / "countries").glob("*.txt"):
        history.setdefault(f.name[:3].upper(), f)

    names = {}
    for yml in (OUT / "localization" / "english").glob("*.yml"):
        for m in re.finditer(r'^ ([A-Z0-9]{3}):0 "(.*)"$', yml.read_text("utf-8-sig"), re.M):
            names.setdefault(m.group(1), m.group(2))

    cultures, out, missing_hist = set(), [], []
    for tag, rel in tag_files.items():
        cfile = SRC / "common" / rel
        color = parse_color(read_text(cfile)) if cfile.exists() else (128, 128, 128)
        h = parse_top_level(read_text(history[tag])) if tag in history else {}
        if tag not in history:
            missing_hist.append(tag)
        culture = h.get("primary_culture", "TODO_culture")
        religion = h.get("religion", "TODO_religion")
        cultures.add(culture)
        name = names.get(tag, tag)
        out.append(
            f"{tag} = {{  # {name}\n"
            f"\tcolor = {{ {color[0]} {color[1]} {color[2]} }}\n"
            f"\tcountry_type = recognized\n"
            f"\ttier = {tier_for(name)}\n"
            f"\tcultures = {{ {culture} }}  # TODO verify Vic3 culture name\n"
            f"\treligion = {religion}  # TODO verify Vic3 religion name\n"
            f"\t# capital = STATE_TODO  # Vic2 capital province {h.get('capital', '?')}\n"
            f"}}\n"
        )
    write_bom(OUT / "common" / "country_definitions" / "dod_countries.txt", "\n".join(out))
    REPORT.append(f"Countries: {len(out)} definitions written; {len(missing_hist)} without history "
                  f"files ({', '.join(missing_hist[:15])}{'...' if len(missing_hist) > 15 else ''}).")
    REPORT.append("Cultures used (check against Vic3 common/cultures):\n  " +
                  ", ".join(sorted(cultures)))
    return set(tag_files)

# ---------------------------------------------------------------- flags

VARIANT_TRIGGERS = {  # TODO verify these scripted triggers exist in your Vic3 version
    "republic": ("coa_def_republic_flag_trigger", 10),
    "communist": ("coa_def_communist_flag_trigger", 20),
    "fascist": ("coa_def_fascist_flag_trigger", 20),
    "fascism": ("coa_def_fascist_flag_trigger", 20),
}


def flags(tags):
    from PIL import Image
    tex_dir = OUT / "gfx" / "coat_of_arms" / "textured_emblems"
    tex_dir.mkdir(parents=True, exist_ok=True)
    by_tag, failed = {}, []
    for f in sorted((SRC / "gfx" / "flags").glob("*.tga")):
        m = re.match(r"^([A-Za-z0-9]{3})(?:_([A-Za-z]+))?$", f.stem)
        if not m:
            continue
        tag, variant = m.group(1).upper(), (m.group(2) or "").lower()
        if tag not in tags:
            continue
        name = f"dod_{tag}" + (f"_{variant}" if variant else "")
        try:
            img = Image.open(f).convert("RGBA").resize((128, 128), Image.LANCZOS)
            img.save(tex_dir / f"{name}.dds")  # 128x128 lossless: holds all detail of the 93x64 originals
        except Exception as e:  # noqa: BLE001
            failed.append(f"{f.name}: {e}")
            continue
        by_tag.setdefault(tag, {})[variant] = name

    coa, defs = [], []
    for tag, variants in sorted(by_tag.items()):
        for name in variants.values():
            coa.append(f'{name} = {{\n\tpattern = "pattern_solid.tga"\n\tcolor1 = "black"\n'
                       f'\ttextured_emblem = {{ texture = "{name}.dds" }}\n}}\n')
        base = variants.get("") or variants.get("monarchy") or next(iter(variants.values()))
        body = [f"\tflag_definition = {{\n\t\tcoa = {base}\n\t\tsubject_canton = {base}\n"
                f"\t\tallow_overlord_canton = yes\n\t\tcoa_with_overlord_canton = {base}\n"
                f"\t\tpriority = 1\n\t}}"]
        for v, name in variants.items():
            if v in VARIANT_TRIGGERS:
                trig, prio = VARIANT_TRIGGERS[v]
                body.append(f"\tflag_definition = {{\n\t\tcoa = {name}\n\t\tsubject_canton = {name}\n"
                            f"\t\tpriority = {prio}\n\t\ttrigger = {{ {trig} = yes }}\n\t}}")
        defs.append(f"{tag} = {{\n" + "\n".join(body) + "\n}\n")
    write_bom(OUT / "common" / "coat_of_arms" / "coat_of_arms" / "dod_flags.txt", "\n".join(coa))
    write_bom(OUT / "common" / "flag_definitions" / "dod_flags.txt", "\n".join(defs))
    REPORT.append(f"Flags: {sum(len(v) for v in by_tag.values())} textures for {len(by_tag)} tags; "
                  f"{len(failed)} failed{': ' + '; '.join(failed[:5]) if failed else ''}.")


if __name__ == "__main__":
    metadata()
    localisation()
    tags = countries()
    flags(tags)
    (OUT / "PORT_REPORT.txt").write_text("\n\n".join(REPORT) + "\n")
    print("\n\n".join(REPORT))
