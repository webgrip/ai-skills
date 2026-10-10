#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m unittest -q scripts/test_grafana_access_audit.py 2>&1 | tail -1

python3 - <<'PY'
import re, sys
docs = open("SKILL.md").read()
source = open("scripts/grafana_access_audit.py").read()
rules = set(re.findall(r'Finding\(\s*"(?:error|warn|note)",\s*"([a-z0-9-]+)"', source))
expected = {line.strip() for line in open("fixtures/careless.expect") if line.strip()}
undocumented = sorted(r for r in rules if f"`{r}`" not in docs)
if undocumented:
    sys.exit(f"audit rules missing from SKILL.md: {undocumented}")
if rules != expected:
    sys.exit(f"careless.expect out of step with the script: missing {sorted(rules - expected)}, extra {sorted(expected - rules)}")
print(f"grafana_access_audit: {len(rules)} rules documented and covered by the careless fixture")
PY
