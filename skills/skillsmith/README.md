# skillsmith

A Claude skill for **writing Claude skills** — authoring, editing, and auditing `SKILL.md` files for the model that consumes them, not the human who reads them. Every rule derives from the verified skill loading/token model, not folklore.

What it teaches Claude:

- **The cost model** — the three token tiers (always-on names, discovery descriptions sharing a ~1% budget with a 1,536-char cap, session-resident bodies) and what each implies for where content belongs
- **Descriptions as routers** — tuning `description` + `when_to_use` for trigger accuracy instead of summarizing
- **Body rules** — decision-first structure, concrete paths over prose, guardrails only for live traps
- **Progressive disclosure** — when to split into `reference.md`/`scripts/` siblings and how deep references may nest
- **Boundaries** — what belongs in a skill vs CLAUDE.md vs memory vs a runbook
- **Auditing & evals** — token-diet passes, smells to cut on sight, and how to measure trigger accuracy and output quality of an installed skill (`reference.md` carries the full frontmatter catalog, string substitutions, and eval methodology)

## Install

**`npx skills` (recommended — works in every agent, not just Claude):**

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s skillsmith -g
```

**Claude Code plugin:**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install skillsmith@ai-skills
```

**Claude Code (manual):** copy `skills/skillsmith/` into your project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `skillsmith.skill` from the [latest release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases/latest), upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

## Use

Open Claude in a project and say, for example:

- *"create a skill for deploying to staging"*
- *"audit my skills for token waste"*
- *"this skill keeps triggering when it shouldn't — fix the description"*
- *"split this skill into a lean body plus reference file"*
- *"should this live in a skill or in CLAUDE.md?"*
- *"evaluate whether the foo skill actually improves output"*

## Why

Skills are procedures injected into a model's context, and every line has a recurring token cost while a vague description mis-routes the whole session. Most skill-writing advice optimizes for human readers; this skill encodes how the loader actually spends tokens (discovery budgets, compaction survival, supporting-file laziness) so each skill triggers exactly when relevant and costs as little as possible when it does.

## Contributing

Issues and PRs welcome. Before submitting: run the skill lint locally (`python3 scripts/lint_skills.py` from the repo root — CI runs the same check via `.forgejo/workflows/ci.yml`), and verify claimed loader mechanics against the [official skills docs](https://code.claude.com/docs/en/skills) rather than memory. Use a release-triggering conventional commit (`fix(skillsmith): ...`) — the release pipeline bumps the version and rebuilds the dist zip automatically.

## License

MIT
