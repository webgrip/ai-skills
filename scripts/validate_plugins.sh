#!/usr/bin/env bash
set -euo pipefail
deliberate='version: No version specified'
if ! output=$(claude plugin validate . 2>&1); then
  printf '%s\n' "$output"
  exit 1
fi
printf '%s\n' "$output"
unexpected=$(printf '%s\n' "$output" | grep '❯' | grep -v "$deliberate" || true)
if [ -n "$unexpected" ]; then
  printf 'FAIL: claude plugin validate warns about more than the deliberately omitted version:\n%s\n' "$unexpected"
  exit 1
fi
echo "plugin validation OK: every warning is the omitted version, which keeps installs on the commit"
