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

# check_retired: clean model with no retired list passes, a surviving word fails
mkdir -p "$TMP/repo/docs/domain"
cat > "$TMP/repo/docs/domain/model.yaml" << 'EOF'
project: Retire
retired:
  - word: widget
    use: Gadget
    because: One noun per concept.
terms:
  - name: Gadget
    definition: A thing that does the job a Widget used to be asked to do, with a serial number.
EOF
echo "A Gadget is a Gadget." > "$TMP/repo/README.md"
python3 $SKILL/scripts/check_retired.py "$TMP/repo"
echo "The old widget is still here." > "$TMP/repo/README.md"
if python3 $SKILL/scripts/check_retired.py "$TMP/repo" 2>/dev/null; then
  echo "check_retired missed a surviving retired word" >&2; exit 1
fi
python3 $SKILL/scripts/check_retired.py "$TMP/repo" --exempt README.md

# retire_nudge: a name that leaves the model without being retired is reported
git -C "$TMP/repo" init -q
git -C "$TMP/repo" -c user.email=t@t -c user.name=t add -A
git -C "$TMP/repo" -c user.email=t@t -c user.name=t commit -qm seed
python3 - "$TMP/repo/docs/domain/model.yaml" << 'EOF'
import sys
path = sys.argv[1]
text = open(path).read().replace("- name: Gadget", "- name: Doohickey")
open(path, "w").write(text)
EOF
NUDGE=$(echo "{\"tool_input\":{\"file_path\":\"$TMP/repo/docs/domain/model.yaml\"}}" \
  | python3 $SKILL/scripts/retire_nudge.py 2>&1 >/dev/null || true)
echo "$NUDGE" | grep -q "Gadget"
echo "{\"tool_input\":{\"file_path\":\"$TMP/repo/README.md\"}}" | python3 $SKILL/scripts/retire_nudge.py

echo "domain-language: ok"
