#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
CHECK="python3 scripts/edge_check.py"

$CHECK config fixtures/clean assets/private-pages --today 2026-10-04 --fail-on note > /dev/null \
  || { echo "clean configs raised findings" >&2; $CHECK config fixtures/clean assets/private-pages --today 2026-10-04 --fail-on never; exit 1; }

for fixture in broken dead-target; do
  if $CHECK config "fixtures/$fixture" --today 2026-10-04 > /dev/null 2>&1; then
    echo "fixture $fixture passed; it must fail" >&2; exit 1
  fi
  $CHECK config "fixtures/$fixture" --today 2026-10-04 --json --fail-on never | python3 -c '
import json, sys
fixture = sys.argv[1]
found = {f["rule"] for f in json.load(sys.stdin)["findings"]}
expected = {line.strip() for line in open(f"fixtures/{fixture}.expect") if line.strip()}
if found != expected:
    sys.exit(f"{fixture}: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
' "$fixture"
done

python3 -m unittest -q scripts/test_edge_check.py 2>&1 | tail -1
python3 -m unittest discover -q -s assets/private-pages/test -p 'test_*.py' 2>&1 | tail -1
if command -v node > /dev/null; then
  (cd assets/private-pages && node --test 2>&1 | grep -E '^ℹ (pass|fail)' | tr '\n' ' '; echo)
  (cd assets/private-pages && node --test > /dev/null 2>&1) || { echo "private-pages worker tests failed" >&2; exit 1; }
fi

python3 - <<'PY'
import re, sys
docs = "".join(open(f).read() for f in ("SKILL.md", "checks.md"))
rules = set(re.findall(r'Finding\("(?:error|warn|note)", "([a-z0-9-]+)"', open("scripts/edge_check.py").read()))
undocumented = sorted(r for r in rules if f"`{r}`" not in docs)
if undocumented:
    sys.exit(f"edge_check rules missing from the docs: {undocumented}")
print(f"edge_check: {len(rules)} rules documented")
PY
