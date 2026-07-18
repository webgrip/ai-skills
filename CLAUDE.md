# CLAUDE.md — ai-skills

Claude-skills plugin marketplace (Forgejo-hosted). **Merged layout: each
`skills/<name>/` directory IS its plugin** — `SKILL.md` at the plugin root,
manifest in `skills/<name>/.claude-plugin/plugin.json` (the shape
`claude plugin init` scaffolds). One tree serves everyone: Claude Code reads
it via `.claude-plugin/marketplace.json`, non-Claude agents and the
`npx skills`/`gh skill` installers walk `skills/` flat, opencode symlinks it.

## Invariants — the automation breaks if you violate these

- **`skills/<name>/.claude-plugin/plugin.json` is the single source of truth.**
  `marketplace.json`'s `plugins[]` is GENERATED from it (`scripts/sync_marketplace.py`);
  never edit that array by hand. Skill `name`s are unique (flat tree).
- **Never add `when_to_use` frontmatter** — it is Claude-Code-only; opencode and every flat-tree
  consumer silently drop it, so trigger text there is invisible to half the estate's consumers.
  All "Use when …" trigger text lives inside `description` (≤ 1024 chars, no angle brackets).
  Lint enforces this.
- **Every skill ships `evals/evals.json`** (skill-creator format, ≥ 3 cases with objective
  assertions) and **has a row in the root README's Skills table**. Add/remove a skill → update
  both in the same PR. Lint enforces both.
- **Plugin machinery stays at the skill root** (`.claude-plugin/`, `README.md`, `test.sh`,
  `.mcp.json`) — `build_dist.py` excludes exactly that set from the claude.ai `.skill` zips;
  everything else in the dir ships everywhere.
- **Per-skill release trains.** Each skill is its own train: tag `<skill>-v<X.Y.Z>`,
  changelog `skills/<skill>/CHANGELOG.md`, version, and `.skill` artifact.
  `scripts/release_skills.py` bumps a skill **only** from conventional commits
  touching `skills/<skill>/` since that skill's own last tag — a change to one
  skill releases that skill and nothing else. **There is no repo-wide release
  tag.** **Never edit `version` anywhere** — the train computes it (breaking →
  major, `feat` → minor, else patch; force a major with `feat(<plugin>)!: ...`);
  CI (`check_plugin_commits.py`) rejects hand-bumps.
- **Commits touching `skills/<name>/` must use a release-triggering type**
  (`feat|fix|perf|refactor|revert` or breaking) — anything else merges without
  releasing that skill, so the change never reaches its Claude Code installs.
  CI enforces this.
- **`dist/` is never committed** (gitignored). The release pipeline builds the
  `.skill` zips fresh; `python3 scripts/build_dist.py` locally if you need one.
- Plugin `name` slugs are immutable once published (renames break installs).
- **Fetch/pull before every authoring session.** Release bots push `chore(release)` commit-backs
  and other sessions push plugins; a stale clone diverges silently (2026-07-13: local checkout was
  two plugins behind its own installed cache).
- **Committing marketplace.json around another stream's uncommitted plugin:** the catalog is
  generated from every `skills/*/.claude-plugin/plugin.json` on disk, so an in-flight skill dir
  would leak into your commit and fail CI's `sync --check` on the pushed tree. Set theirs aside
  → regenerate → commit your paths → restore theirs → regenerate again (working tree keeps
  their state).

## Adding a skill

```bash
python3 scripts/new_skill.py my-skill "One-line description."
# write skills/my-skill/SKILL.md + evals + README (lint fails while TODOs remain)
npm run check && npm test
```

