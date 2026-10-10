# Distribution mechanics — the deep detail

The README covers the happy paths. This page holds the mechanics that matter
when you pin, automate, or debug an install. Verified against `skills` CLI
v1.5.17 and v1.7.1 and Claude Code 2.1.207 to 2.1.251 (July to October 2026);
re-verify after major version bumps.

## The channels

All channels serve the same merged tree: each `skills/<name>/` directory is
simultaneously the flat-layout skill and the Claude Code plugin (manifest in
`skills/<name>/.claude-plugin/`, catalog generated into
`.claude-plugin/marketplace.json`).

| Channel | Consumers | Updates | Pinning |
| --- | --- | --- | --- |
| Claude Code plugin marketplace (generated `marketplace.json` → `./skills/<n>`) | Claude Code | on a skill `version` bump — its own release train (`<skill>-vX.Y.Z`) on each push to main | `#ref` on the marketplace URL, or a full commit `sha` per plugin source |
| `npx skills add <git-url>` (walks the flat `skills/` tree) | 70+ agents incl. opencode, Cursor, Codex | `npx skills update` (re-clones the source) | pin an immutable `#vX.Y.Z` tag in the URL |
| `.skill` zips (release assets + package registry; plugin machinery excluded) | claude.ai / Claude app | manual re-upload | the release you downloaded |
| Manual copy / symlink of `skills/<n>/` into `.claude/skills/` | Claude Code + opencode (opencode reads `.claude/skills/` natively) | `git pull` if symlinked | your checkout |

**Merged-shape nuance:** an installed/copied `skills/<n>/` carries its
`.claude-plugin/plugin.json`. Inside a `.claude/skills/` directory, Claude
Code treats such a folder as a *skills-dir plugin* (the `claude plugin init`
pattern) — it loads namespaced as `<name>@skills-dir` instead of as a plain
personal skill. Functionally equivalent; just don't combine it with a
marketplace install of the same plugin or you'll pay the description budget
twice. Non-Claude agents ignore the extra manifest entirely.

## One channel per skill, per machine

Every channel installs and loads **its own copy** of a skill, and updates only that copy:

| Channel | Where the copy lives | Wires hooks / `.mcp.json` | Update with |
| --- | --- | --- | --- |
| Claude Code plugin (per skill or bundle) | `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, loads as `<plugin>:<skill>` | yes | `claude plugin marketplace update <marketplace>` then `claude plugin update <plugin>@<marketplace>`, then a new session |
| `npx skills add -g` | `~/.agents/skills/<name>/`, symlinked into each chosen agent's folder, plain names | no | `npx skills update -g` |
| `scripts/install_opencode.sh` | its own clone (`~/.webgrip/ai-skills`), every `skills/<name>` linked into `~/.config/opencode/skills/` | opencode plugins only | rerun the script |
| Manual clone + symlink | your checkout | no | `git pull` |

Two channels for the same skill load it twice, without a warning: its description is paid
twice from the shared budget and the router sees two entries — the usual cause of "it
loads twice" and "the other version fired". The opencode installer and an
`npx skills … -a opencode` install are two channels for opencode. Each channel's update
reaches only its own copy: `npx skills update -g` answers "All global skills are up to
date" for a skill you actually got from a plugin.

To find a double load, list every channel's folder and the plugins:

```bash
ls -la ~/.claude/skills ~/.agents/skills ~/.config/opencode/skills
claude plugin list
claude plugin details <plugin>    # components and projected token cost
```

Plugin state lives in `~/.claude/plugins/installed_plugins.json`,
`known_marketplaces.json` and the `cache/` tree above.

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

- **The install folder is the frontmatter `name`** (`sanitizeName(skill.name)`
  in the CLI), and `~/.agents/skills/` holds one folder per name, so two
  sources shipping the same name overwrite each other, last install wins.
  Claude Code also hides a repo-level skill behind a global one of the same
  name, without a warning. With two sources installed, pick one source per
  shared name: `-s` on the second `npx skills add` limits it to the names
  you want from there.
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
- **The global lock is `~/.agents/.skill-lock.json`** (v3): per skill `source`,
  `sourceUrl`, `skillPath` and `skillFolderHash`. A skill's `source` there says
  where it came from. `lastSelectedAgents` in the same file only remembers the
  interactive picker's last choice; it is not an install record — which agents
  a skill reaches shows in the agent folders themselves.
- **Flags:** `-g` (user level), `-a <agent>` (repeatable), `-s <skill>`
  (repeatable, `'*'` for all), `-y`, `--list`, `--copy`. `--all` is shorthand
  for `-s '*' -a '*' -y`: every skill into every agent the CLI knows,
  including agents you don't run; name agents with `-a` to keep the footprint
  to the ones you use.
- **Testing an unreleased change:** an install from the git URL does not see
  edits in your checkout. Install from the checkout's path
  (`npx skills add /path/to/checkout -s <name> -a claude-code -g -y`), then
  reinstall from the URL so the lock's `source` points back at the remote.
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
