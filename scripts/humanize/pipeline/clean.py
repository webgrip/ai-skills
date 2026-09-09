#!/usr/bin/env python3
"""Clean a merged catalog: drop junk cues, house-specific references and foreign-script cues."""
import json
import re
import sys

STOP_CUES = {
    "but", "however", "rather", "it's", "isn't", "it is", "it's not", "not", "and", "or", "so",
    "this", "that", "these", "those", "the", "a", "an", "is", "are", "was", "were", "be",
    "it's about", "isn't about", "not just", "not only", "but also", "but because",
    "that's not", "this isn't just a", "this isn't", "it's not just", "isn't just", "doesn't just",
    "not merely", "not because", "rather than", ", however,", "niet-x-maar-y",
    "maar", "echter", "en", "het is", "dit is",
}
HANGUL = re.compile(r"[가-힯ᄀ-ᇿ㄰-㆏]")
CJK = re.compile(r"[一-鿿぀-ヿ]")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")

HOUSE = [
    (re.compile(r"\s*The twente\.dev house rule bans the 'niet x maar y' template outright in its own copy\.", re.I),
     " A consuming repo may ban the template outright in its own copy; read its AGENTS.md."),
    (re.compile(r"#twentedev\b", re.I), "#devmeetup"),
    (re.compile(r"twente\.dev", re.I), "the consuming repo"),
    (re.compile(r"\bRyan\b"), "the owner"),
]


def clean_cue(cue, foreign_ok):
    cue = cue.strip().strip("“”\"")
    if not cue or len(cue) < 4 or len(cue) > 80:
        return None
    if cue.lower() in STOP_CUES:
        return None
    if not foreign_ok and (HANGUL.search(cue) or CJK.search(cue) or CYRILLIC.search(cue)):
        return None
    if cue.count(" ") > 12:
        return None
    return cue


def dedupe(cues):
    out = []
    for c in cues:
        low = c.lower()
        if any(low != o.lower() and low in o.lower() for o in cues):
            continue
        if low not in {o.lower() for o in out}:
            out.append(c)
    return out


def clean_entry(entry, keys, foreign_ok):
    cues = [c for c in (clean_cue(c, foreign_ok) for c in entry.get("cues", [])) if c]
    entry["cues"] = dedupe(cues)
    for field in (keys["definition"], keys["fp"], keys["name"]):
        if entry.get(field):
            for pattern, replacement in HOUSE:
                entry[field] = pattern.sub(replacement, entry[field])
    for ex in entry.get(keys["examples"], []):
        for k in list(ex):
            for pattern, replacement in HOUSE:
                ex[k] = pattern.sub(replacement, ex[k])
    return entry


if __name__ == "__main__":
    path, lang = sys.argv[1], sys.argv[2]
    keys = ({"definition": "definition", "fp": "false_positives", "name": "name", "examples": "examples"}
            if lang == "en" else
            {"definition": "definitie", "fp": "valse_positieven", "name": "naam", "examples": "voorbeelden"})
    catalog = json.load(open(path))
    before = after = 0
    for category, entries in catalog["categories"].items():
        for entry in entries:
            before += len(entry.get("cues", []))
            clean_entry(entry, keys, foreign_ok=(lang != "en" and category == "translationese"))
            after += len(entry["cues"])
    catalog["count"] = sum(len(v) for v in catalog["categories"].values())
    json.dump(catalog, open(path, "w"), ensure_ascii=False, indent=1)
    blob = json.dumps(catalog, ensure_ascii=False)
    print(f"cues {before} -> {after}; entries {catalog['count']}; house refs left: {len(re.findall('twente|Ryan', blob))}")
