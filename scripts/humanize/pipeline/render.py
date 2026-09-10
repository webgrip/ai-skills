#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

CATEGORY_TITLES = {
    "en": {
        "vocabulary": "Vocabulary", "syntax": "Sentence constructions", "rhetoric": "Rhetorical moves and tone",
        "structure": "Paragraph and document structure", "punctuation-format": "Punctuation and formatting",
        "content": "Content and evidence", "artifacts": "Machine residue", "translationese": "Translationese",
    },
    "nl": {
        "vocabulary": "Woordkeus", "syntax": "Zinsconstructies", "rhetoric": "Retorische zetten en toon",
        "structure": "Alinea- en documentstructuur", "punctuation-format": "Interpunctie en opmaak",
        "content": "Inhoud en bewijs", "artifacts": "Machinesporen", "translationese": "Translationese: Engelsvormig Nederlands",
    },
}
LABELS = {
    "en": dict(sev="Severity", scope="Scope", cues="Cues", before="Before", after="After", fp="Do not flag", contents="Contents", intro=(
        "One entry per pattern: what it is, the literal cues, one before/after, the severity tier and when not to flag it. "
        "Severity: **always** (one hit is enough), **cluster** (a tell only in density or co-occurrence), **context** (register decides). "
        "Regex-detectable cues are also in `scripts/patterns.json` under the same id."), name="name", definition="definition", examples="examples",
        before_key="before", after_key="after", fpkey="false_positives", sevkey="severity"),
    "nl": dict(sev="Ernst", scope="Herkomst", cues="Signalen", before="Voor", after="Na", fp="Niet markeren", contents="Inhoud", intro=(
        "Eén entry per patroon: wat het is, de letterlijke signalen, één voor/na, de ernst en wanneer je het niet markeert. "
        "Ernst: **always** (één treffer volstaat), **cluster** (alleen een tell bij opeenhoping), **context** (het register beslist). "
        "Signalen die een regex kan vangen staan ook in `scripts/patterns.json` onder hetzelfde id; `en_id` koppelt aan de Engelse catalogus."), name="naam", definition="definitie", examples="voorbeelden",
        before_key="voor", after_key="na", fpkey="valse_positieven", sevkey="ernst"),
}
MAX_CUES = 18


def code(text):
    fence = "``" if "`" in text else "`"
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def escape_links(text):
    return text.replace("](", "] (").replace("TODO:", "TODO\u2009:")


def anchor(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_entry(entry, lang):
    L = LABELS[lang]
    lines = [f"### {entry[L['name']]} `{entry['id']}`", ""]
    meta = f"{L['sev']}: **{entry[L['sevkey']]}**"
    if lang == "en":
        meta += f" · {L['scope']}: {entry['scope']}"
    else:
        meta += f" · {L['scope']}: {entry['herkomst']}" + (f" · en: `{entry['en_id']}`" if entry.get("en_id") else "")
    lines += [meta, "", escape_links(entry[L["definition"]].strip()), ""]
    cues = [c for c in entry.get("cues", []) if c and len(c) < 90]
    if cues:
        shown = cues[:MAX_CUES]
        more = f" (+{len(cues) - MAX_CUES})" if len(cues) > MAX_CUES else ""
        lines += [f"{L['cues']}: " + " · ".join(code(escape_links(c.strip())) for c in shown) + more, ""]
    ex = next((e for e in entry.get(L["examples"], []) if e.get(L["before_key"]) and e.get(L["after_key"])), None)
    if ex:
        lines += [f"{L['before']}: {escape_links(ex[L['before_key']].strip())}", "", f"{L['after']}: {escape_links(ex[L['after_key']].strip())}", ""]
    fp = (entry.get(L["fpkey"]) or "").strip()
    if fp:
        lines += [f"{L['fp']}: {escape_links(fp)}", ""]
    return "\n".join(lines)


def visible(entry, domains):
    return entry.get("scope") != "language-specific" and (entry.get("domain") or "general") in domains


def render_catalog(catalog, lang, title, order, note="", domains=frozenset({"general"})):
    L = LABELS[lang]
    catalog = {"categories": {c: [e for e in v if visible(e, domains)] for c, v in catalog["categories"].items()}}
    cats = [c for c in order if catalog["categories"].get(c)]
    out = [f"# {title}", "", L["intro"], ""] + ([note, ""] if note else []) + [
           f"{L['contents']}: " + " · ".join(f"[{CATEGORY_TITLES[lang][c]}](#{anchor(CATEGORY_TITLES[lang][c])}) ({len(catalog['categories'][c])})" for c in cats), ""]
    for c in cats:
        out += [f"## {CATEGORY_TITLES[lang][c]}", ""]
        for e in sorted(catalog["categories"][c], key=lambda x: ({"always": 0, "cluster": 1, "context": 2}[x[L["sevkey"]]], x["id"])):
            out.append(render_entry(e, lang))
    return "\n".join(out).rstrip() + "\n"


def scanner_patterns(catalog, lang, skip_language_specific=False):
    L = LABELS[lang]
    rows = []
    for c, entries in catalog["categories"].items():
        for e in entries:
            if skip_language_specific and e.get("scope") == "language-specific":
                continue
            regex = [r for r in e.get("regex", []) if r]
            if not regex:
                continue
            for r in regex:
                if any(m.end() == m.start() for m in re.finditer(r, "a b. c", re.IGNORECASE)):
                    raise SystemExit(f"{e['id']}: regex matches a zero-length span and would fire everywhere: {r}")
            row = {"id": e["id"], "lang": [lang], "category": c, "severity": e[L["sevkey"]], "regex": regex,
                   "hint": e[L["definition"]].split(". ")[0][:140]}
            if e.get("domain"):
                row["domain"] = e["domain"]
            row.update(e.get("flags", {}))
            rows.append(row)
    return rows


if __name__ == "__main__":
    lang, src, md_out, title, domains_out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    order = ["syntax", "rhetoric", "vocabulary", "structure", "punctuation-format", "content", "artifacts", "translationese"]
    catalog = json.load(open(src))
    note = ("Entries that only make sense on Wikipedia or in fiction are held in the catalog data and rendered "
            "separately in the domains file next to this one; the scanner loads them only with --domain.")
    Path(md_out).write_text(render_catalog(catalog, lang, title, order, note))
    domains_title = ("English catalog, domain-scoped entries (Wikipedia, fiction)" if lang == "en"
                     else "Nederlandse catalogus, domeingebonden entries (Wikipedia, fictie)")
    Path(domains_out).write_text(render_catalog(catalog, lang, domains_title, order, "", frozenset({"wikipedia", "fiction"})))
    rows = scanner_patterns(catalog, lang, skip_language_specific=(lang == "en"))
    print(f"{md_out}: {sum(len(v) for v in catalog['categories'].values())} entries, {len(rows)} scanner entries, {sum(len(r['regex']) for r in rows)} regexes")
    json.dump(rows, open(Path(sys.argv[2]).with_suffix(".patterns.json"), "w"), ensure_ascii=False, indent=1)
