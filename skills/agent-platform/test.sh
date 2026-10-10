#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
CASES="python3 scripts/otlp_cases.py"

python3 -m unittest -q scripts/test_agent_platform.py 2>&1 | tail -1

$CASES check fixtures/collector-careful.log --org example-org --expect-stripped > /dev/null \
  || { echo "careful collector output raised findings" >&2; $CASES check fixtures/collector-careful.log --org example-org --expect-stripped; exit 1; }

if $CASES check fixtures/collector-careless.log --org example-org --expect-stripped > /dev/null 2>&1; then
  echo "careless collector output passed; it must fail" >&2; exit 1
fi
{ $CASES check fixtures/collector-careless.log --org example-org --expect-stripped --json || true; } | python3 -c '
import json, sys
found = sorted(item["kind"] + ":" + item["case"] for item in json.load(sys.stdin)["findings"])
expected = sorted(line.strip() for line in open("fixtures/collector-careless.expect") if line.strip())
if found != expected:
    sys.exit(f"careless: missing {sorted(set(expected) - set(found))}, unexpected {sorted(set(found) - set(expected))}")
print(f"otlp_cases: careless fixture raised {len(found)} expected findings")
'

python3 - <<'PY'
import re, sys
docs = open("references/telemetry.md").read()
kinds = set(re.findall(r'Finding\("([a-z]+)"', open("scripts/otlp_cases.py").read()))
undocumented = sorted(kind for kind in kinds if f"`{kind}`" not in docs)
if undocumented:
    sys.exit(f"otlp_cases finding kinds missing from references/telemetry.md: {undocumented}")
print(f"otlp_cases: {len(kinds)} finding kinds documented")
PY

ALLOY_IMAGE="grafana/alloy:v1.20.0"
if command -v docker > /dev/null && docker image inspect "$ALLOY_IMAGE" > /dev/null 2>&1; then
  for config in assets/org-only-filter.alloy fixtures/careless-filter.alloy; do
    docker run --rm -v "$PWD/$(dirname "$config"):/etc/alloy:ro" "$ALLOY_IMAGE" fmt "/etc/alloy/$(basename "$config")" > /dev/null \
      || { echo "alloy fmt rejected $config" >&2; exit 1; }
  done
  echo "alloy fmt: both configs parse with $ALLOY_IMAGE"
else
  echo "alloy fmt: skipped ($ALLOY_IMAGE not present locally)"
fi
