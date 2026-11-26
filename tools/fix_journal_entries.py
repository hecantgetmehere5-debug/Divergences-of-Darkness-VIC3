"""Convert the DoD journal entries to the Vic3 1.13 outcome layout.

1.13 replaced complete/on_complete, fail/on_fail, invalid/on_invalid and on_timeout with
`outcome = { ... }` blocks, and should_be_pinned_by_default with
should_be_pinned_by_default_uninvolved_or_context. This rewrites every journal entry in
DoD_Vic3/common/journal_entries/dod_*.txt and adds the conclusion texts the new layout needs.

Usage: py tools/fix_journal_entries.py
"""
import re
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent / "DoD_Vic3"
LOC = MOD / "localization/english/dod_journal_outcomes_l_english.yml"


def top_blocks(text):
    for m in re.finditer(r"^(\w+)\s*=\s*\{", text, re.M):
        i, d = m.end(), 1
        while d:
            d += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        yield m.group(1), m.start(), i


def take(body, key):
    """Remove `\tkey = {...}` or `\tkey = value` from a JE body; return (inner, body)."""
    m = re.search(rf"^\t{key}\s*=\s*", body, re.M)
    if not m:
        return None, body
    j = m.end()
    if body[j] == "{":
        i, d = j + 1, 1
        while d:
            d += {"{": 1, "}": -1}.get(body[i], 0)
            i += 1
        inner = body[j + 1:i - 1]
    else:
        i = body.index("\n", j)
        inner = body[j:i].strip()
    end = i + 1 if i < len(body) and body[i] == "\n" else i
    return inner, body[:m.start()] + body[end:]


def indent(inner):
    return "\n".join(("\t" + l if l.strip() else l) for l in inner.strip("\n").split("\n"))


KINDS = [  # trigger key, effect key, suffix, header, effect header, colour, flags, default text
    ("complete", "on_complete", "completed", "je_standard_completion_header", "je_standard_on_completion_header",
     "gold_positive", None, "This chapter of our history has come to a close in our favour."),
    ("fail", "on_fail", "failed", "je_standard_failure_header", "je_standard_on_failure_header",
     "blue_negative", None, "This chapter of our history has ended in failure."),
]

loc = {}
total = 0
for f in sorted((MOD / "common/journal_entries").glob("dod_*.txt")):
    text = f.read_text(encoding="utf-8-sig")
    out, pos = [], 0
    for key, s, e in top_blocks(text):
        body = text[s:e]
        outcomes = []
        for trig, eff, suf, hdr, ehdr, col, flags, txt in KINDS:
            t, body = take(body, trig)
            ef, body = take(body, eff)
            if t is None and ef is None:
                continue
            desc = f"{key}_{suf}_desc"
            loc.setdefault(desc, txt)
            o = [f"\toutcome = {{", f"\t\theader = {hdr}", f"\t\teffect_header = {ehdr}",
                 f"\t\tconclusion_desc = {desc}", f'\t\tcolor = "{col}"',
                 "\t\ttrigger = {", indent(indent(t or "always = no")), "\t\t}"]
            if ef:
                o += ["\t\teffect = {", indent(indent(ef)), "\t\t}"]
            outcomes.append("\n".join(o + ["\t}"]))
        t, body = take(body, "invalid")
        ef, body = take(body, "on_invalid")
        if t is not None:
            desc = f"{key}_invalid_desc"
            loc.setdefault(desc, "This journal entry no longer applies.")
            o = ["\toutcome = {", "\t\tflags = { hidden invalid_outcome }", f"\t\tconclusion_desc = {desc}",
                 "\t\ttrigger = {", indent(indent(t)), "\t\t}"]
            if ef:
                o += ["\t\teffect = {", indent(indent(ef)), "\t\t}"]
            outcomes.append("\n".join(o + ["\t}"]))
        ef, body = take(body, "on_timeout")
        if ef is not None:
            desc = f"{key}_timeout_desc"
            loc.setdefault(desc, "Time has run out.")
            outcomes.append("\n".join(["\toutcome = {", "\t\theader = je_standard_failure_header",
                                       "\t\teffect_header = je_standard_on_failure_header", f"\t\tconclusion_desc = {desc}",
                                       '\t\tcolor = "blue_negative"', "\t\tflags = { timeout }",
                                       "\t\teffect = {", indent(indent(ef)), "\t\t}", "\t}"]))
        body = re.sub(r"^\tshould_be_pinned_by_default\s*=", "\tshould_be_pinned_by_default_uninvolved_or_context =", body, flags=re.M)
        if outcomes:
            body = body[:body.rindex("}")].rstrip() + "\n\n" + "\n\n".join(outcomes) + "\n}"
            total += 1
        out.append(text[pos:s] + body)
        pos = e
    out.append(text[pos:])
    new = "".join(out)
    assert new.count("{") == new.count("}"), f.name
    f.write_text(new, encoding="utf-8-sig")

LOC.write_text("﻿l_english:\n" + "".join(f' {k}: "{v}"\n' for k, v in sorted(loc.items())), encoding="utf-8")
print(f"journal entries converted: {total}; conclusion texts: {len(loc)}")
