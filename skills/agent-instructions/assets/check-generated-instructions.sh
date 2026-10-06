#!/bin/sh
set -e

HAND_WRITTEN_BUDGET="${AGENT_INSTRUCTIONS_BUDGET:-150}"
TOKEN_BUDGET="${AGENT_INSTRUCTIONS_TOKEN_BUDGET:-}"
BOOST_FLAGS="${AGENT_INSTRUCTIONS_BOOST_FLAGS:---guidelines --skills}"
RULES_DIR="${AGENT_INSTRUCTIONS_RULES_DIR:-.ai/rules}"
RULES_CHECK="${AGENT_INSTRUCTIONS_RULES_CHECK:-$(dirname "$0")/check-instruction-rules.php}"
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

if grep -q "<laravel-boost-guidelines>" CLAUDE.md 2>/dev/null; then
  fail "CLAUDE.md contains a generated Boost block. Claude Code ignores AGENTS.md while CLAUDE.md exists, so that block goes stale: remove it and keep only @AGENTS.md plus Claude-only lines."
fi

if [ ! -L .claude/skills ] || [ "$(readlink .claude/skills)" != "../.agents/skills" ]; then
  fail ".claude/skills must be a symlink to ../.agents/skills. Claude Code only reads .claude/skills; the other agents read .agents/skills."
fi

if [ -d "${RULES_DIR}" ] && { [ ! -L .claude/rules ] || [ "$(readlink .claude/rules)" != "../${RULES_DIR}" ]; }; then
  fail ".claude/rules must be a symlink to ../${RULES_DIR}. Claude Code loads a path-scoped rule by itself only from .claude/rules; the committed rules live in ${RULES_DIR}."
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

if [ -n "${TOKEN_BUDGET}" ]; then
  always_loaded_bytes=$(( $(cat AGENTS.md CLAUDE.md | wc -c) ))
  if [ -d "${RULES_DIR}" ]; then
    for rule in "${RULES_DIR}"/*.md; do
      [ -f "${rule}" ] || continue
      if ! sed -n '/^---$/,/^---$/p' "${rule}" | grep -q '^paths:'; then
        always_loaded_bytes=$(( always_loaded_bytes + $(wc -c < "${rule}") ))
      fi
    done
  fi
  always_loaded_tokens=$((always_loaded_bytes / 4))
  echo "Loaded in every session: about ${always_loaded_tokens} of ${TOKEN_BUDGET} tokens (AGENTS.md, CLAUDE.md and rules without paths, bytes / 4)."
  if [ "${always_loaded_tokens}" -gt "${TOKEN_BUDGET}" ]; then
    fail "What every session loads is about ${always_loaded_tokens} tokens, over the budget of ${TOKEN_BUDGET}. A generator upgrade that grows its block shows up here too: move knowledge to docs/ and scope file-specific instructions to a rule with paths."
  fi
fi

if [ -f "${RULES_CHECK}" ] && ! php "${RULES_CHECK}"; then
  failed=1
fi

exit "${failed}"
