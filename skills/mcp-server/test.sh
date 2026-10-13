#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
LINT="python3 -I scripts/tools_lint.py"

$LINT fixtures/clean.json --fail-on note > /dev/null \
  || { echo "clean fixture raised findings" >&2; $LINT fixtures/clean.json --fail-on never; exit 1; }

if $LINT fixtures/broken.json > /dev/null 2>&1; then
  echo "broken fixture passed; it must fail" >&2; exit 1
fi
$LINT fixtures/broken.json --json --fail-on never | python3 -c '
import json, sys
found = {f["rule"] for f in json.load(sys.stdin)["findings"]}
expected = {line.strip() for line in open("fixtures/broken.expect") if line.strip()}
if found != expected:
    sys.exit(f"broken: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
'

status=0
$LINT fixtures/empty.json --json --fail-on error > /dev/null || status=$?
[ "$status" -eq 1 ] || { echo "empty tool list must exit 1, got $status" >&2; exit 1; }

python3 - <<'PY'
import re, sys
source = open("scripts/tools_lint.py").read()
rules = set(re.findall(r'Finding\("(?:error|warn|note)", "([a-z0-9-]+)"', source))
documented = open("evaluate.md").read()
undocumented = sorted(rule for rule in rules if f"`{rule}`" not in documented)
if undocumented:
    sys.exit(f"tools_lint rules missing from evaluate.md: {undocumented}")
print(f"tools_lint: {len(rules)} rules documented, fixtures pass")
PY
