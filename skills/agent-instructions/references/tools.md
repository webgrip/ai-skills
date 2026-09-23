# Which tool reads what

Primary docs per row; re-check before relying on a detail. Claude Code's own mechanics are in
[claude-code.md](claude-code.md).

| Tool | Instruction files | Precedence | Size limits | Path-scoped | Skills dirs |
|---|---|---|---|---|---|
| Claude Code | `CLAUDE.md` hierarchy; `AGENTS.md` only when no `CLAUDE.md`/`CLAUDE.local.md` exists | concatenated, conflicts arbitrary | ~200 lines/file advised, 4 MiB hard | `.claude/rules` `paths:` | `.claude/skills` only (+ plugins) |
| [Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | `~/.codex/AGENTS(.override).md`, then per directory git root → cwd: override, `AGENTS.md`, fallback names | one file per dir, closer wins | **32 KiB combined** (`project_doc_max_bytes`), then stops | nested `AGENTS.md` only | `.agents/skills` (cwd → root), `~/.agents/skills` |
| [Cursor](https://cursor.com/docs/context/rules) | `.cursor/rules/*.mdc`, `AGENTS.md` (nested), user and team rules | team → project → user | rules < 500 lines advised | `.mdc` `globs`, `alwaysApply`, `description`, manual | `.agents/skills`, `.cursor/skills`, compat `.claude/skills` |
| [Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` (nearest), root `CLAUDE.md`/`GEMINI.md` | personal > repo > org, all sent | "no longer than 2 pages" | `applyTo`, `excludeAgent` | `.github/skills`, `.claude/skills`, `.agents/skills` |
| [Gemini CLI](https://geminicli.com/docs/cli/gemini-md/) | `GEMINI.md` hierarchy + just-in-time per directory; `context.fileName: ["AGENTS.md","GEMINI.md"]` to read AGENTS.md | concatenated | `@file` imports | just-in-time directories | `.gemini/skills`, `.agents/skills` (wins) |
| [opencode](https://opencode.ai/docs/rules/) | `AGENTS.md` (walks up), falls back to `CLAUDE.md`; `instructions` array (paths, globs, URLs) | first match per category; `AGENTS.md` beats `CLAUDE.md` | none documented | none: `instructions` globs load at start | `.opencode/skills`, `.claude/skills`, `.agents/skills` |
| [OpenHands](https://docs.openhands.dev/overview/skills) | `AGENTS.md` always; `CLAUDE.md`/`GEMINI.md` as model-specific | project > user > public | keep brief | skills with path or keyword `triggers` | `.agents/skills` (recommended), legacy `.openhands/skills`, `.openhands/microagents` |
| [Junie](https://junie.jetbrains.com/docs/guidelines-and-memory.html) | `.junie/AGENTS.md` or root `AGENTS.md`, `.junie/rules/*.md`; `.junie/guidelines.md` legacy | project > global | none documented | unverified | `.junie/skills` (CLI also `.agents/skills`) |
| [Windsurf/Devin](https://docs.devin.ai/desktop/cascade/memories) | `.windsurf/rules`, `.devin/rules`, `AGENTS.md` | `.devin` > `.windsurf` | 6,000 chars global, 12,000 per workspace file | `trigger: glob` | unverified |
| [Zed](https://zed.dev/docs/ai/rules) | **first match only**: `.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`, copilot file, `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | first match | — | no | — |
| [Kiro](https://kiro.dev/docs/steering/) | `.kiro/steering/*.md`, `AGENTS.md` always | — | — | `fileMatch` inclusion | — |

## What follows for a repo

- **`AGENTS.md` is the shared surface**: every tool above reads it. Make it canonical and let
  `CLAUDE.md` import it (`@AGENTS.md`), because Claude Code skips `AGENTS.md` whenever a
  `CLAUDE.md` exists.
- **Keep `AGENTS.md` under 32 KiB** or Codex silently stops reading.
- **Delete leftovers** (`.cursorrules`, `.rules`, `.windsurfrules`): in Zed the first match hides
  `AGENTS.md`, and elsewhere they are a second, drifting copy.
- **`.agents/skills` is the portable skills directory** (Codex, Cursor, Copilot, Gemini, opencode,
  OpenHands, Amp). Claude Code reads only `.claude/skills`: commit it as a symlink to
  `../.agents/skills`.
- **Path-scoped loading is tool-specific** (`.claude/rules`, `.mdc` globs, `applyTo`, OpenHands
  triggers). For routing that must work everywhere, put a pointer table in `AGENTS.md`; add the
  tool-specific scoping on top where it pays.
- Skills follow the [Agent Skills spec](https://agentskills.io/specification): `name` ≤ 64 chars
  matching the directory, `description` ≤ 1,024 chars, body < 500 lines, references one level
  deep. A description that must trigger in more than Claude Code carries all trigger text itself.
