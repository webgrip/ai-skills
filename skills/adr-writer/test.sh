#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SKILL="$(pwd)"
VALIDATOR="$SKILL/scripts/validate_adr_consistency.py"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() {
  echo "FAIL: $1" >&2
  if [ -n "${2:-}" ]; then
    echo "$2" >&2
  fi
  exit 1
}

require_output() {
  case "$2" in
    *"$1"*) ;;
    *) fail "expected '$1' in the validator output" "$2" ;;
  esac
}

expect_pass() {
  local label=$1 pattern=$2 root=$3 output
  output=$(python3 "$VALIDATOR" "$root" 2>&1) || fail "validator should pass: $label" "$output"
  require_output "$pattern" "$output"
}

expect_fail() {
  local label=$1 pattern=$2 root=$3 output
  if output=$(python3 "$VALIDATOR" "$root" 2>&1); then
    fail "validator should have failed: $label" "$output"
  fi
  require_output "$pattern" "$output"
}

mutate() {
  python3 - "$1" "$2" "$3" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text()
if sys.argv[2] not in text:
    sys.exit(f"mutate: {sys.argv[2]!r} not found in {path}")
path.write_text(text.replace(sys.argv[2], sys.argv[3]))
PY
}

drop_row() {
  { grep -v "$2" "$1" || true; } > "$1.tmp"
  mv "$1.tmp" "$1"
}

append_row() {
  printf '| [%s](%s) | %s | %s | %s |\n' "$2" "$3" "$4" "$5" "$6" >> "$1"
}

write_madr4_record() {
  cat > "$1" <<'EOF'
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
}

write_madr2_record() {
  cat > "$1" <<'EOF'
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
}

write_nygard_record() {
  cat > "$1" <<'EOF'
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
}

CORPUS="$WORK/main"
ADR="$CORPUS/docs/adr"
INDEX="$ADR/index.md"
POSTGRES="$ADR/adr-0001-use-postgresql.md"
mkdir -p "$ADR"
cp "$SKILL/assets/index-template.md" "$INDEX"
cp "$SKILL/assets/adr-template.md" "$ADR/adr-0000-template.md"
write_madr4_record "$POSTGRES"
append_row "$INDEX" 0001 adr-0001-use-postgresql.md "Use PostgreSQL" accepted 2026-01-05
expect_pass "bootstrapped corpus with the template" "OK (1 record" "$CORPUS"
expect_pass "registry detected" "registry-checked" "$CORPUS"

write_madr2_record "$ADR/adr-0002-legacy-record.md"
append_row "$INDEX" 0002 adr-0002-legacy-record.md "Keep the legacy queue" accepted 2026-01-06
expect_pass "MADR 2.x record next to MADR 4.0.0" "OK (2 record" "$CORPUS"

write_nygard_record "$ADR/adr-0003-record-decisions.md"
append_row "$INDEX" 0003 adr-0003-record-decisions.md "Record architecture decisions" accepted 2026-01-07
expect_pass "Nygard record reported" "note: 1 legacy Nygard" "$CORPUS"
expect_pass "Nygard record tolerated" "OK (3 record" "$CORPUS"

mutate "$INDEX" "| accepted | 2026-01-05 |" "| accepted | 2026-02-01 |"
expect_fail "registry date drift" "Last updated 2026-02-01" "$CORPUS"
mutate "$INDEX" "| accepted | 2026-02-01 |" "| accepted | 2026-01-05 |"

mutate "$POSTGRES" 'status: "accepted"' 'status: "acceptedd"'
expect_fail "illegal status" "illegal status" "$CORPUS"
mutate "$POSTGRES" 'status: "acceptedd"' 'status: "accepted"'

mutate "$POSTGRES" "## Considered Options" "## Considered Optionz"
expect_fail "missing required section" "missing required section" "$CORPUS"
mutate "$POSTGRES" "## Considered Optionz" "## Considered Options"

drop_row "$INDEX" "adr-0002-legacy-record"
expect_fail "record without a registry row" "no Records row" "$CORPUS"
append_row "$INDEX" 0002 adr-0002-legacy-record.md "Keep the legacy queue" accepted 2026-01-06

cp "$ADR/adr-0002-legacy-record.md" "$ADR/0004-mixed-style.md"
expect_fail "mixed filename styles" "mixed filename styles" "$CORPUS"
rm "$ADR/0004-mixed-style.md"

for misnamed in adr-0004-Review-Policy.md ADR-0004-review-policy.md 0004_review_policy.md; do
  cp "$POSTGRES" "$ADR/$misnamed"
  expect_fail "record-like file $misnamed" "$misnamed: looks like an ADR" "$CORPUS"
  rm "$ADR/$misnamed"
done

cp "$POSTGRES" "$ADR/adr-0004-template-rollout.md"
expect_fail "a record named like a template is still a record" "no Records row for adr-0004-template-rollout.md" "$CORPUS"
rm "$ADR/adr-0004-template-rollout.md"

mutate "$POSTGRES" 'status: "accepted"' 'status: "superseded"'
mutate "$INDEX" "| Use PostgreSQL | accepted |" "| Use PostgreSQL | superseded |"
expect_fail "superseded without the superseding record" "must name the superseding record" "$CORPUS"
mutate "$POSTGRES" 'status: "superseded"' 'status: "superseded by [ADR-0009](adr-0009-missing.md)"'
expect_fail "superseded by a record that does not exist" "superseded by ADR-0009, which does not exist" "$CORPUS"
mutate "$POSTGRES" 'status: "superseded by [ADR-0009](adr-0009-missing.md)"' 'status: "superseded by [ADR-0002](adr-0002-legacy-record.md)"'
expect_pass "superseded by an existing record" "OK (3 record" "$CORPUS"
mutate "$POSTGRES" 'status: "superseded by [ADR-0002](adr-0002-legacy-record.md)"' 'status: "accepted"'
mutate "$INDEX" "| Use PostgreSQL | superseded |" "| Use PostgreSQL | accepted |"

expect_pass "corpus clean after every revert" "OK (3 record" "$CORPUS"

UNREGISTERED="$WORK/unregistered"
DECISIONS="$UNREGISTERED/docs/decisions"
mkdir -p "$DECISIONS"
cp "$POSTGRES" "$DECISIONS/"
expect_pass "corpus without a registry file is reported" "note: no registry table" "$UNREGISTERED"
expect_pass "corpus without a registry file passes" "OK (1 record" "$UNREGISTERED"

cp "$SKILL/assets/index-template.md" "$DECISIONS/index.md"
expect_fail "registry file without Records rows" "index.md: the registry has no Records rows" "$UNREGISTERED"
rm "$DECISIONS/index.md"
printf '# Decisions\n\nSee the records in this folder.\n' > "$DECISIONS/README.md"
expect_fail "prose README as the only registry" "README.md: the registry has no Records rows" "$UNREGISTERED"

EMPTY="$WORK/empty"
mkdir -p "$EMPTY"
status=0
python3 "$VALIDATOR" "$EMPTY" > /dev/null 2>&1 || status=$?
[ "$status" -eq 2 ] || fail "expected exit 2 for a missing ADR directory, got $status"

echo "adr-writer: all smoke tests passed"
