#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "$0")" && pwd)"
setup_script="${skill_dir}/scripts/agent_setup.py"
workspace="$(mktemp -d)"
trap 'rm -rf "${workspace}"' EXIT
repo="${workspace}/repo"
output=""
cases=0

fail() {
  printf 'FAIL agent-instructions: %s\n' "$1" >&2
  if [ -n "${2:-}" ]; then
    printf '%s\n' "$2" >&2
  fi
  exit 1
}

agent_setup() {
  python3 "${setup_script}" "$@"
}

expect_status() {
  local expected="$1" description="$2" status=0
  shift 2
  output="$("$@" 2>&1)" || status=$?
  cases=$((cases + 1))
  if [ "${status}" -ne "${expected}" ]; then
    fail "${description}: expected exit ${expected}, got ${status}:" "${output}"
  fi
}

expect_output() {
  grep -qF -- "$1" <<< "${output}" || fail "$2: expected \"$1\" in:" "${output}"
}

reject_output() {
  if grep -qE -- "$1" <<< "${output}"; then
    fail "$2: did not expect /$1/ in:" "${output}"
  fi
}

expect_file_line() {
  grep -qxF -- "$2" "${repo}/$1" || fail "$3: expected the line \"$2\" in $1:" "$(cat "${repo}/$1")"
}

snapshot() {
  (cd "$1" && find . -path ./.git -prune -o -print | LC_ALL=C sort | while IFS= read -r entry; do
    if [ -L "${entry}" ]; then
      printf '%s -> %s\n' "${entry}" "$(readlink "${entry}")"
    elif [ -f "${entry}" ]; then
      printf '%s %s\n' "${entry}" "$(cksum < "${entry}")"
    else
      printf '%s/\n' "${entry}"
    fi
  done)
}

expect_unchanged() {
  local after
  after="$(snapshot "${repo}")"
  [ "$1" = "${after}" ] || fail "$2: the repository changed:" "$(diff <(printf '%s\n' "$1") <(printf '%s\n' "${after}") || true)"
}

new_repo() {
  rm -rf "${repo}"
  mkdir -p "${repo}"
}

write_sources() {
  mkdir -p "${repo}/.ai/rules" "${repo}/docs/flows" "${repo}/src/Billing" "${repo}/tests"
  printf '<?php\n' > "${repo}/src/Billing/Invoice.php"
  printf '<?php\n' > "${repo}/tests/InvoiceTest.php"
  printf -- '---\npaths:\n  - "src/**/*.{php,inc}"\n---\n\n# Billing amounts\n\n- Read amounts from the stored snapshot ([billing](../../docs/flows/billing.md#reading-amounts)).\n' > "${repo}/.ai/rules/billing.md"
  printf -- '---\npaths: "tests/**"\n---\n\n# Tests\n\n- Fake the queue in every test ([testing](../../docs/testing.md)).\n' > "${repo}/.ai/rules/tests.md"
  printf '# Billing\n\n## Reading amounts\n\nRead them.\n' > "${repo}/docs/flows/billing.md"
  printf '# Testing\n' > "${repo}/docs/testing.md"
  printf '# Index\n\n- [Billing](flows/billing.md)\n- [Testing](testing.md)\n' > "${repo}/docs/index.md"
  printf 'knowledge_base:\n  code_guidelines:\n    filePatterns:\n      - "docs/**/*.md"\n      # agent-setup:begin\n      # agent-setup:end\n' > "${repo}/.coderabbit.yaml"
}

write_clean_repo() {
  new_repo
  write_sources
  agent_setup layout "${repo}" --apply --targets cursor,copilot,coderabbit,antigravity,kiro,cline,devin-desktop > /dev/null
  agent_setup generate "${repo}" > /dev/null
}

set_config() {
  python3 - "${repo}/.ai/agent-setup.json" "$1" "$2" << 'PYTHON'
import json
import sys
from pathlib import Path

path, key, value = Path(sys.argv[1]), sys.argv[2], json.loads(sys.argv[3])
config = json.loads(path.read_text())
config[key] = value
path.write_text(json.dumps(config, indent=2) + "\n")
PYTHON
}

