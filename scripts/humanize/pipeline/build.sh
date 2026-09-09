#!/usr/bin/env bash
set -euo pipefail

PIPELINE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$PIPELINE/../../.." && pwd)
HUMANIZE="$ROOT/scripts/humanize"
SKILL="$ROOT/skills/humanize"

lang=${1:?usage: build.sh <en|nl>}
case "$lang" in
  en) src="$HUMANIZE/catalog/catalog-en.json"; out=patterns-en.md; title="English catalog: the tells, by category" ;;
  nl) src="$HUMANIZE/catalog/catalog-nl.json"; out=patterns-nl.md; title="Nederlandse catalogus: de tells, per categorie" ;;
  *)  echo "lang must be en or nl" >&2; exit 2 ;;
esac
[ -f "$src" ] || { echo "missing $src" >&2; exit 1; }

staged="$HUMANIZE/catalog/.staged-$lang.json"
cp "$src" "$staged"
python3 "$PIPELINE/clean.py" "$staged" "$lang"
python3 "$PIPELINE/apply_additions.py" "$staged" "$lang" "$PIPELINE/additions.json"
python3 "$PIPELINE/render.py" "$lang" "$staged" "$SKILL/$out" "$title"

python3 - "$SKILL" "$lang" "$staged" <<'PY'
import json
import sys
from pathlib import Path

skill, lang, staged = sys.argv[1], sys.argv[2], sys.argv[3]
target = Path(skill) / "scripts" / "patterns.json"
new = json.load(open(Path(staged).with_suffix(".patterns.json")))
existing = json.load(open(target))["patterns"] if target.exists() else []
kept = [p for p in existing if lang not in p["lang"]]
merged = sorted(kept + new, key=lambda p: (p["category"], p["id"], p["lang"][0]))
json.dump({"patterns": merged}, open(target, "w"), ensure_ascii=False, indent=1)
print(f"patterns.json: {len(merged)} entries ({len(new)} for {lang})")
PY

rm -f "$staged" "${staged%.json}.patterns.json"
