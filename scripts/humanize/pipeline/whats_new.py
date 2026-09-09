#!/usr/bin/env python3
"""Regenerate skills/humanize/whats-new.md: the entries the house did not already have.

An entry counts as new when no baseline source carried it (in_baseline false). Entries scoped to
one language are held in the catalog data and left out of the English listing.
"""
import json
from pathlib import Path

HUMANIZE = Path(__file__).resolve().parents[1]
SKILL = HUMANIZE.parents[1] / "skills" / "humanize"
ORDER = ["syntax", "rhetoric", "vocabulary", "structure", "punctuation-format", "content", "artifacts", "translationese"]
TITLES = {
    "vocabulary": "Vocabulary", "syntax": "Sentence constructions", "rhetoric": "Rhetorical moves and tone",
    "structure": "Paragraph and document structure", "punctuation-format": "Punctuation and formatting",
    "content": "Content and evidence", "artifacts": "Machine residue", "translationese": "Translationese",
}

catalog = json.load(open(HUMANIZE / "catalog" / "catalog-en.json"))
dutch = json.load(open(HUMANIZE / "catalog" / "catalog-nl.json"))
kept = {c: [e for e in es if e["scope"] != "language-specific"] for c, es in catalog["categories"].items()}
total = sum(len(v) for v in kept.values())
fresh = {c: [e for e in es if not e["in_baseline"]] for c, es in kept.items()}
fresh = {c: v for c, v in fresh.items() if v}
new_count = sum(len(v) for v in fresh.values())
dutch_only = [e for es in dutch["categories"].values() for e in es if not e.get("en_id")]

lines = [
    "# What the consolidation added", "",
    f"The English catalog holds {total} entries that apply to English prose. {total - new_count} were already "
    f"covered by the house copy rule or the blog-writer de-AI-ify pass; {new_count} were not. The Dutch catalog "
    f"holds {dutch['count']} entries, {len(dutch_only)} of which have no English counterpart at all. This file "
    "lists the English additions so the gain is visible without reading the whole catalog; entries scoped to one "
    "language are held in the catalog data and left out here.", "",
]
for category in ORDER:
    if category not in fresh:
        continue
    lines += [f"## {TITLES[category]} ({len(fresh[category])})", ""]
    for entry in sorted(fresh[category], key=lambda x: x["id"]):
        first = entry["definition"].split(". ")[0].rstrip(".")
        sources = ", ".join(entry["sources"][:4]) + (" and others" if len(entry["sources"]) > 4 else "")
        lines.append(f"- **{entry['name']}** `{entry['id']}` — {first}. Severity {entry['severity']}; from {sources}.")
    lines.append("")

lines += ["## Dutch entries with no English counterpart", ""]
for entry in sorted(dutch_only, key=lambda x: x["id"]):
    lines.append(f"- **{entry['naam']}** `{entry['id']}` — {entry['definitie'].split('. ')[0].rstrip('.')}.")
lines.append("")

out = "\n".join(lines).replace("](", "] (")
(SKILL / "whats-new.md").write_text(out)
print(f"whats-new.md: {new_count} new of {total} English-applicable, plus {len(dutch_only)} Dutch-only")
