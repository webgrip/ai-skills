---
name: agent-instructions
description: Fixes, cleans up and writes CLAUDE.md and AGENTS.md agent instruction files. Use when a CLAUDE.md or AGENTS.md is created, reviewed, too long, bloated or ignored by Claude, when CLAUDE.md and AGENTS.md are duplicated or out of sync, when composer install, boost:install or another generator rewrites or wipes hand-written instructions, when rules in ~/.claude or a CLAUDE.md leak into other projects or conflict with a client's rules, when cleaning up or slimming down agent instructions, or when deciding whether a rule belongs in CLAUDE.md, a skill, a hook, CI or docs. Covers .claude/rules, CLAUDE.local.md, .cursor/rules, copilot-instructions.md and Laravel Boost .ai/guidelines for Claude Code, Codex, Cursor, Copilot, opencode and OpenHands; ships a measuring script, a CI drift check and a probe-task test method.
---

# Agent instructions — the file every agent loads every session

## What a line costs and what it buys

- Every line is paid in every session, by every subagent, and imports load at launch too.
  `@imports` organise a file; they do not shrink it.
- Content with **measured** effect: commands the agent cannot guess, tool choices, operational
  warnings ("the full suite takes 20 min, run the domain suite"), non-standard practices, recurring
  traps. Overviews, architecture tours, style prose and personas cost tokens without shown benefit;
  `/init`-style generated text mostly repeats the README. Details: [references/evidence.md](references/evidence.md).
- Adherence decays over a long session whatever the file looks like. Anything that must hold every
  time becomes a hook, linter, test or CI check; the file may point at it.
- Budget: ~200 lines per file (Anthropic), `AGENTS.md` under 32 KiB (Codex stops reading there).
  Keep to it for cost and focus.

## Where each thing goes

| Content | Home |
|---|---|
| Command, tool choice, operational warning, repo etiquette, recurring trap | instruction file |
| Must hold every time (format, forbidden files, secrets, commit format) | hook / linter / CI, not prose |
| Knowledge about the product: flows, decisions, reasons | `docs/` + one pointer row in the file |
| Only matters in one subtree | nested `AGENTS.md`, or a path rule (`.claude/rules` `paths:`, Cursor globs, Copilot `applyTo`) plus a pointer row for tools without path loading |
| Multi-step procedure, needed sometimes | skill in `.agents/skills/` |
| Personal preference | `~/.claude/CLAUDE.md`, `CLAUDE.local.md`, or an ancestor-directory file |
| Shared by several repos | one level up: package, plugin, template, managed settings — and deleted from each repo |
| Derivable from the code, standard conventions, generic advice | nowhere |

For every line ask: would removing it cause a mistake? Can a tool enforce it? Is it already in a
doc? Keep it only for yes / no / no.

## Levels

| Level | Carrier | Carries |
|---|---|---|
| Organisation | managed `claudeMd`, a plugin SessionStart hook, or for one person's org an ancestor-directory `CLAUDE.md` (`~/projects/<org>/CLAUDE.md`) | behaviour only; enforcement in hooks and settings |
| Stack / shared | package guideline, generator source, template | rules every repo of that stack shares |
| Repo | `AGENTS.md` + `CLAUDE.md` = `@AGENTS.md` | commands, repo traps, pointer table |
| Path | nested file or path rule | subtree specifics |
| Person | `~/.claude/*`, auto memory | preferences, never team facts |

- Claude Code concatenates levels; nothing overrides anything and conflicts resolve arbitrarily.
  One owner per rule; delete the copy on the other level.
- `~/.claude/CLAUDE.md` and `~/.claude/rules/` load in **every** project, so one organisation's
  rules there leak into another's repos. Scope by ancestor directory instead.

## File layout

- **`AGENTS.md` canonical**: every major tool reads it ([references/tools.md](references/tools.md)).
- **`CLAUDE.md` = `@AGENTS.md` on line 1**, Claude-only lines below. Claude Code skips `AGENTS.md`
  when any `CLAUDE.md` exists, and a `CLAUDE.local.md` disables native loading, so the import is
  what makes it reliable. A symlink blocks Edit/Write and breaks on Windows; a sentence saying
  "read AGENTS.md" is followed only when the model decides to open the file.
