# Claude Code: how instruction files load

Primary source for everything here: <https://code.claude.com/docs/en/memory> (MEM),
<https://code.claude.com/docs/en/context-window> (CW), <https://code.claude.com/docs/en/best-practices>
(BP), <https://code.claude.com/docs/en/sub-agents> (SA). Re-check them before relying on a detail;
Claude Code ships weekly.

## Contents
- [Scopes and order](#scopes-and-order)
- [Imports and comments](#imports-and-comments)
- [Path-scoped rules](#path-scoped-rules)
- [AGENTS.md](#agentsmd)
- [Compaction](#compaction)
- [Subagents, plugins, skills](#subagents-plugins-skills)
- [Tools for inspecting and trimming](#tools-for-inspecting-and-trimming)
- [Auto memory](#auto-memory)

## Scopes and order

Loaded broadest first, concatenated (nothing overrides anything):

| Scope | Location | Note |
|---|---|---|
| Managed | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`, Linux `/etc/claude-code/CLAUDE.md`, or `claudeMd` in managed settings | cannot be excluded |
| User | `~/.claude/CLAUDE.md`, `~/.claude/rules/` | loads in **every** project |
| Ancestors | every `CLAUDE.md` from filesystem root down to the launch directory | closer files read last |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md`, `.claude/rules/**/*.md` | unscoped rules = same priority as CLAUDE.md |
| Local | `./CLAUDE.local.md` | appended after `CLAUDE.md` in the same directory; gitignored |
| Subdirectory | `sub/CLAUDE.md`, `sub/CLAUDE.local.md` | loaded when Claude reads a file in `sub/` |

- "If a user rule and a project rule conflict, Claude may follow either one"; "if two rules
  contradict each other, Claude may pick one arbitrarily" (MEM). No level wins; remove the
  conflict.
- Content is delivered as a user message after the system prompt. Files over 4 MiB are skipped.
- `claudeMdExcludes` (globs on absolute paths, any settings layer, arrays merge) drops user,
  project and local files; never managed ones.
- `--add-dir` directories load their CLAUDE.md only with
  `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- Scoping personal rules to one organisation: an ancestor-directory file
  (`~/projects/<org>/CLAUDE.md`) reaches every repo below it and nothing else, which
  `~/.claude/rules` cannot do.

## Imports and comments

- `@path` on its own line; relative to the importing file; absolute and `~` allowed; max 4 hops.
- Imports skip code spans and fenced blocks, so a backticked path stays literal.
- **Imports do not save context**: imported files load at launch. Splitting a file with imports
  organises it; it does not shrink it.
- An import that resolves outside the working directory asks for approval once per project; a
  declined import stays disabled silently. User-scope files import without asking.
- Block-level `<!-- … -->` HTML comments are stripped before injection (not inside code blocks).
  Maintainer notes cost nothing there.

## Path-scoped rules

```markdown
---
paths:
  - "app/Domains/Sqs/**/Pdf*.php"
---
```

- `paths` is the only frontmatter field read; bad YAML makes the rule load unconditionally.
- Loaded when Claude **reads** a matching file, not on every tool use.
- Symlinked rules match through the link; a link whose target is outside the working directory is
  treated as an external import.
- Tool-enforced path loading also exists in Cursor (`.mdc` globs), Copilot (`applyTo`) and OpenHands (skill `triggers`); opencode and Codex have none. See [tools.md](tools.md).

## AGENTS.md

- Native since v2.1.277: read **only when no** `CLAUDE.md`, `.claude/CLAUDE.md` or
  `CLAUDE.local.md` exists in the working directory or above. `~/.claude/CLAUDE.md`, managed files
  and `.claude/rules/` do not count. `AGENTS.override.md`, `AGENTS.local.md` and `.agents/` are
  never read.
- **Adding a `CLAUDE.local.md` silently stops AGENTS.md loading.**
- Unavailable before v2.1.277, on sessions without feature flags (Bedrock, Vertex, Foundry,
  telemetry off), on the first session after an upgrade, or with the built-in `agents-md` plugin
  disabled.
- `instructionFiles` (`claude-md-or-agents-md` default, `claude-md-and-agents-md`, `claude-md`,
  `managed-only`) lives at `pluginConfigs["agents-md@builtin"].options.instructionFiles` in user
  or managed settings only; project settings ignore it.
- **Recommended**: `CLAUDE.md` = `@AGENTS.md` on the first line, Claude-only lines below. Never
  loads AGENTS.md twice, works on every version and provider.
- Symlink `CLAUDE.md -> AGENTS.md`: Edit/Write refuse to write through it; Windows without
  `core.symlinks` checks it out as a one-line text file.
- Remove old workarounds: a CLAUDE.md that says "read AGENTS.md" in prose (Claude reads it only if
  it decides to), and a SessionStart hook that prints AGENTS.md (second copy).

## Compaction

| Survives `/compact` | How |
|---|---|
| Project-root CLAUDE.md, unscoped rules, auto memory | re-read from disk and re-injected |
| Path-scoped rules, nested CLAUDE.md | summarised away; reload only when a matching file is read again |
| Invoked skills | re-injected, 5,000 tokens each, 25,000 total, oldest dropped first |
| SessionStart hooks with matcher `compact` | re-run, output added |

A rule that must hold after compaction goes in the root CLAUDE.md or an unscoped rule, never
behind `paths:` (CW). A line like "When compacting, preserve the list of modified files and the
test commands" steers the summary (BP).

## Subagents, plugins, skills

- A non-fork subagent loads the whole CLAUDE.md hierarchy including AGENTS.md; the built-in
  **Explore and Plan agents skip it**; frontmatter `omitClaudeMd: true` drops user/project/local.
  A rule a delegated agent must follow goes into the delegation prompt too (SA).
- Auto memory is not loaded into subagents (forks excepted).
- A plugin cannot ship a CLAUDE.md into context; plugins contribute skills, agents, hooks. An
  organisation injects always-on text through managed `claudeMd`, a SessionStart hook in a
  plugin, or files users place themselves.
- A skill body loads on use and stays for the session; move a procedure out of CLAUDE.md into a
  skill ("a section of CLAUDE.md has grown into a procedure rather than a fact").

## Tools for inspecting and trimming

| Command | Use |
|---|---|
| `/context` | what loaded and what it costs, including an AGENTS.md read directly |
| `/memory` | list/open loaded files, toggle auto memory |
| `/init` | starter file; with an existing CLAUDE.md it suggests improvements. `CLAUDE_CODE_NEW_INIT=1` proposes CLAUDE.md, skills and hooks for review. It imports `.cursor/rules`, `.cursorrules`, `.github/copilot-instructions.md` |
| `/doctor` | trims checked-in CLAUDE.md by cutting what Claude can derive from the code and moves remaining guidance into skills and nested files |
| `InstructionsLoaded` hook | logs why each file loaded (`session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`) |

The `#` shortcut no longer exists; ask Claude to "add this to CLAUDE.md". "Remember X" goes to
auto memory instead.

## Auto memory

- On by default; `~/.claude/projects/<project>/memory/`, per repository, shared across worktrees,
  machine-local. `MEMORY.md` loads its first 200 lines or 25 KB.
- It is personal. Anything the team needs goes into the repo (docs or instruction files), never
  only into memory.
