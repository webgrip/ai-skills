#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/design_scan.py"

$SCAN --fail-on note fixtures/disciplined > /dev/null || { echo "disciplined fixture raised findings" >&2; $SCAN --fail-on never fixtures/disciplined; exit 1; }

if $SCAN fixtures/template > /dev/null 2>&1; then
  echo "template fixture passed; it must fail" >&2; exit 1
fi

$SCAN --json --fail-on never fixtures/template | python3 -c '
import json, sys
found = {f["rule"] for f in json.load(sys.stdin)["findings"]}
expected = {line.strip() for line in open("fixtures/template.expect") if line.strip()}
missing, unexpected = expected - found, found - expected
if missing or unexpected:
    sys.exit(f"template fixture: missing {sorted(missing)}, unexpected {sorted(unexpected)}")
print(f"design_scan: {len(expected)} rules fire on the template fixture, none on the disciplined one")
'

python3 - <<'PY'
import re, sys
skill = open("SKILL.md").read() + "".join(open(f).read() for f in ("validation.md",))
rules = re.findall(r'(?:LineRule\(|Finding\([^,]+, [^,]+, )"([a-z-]+)"', open("scripts/design_scan.py").read())
rules += re.findall(r'"(will-change-sprawl|glass-everywhere)"', open("scripts/design_scan.py").read())
undocumented = sorted({r for r in rules if f"`{r}`" not in skill})
if undocumented:
    sys.exit(f"scanner rules missing from the docs: {undocumented}")
PY
