#!/usr/bin/env bash
# Smoke tests for the domain-language plugin. CI runs every skills/*/test.sh.
set -euo pipefail
cd "$(dirname "$0")"
SKILL=.
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Docs generate, all four core files non-empty, zero validation warnings on the example
python3 $SKILL/scripts/generate_docs.py $SKILL/assets/example-model.yaml -o "$TMP/docs" 2> "$TMP/warn.txt"
for f in overview glossary entities rules; do test -s "$TMP/docs/$f.md"; done
if grep -q WARNING "$TMP/warn.txt"; then cat "$TMP/warn.txt" >&2; exit 1; fi

# CML export contains the structural keywords
python3 $SKILL/scripts/generate_cml.py $SKILL/assets/example-model.yaml -o "$TMP/model.cml" > /dev/null
grep -q "ContextMap" "$TMP/model.cml"
grep -q "BoundedContext" "$TMP/model.cml"
grep -q "aggregateLifecycle" "$TMP/model.cml"

# Health check scores the worked example 9+ and survives being piped
python3 $SKILL/scripts/health_check.py $SKILL/assets/example-model.yaml | head -1 | grep -Eq "health: (9|10)"

# Health check discriminates: a thin model must score low and not crash
cat > "$TMP/weak.yaml" << 'EOF'
project: Weak
terms:
  - name: Order
    definition: A customer's order.
rules:
  - id: R1
    statement: Orders must be valid.
EOF
python3 $SKILL/scripts/health_check.py "$TMP/weak.yaml" | head -1 | grep -Eq "health: [0-4]"

echo "domain-language: ok"
