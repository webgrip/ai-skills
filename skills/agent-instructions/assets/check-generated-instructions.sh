#!/bin/sh
set -e

HAND_WRITTEN_BUDGET="${AGENT_INSTRUCTIONS_BUDGET:-150}"
BOOST_FLAGS="${AGENT_INSTRUCTIONS_BOOST_FLAGS:---guidelines --skills}"
failed=0

fail() {
  echo ""
  echo "FAIL: $1"
  failed=1
}

if [ -L CLAUDE.md ]; then
  fail "CLAUDE.md is a symlink. It must be a file whose first line is @AGENTS.md, so Claude-only additions can go below it."
elif [ "$(head -n 1 CLAUDE.md)" != "@AGENTS.md" ]; then
  fail "The first line of CLAUDE.md must be @AGENTS.md. Instructions for every agent belong in .ai/guidelines or docs/."
fi

if [ ! -L .claude/skills ] || [ "$(readlink .claude/skills)" != "../.agents/skills" ]; then
  fail ".claude/skills must be a symlink to ../.agents/skills. Claude Code only reads .claude/skills; the other agents read .agents/skills."
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

header_lines=$(( $(sed -n '/<laravel-boost-guidelines>/q;p' AGENTS.md | wc -l) ))
guideline_lines=0
if [ -d .ai/guidelines ]; then
  guideline_lines=$(( $(find .ai/guidelines -type f -exec cat {} + | wc -l) ))
fi
claude_lines=$(( $(wc -l < CLAUDE.md) ))
hand_written=$((header_lines + guideline_lines + claude_lines))

echo "Hand-written agent instructions: ${hand_written} of ${HAND_WRITTEN_BUDGET} lines (AGENTS.md header ${header_lines}, .ai/guidelines ${guideline_lines}, CLAUDE.md ${claude_lines})."

if [ "${hand_written}" -gt "${HAND_WRITTEN_BUDGET}" ]; then
  fail "The hand-written agent instructions exceed ${HAND_WRITTEN_BUDGET} lines. Every agent loads them in every session and adherence drops as they grow. Move knowledge to docs/ and leave a pointer."
fi

exit "${failed}"
