# Generated instruction files

When a tool writes `AGENTS.md`/`CLAUDE.md` for you, the file has two owners. Everything below is
about keeping them apart. Laravel Boost is the worked case; the rules at the end apply to any
generator (rulesync, ruler, framework installers).

## Contents
- [Laravel Boost: how it writes](#laravel-boost-how-it-writes)
- [Override points](#override-points)
- [Project rules (`.ai/rules`)](#project-rules-airules)
- [Output that differs per machine](#output-that-differs-per-machine)
- [Packages and Boost](#packages-and-boost)
- [Upgrading Boost](#upgrading-boost)
- [Generated text that contradicts the repo](#generated-text-that-contradicts-the-repo)
- [CI drift check](#ci-drift-check)
- [One rule source, generated per tool](#one-rule-source-generated-per-tool)
- [Other generators](#other-generators)
- [Any generator](#any-generator)

## Laravel Boost: how it writes

- `php artisan boost:install` / `boost:update` compose guidelines into one block,
  `<laravel-boost-guidelines>` … `</laravel-boost-guidelines>`, house guidelines first, and
  **replace the whole block** in each agent's file (the first block only; without one it appends
  the block). Text inside is gone on the next run.
- Defaults per agent: guidelines to `AGENTS.md` for Codex, opencode, Cursor, Junie and Copilot;
  Claude Code to `CLAUDE.md` up to 2.9, `AGENTS.md` in 2.10.0, and from 2.10.1 back to an existing
  `CLAUDE.md` unless `guidelines_path` is pinned. Skills to `.agents/skills` (Codex, opencode),
  `.claude/skills`, `.cursor/skills`, `.junie/skills`, `.github/skills`. Every path is
  overridable per agent (`boost.agents.<agent>.guidelines_path`, `.skills_path`).
- **Pin the version in the lockfile and read the notes of every release you skip, patch releases
  included**: they have changed the target file, the always-on text and the bundled skills. 2.8
  stopped touching text outside the block; 2.8.1 made `record-rule` opt-in.
- It deletes and recopies every skill it owns on each run, so a hand edit inside a Boost skill is
  lost. Stale skills are removed only when `boost.json` tracked them.
- Content follows installed packages: PHP versions from `vendor/`, JavaScript packages from
  **`node_modules`** (without it, Echo skills disappear and Inertia skill sections drop out).
- Flags change output: `--guidelines` without `--skills` omits the "Skills Activation" section.
  Compare runs only with identical flags.
- Its commands exist only when `APP_ENV=local` or `APP_DEBUG=true` (and `boost.enabled` is not
  false). With an unreachable database it hangs on the connection instead of failing;
  `DB_CONNECTION=sqlite DB_DATABASE=:memory:` finishes in seconds.

## Override points

| Want | Do |
|---|---|
| House rules composed into every agent's block | `.ai/guidelines/<name>.blade.php` (or `.md`); they appear at the top of the block |
| Replace one Boost guideline | `.ai/guidelines/<path>.blade.php`, named after the guideline's **path**, not its header: `pest/core`, `boost/core`, `herd/core`, but `enforce-tests` for the `tests` header. A file named after the header is silently ignored |
| Replace a package's guideline | `.ai/guidelines/<vendor>/<package>/<file>.blade.php` (usually `core`) |
| Drop a guideline | `config('boost.guidelines.exclude')` by exact **key**, no globs: core `tests`, `pest/core`, `herd`, `deployments`, `pint/core`, `inertia-laravel/core`; a package's guideline is `<vendor>/<package>/<path under resources/boost/guidelines>`, e.g. `acme/quality/core` |
| Drop a bundled skill | `config('boost.skills.exclude')`, e.g. `['infer-conventions']`: the next install deletes the folder and its `boost.json` entry; removing the exclude restores it. Never edit `boost.json`: it is generated state and the next run undoes the edit |
| One file for every agent | Always set `config('boost.agents.claude_code.guidelines_path') = 'AGENTS.md'`. Without it Boost (2.10.1+, laravel/boost#1043) writes the whole block into `CLAUDE.md` as soon as that file exists, wiping the `@AGENTS.md` import. `CLAUDE.md` stays a hand-written `@AGENTS.md`; delete any old block from it, because Claude Code ignores `AGENTS.md` while a `CLAUDE.md` exists |
| One skills directory | `config('boost.agents.<agent>.skills_path') = '.agents/skills'` for `claude_code` and `cursor`; commit `.claude/skills` as a symlink to `../.agents/skills` |
| Own skill | `.ai/skills/<name>/SKILL.md`. Boost links it into every agent's skills path (copies it when it contains Blade) and records it in `boost.json`; it replaces a Boost skill of the same name. A skill placed by hand in `.agents/skills` never reaches an agent with its own generated folder (Junie). In a repo without Boost, `.agents/skills` itself is the source |

- Keep every hand-written agent source under `.ai/` (`guidelines`, `rules`, `skills`); everything
  else Boost writes is output.
- `config/boost.php` is not published by default; the stub lacks `agents` and `guidelines_path`,
  so add them by hand. Laravel merges config shallowly: a published `rules` array replaces the
  package's whole `rules` array.
- Prove an exclude or override by regenerating twice and checking the item is gone or replaced.
- `.gitignore` often has `.ai`. A directory entry cannot be re-included from; use `.ai/*` then one
  negation per tracked subdirectory (`!.ai/guidelines/`, `!.ai/rules/`, `!.ai/skills/`). Every
  **new** subdirectory needs its own negation, and `git add` only prints "The following paths are
  ignored"; run `git check-ignore -v` on a file in each new subdirectory.
- An override of a package guideline is a fork: remove it when the package ships the fix, and say
  so in the override's commit.
- Excluding a package guideline does not drop your override of it: Boost promotes
  `.ai/guidelines/<vendor>/<package>/core.blade.php` to a standalone guideline. Delete the
  override file together with the exclude.
- Runtime settings worth setting: `enforce_tests` as an explicit boolean (otherwise generation
  probes `artisan test --list-tests`); `browser_log_levels` to `error,warning` with a daily
  `browser` log channel (the default writes every browser log line to an unrotated file);
  `tinker_tool_enabled` only as a team decision, because it runs arbitrary PHP. What Boost exposes
  outside local environments: [security.md](security.md#threats).

## Project rules (`.ai/rules`)

Boost adds a `record-rule` MCP tool (on by default from 2.5) and a core guideline section that
tells every agent to read `.ai/rules/index.md` before any edit. From 2.8.1 it records only "when the
user explicitly asks", and that limit lives only in the tool's description: nothing in the code
asks for approval. Rule files carry `paths:` frontmatter; Boost regenerates the index.

- Keep the feature off: `rules.enabled => false` removes the section and unregisters the tool. In
  a repo that ignores `.ai`, every recorded rule would also be silently never committed.
- It is instruction-based: an agent must choose to read the index, and the injected section is an
  always-on "you MUST first open `.ai/rules/index.md`" paragraph. Claude Code's own
  `.claude/rules/*.md` with the same `paths:` frontmatter are loaded by the tool itself; opencode
  and Codex have no path-scoped loading (see [tools.md](tools.md)).
- Layout that gives Claude native loading without that paragraph: rules in `.ai/rules/*.md`
  (flat, `paths:` as the only frontmatter key; `globs` is ignored), `.gitignore` re-including
  `!.ai/rules/`, a committed symlink `.claude/rules` → `../.ai/rules`, `rules.enabled => false`,
  and one plain line in `AGENTS.md` for other agents ("rules for specific paths are in
  `.ai/rules`; read the ones whose `paths` match the file you change"). Verify with the path-rule
  probe in [claude-code.md](claude-code.md#prove-what-loads).
- The symlink makes every Markdown file in `.ai/rules` an instruction: a file without `paths:`
  loads in every session. With the feature on, Boost's pathless `index.md` would load at launch and
  `.ai/rules/boost/*.md` would repeat the "open the index" paragraph. Fail CI on pathless rules and
  on subdirectories ([CI drift check](#ci-drift-check)).
- With `rules.enabled => false` Boost still clears `.ai/rules/boost/` on every run (and rewrites
  `index.md` if that directory existed); hand-written rule files are left alone.
- A rule body is the trap (what to do), the reason, and a link to the `docs/` section that owns
  the full story, at most ~20 lines. Admission bar: [maintenance.md](maintenance.md#when-to-add-a-line).
- `rules.scoped_guidelines` moves five path-bound Boost guidelines (about 2 KB) into
  `.ai/rules/boost/`. Their globs assume Laravel's default folders (`app/Models/**`,
  `app/Http/**`, `routes/**`, `resources/js/**`, …), so on a codebase grouped by domain most match
  nothing (`tests/**` still does). Measure the saving on your layout before turning it on.
- The bundled `infer-conventions` skill has `disable-model-invocation: true`: it runs only when
  asked and costs no per-session context. It wants three or more consistent examples with any rival
  under about 20 %, records decisions rather than defaults, reports a mixed pattern as a conflict
  instead of choosing, and asks for approval per candidate. It reads only code and writes Boost's
  bare rule format (no reason, no docs link), so wrap it instead of excluding it
  ([maintenance.md](maintenance.md#agent-proposed-rules)). Read a vendor skill's `SKILL.md` and
  frontmatter before advising on it.

## Output that differs per machine

A generated file that differs per machine makes every `composer install` dirty for someone and
breaks any drift check. Known cases:

- The `herd` guideline is only generated when `APP_URL` contains `.test`, Laravel Herd is installed
  **and** the project does not use Sail. Agents in containers (OpenHands, cloud agents) also get
  Herd instructions that are false for them. Exclude `herd` and move the text to the repo's
  development docs.
- `.junie/mcp/mcp.json` and `.cursor/mcp.json` get absolute local paths: keep them ignored.
- Without `enforce_tests` set, the tests guideline depends on what `artisan test --list-tests`
  finds on that machine.

Before trusting a drift check, generate once on a machine without Herd, with a non-`.test`
`APP_URL`, and once without `node_modules` to see what changes.

## Packages and Boost

- A Composer package ships guidelines in `resources/boost/guidelines/**/*.blade.php` or `*.md`
  (recursive, sorted by name) and skills in `resources/boost/skills/<name>/SKILL.md`. Boost reads
  them only from a **direct** dependency selected under `packages` in `boost.json`. A package that
  runs `boost:install` itself adds its own name there first, or a fresh install skips it.
- A dependency can be a Composer plugin that runs `boost:install` after every install or update
  and rewrites `boost.json`. Check `allow-plugins` and every `composer-plugin` dependency before
  assuming an install has no side effects. Consequences:
  - Every `composer install` regenerates the block, so hand-written content inside it disappears
    on the next install, and teams learn to revert the whole diff, upstream improvements included.
  - A package guideline that tells agents to "record knowledge here" (in the regenerated file)
    destroys what it asks for. Fix it in the package; override locally until then.
  - Once committed files equal the generator's output, that install-time run is a no-op. The drift
    check below is what makes it harmless.
  - A plugin that swallows a failed `boost:install` leaves stale files with no signal. When you own
    the plugin, print the failure with Boost's output and never fail Composer over it.
- Shipping a stack's agent material as one package: [layering.md](layering.md#distribution-in-order-of-preference).

Always verify against the versions in the lockfile: run `composer install` into a fresh worktree
with its own `vendor/` first. A stale local `vendor/` produces confident wrong conclusions.

## Upgrading Boost

Stay on the latest release and upgrade in a change of its own:

1. Read the release notes (`https://github.com/laravel/boost/releases`) of every version you skip.
2. `composer update laravel/boost`, adding only the dependencies it requires (2.10 needs
   `laravel/mcp` ^1.0). `--with-dependencies` drags unrelated packages along. Revert files the
   update regenerates as a side effect, such as IDE helper stubs.
3. Regenerate twice with the same flags the automatic run uses; the second run must change nothing.
4. Read the diff of `AGENTS.md` ([next section](#generated-text-that-contradicts-the-repo)).
5. Smoke-test the MCP server:
   `(printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'; sleep 4) | php artisan boost:mcp`
   must answer with a result.
6. Re-measure what every session loads and reset the token budget to the new figure plus 15 % in
   the same reviewed change.
7. Update docs and ADRs that cite the version, and read them back.

## Generated text that contradicts the repo

After adopting or upgrading a generator, grep its output:
`grep -nE "CRITICAL|MUST|IMPORTANT|resources/js/Pages|vite.config|tests/Feature" AGENTS.md`.

| Finding | Fix |
|---|---|
| A guideline contradicts a tool the repo uses (`pint/core` runs Pint directly where Duster wraps it) | exclude the guideline |
| A path stated as fact that the repo does not use (`resources/js/Pages`, `tests/Feature` where suites are listed explicitly) | one house line with the real path |
| A pointer to a capability the repo lacks (a skill withheld by `boost.json`, a host the app never deploys to) | exclude the guideline |
| An upstream rule you must keep that contradicts a house rule | one house line naming what it overrides ("This overrides the rule further down that documentation files are only created on request"), plus an upstream issue |

A model resolves contradicting rules arbitrarily, so name every conflict instead of hoping. Never
edit the output and never copy upstream text into an override to change one word.
Boost's guidelines also carry redundancy (repeated `search-docs` reminders, baseline PHP the model
knows): [laravel/boost#606](https://github.com/laravel/boost/issues/606). Trim through
`guidelines.exclude` and overrides.

## CI drift check

Ship [../assets/check-generated-instructions.sh](../assets/check-generated-instructions.sh) with
[../scripts/agent_setup.py](../scripts/agent_setup.py) and [../assets/targets.json](../assets/targets.json);
`AGENT_INSTRUCTIONS_AGENT_SETUP` and `AGENT_INSTRUCTIONS_REGISTRY` override where it finds them.
Run it in the project's test image with `vendor` and `node_modules` linked in. It fails when:

1. `agent_setup.py check .` fails: `CLAUDE.md` is not a file starting with `@AGENTS.md`;
   `.claude/skills` or `.claude/rules` is not the symlink to `../.agents/skills` or `../.ai/rules`;
   a generated rule copy is stale or orphaned; a rule has no `paths`, a glob matches no file, a
   rule exceeds 20 lines or sits in a subdirectory; a relative link or `#anchor` in `AGENTS.md`,
   `.ai/rules` or `docs/` points nowhere; a file in `docs/` is missing from `docs/index.md`;
2. `CLAUDE.md` holds a generated block;
3. the installed generator differs from the lockfile (`vendor/composer/installed.json` against
   `composer.lock`; package `AGENT_INSTRUCTIONS_GENERATOR_PACKAGE`, default `laravel/boost`). The
   check stops there, because generating with another version rewrites files the lock never
   produced. Give every worktree its own install;
4. `AGENTS.md`, `boost.json` or `.agents/skills` differ from a fresh
   `boost:install --guidelines --skills` (same flags as whatever runs Boost automatically), or,
   where `git` exists, generated files are untracked leftovers a clean checkout would not have;
5. the hand-written part (header above the block, `.ai/guidelines`, `CLAUDE.md`) exceeds the
   line budget (`AGENT_INSTRUCTIONS_BUDGET`, default 150);
6. what every session loads (`AGENTS.md`, `CLAUDE.md`, their `@` imports, rules without `paths`)
   exceeds `token_budget` in `.ai/agent-setup.json` (checked by `agent_setup.py`). Tokens are
   estimated at 2.9 bytes per token, measured on Markdown instruction files with
   `claude -p "/context"`; bytes / 4 reads about 40 % low on tables and code spans. Calibrate on
   your own files and set `bytes_per_token` there or `AGENT_INSTRUCTIONS_BYTES_PER_TOKEN`
   (`scripts/measure.py` reads it too). `agent_setup.py layout` sets the budget to the measured
   figure plus 15 %, rounded up to the next 100; that headroom is about 2 KB in a typical repo, so
   it catches a generator that grows, not every added line. It does not count skill descriptions
   or MCP tool definitions.

- `agent_setup.py check` needs neither `vendor/`, Boost nor git: run it on its own in every
  pipeline and in a pre-commit hook gated on staged agent files ([ci.md](ci.md)). The shell script
  runs it first, so its findings show even when `vendor/` is stale.
- Commit the generated files and drift-check them rather than blocking edits with a hook: CI
  catches every agent and person, a hook only one tool. If you ever disable the job, record why and
  what replaces it, or drift returns silently.
- Test it before relying on it: clean tree (green); one hand-written line inside the block, a dead
  glob, a broken link, an unindexed doc, a budget overrun and a `vendor/` older than the lock (each
  red); a non-`.test` `APP_URL` (still green). The test image usually has no `git`; the scripts
  then diff against a snapshot and walk the tree.

## One rule source, generated per tool

- Keep each path rule once, in `.ai/rules/*.md` with `paths:`. Claude Code reads it through the
  `.claude/rules` symlink; tools with their own path format (Cursor `.mdc` globs, Copilot
  `applyTo`) get generated copies; tools without path scoping get the one `AGENTS.md` line, never
  every rule loaded unscoped.
- Generate the per-tool copies with `scripts/agent_setup.py generate`.
- A generator writing into a directory people also write to marks its files, deletes only marked
  files, and refuses to overwrite an unmarked file of the same name.
- CI fails on stale or orphaned generated copies, like the drift check above.

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

## Any generator

- Find the markers and the command. Everything between the markers is the generator's; put team
  text where the generator composes it from (its source directory), never in the output. A
  generator without markers owns the whole file.
- Edit generated files only through their source. On a merge conflict in generated output, take
  the base's version whole and regenerate from the merged source; never hand-merge the output.
- Prefer the generator's own check (`nx configure-ai-agents --check`, `rulesync generate --check`)
  over a hand-written snapshot diff.
- Pin the generator's version in the lockfile, pin every output path it writes (a default target
  can change in a patch release), and regenerate in CI with the same flags.
- Make the output machine-independent: exclude sections that depend on local tools, paths or
  environment.
- If the generator writes one copy per tool, point every tool at one file and one skills
  directory, or generate the copies and ignore them.
