# Turning rules into enforcement

Prose is advisory and adherence decays over a session; a rule that must hold every time needs a
mechanism. Sources: Claude Code [hooks](https://code.claude.com/docs/en/hooks),
[hooks guide](https://code.claude.com/docs/en/hooks-guide),
[permissions](https://code.claude.com/docs/en/permissions); Codex
[hooks](https://learn.chatgpt.com/docs/hooks); Cursor [hooks](https://cursor.com/docs/agent/hooks);
Copilot [hooks](https://docs.github.com/en/copilot/reference/hooks-configuration); Gemini CLI
[hooks](https://geminicli.com/docs/hooks/); opencode [plugins](https://opencode.ai/docs/plugins/);
OpenHands [hooks](https://docs.openhands.dev/openhands/usage/customization/hooks).

## Contents
- [Ladder](#ladder)
- [Rule type → mechanism](#rule-type--mechanism)
- [Checks over prose](#checks-over-prose)
- [Claude Code semantics](#claude-code-semantics)
- [Templates](#templates)
- [Re-surfacing rules in long sessions](#re-surfacing-rules-in-long-sessions)
- [Pitfalls](#pitfalls)
- [Testing a hook](#testing-a-hook)

## Ladder

Pick the earliest step that can catch the rule; each later step catches more but acts later.

1. **Permission deny rule** in settings (`permissions.deny`) — blocks a tool call outright.
2. **PreToolUse hook** — inspects the call (a Bash command, a path) and denies or asks.
3. **PostToolUse hook** — runs a formatter or linter on the edited file and feeds the failure back.
4. **Stop hook** — refuses to finish until a check passed (tests, build).
5. **CI** — the backstop for everything, because agent hooks are per tool and git pre-commit hooks
   are skipped by `--no-verify`, by a checkout without dependencies and by web-editor commits.
   Before caching, narrowing or skipping a check, make sure CI still covers every file with it.

Then delete the prose rule, or shorten it to one line naming the check.

## Rule type → mechanism

| Rule | Claude Code | Codex | Cursor | Copilot | Gemini CLI | opencode |
|---|---|---|---|---|---|---|
| Forbidden or generated path | `deny: ["Edit(path)"]` + PreToolUse on Bash | PreToolUse deny | `preToolUse`, `beforeShellExecution` | `preToolUse` deny | `BeforeTool` | throw in `tool.execute.before` |
| Dangerous command | `deny: ["Bash(git push --force*)"]` or PreToolUse `ask` | PreToolUse | `beforeShellExecution` ask | `preToolUse` ask | `BeforeTool` | `tool.execute.before` |
| Lint / format after edit | PostToolUse, exit 2 or `decision: "block"` | PostToolUse | `afterFileEdit` | `postToolUse` | `AfterTool` | `tool.execute.after` |
| Re-surface rules | UserPromptSubmit `additionalContext` | UserPromptSubmit | `beforeSubmitPrompt` | `userPromptSubmitted` | `BeforeAgent` | `chat.*` |
| Survive compaction | SessionStart matcher `compact` | PostCompact | `preCompact` | `preCompact` | `PreCompress` | `experimental.session.compacting` |
| Tests before finishing | Stop hook | Stop `decision: "block"` | `stop` `followup_message` | `agentStop` | `AfterAgent` | none documented |
| Commit message format | PreToolUse on `git commit` + commitlint in CI | PreToolUse | `beforeShellExecution` | `preToolUse` | `BeforeTool` | `tool.execute.before` |

OpenHands: `.openhands/hooks.json` Stop hook, exit 2 keeps the agent working; its older
`pre-commit.sh` is deprecated for this.

## Checks over prose

A rule a parser can see belongs in a check every agent and person hits, not in prose:

| Rule | Check |
|---|---|
| Must block the merge (layering, forbidden calls, naming) | architecture test in the test suite |
| Structural pattern inside one file | an [ast-grep](https://ast-grep.github.io/) rule: it matches the syntax tree, so formatting and comments cannot hide a match |
| Pure style | formatter or autofixer |

- Test an ast-grep rule against fixtures that must match and against the real codebase. A rule
  with existing hits starts at `info` or with a baseline.
- Run the rule directory in pre-commit and CI. Run only by an AI reviewer, it is an advisory
  comment, not a gate.
- **Introducing a check over existing code**: list the current violations in a sorted baseline
  (or the test's exceptions list) that fails on new violations **and** on entries that no longer
  occur, so it can only shrink. For a count-based exception, assert the exact count. Fix the
  existing violations in follow-up changes, not in the change that adds the check.

## Claude Code semantics

- **Exit 2 blocks, with stderr as the reason. Exit 1 is a non-blocking error**, so a policy hook
  must exit 2. Any other failure (missing `jq`, not executable, bad JSON) fails open.
- Exit 2 per event: PreToolUse blocks the call; PostToolUse cannot block but stderr reaches
  Claude; Stop makes Claude continue; UserPromptSubmit blocks and **erases the prompt**;
  SessionStart shows the message to the user only.
- PreToolUse JSON: `hookSpecificOutput.permissionDecision` = `allow | deny | ask | defer`;
  across hooks deny > defer > ask > allow. A hook deny also holds in `bypassPermissions`; a hook
  allow cannot override a settings deny.
- `additionalContext` and stdout are capped at 10,000 characters.
- An `Edit(...)` deny rule does not cover Bash writes (`sed -i`, `>`, `tee`, `cp`, `mv`, `rm`);
  pair it with a PreToolUse hook on Bash. Bash permission rules are "not a security boundary".
  A `FileChanged` hook watches named files in the working directory and fires whatever wrote them,
  Bash included.
- Hook types besides `command`: `http`, `mcp_tool`, `prompt` (an LLM decides) and `agent` (a
  verifier with tools). An `if` filter (`"if": "Bash(rm *)"`) narrows a hook to matching calls.

## Templates

Shipped in [../assets/hooks/](../assets/hooks/):

| File | Event | Enforces |
|---|---|---|
| `protect-generated.sh` | PreToolUse, matcher `Bash` | no shell writes into generated paths (`PROTECTED_PATHS` regex) |
| `lint-on-edit.sh` | PostToolUse, matcher `Edit\|Write` | the project linter on the one edited file (`LINT_COMMAND`) |
| `tests-before-stop.sh` | Stop | a reminder to run the narrow tests when source changed since the last green run |

Settings snippet (`.claude/settings.json`):

```json
{
  "permissions": { "deny": ["Edit(/public/build/**)"] },
  "hooks": {
    "PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-generated.sh" }] }],
    "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/lint-on-edit.sh", "timeout": 60 }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/tests-before-stop.sh" }] }],
    "SessionStart": [{ "matcher": "compact", "hooks": [{ "type": "command", "command": "cat \"$CLAUDE_PROJECT_DIR\"/.claude/critical-rules.md" }] }]
  }
}
```

Other recipes worth having before adding tools:
- SessionStart (`startup|resume`): check that installed dependencies match the lockfile and that
  the worktree's services and database exist; print the branch.
- PreToolUse on Bash: block destructive database commands (`migrate:fresh`, `db:wipe`, `DROP`)
  and writes to `.env`.
- Stop: the tests for changed files plus static analysis on them, exit 2 with the failures,
  guarded by `stop_hook_active`.
- A `WorktreeCreate` hook **replaces** Claude Code's own `git worktree` step and must print the new
  path: a setup script there has to create the worktree as well.

## Re-surfacing rules in long sessions

- After compaction: a SessionStart hook with matcher `compact` prints a short
  `critical-rules.md` (3–5 lines).
- Mid-session: a UserPromptSubmit hook that adds the same lines every N prompts (counter in a
  file) is cheaper than every prompt; a reminder on every turn gets ignored like prose.
- Delegation: Explore and Plan subagents skip `CLAUDE.md`; put must-follow rules in the prompt,
  including "when a hook blocks you, stop and report; never route around it".

## Pitfalls

- **Stop loops**: check `stop_hook_active`; Claude Code ends the turn after 8 consecutive blocks
  (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`), Cursor after `loop_limit` 5. Stop fires on every response,
  so gate on "code changed".
- **Latency**: UserPromptSubmit times out after 30 s and its output is silently dropped; other
  hooks default to 600 s and run on every matching call. Lint one file, never the suite.
- **Noise**: keep messages short and say what to do instead; truncate tool output (`tail -20`).
- **Text filters**: a hook that greps the raw command string blocks text, not actions: a heredoc
  that writes a file mentioning the command, a `--help` call, a grep pattern. Write files with
  Edit/Write, pass commit messages with `git commit -F <file>`, and keep any escape hatch narrow;
  "anything containing `--dry-run` passes" also passes a dry run whose diff prints secrets.
- **Routing around a block**: an agent, often a subagent, blocked on Edit/Write can make the same
  change through Bash (a script doing string replacement). When that happened, run the skipped
  control over the whole diff before trusting the result, and tell the user.
- **Coverage**: Edit/Write hooks miss Bash writes; Codex hooks skip hosted tools; Copilot CLI has
  open bugs around deny and `additionalContext`. Probe each tool you rely on.
- **Headless**: `claude -p --bare` loads no hooks, skills or CLAUDE.md; the Agent SDK with
  `settingSources: []` neither. CI stays the guarantee.

## Testing a hook

Pipe a sample event in and check the exit code and output:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"sed -i s/a/b/ public/build/app.js"}}' \
  | .claude/hooks/protect-generated.sh; echo "exit $?"
```

Then `/hooks` in Claude Code to confirm registration, and one probe task in a fresh session that
tries the forbidden action.