`test.sh` is optional — only for plugin-specific behavior (see domain-language's);
generic quality rules are enforced by `scripts/lint_skills.py` (frontmatter name==dir + kebab,
description ≤1024 chars with "Use when …" triggers, no `when_to_use`, no angle brackets in
frontmatter, no `TODO:` scaffold markers, SKILL.md <500 lines, no literal bang-backtick token
in SKILL.md, relative links resolve, evals/evals.json ≥3 cases, README catalog row). The
skillsmith plugin documents the skill-authoring craft these rules come from.

## What a plugin can ship / genericizing repo-born skills

Beyond `skills/`, a plugin may ship (all at plugin root): `.mcp.json` (MCP servers — enabling the
plugin wires them for the consumer; a same-named repo-level entry overrides), `hooks/hooks.json`,
`agents/`, `.lsp.json`, `monitors/`, `bin/` (PATH), `settings.json` (`agent`/`subagentStatusLine`
only). `vikunja-product-owner` ships the org vikunja MCP this way. Test locally:
`claude --plugin-dir ./skills/<name>` + `/reload-plugins`.

**Genericizing a repo-born skill** (the vikunja-product-owner pattern): the plugin carries the
*role* (procedures, heuristics, API mechanics); each consumer repo carries the *instance facts*
in a contract block in its `AGENTS.md` (the skill resolves it first, and its README ships the
template); instance *operations* stay in the origin repo's runbook. Never bake one repo's ids,
paths, or hostnames into skill instructions — hostname *defaults* belong in shipped config
(`.mcp.json`, env-overridable scripts), not prose.

## Releases (per-skill trains, on every push to main)

`scripts/release_skills.py apply` (the `release` job in `.forgejo/workflows/release.yml`)
walks each skill independently. For a skill with conventional commits touching
`skills/<skill>/` since its own last `<skill>-vX.Y.Z` tag it: bumps the version,
prepends `skills/<skill>/CHANGELOG.md`, regenerates `marketplace.json`, commits
back `chore(release): <skill>-vX.Y.Z, … [skip ci]`, tags each released skill,
pushes, publishes that skill's `<skill>.skill` zip to the generic package
registry (`…/api/packages/<owner>/generic/<skill>/<version>/<skill>.skill`), and
creates a Forgejo release per tag. A skill with no releasing commit is skipped.
No repo-wide `vX.Y.Z` tag — the old semantic-release train is gone.

- Auth: the `release` job checks out with `WEBGRIP_CI_TOKEN` (push creds for the
  commit-back + tags to protected main) and passes the same token as
  `FORGEJO_TOKEN` for the release + package-registry API (`GITHUB_SERVER_URL` +
  `GITHUB_REPOSITORY` give the base URL and owner/repo).
- Idempotent: each skill bases off its own tag (read from git, not the tree),
  `[skip ci]`/`chore(release)` commits are ignored, and a 409 from the package
  registry or an existing release is tolerated — safe to re-run a partially
  failed release.
- A **red release run is fix-now**: until it's green, the changed skills aren't
  prompted to update. Recovery: the `.skill` zips are deterministic
  (`python3 scripts/build_dist.py <skill>` reproduces byte-for-byte), and a
  re-run converges (idempotent) — the skill whose tag already exists is skipped.

## Verifying changes

`npm run check` (manifests + marketplace sync + lint + opencode config) and `npm test` (plugin
test.sh suites; domain-language's needs PyYAML). CI runs the same via
`.forgejo/workflows/ci.yml` plus a cross-tool install smoke + `claude plugin validate --strict`;
pushes to main add the release flow (`release.yml`).

**Trigger-accuracy eval** (on demand, costs tokens — not in CI): `python3 scripts/run_evals.py
[skill…]` launches a headless `claude -p` per `evals/evals.json` case with only that skill loaded
and checks it actually fired. `"expect_trigger": false` = should-NOT-trigger probe; `null` =
output-quality-only case the probe skips. Under-triggering ⇒ tune the `description` (skillsmith),
re-probe. This is the *triggering* half of the eval contract; output quality still wants the
with/without grading in CONTRIBUTING.md.

## Hook-carrying plugins

`skill-usage` and `guard-secrets` ship a `hooks/hooks.json` alongside their SKILL.md — the skill
dir is still the plugin, and the hook activates on install. Both keep an opencode twin under
`opencode/plugins/` (`skill-usage-log.js`, `guard-secrets.js`), symlinked by
`scripts/install_opencode.sh`, so the same behavior covers both tools. When you change one side's
rules, change the twin — they are a pair, not a canonical/copy.
