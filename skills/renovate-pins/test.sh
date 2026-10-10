#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
COVERAGE="python3 scripts/pin_coverage.py"

$COVERAGE --report fixtures/careful.report.json --root fixtures/careful > /dev/null 2>&1 \
  || { echo "careful fixture raised findings" >&2; $COVERAGE --report fixtures/careful.report.json --root fixtures/careful; exit 1; }

if $COVERAGE --report fixtures/careless.report.json --root fixtures/careless > /dev/null 2>&1; then
  echo "careless fixture passed; it must fail" >&2; exit 1
fi
careless_json=$($COVERAGE --report fixtures/careless.report.json --root fixtures/careless --json 2>/dev/null || true)
printf '%s' "$careless_json" | python3 -c '
import json, sys
found = {f["rule"] for f in json.load(sys.stdin)["findings"]}
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
if found != expected:
    sys.exit(f"careless: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
print(f"pin_coverage: {len(found)} rules fire on careless, none on careful")
'

if $COVERAGE --report fixtures/missing.report.json --root fixtures/careful > /dev/null 2>&1; then
  echo "a missing report must be a usage error" >&2; exit 1
fi

python3 -m unittest -q scripts/test_registry_digest.py 2>&1 | tail -1

python3 - <<'PY'
import re, sys
docs = open("SKILL.md").read()
rules = set(re.findall(r'Finding\(\s*"(?:error|warn)", "([a-z0-9-]+)"', open("scripts/pin_coverage.py").read()))
undocumented = sorted(r for r in rules if f"`{r}`" not in docs)
if undocumented:
    sys.exit(f"pin_coverage rules missing from SKILL.md: {undocumented}")
print(f"pin_coverage: {len(rules)} rules documented")
PY
