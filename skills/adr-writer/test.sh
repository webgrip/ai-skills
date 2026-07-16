#!/usr/bin/env bash
# Smoke tests for the adr-writer plugin. CI runs every skills/*/test.sh.
set -euo pipefail
cd "$(dirname "$0")"
SKILL=.
V="$SKILL/scripts/validate_adr_consistency.py"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

ADR="$TMP/docs/adr"
mkdir -p "$ADR"

mutate() { # file, old, new — portable in-place replace (BSD/GNU sed differ)
  python3 - "$1" "$2" "$3" << 'EOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace(sys.argv[2], sys.argv[3]))
EOF
}

expect_fail() {
  if python3 "$V" "$TMP" > /dev/null 2>&1; then
    echo "FAIL: validator should have failed: $1" >&2
    exit 1
  fi
}

# Bootstrap exactly as the skill instructs: templates in, one MADR 4.0.0 record, one row.
cp "$SKILL/assets/index-template.md" "$ADR/index.md"
cp "$SKILL/assets/adr-template.md" "$ADR/adr-0000-template.md"
cat > "$ADR/adr-0001-use-postgresql.md" << 'EOF'
---
status: "accepted"
date: 2026-01-05
---

# Use PostgreSQL as the primary datastore

## Context and Problem Statement

The service needs a relational datastore with strong consistency.

## Considered Options

* PostgreSQL
* MySQL

## Decision Outcome

Chosen option: "PostgreSQL", because it meets the consistency and tooling drivers.

### Confirmation

`psql -c 'select 1'` against the production instance; migration job green in CI.

## More Information

* 2026-01-05 — accepted (abc1234)
EOF
printf '| [0001](adr-0001-use-postgresql.md) | Use PostgreSQL | accepted | 2026-01-05 |\n' >> "$ADR/index.md"

python3 "$V" "$TMP" | grep -q "OK (1 record" || { echo "FAIL: bootstrap corpus"; exit 1; }
python3 "$V" "$TMP" | grep -q "registry-checked" || { echo "FAIL: registry not detected"; exit 1; }

# A MADR 2.x record coexists (birth-format rule) and is fully checked.
cat > "$ADR/adr-0002-legacy-record.md" << 'EOF'
# Keep the legacy queue

* Status: accepted
* Date: 2026-01-06

## Context and Problem Statement

The queue works; replacing it is not worth the risk now.

## Considered Options

* Keep the legacy queue
* Migrate to Kafka

## Decision Outcome

Chosen option: "Keep the legacy queue", because migration cost outweighs benefit.

## Links

* 2026-01-06 — accepted (def5678)
EOF
printf '| [0002](adr-0002-legacy-record.md) | Keep the legacy queue | accepted | 2026-01-06 |\n' >> "$ADR/index.md"
python3 "$V" "$TMP" | grep -q "OK (2 record" || { echo "FAIL: mixed-generation corpus"; exit 1; }

# A Nygard record is tolerated with reduced checks, and says so.
cat > "$ADR/adr-0003-record-decisions.md" << 'EOF'
# 3. Record architecture decisions

## Status

Accepted

## Context

We need to record architectural decisions.

## Decision

We will use ADRs.

## Consequences

Decisions become reviewable.
EOF
printf '| [0003](adr-0003-record-decisions.md) | Record architecture decisions | accepted | 2026-01-07 |\n' >> "$ADR/index.md"
python3 "$V" "$TMP" | grep -q "note: 1 legacy Nygard" || { echo "FAIL: Nygard tolerance"; exit 1; }
python3 "$V" "$TMP" | grep -q "OK (3 record" || { echo "FAIL: Nygard corpus should pass"; exit 1; }

# Drift and structure violations must fail.
mutate "$ADR/index.md" "| accepted | 2026-01-05 |" "| accepted | 2026-02-01 |"
expect_fail "registry date drift"
mutate "$ADR/index.md" "| accepted | 2026-02-01 |" "| accepted | 2026-01-05 |"

mutate "$ADR/adr-0001-use-postgresql.md" 'status: "accepted"' 'status: "acceptedd"'
expect_fail "illegal status"
mutate "$ADR/adr-0001-use-postgresql.md" 'status: "acceptedd"' 'status: "accepted"'

mutate "$ADR/adr-0001-use-postgresql.md" "## Considered Options" "## Considered Optionz"
expect_fail "missing required section"
mutate "$ADR/adr-0001-use-postgresql.md" "## Considered Optionz" "## Considered Options"

grep -v "adr-0002-legacy-record" "$ADR/index.md" > "$ADR/index.md.tmp" && mv "$ADR/index.md.tmp" "$ADR/index.md"
expect_fail "record without a registry row"
printf '| [0002](adr-0002-legacy-record.md) | Keep the legacy queue | accepted | 2026-01-06 |\n' >> "$ADR/index.md"

cp "$ADR/adr-0002-legacy-record.md" "$ADR/0004-mixed-style.md"
expect_fail "mixed filename styles"
rm "$ADR/0004-mixed-style.md"

python3 "$V" "$TMP" | grep -q "OK (3 record" || { echo "FAIL: corpus should be clean after reverts"; exit 1; }

# A corpus without a registry passes with a notice, in an alternate discovered home.
TMP2=$(mktemp -d)
trap 'rm -rf "$TMP" "$TMP2"' EXIT
mkdir -p "$TMP2/docs/decisions"
cp "$ADR/adr-0001-use-postgresql.md" "$TMP2/docs/decisions/"
python3 "$V" "$TMP2" | grep -q "note: no registry table" || { echo "FAIL: registry-less notice"; exit 1; }
python3 "$V" "$TMP2" | grep -q "OK (1 record" || { echo "FAIL: registry-less corpus should pass"; exit 1; }

# No corpus at all is a usage error (exit 2), not a crash.
TMP3=$(mktemp -d)
trap 'rm -rf "$TMP" "$TMP2" "$TMP3"' EXIT
rc=0
python3 "$V" "$TMP3" > /dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || { echo "FAIL: expected exit 2 for missing ADR dir, got $rc"; exit 1; }

echo "adr-writer: all smoke tests passed"