- **One skills directory**: `.agents/skills/` tracked; `.claude/skills` a committed symlink to
  `../.agents/skills` (Claude Code reads only that path).
- Delete leftovers (`.cursorrules`, `.windsurfrules`, `.rules`): drifting copies, and in Zed the
  first match hides `AGENTS.md`.

## Writing a line

- Imperative, with the reason in one clause, and the scope stated: the model reads literally and
  does not generalise ("in `app/Domains/*/Pdf`, …").
- Plain wording. Emphasis (`IMPORTANT`) on at most one line that keeps being skipped; MUST/CRITICAL
  across the file makes current Claude models overtrigger.
- Commands with exact flags; paths the agent can open; a pointer names its trigger
  ("Before changing a quotation PDF, read `docs/quotation-pdfs.md`").
- A compact **index table** (subject → doc) in the always-loaded file beats putting knowledge in a
  skill that may never fire.
- Leave out verification boilerplate, "think carefully", "show your reasoning" (can trigger a
  `reasoning_extraction` refusal) and personas.
- Maintainer notes go in `<!-- … -->`: Claude Code strips them before loading.
- A rule that must survive `/compact` goes in the root file, never behind `paths:`.

## Audit or slim down an existing file

1. **Measure.** `python3 scripts/measure.py <repo>` reports sizes, what loads at launch, the
   CLAUDE.md/AGENTS.md relation, emphasis counts, paragraph-long lines, dead links, generated
   blocks, duplicate skill directories and the Codex cap. When a generator writes the file,
   measure against the lockfile's versions (fresh worktree, own install).
2. **Inventory** every line in a table: keep / docs (which file) / hook-CI / skill / path rule /
   other level / delete (derivable, duplicate, stale). Check `docs/` first: typically half is
   already documented there.
3. **Move**, leaving one pointer row per subject; remove the moved text.
4. **Fix the layout** (section above).
5. **Verify**: measure again; run probe tasks in fresh sessions with and without the change
   ([references/maintenance.md](references/maintenance.md)); for generated files regenerate twice
   and expect identical output.
6. **Guard** in CI: `measure.py --budget-lines N`, or for Boost repos
   [assets/check-generated-instructions.sh](assets/check-generated-instructions.sh).

## Create a new file

Start from what a newcomer could not guess: install, run, test and lint commands with flags; the
two or three traps that have already bitten; a pointer table to `docs/`. Use `/init` output only as
a draft to cut. Add a line later only when the agent repeats a mistake that no tool can catch
([references/maintenance.md](references/maintenance.md#when-to-add-a-line)).

## Generated files

A Boost/rulesync/Ruler block belongs to the generator: put team text in the generator's source
(`.ai/guidelines`, `.ruler/`, `.rulesync/`), exclude machine-dependent sections, and check in CI
that regenerating changes nothing → [references/generators.md](references/generators.md).

## Gotchas

- Path rules and nested files are summarised away at compaction and reload only when a matching
  file is read again.
- Claude Code's built-in Explore and Plan subagents skip `CLAUDE.md`: repeat a must-follow rule in
  the delegation prompt.
- A stale local install (old `vendor/`, old CLI) gives confident wrong conclusions about what a
  generator produces; verify against the lockfile.
- Generator output that depends on the machine (Boost's Herd section) breaks drift checks and
  hands container agents instructions that are false for them.
- Tool-generated summaries of papers and docs were wrong while researching this skill; quote the
  primary source.

## References

- Claude Code loading, imports, rules, compaction, subagents → [references/claude-code.md](references/claude-code.md)
- Which tool reads which file, limits, skills dirs → [references/tools.md](references/tools.md)
- Studies and vendor guidance → [references/evidence.md](references/evidence.md)
- Laravel Boost and other generators → [references/generators.md](references/generators.md)
- Testing, adding, pruning, ownership, patterns from mature repos → [references/maintenance.md](references/maintenance.md)
