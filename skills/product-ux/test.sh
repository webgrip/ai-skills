#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/ui_scan.py"

$SCAN --fail-on note fixtures/careful > /dev/null || { echo "careful fixture raised findings" >&2; $SCAN --fail-on never fixtures/careful; exit 1; }

if $SCAN fixtures/careless > /dev/null 2>&1; then
  echo "careless fixture passed; it must fail" >&2; exit 1
fi

$SCAN --json --fail-on never fixtures/careless | python3 -c '
import json, sys
found = {f["rule"] for f in json.load(sys.stdin)["findings"]}
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
missing, unexpected = expected - found, found - expected
if missing or unexpected:
    sys.exit(f"careless fixture: missing {sorted(missing)}, unexpected {sorted(unexpected)}")
print(f"ui_scan: {len(expected)} rules fire on the careless fixture, none on the careful one")
'

python3 - <<'PY'
import re, sys
documented = open("validation.md").read()
source = open("scripts/ui_scan.py").read()
rules = set(re.findall(r'"([a-z]+(?:-[a-z]+)*)",\s*"(?:fail|warn|note)"', source)) - {"fail", "warn", "note"}
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
undocumented = sorted(r for r in rules if f"`{r}`" not in documented)
untested = sorted(rules - expected)
if undocumented or untested:
    sys.exit(f"scanner rules undocumented {undocumented}, missing from careless.expect {untested}")
PY
