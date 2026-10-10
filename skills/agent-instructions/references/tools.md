# Which tool reads what

What each interactive agent reads from a repo. Which tools to enable: [targets.md](targets.md).
Claude Code's loading in depth: [claude-code.md](claude-code.md). Each row links the vendor's own
docs; these tools ship weekly, so re-read the page before relying on a cell. "—" means nothing
documented.

## Contents
- [Instructions and path rules](#instructions-and-path-rules)
- [Skills, MCP, ignore files, hooks](#skills-mcp-ignore-files-hooks)
- [What follows for a repo](#what-follows-for-a-repo)

## Instructions and path rules

| Tool | Instruction files | Precedence | Size limit | Path rules |
|---|---|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/memory) | `CLAUDE.md` hierarchy, `CLAUDE.local.md`; `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists | concatenated; conflicts resolved arbitrarily | ~200 lines advised; files over 4 MiB skipped | `.claude/rules/**/*.md`, `paths:` list or comma string; unparseable YAML = always on |
| [GitHub Copilot](https://docs.github.com/en/copilot/reference/custom-instructions-support) | `.github/copilot-instructions.md`, nearest `AGENTS.md`, root `CLAUDE.md`/`GEMINI.md` (cloud agent, CLI); code review also `REVIEW.md`. VS Code: nested `AGENTS.md` only with `chat.useNestedAgentsMdFiles` | all sent; personal > repo > org | — | `.github/instructions/**/*.instructions.md`: `applyTo: "a,b"` (one quoted comma string), `excludeAgent: "code-review"` or `"cloud-agent"`. In VS Code only the Local agent and the Claude harness read `.claude/rules` |
| [OpenAI Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | `~/.codex/AGENTS(.override).md`, then per directory from git root to cwd: `AGENTS.override.md`, else `AGENTS.md`, else `project_doc_fallback_filenames` (empty by default); never below cwd | one file per directory, closer later | **32 KiB combined** (`project_doc_max_bytes`), then stops reading | none; nested `AGENTS.md` only (`.codex/rules/*.rules` are command-approval policies) |
| [Cursor](https://cursor.com/docs/rules) | `AGENTS.md` root and nested; `CLAUDE.md` always applied; `.cursorrules` legacy | team > project > user | rules < 500 lines advised | `.cursor/rules/**/*.mdc` **only** (a `.md` there is ignored): `globs: a, b` unquoted + `alwaysApply: false`. Reads neither `.claude/rules` nor `.ai/rules` |
| [Google Antigravity](https://antigravity.google/docs/rules) | `AGENTS.md` or `GEMINI.md` in any directory (or its `.agents/`), loaded walking up from each file read; no `CLAUDE.md` | concatenated | 24 KB per file (truncated); always-on rules share a 20,000-token budget, largest demoted to pointers | `.agents/rules/*.md` (flat): `trigger: always_on`, `model_decision`, `glob` or `manual` + `globs` comma string; missing or unknown frontmatter = **rule silently discarded** |
| [OpenCode](https://opencode.ai/docs/rules/) | `AGENTS.md` walking up; `CLAUDE.md` only when no `AGENTS.md`; `instructions` array in `opencode.json` (paths, globs, URLs) | first match per category | — | none; `instructions` globs always load |
| [JetBrains Junie](https://junie.jetbrains.com/docs/guidelines-and-memory.html) | first match: custom file, then `.junie/AGENTS.md` (**exclusive**), then root `AGENTS.md` + `.junie/playbook.md` + `.junie/rules/*.md`; no `CLAUDE.md` | project > global | — | none: `.junie/rules/*.md` are always on |
| [Devin Desktop (Windsurf)](https://docs.devin.ai/cli/extensibility/rules) | `AGENTS.md`, `AGENT.md`, `AGENTS.local.md`, `CLAUDE.md`, `.windsurfrules`, all treated alike; subdirectory files on first access | all loaded | 12,000 characters per workspace rule file, 6,000 global | `.devin/rules/*.md` (preferred) and `.windsurf/rules/*.md`: `trigger: glob` + `globs`; also reads `.cursor/rules` and Claude config (`read_config_from`) |
| [Warp](https://docs.warp.dev/agents/capabilities/rules/) | `AGENTS.md` (`WARP.md` legacy), upper-case only; root and current directory, other directories best effort | subdirectory > root > global | — | none |
| [Cline](https://docs.cline.bot/customization/cline-rules) | `.clinerules/` or `.cline/rules/`; also `AGENTS.md`, `.cursorrules`, `.windsurfrules`; each toggled in the UI | — | — | same directories, `paths:` **YAML list only**; a string or bad YAML = always on |
| [Kiro](https://kiro.dev/docs/steering/) | `.kiro/steering/*.md`, `AGENTS.md` always | — | — | `inclusion: fileMatch` + `fileMatchPattern` (string or array); frontmatter must come first |
| [Zed](https://zed.dev/docs/ai/instructions) | **first match only**: `.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | first match | — | none |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) | `GEMINI.md` hierarchy + per directory on access; `AGENTS.md` only with `context.fileName: ["AGENTS.md", "GEMINI.md"]` | concatenated | — | none |
| [OpenHands](https://docs.openhands.dev/overview/skills) | `AGENTS.md` always; `CLAUDE.md`/`GEMINI.md` as model-specific | project > user > public | keep brief | skills with `paths:` or keyword triggers |

## Skills, MCP, ignore files, hooks

| Tool | Skills directories | Repo MCP file | Ignore file | Repo hooks |
|---|---|---|---|---|
| Claude Code | `.claude/skills` only, plus plugins | `.mcp.json` `mcpServers` (remote needs `type`); per-server approval after folder trust; none in headless and cloud runs ([unattended.md](unattended.md#repo-files-that-change-the-security-posture)) | none; `.claudeignore` does nothing: use `permissions.deny` `Read(...)` | `.claude/settings.json` `hooks` |
| Copilot | `.github/skills`, `.claude/skills`, `.agents/skills` | VS Code `.vscode/mcp.json` `servers`; CLI and VS Code Agent Host `.mcp.json` or `.github/mcp.json` `mcpServers`; cloud agent in repo settings only | none for agents (content exclusion skips agent mode and CLI) | `.github/hooks/*.json` (`version: 1`, CLI and cloud agent); the CLI also runs `.claude/settings.json` hooks; VS Code only with `chat.useClaudeHooks` |
| Codex | `.agents/skills` from cwd up to root | `.codex/config.toml` `[mcp_servers.<name>]`, trusted projects only | none; the sandbox keeps `.git`, `.agents`, `.codex` read-only | `.codex/hooks.json` or `[hooks]`, each trusted by hash |
| Cursor | `.agents/skills`, `.cursor/skills`; compat `.claude/skills`, `.codex/skills` | `.cursor/mcp.json` `mcpServers` (stdio needs `type: "stdio"`) | `.cursorignore`; terminal and MCP tools ignore it | `.cursor/hooks.json` (`version: 1`), **and `.claude/settings.json` hooks by default** |
| Antigravity | `.agents/skills` | `.agents/mcp_config.json` `mcpServers`, remote key `serverUrl` | none; a "Respect .gitignore" setting | `.agents/hooks.json` (named hooks, Antigravity tool names) |
| OpenCode | `.opencode/skills`, `.claude/skills`, `.agents/skills` | `opencode.json` `mcp` (`command` is an array) | none; reading `*.env` denied by default | code plugins in `.opencode/plugins/` |
| Junie | `.junie/skills`, `.agents/skills` | `.junie/mcp/mcp.json` `mcpServers` | `.aiignore` (asks before reading) | none from the repo by default |
| Devin Desktop | `.agents/skills`, `.devin/skills`, `.windsurf/skills` | `.devin/mcp_config.json` (`.local.json` for personal) | `.devinignore` | `.devin/hooks.v1.json`, and `.claude/settings.json` hooks by default |
| Warp | `.agents/skills` and nine `.<tool>/skills` directories | `.warp/.mcp.json`; also reads `.mcp.json` and `.codex/config.toml`; approval per session | `.warpindexingignore` (indexing only) | — |
| Cline | `.cline/skills`, `.clinerules/skills`, `.claude/skills`, `.agents/skills`; a global skill wins a name clash | none: global settings only | `.clineignore`, not a boundary and being phased out | `.clinerules/hooks/<Event>` (extension), `.cline/hooks/<Event>.sh` (CLI) |
| Kiro | `.kiro/skills` | `.kiro/settings/mcp.json` | — | `.kiro/hooks/<id>.json` |
| Zed | `.agents/skills` only, flat | `.zed/settings.json` `context_servers` | — | — |
| Gemini CLI | `.agents/skills` (wins), `.gemini/skills` | `.gemini/settings.json` `mcpServers`; not loaded in an untrusted folder | `.geminiignore` | `.gemini/settings.json` `hooks` |
| OpenHands | `.agents/skills`; legacy `.openhands/skills`, `.openhands/microagents` | — | — | `.openhands/hooks.json` |

Sources beyond the first table: Claude Code [MCP](https://code.claude.com/docs/en/mcp),
[hooks](https://code.claude.com/docs/en/hooks), [permissions](https://code.claude.com/docs/en/permissions);
Copilot [hooks](https://docs.github.com/en/copilot/reference/hooks-reference),
[CLI MCP](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers),
[content exclusion](https://docs.github.com/en/copilot/concepts/context/content-exclusion);
Codex [skills](https://learn.chatgpt.com/docs/build-skills), [MCP](https://learn.chatgpt.com/docs/extend/mcp),
[hooks](https://learn.chatgpt.com/docs/hooks); Cursor [skills](https://cursor.com/docs/skills),
[hooks](https://cursor.com/docs/hooks), [third-party hooks](https://cursor.com/docs/reference/third-party-hooks),
[ignore](https://cursor.com/docs/reference/ignore-file); Antigravity [skills](https://antigravity.google/docs/skills),
[MCP](https://antigravity.google/docs/mcp), [hooks](https://antigravity.google/docs/hooks); OpenCode
[skills](https://opencode.ai/docs/skills/), [MCP](https://opencode.ai/docs/mcp-servers/),
[plugins](https://opencode.ai/docs/plugins/); Junie [skills](https://junie.jetbrains.com/docs/agent-skills.html),
[hooks](https://junie.jetbrains.com/docs/junie-cli-hooks.html); Devin
[hooks](https://docs.devin.ai/cli/extensibility/hooks/overview),
[ignore](https://docs.devin.ai/desktop/context-awareness/devin-ignore); Cline
[hooks](https://docs.cline.bot/customization/hooks), [ignore](https://docs.cline.bot/customization/clineignore);
Kiro [MCP](https://kiro.dev/docs/mcp/configuration/), [hooks](https://kiro.dev/docs/hooks/).

## What follows for a repo

- **`AGENTS.md` is the shared surface.** Every tool above reads it, except Claude Code once a
  `CLAUDE.md` exists (hence `CLAUDE.md` = `@AGENTS.md`), Junie once `.junie/AGENTS.md` exists
  (never create that file), Zed when an earlier name in its list exists, and Gemini CLI without
  `context.fileName`.
- **`CLAUDE.md` is not private to Claude Code.** Cursor applies it always, Devin treats it as a
  rule, Copilot's cloud agent and CLI accept it at the root. Lines below the import must hold for
  every tool, or move to `.claude/rules` or a Claude-only skill.
- **Size caps that cut silently:** Codex stops at 32 KiB combined, Antigravity truncates each file
  at 24 KB, Devin Desktop caps a workspace rule file at 12,000 characters.
- **Delete leftovers** (`.cursorrules`, `.windsurfrules`, `.rules`, a single-file `.clinerules`,
  `WARP.md`, `AGENT.md`): Zed loads only the first match and hides `AGENTS.md` behind them; Cline,
  Devin and Warp load them as a second copy that drifts.
- **`.agents/skills` is the skills directory nearly every tool reads.** Claude Code is the
  exception: commit `.claude/skills` as a symlink to `../.agents/skills`. Zed reads it flat only.
- **Path rules need one native format per tool**, generated from `.ai/rules`
  ([generators.md](generators.md#one-rule-source-generated-per-tool)): Cursor loads only `.mdc`,
  Copilot only `applyTo`, Cline only a `paths:` list, Antigravity drops a rule without valid
  `trigger`. Codex, OpenCode, Junie, Warp, Zed and Gemini CLI have no path scoping: give them the
  one `AGENTS.md` line pointing at `.ai/rules`.
- **Claude Code hooks run in other tools.** Cursor and Devin run `.claude/settings.json` hooks by
  default, Copilot CLI too, VS Code on opt-in. Probe every hook in each tool the team uses; event
  names and payloads differ ([enforcement.md](enforcement.md#rule-type--mechanism)).
- **Root `.mcp.json` reaches Claude Code, Copilot CLI, VS Code's Agent Host and Warp.** Cursor,
  Codex, Antigravity, OpenCode, Junie and Devin each need their own file; keep them in step.
- **No ignore file is a security boundary.** Terminal and MCP tools bypass them, and Claude Code has
  none. Keep secrets out of the checkout and deny reads in each tool's permissions
  ([security.md](security.md)).
- **Personal files stay untracked:** `CLAUDE.local.md`, `AGENTS.local.md`,
  `.claude/settings.local.json`, `.github/copilot/settings.local.json`, `.devin/*.local.json`. A
  tool that keeps writing its own config into the checkout (an untracked `.codex/config.toml`) is
  excluded per clone, for every worktree:
  `E="$(git rev-parse --git-common-dir)/info/exclude"; grep -qx '/.codex/' "$E" || printf '/.codex/\n' >> "$E"`.
- **Gemini CLI serves only Gemini Code Assist Standard/Enterprise and API-key users**; individual
  accounts use Antigravity, which reads `AGENTS.md` and `.agents/` natively
  ([migration](https://antigravity.google/docs/cli/gcli-migration)).
- Skills follow the [Agent Skills spec](https://agentskills.io/specification): `name` ≤ 64 chars
  matching the directory, `description` ≤ 1,024 chars, body < 500 lines, references one level
  deep. A description that must trigger in more than Claude Code carries all trigger text itself.
- **Revisit the `.ai/rules` layout** when [AGENTS.md](https://agents.md) gains frontmatter or an
  `.agents/rules` directory, the Agent Skills spec gains `paths`, Cursor reads `.claude/rules`, or
  a generator the repo uses ships its own per-tool rule sync.