expect_check_failure() {
  expect_status 1 "check should fail on: $2" agent_setup check "${repo}"
  expect_output "$1" "check finding for $2"
}

test_inventory() {
  new_repo
  expect_status 0 "inventory of an empty repository" agent_setup inventory "${repo}" --json
  python3 - "${output}" << 'PYTHON' || fail "inventory of an empty repository reported something" "${output}"
import json
import sys

report = json.loads(sys.argv[1])
assert report["instruction_files"] == [], report["instruction_files"]
assert report["claude_md"] == "absent"
assert report["agents_detected"] == []
assert report["targets"] == ["claude-code"]
assert report["always_loaded"]["tokens"] == 0
assert [row["state"] for row in report["symlinks"]] == ["missing", "missing"]
PYTHON

  mkdir -p "${repo}/packages/api" "${repo}/.cursor/rules" "${repo}/.github/workflows" "${repo}/.claude" "${repo}/docs"
  printf '# Our rules\n\n- Use tabs.\n' > "${repo}/CLAUDE.md"
  printf '# Agents\n\nSee [docs](docs/index.md).\n\n## Code Review Rules\n\n- Flag raw SQL.\n' > "${repo}/AGENTS.md"
  printf '# Review\n\n- Flag raw SQL.\n' > "${repo}/REVIEW.md"
  printf 'jobs:\n  claude:\n    steps:\n      - uses: anthropics/claude-code-action@v1\n' > "${repo}/.github/workflows/claude.yml"
  printf '# API\n' > "${repo}/packages/api/AGENTS.md"
  printf 'Always use tabs.\n' > "${repo}/.cursorrules"
  printf -- '---\nglobs: src/**\nalwaysApply: false\n---\nOld rule.\n' > "${repo}/.cursor/rules/old.mdc"
  printf '# Copilot\n' > "${repo}/.github/copilot-instructions.md"
  printf 'steps: []\n' > "${repo}/.github/workflows/copilot-setup-steps.yml"
  printf 'reviews:\n  profile: chill\n' > "${repo}/.coderabbit.yaml"
  printf '{"require-dev": {"laravel/boost": "^2.0"}}\n' > "${repo}/composer.json"
  printf '{"simple-git-hooks": {"pre-commit": "npm test"}}\n' > "${repo}/package.json"
  printf 'stages: [test]\n' > "${repo}/.gitlab-ci.yml"
  printf 'pre-commit:\n  jobs: []\n' > "${repo}/lefthook.yml"
  printf '{"mcpServers": {}}\n' > "${repo}/.mcp.json"
  printf '{"hooks": {}}\n' > "${repo}/.claude/settings.json"
  printf '# Docs\n' > "${repo}/docs/index.md"
  printf 'site_name: x\n' > "${repo}/mkdocs.yml"
  expect_status 0 "inventory of a messy repository" agent_setup inventory "${repo}" --json
  python3 - "${output}" << 'PYTHON' || fail "inventory of a messy repository missed something" "${output}"
import json
import sys

report = json.loads(sys.argv[1])
paths = {entry["path"]: entry for entry in report["instruction_files"]}
assert {"CLAUDE.md", "AGENTS.md", ".cursorrules", ".github/copilot-instructions.md"} <= set(paths), sorted(paths)
assert paths["packages/api/AGENTS.md"]["nested"] is True
assert report["claude_md"] == "other-content"
assert {"claude-code", "cursor", "copilot", "copilot-cloud-agent", "claude-code-action", "coderabbit"} <= set(report["agents_detected"]), report["agents_detected"]
assert [row["tool"] for row in report["review_bots"]] == ["coderabbit", "codex-code-review"], report["review_bots"]
assert "REVIEW.md" in paths
assert any(note.startswith("REVIEW.md is present: GitHub Copilot code review") for note in report["notes"]), report["notes"]
assert [row["tool"] for row in report["generators"]] == ["laravel-boost"]
assert {"gitlab-ci", "github-actions"} <= {row["tool"] for row in report["ci"]}
assert {"lefthook", "simple-git-hooks"} <= {row["tool"] for row in report["hook_managers"]}
assert ".mcp.json" in report["mcp_configs"]
assert ".github/workflows/copilot-setup-steps.yml" in [row["path"] for row in report["cloud_agent_setup"]]
assert ".claude/settings.json" in [row["path"] for row in report["hooks_files"]]
assert report["docs"]["sites"] == ["mkdocs.yml"]
assert report["always_loaded"]["tokens"] > 0
assert any(note.startswith("Cursor also runs Claude Code's hooks") for note in report["notes"]), report["notes"]
PYTHON
  expect_status 0 "inventory text report" agent_setup inventory "${repo}"
  expect_output "CLAUDE.md: holds its own instructions" "inventory text report"
}

