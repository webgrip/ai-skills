#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
LINT="python3 scripts/dashboard_lint.py"

$LINT --fail-on note fixtures/careful > /dev/null || { echo "careful fixture raised findings" >&2; $LINT --fail-on never fixtures/careful; exit 1; }

if $LINT fixtures/careless > /dev/null 2>&1; then
  echo "careless fixture passed; it must fail" >&2; exit 1
fi

$LINT --json --fail-on never fixtures/careful fixtures/careless | python3 -c '
import json, sys
report = json.load(sys.stdin)
coverage = report["coverage"]
if coverage["skipped"]:
    sys.exit(f"fixtures not parsed: {coverage}")
if coverage["dashboards"] != 4:
    sys.exit(f"expected 4 fixture dashboards: {coverage}")
careful = [finding for finding in report["findings"] if "/careful/" in finding["path"]]
if careful:
    sys.exit(f"careful fixture fired: {careful}")
found = {finding["rule"] for finding in report["findings"]}
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
if found != expected:
    sys.exit(f"careless fixture: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
print(f"dashboard_lint: {len(expected)} rules fire on the careless fixtures, none on the careful ones")
'

if ! unit_output=$(python3 -m unittest -q scripts/test_scripts.py 2>&1); then
  echo "$unit_output" >&2; exit 1
fi
echo "$unit_output" | grep -E "^(Ran|OK)" | tr '\n' ' '; echo

projection=$(python3 scripts/forecast.py --json --at 2026-10-25T12:30:00Z capped --inventory examples/hetzner-inventory.json)
echo "$projection" | python3 -c '
import json, sys
projected = round(json.load(sys.stdin)["projected"], 2)
if projected != 32.96:
    sys.exit(f"capped example projected {projected}, expected 32.96 (case-unfold-hetzner.md)")
'
python3 scripts/forecast.py --at 2026-10-25T09:00:00Z --budget 30 daily --csv examples/daily-spend.csv | grep -q "anomaly 2026-10-14" \
  || { echo "daily example lost its anomaly" >&2; exit 1; }
echo "forecast: examples reproduce the figures in case-unfold-hetzner.md"

$LINT --rules --json | python3 -c '
import json, sys
rules = json.load(sys.stdin)
documented = open("checks.md").read()
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
undocumented = []
for rule in rules:
    name, number = rule["name"], rule["number"]
    if f"`{name}`" not in documented or f"| {number} |" not in documented or f"### {name}" not in documented:
        undocumented.append(name)
untested = sorted({rule["name"] for rule in rules} - expected)
if undocumented or untested:
    sys.exit(f"dashboard_lint rules undocumented {undocumented}, untested {untested}")
print(f"dashboard_lint: {len(rules)} rules documented in checks.md and covered by the careless fixtures")
'
