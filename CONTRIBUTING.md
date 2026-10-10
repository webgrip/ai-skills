# Contributing

Issues and PRs welcome — including new skills. The estate stays valuable by
being **curated, not collected**: a small set of skills that trigger reliably
beats a drawer of half-maintained ones, so expect review to push back on
scope, and treat "fold it into an existing skill" as a good outcome.
(superpowers, the most-adopted public estate, merged four debugging skills
into one and near-stopped accepting new-skill PRs — sprawl is the documented
failure mode.)

The automation invariants (generated `skills/` + `marketplace.json`, computed
versions, release-triggering commit types) live in [CLAUDE.md](CLAUDE.md) —
read it first; CI enforces all of it.

## Does it even belong here?

| It is… | Home |
| --- | --- |
| A repeatable workflow / procedure with judgment in it | **A skill here** |
| An always-true rule for one repo ("we use conventional commits") | That repo's `CLAUDE.md` / `AGENTS.md` |
| Instance facts (ids, hostnames, project names) | The consuming repo's contract block — see "genericizing" in [CLAUDE.md](CLAUDE.md) |
| Long-form human reference | A `docs/` tree, linked from the skill |
| Personal / machine-specific preference | Your own `~/.claude/skills` or memory |

When in doubt, run the `skillsmith` skill — routing content to the right home
is one of its jobs.

## The quality bar

**Enforced by `scripts/lint_skills.py` (CI):** frontmatter `name` == directory
(kebab, ≤64 chars); `description` ≤ 1,024 chars containing "Use when …"
trigger text; **no `when_to_use`** (Claude-Code-only — opencode and the flat
`skills/` consumers drop it, so trigger text belongs in `description`); no
angle brackets in frontmatter; body < 500 lines with heavy detail split into
sibling files linked one level deep; relative links resolve; no `TODO:`
scaffold leftovers; `evals/evals.json` with ≥ 3 cases; a row in the README
Skills table.

**Checked in review (can't be linted):** the description routes rather than
summarizes — an agent that thinks it knows the workflow from the description
will wing it instead of reading the body; one consistent term per concept;
one recommended tool with an escape hatch, not a menu; no time-sensitive
content; bundled scripts handle their own errors, justify their constants,
and declare dependencies; specificity matches fragility (exact commands where
deviation breaks things, prose where judgment is the point).

## Evals are the definition of done

Every skill ships `evals/evals.json` (skill-creator format): realistic
prompts, objective assertions, ideally one should-NOT-trigger case. Write
them *before* polishing the body — a skill without evals is documentation for
an imagined problem. To test a change, run each prompt in a fresh session
with and without the skill and grade the assertions (Claude Code's
`skill-creator` plugin automates this). Probe symptom phrasings, not just
canonical ones — under-triggering hides in prompts that don't contain the
skill's name. `python3 scripts/run_evals.py <name>` runs the triggering half:
three isolated runs per case, PASS / FLAKY / FAIL.

## Process

1. Branch; scaffold with `python3 scripts/new_skill.py <name> "…"` for a new
   skill (or edit under `skills/<name>/`).
2. Seed/update the evals.
3. `npm run check && npm test` locally — CI runs the same. Run
   `claude plugin validate .` too if you have Claude Code installed.
4. Conventional commit messages; anything under `skills/**` needs a
   release-triggering type (`feat`/`fix`/`perf`/`refactor`/`revert` or
   breaking) or your change never ships to installs.
5. Open the PR — the template's checklist is the review contract. Editing an
   existing skill? The bar is a failure you actually watched (a gotcha that
   cost a loop, a drifted path): state its root cause as a rule at the step
   where it bites, and add an eval that would have caught it. A skill states
   rules as they stand now — no dates, names or "since"/"added" history in
   skill files (the generated `CHANGELOG.md` aside); that story belongs in the
   commit message.

**Deprecating a skill:** plugin `name` slugs are immutable once published, so
deprecation = remove the plugin dir + README row in one release-triggering PR
that states the replacement. Git history is the archive.

## Security model

A skill is **instructions a consumer's agent will follow**, and plugins can
ship MCP servers and pre-approve tool access — review PRs with the scrutiny
of code, because that review *is* the trust boundary. Nothing that writes
plaintext secrets, exfiltrates data, or phones home; scripts that touch the
network must say so in the skill and default to opt-in.