test_layout() {
  local before
  new_repo
  before="$(snapshot "${repo}")"
  expect_status 0 "layout dry run on an empty repository" agent_setup layout "${repo}"
  expect_output "(dry run; --apply writes it)" "layout dry run"
  expect_output "create  AGENTS.md" "layout dry run"
  expect_unchanged "${before}" "layout without --apply"

  expect_status 0 "layout --apply on an empty repository" agent_setup layout "${repo}" --apply
  [ "$(head -n 1 "${repo}/CLAUDE.md")" = "@AGENTS.md" ] || fail "CLAUDE.md does not start with @AGENTS.md"
  [ "$(readlink "${repo}/.claude/rules")" = "../.ai/rules" ] || fail ".claude/rules is not a symlink to ../.ai/rules"
  [ "$(readlink "${repo}/.claude/skills")" = "../.agents/skills" ] || fail ".claude/skills is not a symlink to ../.agents/skills"
  for path in .ai/agent-setup.json AGENTS.md docs/index.md .ai/rules/.gitkeep .agents/skills/.gitkeep; do
    [ -e "${repo}/${path}" ] || fail "layout --apply did not create ${path}"
  done
  expect_file_line .gitignore "CLAUDE.local.md" "layout --apply"
  expect_file_line .gitignore ".claude/settings.local.json" "layout --apply"
  before="$(snapshot "${repo}")"
  expect_status 0 "a second layout --apply" agent_setup layout "${repo}" --apply
  reject_output "^(create|update|link) " "a second layout --apply"
  expect_unchanged "${before}" "a second layout --apply"
  expect_status 0 "check after layout --apply" agent_setup check "${repo}"

  new_repo
  python3 -c 'import sys; open(sys.argv[1], "w").write("x" * 9999 + "\n")' "${repo}/AGENTS.md"
  expect_status 0 "layout measures the token budget" agent_setup layout "${repo}" --apply
  expect_output "token_budget 4000: every session will load about 3452 tokens (10011 bytes / 2.9), plus 15%, rounded up to the next 100" "layout measures the token budget"
  python3 -c 'import json, sys; assert json.load(open(sys.argv[1]))["token_budget"] == 4000' "${repo}/.ai/agent-setup.json" || fail "layout did not write the measured token_budget"
  expect_status 0 "check within the measured token budget" agent_setup check "${repo}"

  new_repo
  printf '# Project rules\n\n- Use tabs.\n' > "${repo}/CLAUDE.md"
  before="$(cksum < "${repo}/CLAUDE.md")"
  expect_status 1 "layout with a hand-written CLAUDE.md" agent_setup layout "${repo}" --apply
  expect_output "merge by hand: move its content into AGENTS.md or docs/, then make line 1 \`@AGENTS.md\`" "layout with a hand-written CLAUDE.md"
  [ "$(cksum < "${repo}/CLAUDE.md")" = "${before}" ] || fail "layout --apply changed a hand-written CLAUDE.md"

  new_repo
  printf '# Agents\n' > "${repo}/AGENTS.md"
  ln -s AGENTS.md "${repo}/CLAUDE.md"
  expect_status 0 "layout with CLAUDE.md as a symlink to AGENTS.md" agent_setup layout "${repo}" --apply
  { [ ! -L "${repo}/CLAUDE.md" ] && [ "$(cat "${repo}/CLAUDE.md")" = "@AGENTS.md" ]; } || fail "layout did not turn the CLAUDE.md symlink into an import"
  [ "$(cat "${repo}/AGENTS.md")" = "# Agents" ] || fail "layout changed AGENTS.md while replacing the CLAUDE.md symlink"

  new_repo
  mkdir -p "${repo}/.claude/skills/mine"
  expect_status 1 "layout with a real .claude/skills directory" agent_setup layout "${repo}" --apply
  expect_output ".claude/skills  is a real directory, which layout never replaces" "layout with a real .claude/skills directory"
  { [ -d "${repo}/.claude/skills/mine" ] && [ ! -L "${repo}/.claude/skills" ]; } || fail "layout replaced a real .claude/skills directory"

  new_repo
  printf 'node_modules/\n.ai/\n/.claude/\n' > "${repo}/.gitignore"
  expect_status 0 "layout with .ai and .claude ignored wholesale" agent_setup layout "${repo}" --apply
  for line in ".ai/*" "!.ai/rules/" "!.ai/guidelines/" "!.ai/skills/" "!.ai/agent-setup.json" ".claude/*" "!.claude/rules" "!.claude/skills" "!.claude/settings.json" "node_modules/"; do
    expect_file_line .gitignore "${line}" "the .gitignore allowlist"
  done
  if grep -qxF ".ai/" "${repo}/.gitignore"; then
    fail "layout kept the wholesale .ai/ ignore"
  fi
  before="$(cksum < "${repo}/.gitignore")"
  expect_status 0 "a second layout with the allowlist in place" agent_setup layout "${repo}" --apply
  [ "$(cksum < "${repo}/.gitignore")" = "${before}" ] || fail "a second layout --apply changed .gitignore"
  if command -v git > /dev/null 2>&1; then
    git -C "${repo}" init -q
    for path in .ai/agent-setup.json .ai/rules/.gitkeep .claude/rules .claude/skills; do
      if git -C "${repo}" check-ignore -q "${path}"; then
        fail "git still ignores ${path} after layout --apply"
      fi
    done
  fi

  new_repo
  printf '{"require-dev": {"laravel/boost": "^2.0"}}\n' > "${repo}/composer.json"
  expect_status 0 "layout in a Laravel Boost repository" agent_setup layout "${repo}" --apply
  expect_output "is generated by Laravel Boost" "layout in a Laravel Boost repository"
  [ -f "${repo}/.ai/skills/.gitkeep" ] || fail "layout did not create .ai/skills in a Boost repository"
  [ ! -e "${repo}/.agents/skills" ] || fail "layout created .agents/skills, which Boost generates"
  [ "$(readlink "${repo}/.claude/skills")" = "../.agents/skills" ] || fail ".claude/skills is not linked in a Boost repository"
  mkdir -p "${repo}/.ai/rules/boost"
  printf -- '---\npaths:\n  - "nowhere/**"\n---\n# Boost\n' > "${repo}/.ai/rules/boost/laravel.md"
  printf '# Rule index\n' > "${repo}/.ai/rules/index.md"
  expect_status 0 "check skips the rules Laravel Boost owns" agent_setup check "${repo}"

  new_repo
  printf '{"require": {"symfony/ai-mate": "^1.0"}}\n' > "${repo}/composer.json"
  mkdir -p "${repo}/.claude/skills"
  expect_status 0 "layout in a Symfony AI Mate repository" agent_setup layout "${repo}" --apply
  reject_output "^manual" "layout in a Symfony AI Mate repository"
  expect_status 0 "check leaves .claude/skills to Symfony AI Mate" agent_setup check "${repo}"
  expect_status 0 "inventory in a Symfony AI Mate repository" agent_setup inventory "${repo}"
  expect_output "Symfony AI Mate manages .claude/skills/" "inventory in a Symfony AI Mate repository"
}

