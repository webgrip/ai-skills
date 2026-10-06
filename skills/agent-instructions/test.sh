#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "$0")" && pwd)"
checker="${skill_dir}/assets/check-instruction-rules.php"

if ! command -v php > /dev/null 2>&1; then
  echo "SKIP agent-instructions: php is not installed, so check-instruction-rules.php cannot run here."
  exit 0
fi

fixture="$(mktemp -d)"
trap 'rm -rf "${fixture}"' EXIT

write_clean_repository() {
  rm -rf "${fixture:?}"/*
  mkdir -p "${fixture}/.ai/rules" "${fixture}/docs/flows" "${fixture}/src/Billing" "${fixture}/tests"
  printf '<?php\n' > "${fixture}/src/Billing/Invoice.php"
  printf '<?php\n' > "${fixture}/tests/InvoiceTest.php"
  printf -- '---\npaths:\n  - "src/**/*.{php,inc}"\n---\n\n# Billing\n\n- Read amounts from the stored snapshot ([billing](../../docs/flows/billing.md#reading-amounts)).\n' > "${fixture}/.ai/rules/billing.md"
  printf -- '---\npaths: tests/**\n---\n\n# Tests\n\n- Fake the queue in every test ([testing](../../docs/testing.md)).\n' > "${fixture}/.ai/rules/tests.md"
  printf '# Billing\n\n## Reading amounts\n\nRead them.\n' > "${fixture}/docs/flows/billing.md"
  printf '# Testing\n' > "${fixture}/docs/testing.md"
  printf '# Index\n\n- [Billing](flows/billing.md)\n- [Testing](testing.md)\n' > "${fixture}/docs/index.md"
}

run_checker() {
  (cd "${fixture}" && php "${checker}")
}

expect_failure() {
  local expected="$1" output
  if output="$(run_checker)"; then
    echo "FAIL agent-instructions: expected a failure containing \"${expected}\", the checker passed." >&2
    exit 1
  fi
  if ! grep -qF -- "${expected}" <<< "${output}"; then
    echo "FAIL agent-instructions: expected \"${expected}\" in:" >&2
    echo "${output}" >&2
    exit 1
  fi
}

write_clean_repository
run_checker > /dev/null || { echo "FAIL agent-instructions: the clean repository did not pass." >&2; run_checker >&2; exit 1; }

write_clean_repository
printf -- '---\npaths:\n  - "lib/**"\n---\n# Gone\n' > "${fixture}/.ai/rules/gone.md"
expect_failure 'the glob "lib/**" matches no file'

write_clean_repository
printf '# No scope\n' > "${fixture}/.ai/rules/unscoped.md"
expect_failure 'has no `paths:` frontmatter'

write_clean_repository
mkdir -p "${fixture}/.ai/rules/nested"
expect_failure 'is a directory'

write_clean_repository
{ printf -- '---\npaths: tests/**\n---\n'; seq 1 25; } > "${fixture}/.ai/rules/long.md"
expect_failure 'over the 20-line budget'

write_clean_repository
printf -- '---\npaths: tests/**\n---\n- [missing](../../docs/missing.md)\n' > "${fixture}/.ai/rules/broken.md"
expect_failure 'which does not exist'

write_clean_repository
printf -- '---\npaths: tests/**\n---\n- [anchor](../../docs/testing.md#nowhere)\n' > "${fixture}/.ai/rules/anchor.md"
expect_failure 'has no heading with the anchor #nowhere'

write_clean_repository
printf '# Orphan\n' > "${fixture}/docs/orphan.md"
expect_failure 'docs/orphan.md is not linked from docs/index.md'

echo "agent-instructions: check-instruction-rules.php passed 8 cases"
