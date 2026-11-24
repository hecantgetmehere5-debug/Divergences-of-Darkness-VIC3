#!/usr/bin/env python3
"""Convert the French, German and Spanish columns of the Vic2 localisation CSVs
into Vic3 YAML, for the same keys the English conversion produced.
Usage: python port_translations.py <vic2_mod_dir> <vic3_mod_dir>
Polish and Russian are skipped: Vic2 stored them in a custom 8-bit encoding."""
import re, sys
from pathlib import Path
V2, V3 = Path(sys.argv[1]), Path(sys.argv[2])
COLS = {2: "french", 3: "german", 5: "spanish"}
COLOR = re.compile("§.")
def slug(n): return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
counts = {}
for lang in COLS.values():
    seen = set()
    for csv in sorted((V2/"localisation").glob("*.csv")):
        out = []
        for raw in csv.read_bytes().decode("cp1252", "replace").splitlines():
            p = raw.split(";")
            if len(p) < 6 or not p[0].strip() or p[0].lstrip().startswith("#"): continue
            key = p[0].strip()
            col = {v: k for k, v in COLS.items()}[lang]
            text = p[col].strip()
            if not text or text.lower() == "x" or key in seen or not re.fullmatch(r"[A-Za-z0-9_.\-']+", key): continue
            seen.add(key)
            text = COLOR.sub("", text).replace("§", "").replace('"', "'")
            out.append(f' {key}:0 "{text}"')
        if out:
            d = V3/"localization"/lang; d.mkdir(parents=True, exist_ok=True)
            (d/f"dod_{slug(csv.stem)}_l_{lang}.yml").write_text(f"l_{lang}:\n" + "\n".join(out) + "\n", encoding="utf-8-sig")
    counts[lang] = len(seen)
print(counts)