test_generate() {
  local before
  write_clean_repo
  for path in .cursor/rules/billing.mdc .github/instructions/billing.instructions.md .agents/rules/billing.md .kiro/steering/billing.md .clinerules/billing.md .devin/rules/billing.md .cursor/rules/tests.mdc; do
    grep -qF '<!-- Generated by agent_setup.py from .ai/rules/' "${repo}/${path}" || fail "generate did not write ${path} with its marker"
  done
  expect_file_line .cursor/rules/billing.mdc "description: Billing amounts" "cursor rule"
  expect_file_line .cursor/rules/billing.mdc "globs: src/**/*.php, src/**/*.inc" "cursor rule"
  expect_file_line .cursor/rules/billing.mdc "alwaysApply: false" "cursor rule"
  expect_file_line .github/instructions/billing.instructions.md 'applyTo: "src/**/*.php,src/**/*.inc"' "copilot instructions"
  expect_file_line .agents/rules/billing.md "trigger: glob" "antigravity rule"
  expect_file_line .agents/rules/billing.md 'globs: "src/**/*.php, src/**/*.inc"' "antigravity rule"
  expect_file_line .devin/rules/billing.md "trigger: glob" "devin desktop rule"
  expect_file_line .devin/rules/billing.md "globs: src/**/*.php, src/**/*.inc" "devin desktop rule"
  expect_file_line .kiro/steering/billing.md 'fileMatchPattern: ["src/**/*.php", "src/**/*.inc"]' "kiro steering"
  expect_file_line .kiro/steering/tests.md 'fileMatchPattern: "tests/**"' "kiro steering"
  expect_file_line .clinerules/billing.md '  - "src/**/*.php"' "cline rule"
  expect_file_line .clinerules/billing.md '- Read amounts from the stored snapshot ([billing](../docs/flows/billing.md#reading-amounts)).' "cline rule links rebased to depth 1"
  expect_file_line .coderabbit.yaml '      - "docs/**/*.md"' "a hand-written CodeRabbit entry"
  expect_file_line .coderabbit.yaml '      - files: ".ai/rules/billing.md"' "the CodeRabbit block"
  expect_file_line .coderabbit.yaml '        applyTo: "src/**/*.php,src/**/*.inc"' "the CodeRabbit block"

  before="$(snapshot "${repo}")"
  expect_status 0 "a second generate" agent_setup generate "${repo}"
  expect_output "every generated file is up to date" "a second generate"
  expect_unchanged "${before}" "a second generate"
  expect_status 0 "generate --check on a clean repository" agent_setup generate "${repo}" --check
  expect_status 0 "check on a clean repository" agent_setup check "${repo}"
  expect_output "agent_setup.py check: clean" "check on a clean repository"

  printf -- '- Seed the clock.\n' >> "${repo}/.ai/rules/tests.md"
  before="$(snapshot "${repo}")"
  expect_status 1 "generate --check after a rule changed" agent_setup generate "${repo}" --check
  expect_output "would update .cursor/rules/tests.mdc (from .ai/rules/tests.md)" "generate --check after a rule changed"
  reject_output "would update \.coderabbit\.yaml" "generate --check after a change that keeps the paths"
  expect_unchanged "${before}" "generate --check"

  write_clean_repo
  rm "${repo}/.ai/rules/tests.md"
  expect_status 0 "generate after a rule was deleted" agent_setup generate "${repo}"
  expect_output "delete .cursor/rules/tests.mdc (generated from .ai/rules/tests.md, which is gone)" "generate after a rule was deleted"
  for path in .cursor/rules/tests.mdc .github/instructions/tests.instructions.md .agents/rules/tests.md .kiro/steering/tests.md .clinerules/tests.md .devin/rules/tests.md; do
    [ ! -e "${repo}/${path}" ] || fail "generate left the stale ${path}"
  done
  if grep -qF ".ai/rules/tests.md" "${repo}/.coderabbit.yaml"; then
    fail "generate left the deleted rule in the CodeRabbit block"
  fi

  write_clean_repo
  printf 'My own Cursor rule.\n' > "${repo}/.cursor/rules/billing.mdc"
  printf -- '---\nalwaysApply: true\n---\nMy unrelated rule.\n' > "${repo}/.cursor/rules/mine.mdc"
  expect_status 1 "generate over a hand-written file of the same name" agent_setup generate "${repo}"
  expect_output ".cursor/rules/billing.mdc is hand-written, and .ai/rules/billing.md would generate a file with the same name" "generate over a hand-written file"
  [ "$(cat "${repo}/.cursor/rules/billing.mdc")" = "My own Cursor rule." ] || fail "generate overwrote a hand-written .mdc"
  [ -f "${repo}/.cursor/rules/mine.mdc" ] || fail "generate deleted an unrelated hand-written .mdc"

  write_clean_repo
  printf 'knowledge_base:\n  code_guidelines:\n    enabled: true\n' > "${repo}/.coderabbit.yaml"
  expect_status 1 "generate without CodeRabbit markers" agent_setup generate "${repo}"
  expect_output "# agent-setup:begin generated from .ai/rules by agent_setup.py generate" "the block to paste"
  expect_output '      - files: ".ai/rules/billing.md"' "the block to paste"

  write_clean_repo
  printf 'knowledge_base:\n  code_guidelines:\n    # agent-setup:begin\n    # agent-setup:end\n' > "${repo}/.coderabbit.yaml"
  expect_status 1 "generate with misplaced CodeRabbit markers" agent_setup generate "${repo}"
  expect_output "not under knowledge_base.code_guidelines.filePatterns" "generate with misplaced CodeRabbit markers"

  write_clean_repo
  rm "${repo}/.coderabbit.yaml"
  printf 'export default {};\n' > "${repo}/.coderabbit.config.ts"
  expect_status 1 "generate next to a CodeRabbit TypeScript config without markers" agent_setup generate "${repo}"
  expect_output "in a YAML file under .coderabbit/ that .coderabbit.config.ts imports" "generate next to a CodeRabbit TypeScript config"
  [ ! -e "${repo}/.coderabbit.yaml" ] || fail "generate created .coderabbit.yaml next to .coderabbit.config.ts"
  mkdir -p "${repo}/.coderabbit"
  printf 'knowledge_base:\n  code_guidelines:\n    filePatterns:\n      # agent-setup:begin\n      # agent-setup:end\n' > "${repo}/.coderabbit/guidelines.yaml"
  expect_status 0 "generate into a CodeRabbit fragment the TypeScript config imports" agent_setup generate "${repo}"
  expect_file_line .coderabbit/guidelines.yaml '      - files: ".ai/rules/billing.md"' "the CodeRabbit fragment"
  expect_status 0 "check with the CodeRabbit block in a fragment" agent_setup check "${repo}"

  write_clean_repo
  rm "${repo}/.coderabbit.yaml"
  expect_status 1 "generate without any CodeRabbit config" agent_setup generate "${repo}"
  expect_output "Paste this in a new .coderabbit.yaml that starts with # yaml-language-server: \$schema=https://coderabbit.ai/integrations/schema.v2.json" "generate without any CodeRabbit config"
  expect_output '      - files: ".ai/rules/billing.md"' "generate without any CodeRabbit config"
  [ ! -e "${repo}/.coderabbit.yaml" ] || fail "generate created a CodeRabbit config instead of printing the block"

  write_clean_repo
  set_config targets '["claude-code", "copilot"]'
  expect_status 0 "generate with cursor no longer a target" agent_setup generate "${repo}"
  [ -f "${repo}/.cursor/rules/billing.mdc" ] || fail "generate pruned the files of a target that is no longer enabled"

  write_clean_repo
  printf -- '---\npaths:\n  - *.php\n---\n# Bare glob\n' > "${repo}/.ai/rules/bare.md"
  before="$(snapshot "${repo}")"
  expect_status 1 "generate with an unquoted * glob" agent_setup generate "${repo}"
  expect_output "starts with *, which YAML does not read as text; quote it" "generate with an unquoted * glob"
  expect_output "nothing was written" "generate with an unquoted * glob"
  expect_unchanged "${before}" "generate with an unreadable rule"
}

