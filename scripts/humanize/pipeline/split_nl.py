#!/usr/bin/env python3
"""Split the Dutch extract and transfer output into one raw file per category.

The merge workflow reads one file per category; inlining the whole set into an
agent prompt stalls the agent.
"""
import collections
import glob
import json
from pathlib import Path

EXTRACTS = Path(__file__).resolve().parents[1] / "extracts" / "nl"
CATS = ["vocabulary", "syntax", "rhetoric", "structure", "punctuation-format", "content", "artifacts", "translationese"]

raw = collections.defaultdict(list)
for path in sorted(glob.glob(str(EXTRACTS / "nl-extract-*.json"))) + sorted(glob.glob(str(EXTRACTS / "nl-transfer-*.json"))):
    data = json.load(open(path))
    source = data.get("bron") or Path(path).name
    for pattern in data.get("patronen", []):
        category = pattern.get("categorie")
        pattern["bron"] = source
        raw[category if category in CATS else "rhetoric"].append(pattern)

for category in CATS:
    items = raw.get(category, [])
    out = EXTRACTS / f"nl-raw-{category}.json"
    json.dump(items, open(out, "w"), ensure_ascii=False, indent=1)
    size = len(json.dumps(items, ensure_ascii=False)) // 1024
    print(f"  {len(items):4d} raw  {size:4d} KB  {category}")
print("  total:", sum(len(v) for v in raw.values()))
