# Generated instruction files

When a tool writes `AGENTS.md`/`CLAUDE.md` for you, the file has two owners. Everything below is
about keeping them apart. Laravel Boost is the worked case; the rules at the end apply to any
generator (rulesync, ruler, framework installers).

## Contents
- [Laravel Boost: how it writes](#laravel-boost-how-it-writes)
- [Override points](#override-points)
- [Project rules (`.ai/rules`)](#project-rules-airules)
- [Output that differs per machine](#output-that-differs-per-machine)
- [Packages that run Boost for you](#packages-that-run-boost-for-you)
- [CI drift check](#ci-drift-check)
- [Any generator](#any-generator)

## Laravel Boost: how it writes

- `php artisan boost:install` / `boost:update` compose guidelines into one block,
  `<laravel-boost-guidelines>` … `</laravel-boost-guidelines>`, and **replace the whole block** in
  each agent's file (the first block only; without one it appends the block). Text inside is gone
  on the next run. Up to 2.7 it also collapsed blank lines outside the block; 2.8 stopped that.
- Defaults per agent: guidelines to `AGENTS.md` for Codex, opencode, Cursor, Junie and Copilot;
  Claude Code to `CLAUDE.md` up to 2.9 and **`AGENTS.md` from 2.10**. Skills to `.agents/skills`
  (Codex, opencode), `.claude/skills`, `.cursor/skills`, `.junie/skills`, `.github/skills`.
- **Version matters; pin it in the lockfile and read its release notes:** 2.8 stopped touching
  text outside the block, 2.8.1 made `record-rule` opt-in ("only when the user explicitly asks"),
  2.10 moved Claude Code to `AGENTS.md` without migrating an existing `CLAUDE.md`.
- It deletes and recopies every skill it owns on each run; a hand edit inside a Boost skill is
  lost. Skills it does not own (not listed in `boost.json`) are left alone.
- Content follows installed packages: PHP versions from `vendor/`, JavaScript packages from
  **`node_modules`** (without it, Echo skills disappear and Inertia skill sections drop out).
- Flags change output: `--guidelines` without `--skills` omits the "Skills Activation" section.
  Compare runs only with identical flags.
- Boost only boots when `APP_ENV=local` or `APP_DEBUG=true`. With an unreachable database it hangs
  on the connection instead of failing; `DB_CONNECTION=sqlite DB_DATABASE=:memory:` finishes in
  seconds.

## Override points

| Want | Do |
|---|---|
| House rules composed into every agent's block | `.ai/guidelines/<name>.blade.php` (or `.md`); they appear at the top of the block |
| Replace one Boost guideline | `.ai/guidelines/<path>.blade.php`, named after the guideline's **path**, not its header: `pest/core`, `boost/core`, `herd/core`, but `enforce-tests` for the `tests` header |
| Replace a package's guideline | `.ai/guidelines/<vendor>/<package>/<file>.blade.php` (usually `core`) |
| Drop a guideline | `config('boost.guidelines.exclude')` by **header name**, e.g. `['tests', 'pest/core', 'herd']` |
| One file for every agent | 2.10+: the default. Before: `config('boost.agents.claude_code.guidelines_path') = 'AGENTS.md'`. Either way `CLAUDE.md` becomes a hand-written `@AGENTS.md` that Boost never touches; delete any old block from it, because Claude Code ignores `AGENTS.md` while a `CLAUDE.md` exists |
| One skills directory | `config('boost.agents.<agent>.skills_path') = '.agents/skills'` for `claude_code` and `cursor`; commit `.claude/skills` as a symlink to `../.agents/skills` |
| Own skill | a directory in `.agents/skills/<name>/` that Boost does not own, or `.ai/skills/<name>/` (overrides a same-named Boost skill; symlinked into each agent's folder, copied when it contains Blade) |

- `config/boost.php` is not published by default and its stub lacks `agents`; add it by hand. Laravel merges config shallowly: a published `rules` array replaces the
  package's whole `rules` array.
- `.gitignore` often has `.ai`. A directory entry cannot be re-included from; use `.ai/*` then
  `!.ai/guidelines/` (and `!.ai/rules/`, `!.ai/skills/` when used). Verify with
  `git check-ignore -v .ai/guidelines/x.blade.php`.
- An override of a package guideline is a fork: remove it when the package ships the fix, and say
  so in the override's commit.

## Project rules (`.ai/rules`)

Boost adds a `record-rule` MCP tool (2.4.12, on by default from 2.5) and a core guideline section that tells every agent to
read `.ai/rules/index.md` before any edit; up to 2.8.0 it also told agents to record rules on
their own, from 2.8.1 only when the user explicitly asks. Rule files carry `paths:` frontmatter;
Boost regenerates the index.

- In a repo that ignores `.ai`, every recorded rule is silently never committed. Until the repo
  decides, set `rules.enabled => false` (removes the section and unregisters the tool).
- It is instruction-based: an agent must choose to read the index. Claude Code's own
  `.claude/rules/*.md` with the same `paths:` frontmatter are loaded by the tool itself; opencode
  and Codex have no path-scoped loading (see [tools.md](tools.md)).
- Rule files invite a second home for knowledge next to `docs/`. If enabled, keep each rule a
  pointer ("working here, read docs/X first") and the content in `docs/`.
- `rules.scoped_guidelines` moves Boost's own path-scoped guidelines into `.ai/rules/boost/`. Its
  globs include `app/Models/**`, `app/Http/**`, `routes/**`, `tests/**`, `database/migrations/**`,
  `resources/js/**`, `resources/views/**`, `app/Livewire/**`; on a domain-structured app
  (`app/Domains/*/…`) several miss, and the saving is small (one measured repo: 23 lines).

## Output that differs per machine

A generated file that differs per machine makes every `composer install` dirty for someone and
breaks any drift check. Known case: the `herd` guideline is only generated when `APP_URL`
contains `.test`, Laravel Herd is installed **and** the project does not use Sail. Agents in containers (OpenHands, cloud agents)
also get Herd instructions that are false for them. Exclude `herd` and move the text to the
repo's development docs. Before trusting a drift check, generate once on a machine without Herd
and with a non-`.test` `APP_URL`.

## Packages that run Boost for you

A Composer package can be a plugin that runs `boost:install` after every install or update and
rewrites `boost.json` (seen in an internal quality package). Consequences:

- Every `composer install` regenerates the block, so hand-written content inside it disappears
  on the next install, and teams learn to revert the whole diff, upstream improvements included.
- A package guideline that tells agents to "record knowledge here" (in the regenerated file)
  destroys what it asks for. Fix it in the package; override locally until then.
- Once committed files equal the generator's output, that install-time run is a no-op. The drift
  check below is what makes it harmless.

Always verify against the versions in the lockfile: run `composer install` into a fresh worktree
with its own `vendor/` first. A stale local `vendor/` produces confident wrong conclusions.

## CI drift check

Ship [../assets/check-generated-instructions.sh](../assets/check-generated-instructions.sh) and
run it in the project's test image with `vendor` and `node_modules` linked in. It fails when:

1. `CLAUDE.md` is not a file starting with `@AGENTS.md`;
2. `.claude/skills` is not the symlink to `../.agents/skills`;
3. `AGENTS.md`, `boost.json` or `.agents/skills` differ from a fresh
   `boost:install --guidelines --skills` (same flags as whatever runs Boost automatically);
4. the hand-written part (header above the block, `.ai/guidelines`, `CLAUDE.md`) exceeds the
   budget.

Test it three ways before relying on it: clean tree (green), one hand-written line inside the
block (red), budget exceeded (red). The test image usually has no `git`; the script diffs against
a snapshot instead.

## Other generators

| Generator | Markers | Source of truth | Commit or ignore | Drift check |
|---|---|---|---|---|
| Laravel Boost | `<laravel-boost-guidelines>` block; skills it lists in `boost.json` | `.ai/guidelines`, `.ai/skills`, `config/boost.php`, installed packages | Laravel's docs allow ignoring; commit + drift check when worktrees, cloud agents or CI need the files | none built in: regenerate and diff ([CI drift check](#ci-drift-check)) |
| Next.js 16.3 | `<!-- BEGIN/END:nextjs-agent-rules -->` | `next` package (`next dev`, create-next-app) | commit; stopped writing `CLAUDE.md` | none; `next dev` re-adds it |
| [Nx](https://nx.dev/docs/features/enhance-ai) | `<!-- nx configuration start/end-->` | Nx generator | commit | `nx configure-ai-agents --check` |
| Symfony AI Mate | `<!-- BEGIN/END AI_MATE_INSTRUCTIONS -->`; `@AGENTS.md` import block in `CLAUDE.md` | `mate discover` | commit | none |
| rails-ai-context | `<!-- BEGIN/END rails-ai-context -->` | app introspection | commit (not `.ai-context.json`) | none |
| [rulesync](https://github.com/dyoshikawa/rulesync) | none; owns whole files | `.rulesync/rules/*.md` (`root: true`), `rulesync.jsonc` | commit (deliberately not ignored) | `rulesync generate --check --targets "*" --features "*"` |
| [Ruler](https://github.com/intellectronica/ruler) | none; full overwrite, `.bak` backups | `.ruler/`, `ruler.toml` | ignored by default via a managed `.gitignore` block | `ruler apply` + `git diff` |
| Claude Code `/import` | none | one-time copy | — | a copy drifts from then on |

The convention is converging on a marked block inside `AGENTS.md` plus `CLAUDE.md` = `@AGENTS.md`.

Boost's own guidelines carry redundancy (repeated `search-docs` reminders, baseline PHP the model
knows): [laravel/boost#606](https://github.com/laravel/boost/issues/606). Trim through
`guidelines.exclude` and overrides, not by editing the output.

## Any generator

- Find the markers and the command. Everything between the markers is the generator's; put team
  text where the generator composes it from (its source directory), never in the output. A
  generator without markers owns the whole file.
- Prefer the generator's own check (`nx configure-ai-agents --check`, `rulesync generate --check`)
  over a hand-written snapshot diff.
- Pin the generator's version in the lockfile and regenerate in CI with the same flags.
- Make the output machine-independent: exclude sections that depend on local tools, paths or
  environment.
- If the generator writes one copy per tool, point every tool at one file and one skills
  directory, or generate the copies and ignore them.
