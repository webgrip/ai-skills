#!/bin/sh
LINT_COMMAND="${LINT_COMMAND:-vendor/bin/duster lint}"
LINT_PATTERN="${LINT_PATTERN:-\.php$}"
file=$(jq -r '.tool_input.file_path // empty')
printf '%s' "$file" | grep -Eq "${LINT_PATTERN}" || exit 0
if ! output=$(${LINT_COMMAND} "$file" 2>&1); then
  printf '%s\n' "$output" | tail -20 >&2
  exit 2
fi
exit 0
