#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/seo_scan.py"

$SCAN site fixtures/careful --fail-on note > /dev/null || { echo "careful fixture raised findings" >&2; $SCAN site fixtures/careful --fail-on never; exit 1; }

if $SCAN site fixtures/careless/broken > /dev/null 2>&1; then
  echo "careless fixture passed; it must fail" >&2; exit 1
fi

for site in fixtures/careless/*/; do
  $SCAN site "$site" --json --fail-on never
done | python3 -c '
import json, sys
text, decoder, found, index = sys.stdin.read(), json.JSONDecoder(), set(), 0
while text[index:].strip():
    rest = text[index:].lstrip()
    report, end = decoder.raw_decode(rest)
    index = len(text) - len(rest) + end
    found |= {finding["rule"] for finding in report["findings"]}
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
if found != expected:
    sys.exit(f"careless fixtures: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
print(f"seo_scan: {len(expected)} site rules fire across the careless fixtures, none on the careful one")
'

python3 -m unittest -q scripts/test_seo_scan.py 2>&1 | tail -1

python3 - <<'PY'
import json, re, sys
source = open("scripts/seo_scan.py").read()
rules = set(re.findall(r'"([a-z0-9]+(?:-[a-z0-9]+)+)",\s*(?:"(?:fail|warn|note)"|severity)', source))
documented = open("checks.md").read()
tested = {line.strip() for line in open("fixtures/careless.expect") if line.strip()} | set(re.findall(r'"((?:live|html)-[a-z0-9-]+)"', open("scripts/test_seo_scan.py").read()))
undocumented = sorted(rule for rule in rules if f"`{rule}`" not in documented)
untested = sorted(rules - tested)
if undocumented or untested:
    sys.exit(f"seo_scan rules undocumented {undocumented}, untested {untested}")
for name in ("crawlers.json", "rich-results.json"):
    data = json.load(open(f"scripts/{name}"))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data.get("checked", "")):
        sys.exit(f"scripts/{name} needs a checked date")
print(f"seo_scan: {len(rules)} rules documented and tested; data files dated")
PY
