"""Check which Vic2 DoD events and decisions the port covers.

Reads the KEEP section of docs/PORT_CONTENT_PLAN.md to get the Vic2 event and decision
files that were meant to be ported, then looks for each Vic2 event (by its title) and
decision (by its name) among the port's events, decisions and journal entries. A match is an
equal title after normalising, or a title sharing most of its words.

Usage: py tools/content_audit.py <vic2_mod_dir>
Writes docs/CONTENT_AUDIT.md and start_data/content_audit_missing.csv
"""
import csv, glob, re, sys
from pathlib import Path

V2 = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "DoD_Vic3"
rd = lambda p: p.read_bytes().decode("cp1252", "replace")
STOP = {"the", "of", "a", "an", "and", "in", "to", "for", "on", "at", "by", "with", "from", "is", "our", "we", "de", "la", "le"}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower().replace("&", "and"))


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP and len(w) > 2}


# ---------- which Vic2 files were kept ----------
plan = (ROOT / "docs/PORT_CONTENT_PLAN.md").read_text(encoding="utf-8")
keep = plan.split("## KEEP")[1].split("## DROP")[0]
files = []  # (storyline, name, kinds)
story = ""
for line in keep.splitlines():
    h = re.match(r"### (\d+\. .+)", line)
    if h:
        story = h.group(1)
    for name, kinds in re.findall(r"([A-Za-z0-9_' &.\-]+?)\s*\(((?:ev|dec)[^)]*)\)", line):
        name = name.strip(" -*:").split("**")[-1].strip()
        if name.lower().startswith("merge"):
            name = name.split(":", 1)[-1].strip()
        files.append((story, name, kinds))

# ---------- Vic2 text ----------
loc = {}
for f in sorted((V2 / "localisation").glob("*.csv")):
    for l in rd(f).splitlines():
        p = l.split(";")
        if len(p) > 1 and p[0].strip() and p[0].strip() not in loc:
            loc[p[0].strip()] = re.sub("§.", "", p[1]).strip()


def find(sub, name):
    exact = V2 / sub / f"{name}.txt"
    if exact.exists():
        return exact
    n = norm(name)
    for f in (V2 / sub).glob("*.txt"):  # "Hungary -26540X", "ARC - Arcadia", "Iberian Union-33322X"
        stem = norm(re.sub(r"\s*-\s*\d+X*\s*$", "", f.stem))
        if stem == n or norm(f.stem.split(" - ")[-1]) == n:
            return f
    return None


def decision_keys(text):
    """Keys of the decisions inside political_decisions = { ... } (brace depth 2)."""
    out, depth, i = [], 0, 0
    text = re.sub(r"#[^\n]*", "", text)
    for m in re.finditer(r"([\w.]+)\s*=\s*\{|\{|\}", text):
        tok = m.group(0)
        if tok == "}":
            depth -= 1
        else:
            if m.group(1) and depth == 1:
                out.append(m.group(1))
            depth += 1
    return out


# ---------- port titles ----------
port = {}  # normalised title -> key
port_words = []
for f in glob.glob(str(MOD / "localization/english/dod_*.yml")):
    for k, v in re.findall(r'^\s*([\w.]+):\d*\s*"(.*)"', open(f, encoding="utf-8-sig", errors="ignore").read(), re.M):
        if re.match(r"(dod_\w+\.\d+\.t|dod_\w+|je_dod_\w+)$", k) and not re.search(r"_(desc|d|f|tt|a|b|c)$", k):
            if k.endswith(".t") or not re.search(r"\.\d+", k):
                port.setdefault(norm(v), k)
                port_words.append((words(v), k))


def match(title):
    n = norm(title)
    if not n:
        return None
    if n in port:
        return port[n]
    w = words(title)
    if len(w) >= 2:
        best = max(port_words, key=lambda pw: len(w & pw[0]) / len(w | pw[0]) if pw[0] else 0)
        if best[0] and len(w & best[0]) / len(w | best[0]) >= 0.6:
            return best[1]
    return None


# ---------- audit ----------
rows, summary = [], []
for story, name, kinds in files:
    for sub, kind in (("events", "ev"), ("decisions", "dec")):
        if kind not in kinds:
            continue
        f = find(sub, name)
        if not f:
            summary.append((story, name, kind, 0, 0, "Vic2 file not found"))
            continue
        text = rd(f)
        items = []
        if sub == "events":
            for b in re.findall(r"(?:country|province)_event\s*=\s*\{(.*?)\n\}", text, re.S):
                i = re.search(r"\bid\s*=\s*(\d+)", b)
                t = re.search(r'title\s*=\s*"?([^"\n]+)', b)
                if i and t:
                    items.append((i.group(1), loc.get(t.group(1).strip(), t.group(1).strip())))
        else:
            for k in decision_keys(text):
                items.append((k, loc.get(f"{k}_title", loc.get(k, k.replace("_", " ")))))
        hit = 0
        for iid, title in items:
            m = match(title)
            if m:
                hit += 1
            else:
                rows.append((story, f.name, kind, iid, title))
        summary.append((story, name, kind, len(items), hit, ""))

with open(ROOT / "start_data/content_audit_missing.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["storyline", "vic2_file", "kind", "vic2_id", "title"])
    w.writerows(rows)

tot = sum(s[3] for s in summary)
hit = sum(s[4] for s in summary)
md = ["# Content audit: Vic2 DoD vs the Vic3 port", "",
      "Generated by `tools/content_audit.py`. For every Vic2 file in the KEEP section of the port plan, each event",
      "(by title) and decision (by name) is looked up among the port's events, decisions and journal entries.",
      "A miss means no port item has the same or a very similar title. Some misses are covered under another",
      "name or folded into a journal entry; check `start_data/content_audit_missing.csv` for the full list.", "",
      f"**Total:** {hit} of {tot} matched ({100 * hit // max(tot, 1)}%).", "",
      "| Storyline | Vic2 file | Kind | Items | Matched | Note |", "|---|---|---|---|---|---|"]
for s in summary:
    md.append(f"| {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} | {s[5]} |")
(ROOT / "docs/CONTENT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"matched {hit} of {tot}; missing rows: {len(rows)}; files: {len(summary)}; not found: {sum(1 for s in summary if s[5])}")
