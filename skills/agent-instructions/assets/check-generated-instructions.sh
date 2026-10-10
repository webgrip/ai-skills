#!/bin/sh
set -e

HAND_WRITTEN_BUDGET="${AGENT_INSTRUCTIONS_BUDGET:-150}"
GENERATOR_PACKAGE="${AGENT_INSTRUCTIONS_GENERATOR_PACKAGE:-laravel/boost}"
BOOST_FLAGS="${AGENT_INSTRUCTIONS_BOOST_FLAGS:---guidelines --skills}"
AGENT_SETUP="${AGENT_INSTRUCTIONS_AGENT_SETUP:-$(dirname "$0")/../scripts/agent_setup.py}"
AGENT_SETUP_REGISTRY="${AGENT_INSTRUCTIONS_REGISTRY:-$(dirname "$0")/targets.json}"
failed=0

fail() {
  echo ""
  echo "FAIL: $1"
  failed=1
}

if ! python3 "${AGENT_SETUP}" check . --registry "${AGENT_SETUP_REGISTRY}"; then
  failed=1
fi

if grep -q "<laravel-boost-guidelines>" CLAUDE.md 2>/dev/null; then
  fail "CLAUDE.md contains a generated Boost block. Claude Code ignores AGENTS.md while CLAUDE.md exists, so that block goes stale: remove it and keep only @AGENTS.md plus Claude-only lines."
fi

composer_version() {
  php -r '$data = json_decode((string) @file_get_contents($argv[1]), true); $packages = is_array($data) ? array_merge($data["packages"] ?? $data, $data["packages-dev"] ?? []) : []; foreach ($packages as $package) { if (is_array($package) && ($package["name"] ?? "") === $argv[2]) { echo $package["version"] ?? ""; } }' "$1" "${GENERATOR_PACKAGE}"
}

installed_version=$(composer_version vendor/composer/installed.json)
locked_version=$(composer_version composer.lock)

if [ -z "${installed_version}" ] || [ -z "${locked_version}" ] || [ "${installed_version}" != "${locked_version}" ]; then
  fail "vendor/ has ${GENERATOR_PACKAGE} ${installed_version:-none}, composer.lock pins ${locked_version:-none}. Run your package manager's install (composer install) and check again; generating with another version rewrites files the lock never produced."
  exit 1
fi

snapshot=$(mktemp -d)
cp AGENTS.md boost.json "${snapshot}/"
cp -R .agents/skills "${snapshot}/skills"

APP_ENV=local APP_DEBUG=true DB_CONNECTION=sqlite DB_DATABASE=:memory: \
  php artisan boost:install ${BOOST_FLAGS} --no-interaction > /dev/null

for file in AGENTS.md boost.json; do
  if ! diff -u "${snapshot}/${file}" "${file}"; then
    fail "${file} differs from what 'php artisan boost:install ${BOOST_FLAGS}' generates. Do not edit the generated block by hand: put standing instructions in .ai/guidelines and knowledge in docs/, then regenerate and commit."
  fi
done

if ! diff -ru "${snapshot}/skills" .agents/skills; then
  fail ".agents/skills differs from what Boost generates. Boost overwrites its own skills on every run; put a change in a skill of your own instead of editing one Boost owns."
fi

if command -v git > /dev/null 2>&1 && git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  uncommitted=$(git status --porcelain --untracked-files=all -- AGENTS.md boost.json .agents/skills)
  if [ -n "${uncommitted}" ]; then
    echo "${uncommitted}"
    fail "Generated files are untracked or uncommitted. A clean CI checkout would not have them, so commit what Boost generates and delete leftovers from earlier runs."
  fi
fi

header_lines=$(( $(sed -n '/<laravel-boost-guidelines>/q;p' AGENTS.md | wc -l) ))
guideline_lines=0
if [ -d .ai/guidelines ]; then
  guideline_lines=$(( $(find .ai/guidelines -type f -exec cat {} + | wc -l) ))
fi
claude_lines=$(( $(wc -l < CLAUDE.md) ))
hand_written=$((header_lines + guideline_lines + claude_lines))

echo "Hand-written agent instructions: ${hand_written} of ${HAND_WRITTEN_BUDGET} lines (AGENTS.md header ${header_lines}, .ai/guidelines ${guideline_lines}, CLAUDE.md ${claude_lines})."

if [ "${hand_written}" -gt "${HAND_WRITTEN_BUDGET}" ]; then
  fail "The hand-written agent instructions exceed ${HAND_WRITTEN_BUDGET} lines. Every agent pays for them in every session. Move knowledge to docs/ and leave a pointer."
fi

exit "${failed}"
