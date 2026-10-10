#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

for suite in test_ci_recurrence test_repeat_run test_layer_diff; do
  if ! output=$(python3 -m unittest -q "scripts/$suite.py" 2>&1); then
    echo "$output" >&2
    echo "$suite failed" >&2
    exit 1
  fi
  echo "$suite: $(echo "$output" | grep -E '^Ran [0-9]+ tests' | head -1)"
done

for script in ci_recurrence repeat_run layer_diff; do
  python3 "scripts/$script.py" --help > /dev/null
  grep -q "scripts/$script.py" SKILL.md || { echo "SKILL.md never mentions scripts/$script.py" >&2; exit 1; }
done

if grep -rnE '^[[:space:]]*#[^!]' scripts/*.py; then
  echo "comments found in scripts" >&2
  exit 1
fi
echo "flaky-ci-forensics: ok"
