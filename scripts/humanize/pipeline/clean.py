#!/usr/bin/env python3
"""Clean a merged catalog: drop junk cues and foreign-script cues, and neutralise house references.

Prose about a rule and an example sentence need different substitutions: rewriting a house name to
"the consuming repo" inside a Dutch example sentence produces broken Dutch, so examples get a
neutral placeholder that still reads as a sentence.
"""
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

HOUSE_PROSE = {
    "en": [
        (re.compile(r"\s*The twente\.dev house rule bans the 'niet x maar y' template outright in its own copy\.", re.I),
         " A consuming repo may ban the template outright in its own copy; read its AGENTS.md."),
        (re.compile(r"the banners of twente\.dev that carry the dash as data", re.I),
         "a house asset whose ratified form carries the dash as data"),
        (re.compile(r"twente\.dev", re.I), "the consuming repo"),
        (re.compile(r"\bRyan\b"), "the owner"),
    ],
    "nl": [
        (re.compile(r"de banners van twente\.dev die het streepje in datavorm dragen", re.I),
         "een vastgesteld huismiddel dat het streepje in datavorm draagt"),
        (re.compile(r"(?:van|op|bij|voor)\s+twente\.dev", re.I), "van de eigen organisatie"),
        (re.compile(r"twente\.dev", re.I), "de eigen organisatie"),
        (re.compile(r"\bRyan\b"), "de eigenaar"),
    ],
}

HOUSE_EXAMPLES = [
    (re.compile(r"#twentedev\b", re.I), "#devmeetup"),
    (re.compile(r"\btwente\.dev\b", re.I), "devmeetup.nl"),
    (re.compile(r"\bTwente\.dev\b"), "Devmeetup.nl"),
    (re.compile(r"\bhallo@twente\.dev\b", re.I), "hallo@devmeetup.nl"),
    (re.compile(r"\bRyan's\b"), "Peter's"),
    (re.compile(r"\bRyans\b"), "Peters"),
    (re.compile(r"\bRyan\b"), "Peter"),
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


def clean_entry(entry, keys, foreign_ok, lang):
    cues = [c for c in (clean_cue(c, foreign_ok) for c in entry.get("cues", [])) if c]
    entry["cues"] = dedupe(cues)
    for field in (keys["definition"], keys["fp"], keys["name"]):
        if entry.get(field):
            for pattern, replacement in HOUSE_PROSE[lang]:
                entry[field] = pattern.sub(replacement, entry[field])
    for text_field in ("cues",):
        entry[text_field] = [sub_examples(c) for c in entry[text_field]]
    for ex in entry.get(keys["examples"], []):
        for k in list(ex):
            ex[k] = sub_examples(ex[k])
    return entry


def sub_examples(text):
    for pattern, replacement in HOUSE_EXAMPLES:
        text = pattern.sub(replacement, text)
    return text


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
            clean_entry(entry, keys, foreign_ok=(lang != "en" and category == "translationese"), lang=lang)
            after += len(entry["cues"])
    catalog["count"] = sum(len(v) for v in catalog["categories"].values())
    json.dump(catalog, open(path, "w"), ensure_ascii=False, indent=1)
    blob = json.dumps(catalog, ensure_ascii=False)
    print(f"cues {before} -> {after}; entries {catalog['count']}; house refs left: {len(re.findall('twente[.]dev|Ryan', blob, re.I))}")
