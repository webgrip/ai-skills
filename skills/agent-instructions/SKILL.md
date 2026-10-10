---
name: agent-instructions
description: Sets up a repository for AI coding agents end to end and keeps it right - AGENTS.md and CLAUDE.md, knowledge moved to docs, one rule source generated for every tool, skills, MCP, review bots, cloud-agent setup and a CI check - then audits, slims and fixes the files. Use when setting up or onboarding a repo for AI agents or agentic coding, making a repo agent-ready, adding Claude Code, Cursor, Copilot, Codex, Antigravity, OpenHands, opencode, Junie, Devin or Windsurf, or CodeRabbit to a repo, when CLAUDE.md is too long, ignored or drifts from AGENTS.md, when Claude keeps doing something the file forbids, when a generator such as Laravel Boost wipes hand-written instructions, when rules in ~/.claude leak into other projects, when reviewing a PR that changes agent config, when testing whether an instruction change works, or when deciding whether a rule belongs in CLAUDE.md, docs, a skill, a hook or CI. Dutch - zet deze repo op voor AI-agents, agentic setup, CLAUDE.md opschonen.
---

# Agent instructions — set up a repo for AI agents, and keep it right

## Pick the job

| Job | Go to |
|---|---|
| Set up a repo: new, or one with scattered or stale agent files | [Set up a repo](#set-up-a-repo) |
| Slim, fix or audit an existing `CLAUDE.md` / `AGENTS.md` | [Audit or slim](#audit-or-slim) |
| Add a rule after a repeated mistake | [references/maintenance.md](references/maintenance.md#when-to-add-a-line) |
| Review a PR that changes agent config, or open an unknown repo | [references/security.md](references/security.md) |
| Cloud, CI or headless agents | [references/unattended.md](references/unattended.md) |
| A generator (Laravel Boost, Nx, rulesync) owns the file | [references/generators.md](references/generators.md) |
| Set up or tune an AI review bot | [references/review-bots.md](references/review-bots.md) |

## Set up a repo

Nothing is written before step 3 is approved. Run the scripts from this skill's directory against
the target repo.

1. **Inventory.** `python3 scripts/agent_setup.py inventory <repo>` lists instruction files, path
   rules, skills directories, MCP, review-bot and cloud-agent configs, generators, the CI forge,
   the hook manager, docs, and what every session loads. `python3 scripts/measure.py <repo>` adds
   the line-level report. Detection finds files, not habits: ask which tools the team uses.
2. **Choose targets** per category from [references/targets.md](references/targets.md): only the
   tools in use. `AGENTS.md` alone already reaches most agents; tool-specific files are for path
   rules, skills, MCP and cloud setup.
3. **Plan, then wait.** One table for every existing instruction line (keep / `docs/` file / path
   rule / hook or CI / skill / other level / delete), the files to create per target, and the CI
   and hook wiring. Get approval before writing.
4. **Lay out** on a branch: `python3 scripts/agent_setup.py layout <repo> --apply` writes
   `.ai/agent-setup.json` (targets, budgets), `AGENTS.md`, `CLAUDE.md` = `@AGENTS.md`,
   `docs/index.md`, `.ai/rules/`, the skills directory and the symlinks. It never overwrites a
   hand-written file; it reports what you must merge by hand.
5. **Move knowledge** into `docs/`, one pointer row per subject ([Where each thing goes](#where-each-thing-goes));
   write path rules only for traps: `paths:` frontmatter, the trap, its reason, a link to the doc,
   at most 20 lines ([references/maintenance.md](references/maintenance.md#when-to-add-a-line)).
6. **Generate** each tool's rule files from `.ai/rules`: `python3 scripts/agent_setup.py generate <repo>`.
   Generated files carry a marker; the generator refuses to overwrite a same-named hand-written file.
7. **Configure the tools**: Claude Code `.claude/settings.json` (permissions; hooks from
   [assets/hooks/](assets/hooks/)), MCP servers with least privilege, cloud-agent setup files
   ([references/unattended.md](references/unattended.md)), the review bot
   ([references/review-bots.md](references/review-bots.md)). Telemetry is never a repo setting:
   it belongs at user or managed level ([references/claude-code.md](references/claude-code.md)).
8. **Enforce**: a CI job and a pre-commit hook run `python3 scripts/agent_setup.py check <repo>`
   ([references/ci.md](references/ci.md)); a generator-owned file also gets a regenerate-and-diff
   job ([references/generators.md](references/generators.md#ci-drift-check)). Make each gate fail
   once on purpose before trusting it.
9. **Verify and hand over**: `check` is green, regenerating twice changes nothing, a headless marker
   probe shows each rule loading where a tool can run headless, the review bot's own validator
   passes. The MR description carries the step-3 table.

## What a line costs and what it buys

- Every always-loaded line is paid in every request of every session and subagent; `@imports`
  organise a file, they do not shrink it. Estimate Markdown at 2.9 bytes per token, not 4.
- Measured effect: commands the agent cannot guess, tool choices, operational warnings, non-standard
  practices, recurring traps. Overviews, architecture tours, style prose and personas cost tokens
  without shown benefit ([references/evidence.md](references/evidence.md)).
- Adherence decays over a long session. Anything that must hold every time becomes a hook, linter,
  test or CI check; the file may point at it ([references/enforcement.md](references/enforcement.md)).
- Budget: ~200 lines per file, `AGENTS.md` under 32 KiB (Codex stops reading there).

## Where each thing goes

| Content | Home |
|---|---|
| Command, tool choice, operational warning, repo etiquette, recurring trap | instruction file |
| Must hold every time (format, forbidden files, secrets, commit format) | permission rule / hook / linter / CI |
| Structure a parser can see (a call, a name, a file location) | architecture test or ast-grep rule |
| Knowledge about the product: flows, decisions, reasons | `docs/` + one pointer row in the file |
| Review convention | the same `.ai/rules` file, mapped to the review bot; a bot learning moves into a rule, check or doc and is then deleted in the bot |
| Only matters in one subtree | path rule in `.ai/rules/` (generated per tool) or a nested `AGENTS.md` |
| Multi-step procedure, needed sometimes | skill, named in a pointer row (skills fire about half the time on their own) |
| Version-specific framework API | docs MCP (Boost `search-docs`, Context7) + one line saying when to call it |
| Tone, length, response format | output style, not the instruction file |
| Code facts (where X lives, who calls Y) | nothing: grep finds them, a written copy goes stale |
| Personal preference | `~/.claude/CLAUDE.md`, `CLAUDE.local.md`, or an ancestor-directory file |
| Shared by several repos | one level up: package, plugin, template, managed settings |
| Derivable from the code, standard conventions, generic advice | nowhere |

Each kind of rule has exactly one home. For every line ask: would removing it cause a mistake? Can
a tool enforce it? Is it already in a doc? Keep it only for yes / no / no.

## Levels

| Level | Carrier | Carries |
|---|---|---|
| Organisation | managed settings, a plugin SessionStart hook, or an ancestor-directory `CLAUDE.md` (`~/projects/<org>/CLAUDE.md`) | behaviour; enforcement in hooks and settings |
| Stack | package guideline, generator source, template | rules every repo of that stack shares |
| Repo | `AGENTS.md` + `CLAUDE.md` = `@AGENTS.md` | commands, repo traps, pointer table |
| Path | `.ai/rules/*.md` or a nested file | subtree specifics |
| Client (agency) | the client repo's own files, an ancestor directory per client | client rules stay in client repos |
| Person | `~/.claude/*` | preferences, never team facts |

Claude Code concatenates levels and resolves conflicts arbitrarily: one owner per rule.
`~/.claude/CLAUDE.md`, `~/.claude/rules/`, user-scope MCP servers, plugin hooks and a user-level
telemetry env reach **every** repo on the machine, so one organisation's config leaks into
another's; scope by ancestor directory, per project, or in the collector
([references/layering.md](references/layering.md)).

## File layout

- **`AGENTS.md` is canonical**; nearly every tool reads it ([references/tools.md](references/tools.md)).
- **`CLAUDE.md` is `@AGENTS.md` on line 1.** Claude Code reads `AGENTS.md` natively only when no
  `CLAUDE.md` or `CLAUDE.local.md` exists, so the import is what makes it reliable. A symlink blocks
  Edit/Write and breaks on Windows; "read AGENTS.md" is followed only when the model opens it.
- **Path rules** live flat in `.ai/rules/*.md` with `paths:` frontmatter. `.claude/rules` is a
  committed symlink to `../.ai/rules`; every other tool gets a generated file; tools without path
  loading get one `AGENTS.md` line pointing at the folder.
- **One skills directory**: `.agents/skills/` with `.claude/skills` a committed symlink to
  `../.agents/skills`. In a Boost repo the hand-written source is `.ai/skills/`, which Boost links in.
- Delete leftovers (`.cursorrules`, `.windsurfrules`, `.rules`): drifting copies, and in Zed the
  first match hides `AGENTS.md`.

## Writing a line

- Imperative, with the reason in one clause and the scope stated: the model reads literally
  ("in `src/Billing/**`, …"). A pointer names its trigger ("Before changing an invoice PDF, read
  `docs/billing.md`").
- Plain wording. Emphasis on at most one line that keeps being skipped; MUST/CRITICAL across the
  file makes current Claude models overtrigger. No hedges ("try to", "if possible").
- Commands with exact flags; paths the agent can open; no worked examples, they narrow exploration.
- A compact **index table** (subject → doc) in the always-loaded file beats knowledge in a skill
  that may never fire ([references/routing.md](references/routing.md)).
- State the criterion, not a list of instances. A rule a tool enforces shrinks to one line naming the tool.
- Check pairs of rules for contradictions, not only the line count. Generated or upstream text that
  contradicts the repo gets one explicit override line and an upstream report.
- One session's stumble is not a rule: add a line only when the mistake repeats.
- No verification boilerplate, "think carefully", "show your reasoning" or personas.
- Maintainer notes go in `<!-- … -->`: Claude Code strips them (other tools may not, so never hide
  an instruction there). Text a hook injects is written as facts, not commands.
- A rule that must survive `/compact` goes in the root file, never behind `paths:`.

## Audit or slim

1. **Measure**: `python3 scripts/measure.py <repo>`; for a generated file, against the lockfile's
   versions in a fresh worktree.
2. **Scan** with `measure.py --security-only` when the file comes from someone else, and run
   `claude -p "/doctor prompt-audit <path>"` (needs 2.1.283+ on the binary that runs it,
   [references/claude-code.md](references/claude-code.md#which-binary-runs)); its findings are
   claims to check, and apply only to text you own.
3. **Inventory** every line: keep / docs (which file) / hook-CI / skill / path rule / other level /
   delete. Check `docs/` first: typically half is already there.
4. **Move**, one pointer row per subject; before moving, trial-merge open branches that edit the file
   ([references/maintenance.md](references/maintenance.md)).
5. **Fix the layout**, then continue from step 6 of [Set up a repo](#set-up-a-repo).
6. **Verify**: measure again; `scripts/probe.py` (10 runs per arm) on the rules that changed.

## Gotchas

- Two Claude Code binaries can run on one machine: the IDE extension bundles its own, and `claude`
  on `PATH` may be months older. A headless probe describes the `PATH` version; compare
  `claude --version` with the extension before concluding what loads.
- A review bot ignores rule frontmatter: a guideline file listed as a plain glob applies only to its
  own folder. Map each rule to its paths explicitly ([references/review-bots.md](references/review-bots.md)).
- Path rules and nested files are summarised away at compaction and reload only when a matching
  file is touched again. Built-in Explore and Plan subagents skip `CLAUDE.md`: repeat a must-follow
  rule in the delegation prompt.
- A stale local install (old `vendor/`, old CLI) gives confident wrong conclusions about generator
  output; verify against the lockfile.
- An `Edit(...)` deny rule does not stop `sed -i` or `>` in Bash; pair it with a PreToolUse hook.
- Agents may propose rules, skills and memory; they land only through review. Self-generated skills
  measured worse than curated ones.
- Tool-generated summaries of papers, docs and release notes are claims; quote the primary source.

## References

- Tools per category, what each reads, generator targets → [references/targets.md](references/targets.md), [references/tools.md](references/tools.md)
- Claude Code loading, settings, telemetry, versions → [references/claude-code.md](references/claude-code.md)
- Review bots: config, rule mapping, isolation, measuring → [references/review-bots.md](references/review-bots.md)
- CI jobs and pre-commit hooks per forge and hook manager → [references/ci.md](references/ci.md)
- Laravel Boost and other generators, drift check → [references/generators.md](references/generators.md)
- Testing, adding, pruning, migrating in-flight branches → [references/maintenance.md](references/maintenance.md)
- Rules into permissions, hooks and CI; hook templates → [references/enforcement.md](references/enforcement.md)
- Levels, distribution and precedence per tool → [references/layering.md](references/layering.md)
- Routing to knowledge: index, skills, docs MCP → [references/routing.md](references/routing.md)
- Cloud, CI and headless agents → [references/unattended.md](references/unattended.md)
- Threats, review checklist, security scan → [references/security.md](references/security.md)
- Studies and vendor guidance → [references/evidence.md](references/evidence.md)
