# Claude Code: how instruction files load

Primary source for everything here: <https://code.claude.com/docs/en/memory> (MEM),
<https://code.claude.com/docs/en/context-window> (CW), <https://code.claude.com/docs/en/best-practices>
(BP), <https://code.claude.com/docs/en/sub-agents> (SA). Re-check them before relying on a detail;
Claude Code ships weekly. Versions below are the first release with that behaviour
([changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)).

## Contents
- [Scopes and order](#scopes-and-order)
- [Imports and comments](#imports-and-comments)
- [Path-scoped rules](#path-scoped-rules)
- [AGENTS.md](#agentsmd)
- [Compaction](#compaction)
- [Subagents, plugins, skills](#subagents-plugins-skills)
- [Hook-injected instructions and output styles](#hook-injected-instructions-and-output-styles)
- [Tools for inspecting and trimming](#tools-for-inspecting-and-trimming)
- [Prove what loads](#prove-what-loads)
- [Which binary runs](#which-binary-runs)
- [Telemetry in project settings](#telemetry-in-project-settings)
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
  The startup warning fires for one file over ~200 lines and for files that each fit but add up
  past a combined limit (2.1.281).
- `claudeMdExcludes` (globs on absolute paths, any settings layer, arrays merge) drops user,
  project and local files; never managed ones.
- `--add-dir` directories load their CLAUDE.md only with
  `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- Scoping personal rules to one organisation: an ancestor-directory file
  (`~/projects/<org>/CLAUDE.md`) reaches every repo below it and nothing else, which
  `~/.claude/rules` cannot do. A running session keeps what it loaded until restart.

## Imports and comments

- `@path` anywhere outside code spans (`See @README for an overview`); relative to the importing file; absolute and `~` allowed; max 4 hops.
- Imports skip code spans and fenced blocks, so a backticked path stays literal.
- **Imports do not save context**: imported files load at launch. Splitting a file with imports
  organises it; it does not shrink it.
- An import that resolves outside the working directory asks for approval once per project; a
  declined import stays disabled silently. User-scope files import without asking.
- Block-level `<!-- … -->` HTML comments are stripped before injection (2.1.72; not inside code
  blocks, and the Read tool still shows them). Maintainer notes cost nothing there.

## Path-scoped rules

```markdown
---
paths:
  - "src/Billing/**/*.php"
---
```

- `paths` is the only frontmatter field read: a YAML list or a comma-separated string, with globs
  and braces. Bad YAML makes the rule load unconditionally.
- Loaded when Claude uses Read, Write or Edit on a matching file, or reads one file with a Bash
  `cat`/`head`; not on every tool use. Rules without `paths` load at launch.
- Symlinked rules and symlinked paths match (2.1.198). A link whose target is outside the project
  is an external import: it asks for approval (2.1.284; older versions skip it silently), and after
  approval only its unscoped rules load.
- Tool-enforced path loading also exists in Cursor (`.mdc` globs), Copilot (`applyTo`) and OpenHands (skill `triggers`); opencode and Codex have none. See [tools.md](tools.md).

## AGENTS.md

- Native since 2.1.277: read **only when no** `CLAUDE.md`, `.claude/CLAUDE.md` or
  `CLAUDE.local.md` exists in the working directory or above. `~/.claude/CLAUDE.md`, managed files
  and `.claude/rules/` do not count. `AGENTS.override.md`, `AGENTS.local.md` and `.agents/` are
  never read. A subdirectory's `AGENTS.md` loads when Claude reads a file there and that directory
  has no `CLAUDE.md` of its own.
- **Adding a `CLAUDE.local.md` silently stops AGENTS.md loading.**
- Not read natively before 2.1.277, on the first session after an upgrade, with the built-in
  `agents-md` plugin disabled, and before 2.1.281 also on Bedrock, Vertex, Foundry, LLM gateways
  and sessions with telemetry off.
- `instructionFiles` (`claude-md-or-agents-md` default, `claude-md-and-agents-md`, `claude-md`,
  `managed-only`) lives at `pluginConfigs["agents-md@builtin"].options.instructionFiles` in user
  or managed settings only; project settings ignore it, so a repo cannot rely on it.
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
  **Explore and Plan agents skip it**; frontmatter `omitClaudeMd: true` (2.1.271) drops
  user/project/local. A rule a delegated agent must follow goes into the delegation prompt too (SA).
- Auto memory is not loaded into subagents (forks excepted).
- A plugin cannot ship a CLAUDE.md into context; plugins contribute skills, agents, hooks. An
  organisation injects always-on text through managed `claudeMd`, a SessionStart hook in a
  plugin, or files users place themselves.
- A skill body loads on use and stays for the session; move a procedure out of CLAUDE.md into a
  skill ("a section of CLAUDE.md has grown into a procedure rather than a fact").

## Hook-injected instructions and output styles

Source: [hooks](https://code.claude.com/docs/en/hooks), [output styles](https://code.claude.com/docs/en/output-styles).

- `additionalContext`, `systemMessage` and hook stdout are capped at **10,000 characters**; above
  that Claude gets a 2,000-character preview and is not told to read the rest.
- Write injected text **as facts, not as imperative system commands**: text framed as out-of-band
  commands can trip prompt-injection defences, and Claude then shows it to the user instead of
  using it. "For instructions that never change, prefer CLAUDE.md."
- PostToolUse `additionalContext` suits conditional rules at the moment they apply ("which test
  command applies to the file just edited").
- On `--resume`, earlier hook text is replayed, not re-run; SessionStart runs again with
  `source: "resume"`.
- `InstructionsLoaded` (2.1.69) does not fire for an `AGENTS.md` read natively, but does when
  `CLAUDE.md` imports it: a way to confirm the `@AGENTS.md` layout loaded.
- **Output styles** set how Claude responds (tone, length, format); `CLAUDE.md` carries what it
  should know. Styles go into the system prompt with per-turn reminders, so tone rules that drift
  belong there. A custom style drops the built-in coding instructions unless
  `keep-coding-instructions: true`; styles do not reach non-fork subagents.

## Tools for inspecting and trimming

| Command | Use |
|---|---|
| `/context` | what loaded and what it costs (an `AGENTS.md` read natively is listed from 2.1.280) |
| `/memory` | list/open loaded files, toggle auto memory |
| `/init` | starter file; with an existing CLAUDE.md it suggests improvements. `CLAUDE_CODE_NEW_INIT=1` proposes CLAUDE.md, skills and hooks for review. It imports `.cursor/rules`, `.cursorrules`, `.github/copilot-instructions.md` |
| `/doctor` (`/checkup`) | trims checked-in CLAUDE.md by cutting what Claude can derive from the code, dedupes local files against checked-in ones, and moves remaining guidance into skills and nested files; keeps "pitfalls, rationale, and conventions that differ from tool defaults". `/doctor prompt-audit` (2.1.283) audits wording written for older models, stale paths and contradicting files |
| `/import` | appends a one-time **copy** of `AGENTS.md` into `CLAUDE.md`; do not use it with the `@AGENTS.md` layout, it creates the drift that layout prevents |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | a session without instruction files: the "without" arm of a probe |
| `CLAUDE_CODE_SIMPLE=1` | disables all customisations, to rule them out when behaviour is odd |
| `InstructionsLoaded` hook | logs why each file loaded (`session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`) |

The `#` shortcut no longer exists; ask Claude to "add this to CLAUDE.md". "Remember X" goes to
auto memory instead.

**When an instruction "is ignored"**, in this order: confirm it loaded (`/context` → Memory
files, or a probe below); rule out customisations with a `CLAUDE_CODE_SIMPLE=1` session and check
the effort level; check the binary's version against the behaviour you rely on; only then rewrite
the text. A bug report needs the `/bug` transcript, the effort level and the
`CLAUDE_CODE_SIMPLE=1` result, not a shorter file.

## Prove what loads

Ask a fresh headless session what it has, with unique markers; reading config proves nothing.
Probe again after every new symlink, rule or scope change: a link can exist and still fail.

```sh
cd <directory> && claude -p 'Is there a section titled "<unique title>" in your loaded instructions? Reply exactly YES or NO.' < /dev/null
claude -p "Read the first 5 lines of <matching file>. Then list, verbatim, the first heading line of every project rule file that entered your context because of that read. If none, say NONE." --allowedTools Read < /dev/null
claude -p "List every skill available to you whose name starts with zz, each with its full description, verbatim." < /dev/null
```

- **Scope leaks**: run the first probe from a directory that should get the section and from one
  that should not; expect YES and NO.
- **Path rules**: the second probe, once per rule you add.
- **Skill precedence**: create throwaway `zz-probe` skills in each location (project, personal,
  plugin) with a marker in each description (`PROJECT-COPY`, `PERSONAL-COPY`), run the third
  probe, then delete them.
- Finer: `/context`, `/memory`, the `InstructionsLoaded` hook, and the stream-json `system/init`
  event, which lists `skills`, `plugins` and `memory_paths`.

## Which binary runs

An editor extension can ship its own Claude Code binary: the VS Code extension runs
`~/.vscode/extensions/anthropic.claude-code-<version>-<platform>/resources/native-binary/claude`,
while `claude` on PATH is a separate install that can be months older and stop updating. Every
`claude -p` probe, script and CI run uses the PATH binary, so its results describe that version,
not what interactive sessions load.

```sh
claude --version
ps -eo pid,command | grep -E 'native-binary/claude' | grep -v grep
```

Before reasoning about a version-gated behaviour (the versions on this page), check the version
per entrypoint, and update the PATH install or probe with the binary your users run.

## Telemetry in project settings

From 2.1.282 Claude Code ignores the OpenTelemetry variables that turn export on, set where it
goes or capture content (`CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_*_EXPORTER`, `OTEL_LOG_*`,
`OTEL_EXPORTER_OTLP_*_ENDPOINT` and the like) when they come from a repository's
`.claude/settings.json` or `.claude/settings.local.json`. A telemetry rollout goes in managed
settings, or each developer's shell or `~/.claude/settings.json`; an `env` block committed to the
repo does nothing on current versions. A repository can still turn a signal off:
`OTEL_METRICS_EXPORTER=none` (or `OTEL_LOGS_EXPORTER=none`) is honoured there, while
`CLAUDE_CODE_ENABLE_TELEMETRY=0` is not; neither beats a value set by managed settings, a
`--settings` file or the launch environment
([monitoring](https://code.claude.com/docs/en/monitoring-usage)).

## Auto memory

- On by default; `~/.claude/projects/<project>/memory/`, per repository, shared across worktrees,
  machine-local. `MEMORY.md` loads its first 200 lines or 25 KB.
- It is personal: preferences and pointers only. Anything the team needs goes into the repo (docs
  or instruction files), never only into memory; some repos forbid agent memory altogether and
  keep every learning in `docs/`.
- Remembered facts go stale unseen. Before moving a memory into the repo or acting on it, re-run
  its check; for a credential, a status-code-only request that never prints the secret.
