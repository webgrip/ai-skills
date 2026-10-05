#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/perf_scan.py"

$SCAN site fixtures/careful --fail-on note > /dev/null || { echo "careful fixture raised findings" >&2; $SCAN site fixtures/careful --fail-on never; exit 1; }

python3 -m unittest -q scripts/test_perf_scan.py 2>&1 | tail -1
if command -v node > /dev/null; then
  (cd assets/rum && node --test > /dev/null 2>&1) || { echo "rum worker tests failed" >&2; (cd assets/rum && node --test); exit 1; }
  echo "rum worker: node tests pass"
fi

python3 - <<'PY'
import re, sys
source = open("scripts/perf_scan.py").read()
rules = set(re.findall(r'"([a-z0-9]+(?:-[a-z0-9]+)+)",\s*(?:"(?:fail|warn|note)"|severity|"fail" if)', source))
documented = open("checks.md").read()
tested = set(re.findall(r'"([a-z0-9]+(?:-[a-z0-9]+)+)"', open("scripts/test_perf_scan.py").read()))
undocumented = sorted(rule for rule in rules if f"`{rule}`" not in documented)
untested = sorted(rules - tested)
if undocumented or untested:
    sys.exit(f"perf_scan rules undocumented {undocumented}, untested {untested}")
print(f"perf_scan: {len(rules)} rules documented and tested")
PY