test_check_failures() {
  write_clean_repo
  printf '# Notes\n\n@AGENTS.md\n' > "${repo}/CLAUDE.md"
  expect_check_failure "line 1 of CLAUDE.md is '# Notes', not @AGENTS.md" "CLAUDE.md line 1"

  write_clean_repo
  rm "${repo}/CLAUDE.md"
  ln -s AGENTS.md "${repo}/CLAUDE.md"
  expect_check_failure "CLAUDE.md is a symlink to AGENTS.md" "a CLAUDE.md symlink"

  write_clean_repo
  rm "${repo}/.claude/rules"
  expect_check_failure ".claude/rules is missing: make it a symlink to ../.ai/rules" "a missing .claude/rules"

  write_clean_repo
  ln -sfn ../elsewhere "${repo}/.claude/skills"
  expect_check_failure ".claude/skills points to ../elsewhere, not ../.agents/skills" "a wrong .claude/skills"

  write_clean_repo
  printf -- '- Seed the clock.\n' >> "${repo}/.ai/rules/tests.md"
  expect_check_failure ".cursor/rules/tests.mdc is out of date with .ai/rules/tests.md" "a stale generated file"

  write_clean_repo
  printf -- '- A hand edit.\n' >> "${repo}/.cursor/rules/billing.mdc"
  expect_check_failure ".cursor/rules/billing.mdc is out of date with .ai/rules/billing.md" "a hand edit in a generated file"

  write_clean_repo
  rm "${repo}/.ai/rules/tests.md"
  expect_check_failure ".cursor/rules/tests.mdc was generated from .ai/rules/tests.md, which no longer exists" "an orphaned generated file"

  write_clean_repo
  mkdir -p "${repo}/build"
  printf '<?php\n' > "${repo}/build/cache.php"
  printf 'build/\n' >> "${repo}/.gitignore"
  printf -- '---\npaths:\n  - "build/**"\n---\n# Build\n' > "${repo}/.ai/rules/build.md"
  agent_setup generate "${repo}" > /dev/null
  expect_check_failure ".ai/rules/build.md: the glob build/** matches no file" "a glob matching only ignored files without git"

  write_clean_repo
  printf '# Unscoped\n\n- Always do this.\n' > "${repo}/.ai/rules/unscoped.md"
  expect_check_failure ".ai/rules/unscoped.md has no paths: frontmatter" "a rule without paths"

  write_clean_repo
  printf -- '---\npaths:\n  - "lib/**"\n---\n# Gone\n' > "${repo}/.ai/rules/gone.md"
  expect_check_failure ".ai/rules/gone.md: the glob lib/** matches no file" "a glob matching nothing"

  write_clean_repo
  printf -- '---\npaths:\n  - "*.php"\n---\n# Root only\n' > "${repo}/.ai/rules/root.md"
  expect_check_failure ".ai/rules/root.md: the glob *.php matches no file" "a glob anchored at the root"

  write_clean_repo
  { printf -- '---\npaths: "tests/**"\n---\n'; seq 1 25; } > "${repo}/.ai/rules/long.md"
  expect_check_failure ".ai/rules/long.md has 28 lines, over the 20-line limit" "a rule over the line limit"

  write_clean_repo
  mkdir -p "${repo}/.ai/rules/nested"
  expect_check_failure ".ai/rules/nested is a subdirectory" "a rule subdirectory"

  write_clean_repo
  printf -- '---\npaths:\n  - *.php\n---\n# Bare\n' > "${repo}/.ai/rules/bare.md"
  expect_check_failure ".ai/rules/bare.md: cannot read its frontmatter" "an unquoted glob"

  write_clean_repo
  printf -- '---\npaths: "tests/**"\n---\n- [missing](../../docs/missing.md)\n' > "${repo}/.ai/rules/broken.md"
  expect_check_failure ".ai/rules/broken.md links to ../../docs/missing.md, which does not exist" "a broken link in a rule"

  write_clean_repo
  printf '\nSee [the guide](docs/gone.md).\n' >> "${repo}/AGENTS.md"
  expect_check_failure "AGENTS.md links to docs/gone.md, which does not exist" "a broken link in AGENTS.md"

  write_clean_repo
  printf -- '---\npaths: "tests/**"\n---\n- [anchor](../../docs/testing.md#nowhere)\n' > "${repo}/.ai/rules/anchor.md"
  expect_check_failure "docs/testing.md has no heading with the anchor #nowhere" "a broken anchor in a rule"

  write_clean_repo
  printf -- '- [Gone](flows/gone.md)\n' >> "${repo}/docs/index.md"
  expect_check_failure "docs/index.md links to flows/gone.md, which does not exist" "a broken link in docs"

  write_clean_repo
  printf '# Orphan\n' > "${repo}/docs/orphan.md"
  expect_check_failure "docs/orphan.md is not linked from docs/index.md" "a doc missing from the index"

  write_clean_repo
  set_config token_budget 10
  expect_check_failure "over the token_budget of 10 in .ai/agent-setup.json" "the token budget"

  write_clean_repo
  python3 -c 'import sys; open(sys.argv[1], "a").write("x" * 33000 + "\n")' "${repo}/AGENTS.md"
  expect_check_failure "over the 32768-byte cap" "the AGENTS.md size cap"

  write_clean_repo
  printf '@AGENTS.md\n@docs/missing.md\n' > "${repo}/CLAUDE.md"
  expect_check_failure "CLAUDE.md imports @docs/missing.md, which does not exist" "a missing import"

  write_clean_repo
  expect_status 0 "check with a measured bytes-per-token" agent_setup check "${repo}" --bytes-per-token 4
  expect_output "/ 4.0; budget 200)" "check with a measured bytes-per-token"
  expect_status 2 "check with zero bytes per token" agent_setup check "${repo}" --bytes-per-token 0
  set_config targets '["claude-code", "no-such-tool"]'
  expect_status 2 "check with an unknown target" agent_setup check "${repo}"
  expect_output "unknown tool 'no-such-tool'" "check with an unknown target"
  printf '{"targets": [' > "${repo}/.ai/agent-setup.json"
  expect_status 2 "check with broken JSON config" agent_setup check "${repo}"
  printf '{"rule_limit": 5}\n' > "${repo}/.ai/agent-setup.json"
  expect_status 2 "check with an unknown config key" agent_setup check "${repo}"
  expect_output "unknown keys rule_limit" "check with an unknown config key"
}

