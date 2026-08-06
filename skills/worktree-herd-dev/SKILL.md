---
name: worktree-herd-dev
description: Sets up and tears down git worktrees with Laravel Herd sites, isolated Vite ports, and optional per-worktree databases for parallel browser testing. Use when the user wants worktree Herd links, parallel .test domains, a database per branch, switching workspaces in the browser, worktree dev environments, or global worktree tooling.
---

# Worktree Herd Dev

Parallel git worktrees, each with a dedicated Herd `.test` domain, its own Vite port, and (opt-in) its own database. Setup rolls back on failure; cleanup never guesses which Herd site or database to remove.

**Announce:** "I'm using the worktree-herd-dev skill."

## Prerequisites

- macOS with [Laravel Herd](https://herd.laravel.com)
- `git`, `node`, `composer` (`psql`/`mysql` only for per-worktree databases)
- One-time install (run from this skill's directory):

```bash
scripts/install.sh
```

This links `worktree-herd-setup`, `worktree-herd-cleanup`, and `worktree-herd-install-tasks` into `~/.local/bin`.

## Quick commands

```bash
# Worktree + Herd site for an existing branch (local or origin)
worktree-herd-setup feature/my-branch

# New branch (based on config base_branch, else origin's default branch)
worktree-herd-setup --create feature/new-branch
worktree-herd-setup --create --base development feature/new-branch

# Own database for this worktree (created + migrated; dropped on cleanup)
worktree-herd-setup --create --db feature/my-branch

# Custom Herd site name (without TLD) / configure the current workspace
worktree-herd-setup feature/my-branch afmetingen.heebink
worktree-herd-setup --current

# Other setup flags: --no-install --build --no-secure --open

# Remove worktree + Herd link (+ database if this tool created one)
worktree-herd-cleanup feature/my-branch
worktree-herd-cleanup --current
worktree-herd-cleanup --dry-run feature/my-branch   # print the plan first
# Other cleanup flags: --yes --force --keep-herd --keep-db
```

## Per-project config (optional)

`worktree-herd.yml` in the main repo root; flags override it. All keys optional — see [reference.md](reference.md) for the full list and defaults:

```yaml
base_branch: development     # what --create branches from
database: per-worktree       # every worktree gets its own DB
build_assets: true           # build once so the site works without a dev server
site_separator: "-"          # flat site names — REQUIRED for apps that route their own subdomains
editor: cursor               # used by --open
```

Project-specific steps (seeders, admin users, extra .env rewrites) belong in executable hooks at `.worktree-herd/post-setup` and `.worktree-herd/pre-cleanup` — the hook contract is in [reference.md](reference.md). **When setting this up for a project, start from [projects.md](projects.md)**: it has an onboarding checklist and ready-to-copy recipes (single-domain, multi-domain/subdomain-routing, per-worktree data). Multi-domain apps misbehave without their recipe — the worktree URL silently lands in the main checkout.

## What setup does

1. Creates `<repo>-worktrees/<branch>` next to the main repo (or reuses a registered worktree; location configurable via `worktrees_dir`)
2. Copies `.env` from the main repo; sets `APP_URL`, `VITE_PORT` (auto-increment from 5174), and a unique `SESSION_COOKIE`
3. Derives the Herd site from the main `herd.yml`/`APP_URL` (`mijn.heebink` → `slug.heebink`, or `slug-heebink` with `site_separator: "-"`); refuses to clobber an existing Herd site — a derived name that collides gets a hash suffix instead
4. Runs `herd link --secure --update-env --isolate=<php>`
5. Installs composer + node dependencies, runs `artisan storage:link`
6. With `--db`/`database: per-worktree`: creates the database (pgsql/mysql/sqlite from `DB_CONNECTION`), sets `DB_DATABASE`, runs `artisan migrate`
7. Runs your `post-setup` hook, then records everything in `<worktrees-dir>/.registry.json` and a `.worktree-herd.json` marker inside the worktree
8. If any step fails, everything this run created is rolled back (worktree, Herd link/cert, database, registry entry)

## Cleanup safety

Teardown order is hook → Herd (verified) → database → git worktree. After unlinking, cleanup also prunes the traces Herd itself leaves behind: the removed site's entries in Herd's PHP CA bundle (`config/php/cacert.pem`, plus any orphaned entries from earlier removals) and a `herd.json` `lastSite` pointing at the deleted worktree. Cleanup refuses to run when the site can't be resolved from the marker/registry, when the path isn't a registered worktree, when another process has files open in it, or (without `--force`) when the worktree has real uncommitted changes — the tool's own artifacts don't count. `--dry-run` shows the exact plan.

## Browser workflow

Each worktree gets its own URL — switch branches by switching tabs:

- Main: `https://mijn.heebink.test`
- Worktree: `https://afmetingen.heebink.test`

Start a dev server per worktree (or set `build_assets: true` to skip it):

```bash
cd <worktree> && composer run dev
```

## Editor tasks (per project)

```bash
worktree-herd-install-tasks /path/to/project
```

Then: **Tasks: Run Task** → choose a Worktree task (VS Code / Cursor).

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Port conflict | Check `<worktrees-dir>/.registry.json` for used `vite_port` values |
| Wrong domain | Pass an explicit site: `worktree-herd-setup branch custom.site` |
| `herd` not found | Ensure the Herd CLI is installed and on PATH |
| "Cannot determine the Herd site" | The marker/registry is gone; pass `--keep-herd` and unlink manually |
| Database drop fails | Open sessions are listed with a `pg_terminate_backend` one-liner |
| Cleanup refuses: worktree in use | Stop dev servers / close editors in that worktree, retry |

## Script locations

Relative to this skill's directory:

```
scripts/
├── lib.sh
├── worktree-herd-setup.sh
├── worktree-herd-cleanup.sh
├── install.sh
└── install-project-tasks.sh
```

For the config reference, hook contract, database behavior, and naming rules, see [reference.md](reference.md).
