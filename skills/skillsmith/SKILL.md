---
name: skillsmith
description: Author, edit, and audit agent skills (.claude/skills/*/SKILL.md or plugin skills) for token-efficient, high-trigger-accuracy LLM ingestion. Use when creating a new skill, refactoring/auditing an existing one, writing or tuning a frontmatter description, a skill that never fires or fires only sometimes, probing whether a skill triggers, building a skill from articles or research, cutting a skill's token weight, splitting a skill into supporting files, or deciding what belongs in a skill vs CLAUDE.md vs memory vs a runbook.
---

# Skillsmith — write skills for the model, not the reader

A skill is a procedure injected into another model's context. Optimize for *its* ingestion. Every
rule here derives from the **verified loading/token model** (sources at bottom) — not folklore.

## Cost model (internalize this; everything follows)

Three tiers, by when tokens are paid:

- **Skill names** — always in context, every session. Negligible.
- **`description` (+`when_to_use`)** — loaded for discovery, but they **share a budget ≈ 1% of the
  context window**. Per-entry cap **1,536 chars**. Over budget, the **least-used** skills'
  descriptions are shortened/dropped first. → A bloated description steals budget from *every* skill.
  `/doctor` shows what's being dropped.
- **SKILL.md body** — loads when the skill fires and **stays in context for the whole session**
  (not re-read per turn). After auto-compaction only the **first 5,000 tokens** of each skill survive
  (**25,000** combined, most-recent-first). → Every body line is a *recurring* cost.
- **Supporting files** (`reference.md`, `scripts/`) — cost **~0 until the model opens them**. Cheapest
  tier; push bulk/rare detail here.

→ Maximize description trigger-accuracy; keep the body to "what's needed to act"; defer everything else
to siblings. Official tip: **keep SKILL.md < 500 lines** (the split rule below is much tighter).

## The `description` is a router, not a summary

Its one job: load this skill **exactly when relevant, never otherwise**.
- `description` = *what it does* + the highest-signal nouns (tool/CRD/file names, the domain) + *trigger
  phrases* the user would actually say + symptoms ("Use when …").
- **Portability:** `when_to_use` is a Claude-Code-only field — opencode (and the agentskills.io spec)
  ignore it. A skill shipped to more than one tool folds all trigger text into `description`
  (spec cap **1,024 chars**); only a personal CC-only skill may split into `when_to_use`
  (combined 1,536 cap either way — trim both).
- Third person, present tense, verb-first. **Never** "this skill", "helps you", "designed to".
- **Lead with the outcome the user asks for, then the request shapes they type.** "Refactors code so
  agents spend fewer tokens" fires where "Fowler-catalog refactoring harness" stays quiet; "split a
  big file", "cancel flow" are what people say. Method nouns go last.
- A word absent from description/when_to_use can't match. A word that's pure filler costs the whole set.

## Body rules

- **Decision first, procedure second.** Lead with the branch ("if X do Y"); models act top-down.
- **Imperative, present tense, articles dropped** where unambiguous. No intro/overview/summary/motivation.
- **State what to do, not how or why** — one clause of *why* only when it changes the action.
- **No history, no dates.** A skill states the rule as it stands now. No `(2026-01-01)` stamp,
  no `verified <date>` / `(accepted <date>)`, no "this overrides X", "two exceptions, both
  deliberate", "we decided …" — cut every line that narrates the rule instead of being it.
- **Concrete beats abstract:** exact paths, field names, commands, `file:line`. A path the model can
  open out-earns a paragraph describing it.
- **One real in-repo example by path** beats an inlined synthetic template (which rots and costs tokens).
- **Anchors for skimming:** bold the scan keywords, tables for name→value lookups, bullets over prose.
- **Guardrails as `Never`/gotchas** — the expensive mistake the model can't infer is the highest-ROI line.
- **Forbid only live traps.** A `Never X` earns its line *only* when X is an attractive mistake the model would otherwise make. Forbidding what it wasn't going to do anyway plants the bad pattern as baggage and burns tokens — state the right thing and leave the wrong alternative **unsaid**. Positive (`use github.server_url`) beats negative (`don't read vars.FOO because it's always empty`); the negative smuggles in the dead concept you're trying to retire.
- **Don't duplicate** CLAUDE.md, the codebase, or git history — link to a **committed in-repo doc** (ADR/runbook/incident under `docs/`). **Never link `[[memory]]` from a committed skill** — memory lives in `~/.claude`, per-user/per-machine, so the link dangles on anyone else's clone. `[[memory]]` is portable only inside *personal* (`~/.claude`) skills + memory files.

## Single source of truth

No fact lives in two skills. Pick one **canonical home**; everywhere else is a one-line summary + "see
the X skill". Duplication multiplies token cost *and* drifts out of sync. When you catch the same rule
in two skills, that's a bug — consolidate: move the rule to one home, leave a one-line pointer, and
add a routing hint to the other skill's description.

**Inside one skill too.** A rule lives in the body, reference files, templates, examples, evals and
any bundled linter at once. After changing a rule, find every restatement with
`grep -rn '<rule phrase>' <skill-dir>` (a read-only background audit for a large skill) and fix them,
the evals included, in the same change.

## Progressive disclosure (supporting files)

Split out **lookup material** — tables, catalogs, link lists, rare branches — once the body passes
**~60 lines**. **Never split out the steps:** the checks an answer depends on (run this script, give a
verdict per line) stay in the section the agent reads, even if that keeps the body longer. The agent
answers from the paragraph in front of it; a step that lives only in a linked file gets skipped.
Move the lookup material to a sibling and reference it:

```markdown
## Additional resources
- Deep query/panel/table detail → [reference.md](reference.md)
```

- **Keep references one level deep** (SKILL.md → reference.md, not → a → b). The model may `head -100`
  a nested file and miss the rest.
- For a reference file > 100 lines, put a short **table of contents** at top so a partial read sees scope.
- **Scripts** the model *runs* (output consumed, code never loaded) are the cheapest reference of all —
  ship a `scripts/foo.sh` and say "run it", with `allowed-tools` pre-approving the command.

## What does NOT go in a skill

- Always-on project rules → `CLAUDE.md`. Mutable state / incident history → the memory system (but a *committed* skill links the in-repo incident doc/runbook, never the `[[memory]]`).
- Long-form human reference → `docs/…/runbooks/`. One-off facts / anything derivable from the repo → omit.
- Generic knowledge a competent model already has → omit. Skills carry only the *specific* and *non-obvious*.

## Frontmatter — the fields worth knowing

`name` and `description` cover most skills. The high-value extras:

| Field | Use it for |
|---|---|
| `when_to_use` | CC-only trigger text appended to `description`. Fine for personal CC skills; **cross-tool skills fold triggers into `description` instead** (opencode drops unknown fields). |
| `allowed-tools` | **Additive** pre-approval of safe commands (cuts prompts). Needs workspace-trust for project skills. NOT a restriction. |
| `disable-model-invocation: true` | Manual-only `/cmd` with side effects (deploy/commit). Removes it from Claude's auto-context. |
| `user-invocable: false` | Background knowledge Claude should auto-load but isn't a user command. |

Full field catalog, string substitutions (`$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`…), and the advanced
levers (`paths`, `context: fork`/`agent`, dynamic bang-backtick shell injection) with **when each fits**
→ [reference.md](reference.md). Note: command name comes from the **directory name**, not `name:`.

<!-- Don't write the literal bang-backtick token in THIS file: the loader executes that pattern at
     skill-load time, so a documentation example self-triggers ("command not found: cmd"). The syntax
     is shown safely in reference.md (a sibling — not scanned for injection). -->


## Create

"Make a skill for X" means a researched, tested package — script, evals, probe — not a prose draft.

0. **Name first:** `npx skills find <name>` (or `https://skills.sh/api/search?q=<name>`). A published
   twin means two same-named skills on every machine that installs both, and a slug is immutable once
   published — pick a distinct name before writing a line. In an estate with per-skill release tags,
   `git tag -l '<name>-v*'` too: a retired name's old tags resume its release series.
   **One name, one content:** a same-named skill elsewhere is a conflict only if its content differs —
   `diff -rq -x .claude-plugin -x CHANGELOG.md <a> <b>` first. Rename only a real variant, after what
   differs, never after who owns it.
1. Read the neighbouring skills and runbooks; start parallel read-only research in the background
   ([reference.md](reference.md#research-backed-skills)).
2. While it runs, write the bundled script and test it against the real system.
3. Check every claim that would change the skill at a primary source.
4. `.claude/skills/<name>/SKILL.md`. `<name>` kebab-case, == dir, reads as `/<name>`. Frontmatter:
   `description` with "Use when …" triggers folded in; add others only with a reason from the table.
5. Body: decision → procedure → gotchas; point at one real example. Heavy/rare detail → sibling file,
   referenced one level deep.
6. Evals with should-trigger cases and should-not cases from neighbouring skills
   ([reference.md](reference.md#eval-cases)); then probe triggering.
7. Add pointer lines in CLAUDE.md and the neighbouring skills; move overlapping content to one home.
8. No registration — Claude Code auto-discovers `.claude/skills/*/SKILL.md` (live, no restart for edits).

## Edit / audit

- **Trigger to update:** a gotcha cost a failure loop, a recommended pattern proved wrong, paths drifted.
  Bake the **root cause** as a `Never`/gotcha at the relevant step — as the rule, not as its story.
- **Token-diet pass:** cut human-only prose, generic LLM knowledge, duplication (apply single-source),
  stale paths. Tighten description/when_to_use. Confirm cited examples still exist (`test -e`).
- **Measure, don't guess:** the `skill-creator` plugin runs with/without A/B on real prompts and reports
  trigger hit-rate + token/time overhead; `/doctor` flags dropped descriptions. (See reference.md.)
- **Probe triggers in isolation, ≥ 3 runs per prompt,** on an otherwise idle machine, with a model calibrated
  on a skill known to fire. Tune the description only on a consistent miss; one run, a small model, or a
  timeout is noise. (See reference.md.)
- **Built from research or an article?** Label each claim's evidence strength and find the controlled
  study or replication behind every headline number; the skill carries the replicated size, the headline
  only as motivation. Volatile numbers (prices, limits) go in a dated data file the scripts read.
  → [reference.md](reference.md#research-backed-skills)
- **Ships a scanner or linter?** A fixture where every rule fires, one where none does, and a
  false-positive pass on real code before release → [reference.md](reference.md#skills-that-ship-a-scanner)
- **Ships scripts or commands?** Test them on macOS bash 3.2 and inside the CI image, and never depend on
  an install script running again → [reference.md](reference.md#bundled-scripts)
- **Wraps an expensive operation?** The skill plans, gates read-only and verifies; the human runs the
  mutation → [reference.md](reference.md#skills-that-wrap-risky-operations)

## Evaluate an installed skill

Full eval methodology (faithful triggering probe, benchmark isolation, worktree traps) → [reference.md](reference.md).

## Skeleton

```markdown
---
name: <kebab-name>
description: <verb> <what it does> + highest-signal nouns. Use when <trigger phrases + symptoms>.
---

# <Name> — <one-line what/for-whom>

## <Decision or cost model that drives everything>
## <Do the thing>   (numbered steps)
## Gotchas          (**Never** …)
```

## Smells → cut on sight

- `## Overview` / `## Introduction` / "This skill helps you…"
- Inlined templates duplicating a real file; a fact restated in another skill.
- A paragraph of *why* where one clause suffices; a date or a `verified …` stamp on a rule.
- Anything that reads as a changelog, decision log, or justification of the skill's own text.
- A description that summarizes instead of triggering, or repeats the skill name.
- A `Never`/`don't` guarding a pattern the model wouldn't reach for anyway — the prohibition *is* the baggage. Show the right thing; omit the wrong one.
- Walls of prose where a table or bullets parse faster.
- A lookup table or link list sitting in the always-on body instead of a sibling.

## Sources

Official: <https://code.claude.com/docs/en/skills> · best practices
<https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>. Verify mechanics
there before changing this guide — don't trust memory.
