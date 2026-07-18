# skill-usage

Local skill-usage telemetry for a skills estate: a `PostToolUse` hook logs
every Skill invocation to `~/.claude/skill-usage.jsonl`, and the bundled
skill turns that log into a usage report — invocation counts, dead-skill
candidates, undertriggering suspects.

Why: install counts don't exist for private estates, and "which skills
actually get used?" is the question that keeps a curated estate curated
(the Claude Code team runs the same trick internally). Everything stays on
your machine — one local JSONL, no network, fail-open hook.

**Install (Claude Code plugin — recommended for this skill):**

```text
/plugin install skill-usage@ai-skills
```

**Install (`npx skills`) — read this first:** the CLI copies `hooks/hooks.json`
but nothing registers it, so **nothing is logged** and the report has no data.
Either use the plugin route above, or register the hook yourself in
`~/.claude/settings.json` (`${CLAUDE_PLUGIN_ROOT}` does not exist outside the
plugin loader):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          { "type": "command", "command": "python3 \"$HOME/.agents/skills/skill-usage/scripts/log_usage.py\"" }
        ]
      }
    ]
  }
}
```

**opencode twin:** `opencode/plugins/skill-usage-log.js` (installed by
`scripts/install_opencode.sh`) writes `~/.config/opencode/skill-usage.jsonl`.

**Example prompts:**

- "Which of our skills do we actually use? Usage report."
- "Find dead skills we should consolidate or remove."
- "Which skills look like they undertrigger?"
