#!/usr/bin/env python3
"""Merge hand-verified extra cues and regexes into a rendered catalog, and dedupe ids across categories."""
import json
import re
import sys

path, lang, additions_path = sys.argv[1], sys.argv[2], sys.argv[3]
catalog = json.load(open(path))
raw = json.load(open(additions_path))
additions = raw.get(lang, {})
flags = raw.get("flags", {})
cue_key = "cues"

seen = {}
for category, entries in catalog["categories"].items():
    survivors = []
    for entry in entries:
        previous = seen.get(entry["id"])
        if previous is None:
            seen[entry["id"]] = (category, entry)
            survivors.append(entry)
            continue
        keep = previous[1]
        keep[cue_key] = list(dict.fromkeys(keep[cue_key] + entry[cue_key]))
        keep["regex"] = list(dict.fromkeys(keep["regex"] + entry["regex"]))
        print(f"deduped {entry['id']}: {category} folded into {previous[0]}")
    catalog["categories"][category] = survivors

added = 0
for entry_id, extra in additions.items():
    match = seen.get(entry_id)
    if not match:
        sys.exit(f"addition for unknown id {entry_id}")
    entry = match[1]
    for expression in extra.get("regex", []):
        re.compile(expression, re.IGNORECASE)
    entry[cue_key] = list(dict.fromkeys(entry[cue_key] + extra.get(cue_key, [])))
    entry["regex"] = list(dict.fromkeys(entry["regex"] + extra.get("regex", [])))
    added += len(extra.get("regex", []))

for entry_id, flag in flags.items():
    match = seen.get(entry_id)
    if match:
        match[1]["flags"] = flag

catalog["count"] = sum(len(v) for v in catalog["categories"].values())
json.dump(catalog, open(path, "w"), ensure_ascii=False, indent=1)
print(f"additions: {added} regexes into {len(additions)} entries; catalog now {catalog['count']} entries")