test_git_checkout() {
  if ! command -v git > /dev/null 2>&1; then
    echo "SKIP agent-instructions: git is not installed, so the git-mode checks of agent_setup.py did not run."
    return
  fi
  write_clean_repo
  git -C "${repo}" init -q
  git -C "${repo}" add -A
  expect_status 0 "check in a git checkout" agent_setup check "${repo}"

  mkdir -p "${repo}/build"
  printf '<?php\n' > "${repo}/build/cache.php"
  printf 'build/\n' >> "${repo}/.gitignore"
  printf -- '---\npaths:\n  - "build/**"\n---\n# Build\n' > "${repo}/.ai/rules/build.md"
  agent_setup generate "${repo}" > /dev/null
  expect_check_failure ".ai/rules/build.md: the glob build/** matches no file" "a glob matching only ignored files"
  expect_output ".ai/rules/build.md is not in git: git add it" "an untracked rule"
  expect_output ".cursor/rules/build.mdc is not in git" "an untracked generated file"
}

test_drift_script() {
  write_clean_repo
  printf '# Orphan\n' > "${repo}/docs/orphan.md"
  expect_status 1 "the drift script with a file-level finding" sh -c 'cd "$1" && sh "$2"' drift "${repo}" "${skill_dir}/assets/check-generated-instructions.sh"
  expect_output "FAIL: docs/orphan.md is not linked from docs/index.md" "the drift script runs agent_setup.py check"
}

run_agent_setup_tests() {
  test_inventory
  test_layout
  test_generate
  test_check_failures
  test_git_checkout
  test_drift_script
  echo "agent-instructions: agent_setup.py passed ${cases} cases"
}

if command -v python3 > /dev/null 2>&1; then
  run_agent_setup_tests
else
  echo "SKIP agent-instructions: python3 is not installed, so agent_setup.py did not run."
fi
