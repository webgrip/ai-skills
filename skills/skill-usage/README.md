# skill-usage

Local skill-usage telemetry for a skills estate: a `PostToolUse` hook logs
every Skill invocation to `~/.claude/skill-usage.jsonl`, and the bundled
skill turns that log into a usage report — invocation counts, dead-skill
candidates, undertriggering suspects.

Why: install counts don't exist for private estates, and "which skills
actually get used?" is the question that keeps a curated estate curated
(the Claude Code team runs the same trick internally). Everything stays on
your machine — one local JSONL, no network, fail-open hook.

**Install (Claude Code):**

```text
/plugin install skill-usage@webgrip-ai-skills
```

**opencode twin:** `opencode/plugins/skill-usage-log.js` (installed by
`scripts/install_opencode.sh`) writes `~/.config/opencode/skill-usage.jsonl`.

**Example prompts:**

- "Which of our skills do we actually use? Usage report."
- "Find dead skills we should consolidate or remove."
- "Which skills look like they undertrigger?"
