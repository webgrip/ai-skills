# agent-instructions

A skill for the files every coding agent loads in every session: `CLAUDE.md`, `AGENTS.md` and
their relatives (`.claude/rules`, `.cursor/rules`, `copilot-instructions.md`). It writes new ones,
audits and slims down bloated ones, and decides where each line belongs.

- **What goes where**: instruction file, `docs/` with a pointer, hook or CI check, skill, path
  rule, another level, or nowhere, with the line test "would removing this cause a mistake?".
- **Levels**: organisation, stack, repo, path and person, with one owner per rule, and personal
  rules scoped so they do not leak into other organisations' repos.
- **One canonical file**: `AGENTS.md` for every tool, `CLAUDE.md` as `@AGENTS.md`, one skills
  directory (`.agents/skills`, with `.claude/skills` as a symlink).
- **Measure**: `scripts/measure.py` reports sizes, launch cost, the CLAUDE.md/AGENTS.md relation,
  emphasis, paragraph-long lines, dead links, generated blocks, duplicate skills and the Codex
  32 KiB cap. Stdlib only; `--budget-lines` and `--fail-on` make it a CI gate.
- **Generated files**: Laravel Boost, rulesync, Ruler and Nx; where team text goes, what breaks on
  regeneration, machine-dependent output, and `assets/check-generated-instructions.sh` as a CI
  drift check for Boost repos.
- **Enforcement**: rules turned into permission rules, hooks and CI, with hook templates for
  generated paths, lint-on-edit and a tests-before-stop gate.
- **Probe**: `scripts/probe.py` A/B-tests an instruction change with headless Claude Code runs in
  fresh worktrees, deterministic graders, pass rates with a Fisher exact p, tokens and cost.
- **Security**: `measure.py --security-only` flags hidden Unicode, fetch-and-execute lines,
  secrets, broad permission grants and risky MCP or hook config, with a review checklist.
- **Layering, routing, unattended agents**: per-level distribution and precedence per tool, a
  pointer-table template for routing to docs, and what cloud, CI and headless agents need.
- **Evidence**: the studies (ETH, McMillan, Vercel's eval and others) with what they do and do not
  show, and the cross-tool loading table for Claude Code, Codex, Cursor, Copilot, Gemini CLI,
  opencode, OpenHands, Junie, Windsurf, Zed and Kiro.

## Install

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s agent-instructions -g
```

Claude Code plugin: `/plugin install agent-instructions@ai-skills`.

## Example prompts

- "Our CLAUDE.md is 500 lines and Claude ignores half of it. Clean it up."
- "Set up AGENTS.md for this repo; the team uses Claude Code, Cursor and opencode."
- "boost:install keeps wiping our project rules. How do we stop that?"
- "Should this rule be in CLAUDE.md, a skill or a hook?"
