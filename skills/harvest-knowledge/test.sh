#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
DUMP=scripts/dump_transcript.py
FIXTURE=fixtures/transcript.jsonl
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

occurrences() {
  { grep -c -F -- "$1" "$2" || true; }
}

expect_once() {
  [ "$(occurrences "$1" "$WORK/dump.txt")" -eq 1 ] || fail "expected exactly one '$1' in the dump"
}

expect_absent() {
  [ "$(occurrences "$1" "$WORK/dump.txt")" -eq 0 ] || fail "the dump must not contain '$1'"
}

python3 "$DUMP" "$FIXTURE" -o "$WORK/dump.txt" > "$WORK/written.txt" 2> "$WORK/stats.txt"
[ "$(cat "$WORK/written.txt")" = "$WORK/dump.txt" ] || fail "a dump without --split-chars writes exactly the --output file"

expect_once "[SUMMARY] Earlier session about the deploy pipeline"
expect_once "USER] How do we deploy the billing service?"
expect_once "ASSISTANT] Let me check the pipeline."
expect_once "TOOL_CALL] Bash: cat deploy.yml"
expect_once "TOOL_CALL] Edit: deploy.yml :: canary: true"
expect_once "TOOL_CALL] Agent: Research rollout :: Find the rollout runbook"
expect_once "more chars]"
expect_absent "LONG-RESULT-TAIL"
expect_absent "THINKING-MARKER"
expect_once "ROLLOUT-REPORT-BODY"
expect_once "NOTIFICATION-RESULT"
expect_absent "SKILL-BODY-MARKER"
expect_once "Also check the staging config"
expect_once "USER] Also check the staging config"
expect_once "QUEUED_USER] QUEUED-ONLY: and fix the docs too"
expect_once "SUMMARY] COMPACT-SUMMARY: the canary rollout was configured."
expect_once "USER] Second question: what about rollback?"
grep -q -F "2 reports, 1 queued user messages, 2 unreadable lines skipped" "$WORK/stats.txt" \
  || fail "stats line must count reports, queued messages and unreadable lines: $(cat "$WORK/stats.txt")"

python3 "$DUMP" "$FIXTURE" > "$WORK/stdout.txt" 2> /dev/null
cmp -s "$WORK/stdout.txt" "$WORK/dump.txt" || fail "stdout and --output must carry the same dump"

python3 "$DUMP" "$FIXTURE" -o "$WORK/split.txt" --split-chars 200 > "$WORK/parts.txt" 2> /dev/null
[ "$(wc -l < "$WORK/parts.txt")" -ge 2 ] || fail "--split-chars 200 must write more than one part"
first_part=""
while IFS= read -r part; do
  [ -s "$part" ] || fail "part $part is empty"
  if [ -z "$first_part" ]; then
    first_part="$part"
    continue
  fi
  head -n 1 "$part" | grep -q " USER\] " || fail "part $part must start at a user turn"
done < "$WORK/parts.txt"
cat $(cat "$WORK/parts.txt") > "$WORK/joined.txt"
[ "$(occurrences "ROLLOUT-REPORT-BODY" "$WORK/joined.txt")" -eq 1 ] || fail "splitting must keep every block exactly once"
[ "$(grep -c '^\[' "$WORK/joined.txt")" -eq "$(grep -c '^\[' "$WORK/dump.txt")" ] || fail "splitting must keep the block count"

status=0
python3 "$DUMP" "$WORK/missing.jsonl" > /dev/null 2>&1 || status=$?
[ "$status" -eq 2 ] || fail "a missing transcript must exit 2, got $status"

status=0
python3 "$DUMP" "$FIXTURE" --split-chars 200 > /dev/null 2>&1 || status=$?
[ "$status" -eq 2 ] || fail "--split-chars without --output must exit 2, got $status"

printf 'not json\n' > "$WORK/garbage.jsonl"
status=0
python3 "$DUMP" "$WORK/garbage.jsonl" > /dev/null 2>&1 || status=$?
[ "$status" -eq 1 ] || fail "a file with no transcript records must exit 1, got $status"

echo "harvest-knowledge: dump_transcript.py tests passed"
