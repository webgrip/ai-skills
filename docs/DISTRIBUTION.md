# Distribution mechanics — the deep detail

The README covers the happy paths. This page holds the mechanics that matter
when you pin, automate, or debug an install. Verified against `skills` CLI
v1.5.17 and Claude Code 2.1.207 (July 2026); re-verify after major version
bumps.

## The channels

All channels serve the same merged tree: each `skills/<name>/` directory is
simultaneously the flat-layout skill and the Claude Code plugin (manifest in
`skills/<name>/.claude-plugin/`, catalog generated into
`.claude-plugin/marketplace.json`).

| Channel | Consumers | Updates | Pinning |
| --- | --- | --- | --- |
| Claude Code plugin marketplace (generated `marketplace.json` → `./skills/<n>`) | Claude Code | on a skill `version` bump — its own release train (`<skill>-vX.Y.Z`) on each push to main | `#ref` on the marketplace URL, or a full commit `sha` per plugin source |
| `npx skills add <git-url>#npx` (the generated `npx` branch: `skills/webgrip-<n>/`, plugin machinery stripped) | 70+ agents incl. Claude Code, opencode, Cursor, Codex | `npx skills update` (re-clones the branch) | none yet: the branch moves on every release |
| `.skill` zips (release assets + package registry; plugin machinery excluded) | claude.ai / Claude app | manual re-upload | the release you downloaded |
| Manual copy / symlink of `skills/<n>/` into `.claude/skills/` | Claude Code + opencode (opencode reads `.claude/skills/` natively) | `git pull` if symlinked | your checkout |

**Merged-shape nuance:** an installed/copied `skills/<n>/` carries its
`.claude-plugin/plugin.json`. Inside a `.claude/skills/` directory, Claude
Code treats such a folder as a *skills-dir plugin* (the `claude plugin init`
pattern) — it loads namespaced as `<name>@skills-dir` instead of as a plain
personal skill. Functionally equivalent; just don't combine it with a
marketplace install of the same plugin or you'll pay the description budget
twice. Non-Claude agents ignore the extra manifest entirely.

## Version semantics — per-skill release trains

Each skill is its **own release train**. Claude Code prompts consumers to
update a skill when its `plugin.json` `version` rises, and that bump is
**computed at release time** by `scripts/release_skills.py` from the
conventional commits **touching that skill** since its own `<skill>-vX.Y.Z`
tag — so a change to one skill releases, tags (`<skill>-vX.Y.Z`), changelogs
(`skills/<skill>/CHANGELOG.md`), and re-publishes **only that skill**; the
others don't move, and there's no repo-wide tag. Hand-edits are rejected;
a commit type that releases nothing (`chore:`, `docs:`) never reaches a
skill's installs. Corollary: between a merge and its release commit, `main`
briefly carries new content under the old version; installs converge on the
bump. A red release run must be fixed promptly — the trains are idempotent
(each skill bases off its own tag, and every remote write is gated on a state
query first: an artifact already published at the right sha256 is verified and
left alone, an existing release is skipped), so a fixed re-run resumes cleanly
without rewriting what earlier runs got right.

## skills CLI specifics

- **The install folder is the frontmatter `name`**, not the source folder
  (`sanitizeName(skill.name)` in the CLI), and `~/.agents/skills/` holds one
  folder per name. Two estates that both ship `adr-writer` overwrite each other
  there, silently, last install wins. That is why npx consumers install from
  the `npx` branch, where `scripts/build_npx_branch.py` rewrites every
  `name:` to `webgrip-<skill>` and drops the plugin machinery (a copied
  `.claude-plugin/plugin.json` would otherwise make Claude Code load the
  folder as `<name>@skills-dir` under the unprefixed plugin name). The
  release job publishes it after the per-skill trains; it reads the remote
  branch first and pushes nothing when the tree is unchanged.
- Project-scope installs write `skills-lock.json` in the consuming repo
  (source, skillPath, optional `ref`, content hash). Commit it; restore with
  `npx skills experimental_install`. **The hash is drift-detection, not
  pinning** — restore re-resolves the ref; pin a `#vX.Y.Z` tag for real
  reproducibility. `ref` must be a branch/tag, not a commit SHA.
- Default install copies once into `.agents/skills/` and symlinks agent dirs.
  Gotcha: if the project has no `.claude/` directory yet, the Claude Code
  symlink can be silently skipped — and Claude Code does **not** read
  `.agents/skills/`. Create `.claude/` first or re-run. opencode is
  unaffected (it reads `.agents/skills/` natively).
- Subpath/`@skill` URL fragments don't work on `git@`/`.git` URLs — use
  `--skill <name>`.
- **Telemetry**: the CLI beacons installs (source, skill names, agents) to
  `add-skill.vercel.sh` and is **not** auto-disabled in CI (only tagged).
  Set `DISABLE_TELEMETRY=1` / `DO_NOT_TRACK=1` — this repo's CI does.

## Marketplace-over-Forgejo specifics

- `/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git`
  works because Claude Code accepts any git host; scp-form SSH URLs work too.
- Background marketplace auto-refresh disables git credential helpers — fine
  for this public repo over https; a **private** Forgejo marketplace should
  be added by SSH URL (ssh-agent still works in the background refresh).
- Team auto-enable: commit to the consuming repo's `.claude/settings.json`
  (exact snippet in the README) — members are prompted on folder trust,
  skills load namespaced `<plugin>:<skill>`.
- `claude plugin validate .` validates the manifests + skill frontmatter;
  CI runs it with `--strict` (this repo's plugin.json files carry versions
  and descriptions, so strict passes).

## opencode

No channel of its own needed: opencode natively reads a project's
`.claude/skills/` and `.agents/skills/` plus `~/.claude/skills/` — any
install path above covers it. Org defaults, permission profiles, and the
API-key auth story live in [onboarding-opencode.md](onboarding-opencode.md)
and [auth.md](auth.md).
