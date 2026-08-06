# Worktree Herd Dev — Reference

## Config file: `worktree-herd.yml`

Optional, in the main repo root. Flat `key: value` lines (no nesting); quotes and trailing `# comments` are stripped. CLI flags always override config.

| Key | Default | Meaning |
| --- | --- | --- |
| `worktrees_dir` | `<parent>/<repo>-worktrees` | Where worktrees live. Relative paths resolve against the main repo root (e.g. `.worktrees` keeps them inside the repo — then gitignore it). |
| `base_branch` | origin's default branch, else current `HEAD` | What `--create` branches from (`origin/<base>` is preferred over a local `<base>`). |
| `database` | `shared` | `per-worktree` gives every worktree its own database (see below). |
| `site_separator` | `.` | How the site name joins slug and suffix. `-` gives a flat single-label site (`afmetingen-heebink`) — required for apps that route their own subdomains (see below). |
| `build_assets` | `false` | `true` runs `<pm> run build` after install, so the site works without a Vite dev server. |
| `editor` | `cursor` | Editor opened by `--open`: `cursor`, `code`, `none`, or any command taking a path. |
| `post_setup_hook` | `.worktree-herd/post-setup` | Run after a successful setup, before the summary. |
| `pre_cleanup_hook` | `.worktree-herd/pre-cleanup` | Run at the start of teardown, while Herd/DB still exist. |

## Domain detection and naming

The Herd site is `<branch-slug>.<suffix>`:

1. Suffix from the main repo's `herd.yml` → `name: mijn.heebink` → `heebink`
2. Fallback: `.env` → `APP_URL=https://mijn.heebink.test` → `heebink`
3. The TLD comes from `herd tld` (default `test`)

Branch slug rules: strip a ClickUp prefix (`CU-86cagjaua_`) and author suffix (`_Jos-Last`, `_Jos-Last-v2`), lowercase, non-alphanumerics become hyphens, clamped to a 63-char DNS label. Override with an explicit second argument: `worktree-herd-setup CU-123_Feature_Jos-Last custom-name.heebink`.

**Flat names for subdomain-routing apps (`site_separator: "-"`):** Herd resolves a request host in exactly two ways — an exact link-name match, or a fallback to the *last* label before the TLD. With the default dotted site `slug.project`, a request to `shared.slug.project.test` matches neither the link `slug.project` nor its exact name, so the last-label fallback (`project`) serves it from the **main repo**. Apps that route across their own subdomains (`shared.`, `api.`, …) therefore need a single-label site: `site_separator: "-"` derives `slug-project` instead, and `shared.slug-project.test` falls back to the worktree's own link — the same mechanism that makes `shared.project.test` work for the main checkout. Herd's per-site nginx config and TLS certificate already cover `*.<site>.test`, so the subdomains need no extra links. The `.env` still has to point the app's domain config at those subdomains — that's the post-setup hook's job (see [projects.md](projects.md)).

**Collision guard:** before creating anything, setup checks `herd links` and `herd secured`. A *derived* name that already exists gets a 6-char hash suffix (`afmetingen-3f2a1c.heebink`, logged); an *explicitly passed* name that exists is refused. Re-running setup for the same branch recognizes its own site and is idempotent.

## Registry and marker

- `<worktrees_dir>/.registry.json` — branch → `{herd_site, vite_port, path, db_name}`. Owns Vite port allocation (starts at 5174; 5173 is reserved for the main repo). Safe to delete entries for manually removed worktrees.
- `<worktree>/.worktree-herd.json` — marker written into each worktree: `{herd_site, branch, vite_port, db_name, main_repo}`. Cleanup resolves the Herd site *marker → registry → refuse*; it never derives a site name from `.env` or the folder name. If both are gone, run with `--keep-herd` and `herd unlink` manually.

## Per-worktree databases

Enable with `--db` or `database: per-worktree`. The driver comes from `DB_CONNECTION` in the worktree's `.env`:

| Driver | Create | Drop on cleanup |
| --- | --- | --- |
| `pgsql` | `CREATE DATABASE` via `psql` (skipped if it exists) | `DROP DATABASE IF EXISTS`; on failure, open sessions are listed from `pg_stat_activity` with a `pg_terminate_backend` one-liner |
| `mysql` / `mariadb` | `CREATE DATABASE IF NOT EXISTS` | `DROP DATABASE IF EXISTS` |
| `sqlite` | `database/database.sqlite` file inside the worktree | nothing to do — the file dies with the worktree |

The name is `<main DB_DATABASE>_<slug with underscores>` (max 63 chars), e.g. `myapp_afmetingen_heebink`. `DB_DATABASE` is set in the worktree's `.env`, then `artisan migrate --force` runs. Credentials (`DB_HOST`/`DB_PORT`/`DB_USERNAME`/`DB_PASSWORD`) are read from the same `.env`. Seeding is project-specific — do it in the post-setup hook.

`--keep-db` on cleanup preserves the database; `--no-db` on setup forces shared mode.

## Hook contract

Executable scripts (a hook that exists but isn't executable is an error, not a skip). Run with the worktree as working directory and these variables exported:

`WHD_WORKTREE_PATH`, `WHD_BRANCH`, `WHD_HERD_SITE`, `WHD_HERD_DOMAIN`, `WHD_VITE_PORT`, `WHD_DB_NAME` (empty unless per-worktree), `WHD_MAIN_REPO`.

`post-setup` runs after deps/DB/build succeed; a non-zero exit fails the setup and triggers rollback. `pre-cleanup` runs before Herd/DB teardown, so the site and database still work inside it.

Everything that hardcodes one project — multi-domain `.env` rewrites, session sharing across subdomains, seeders, a known admin login — lives in that project's hooks, not in the tool. Ready-to-copy recipes per project archetype (including a full multi-domain example) are in [projects.md](projects.md).

## Cleanup safety ladder

In order: resolve site (marker → registry → refuse) → `--dry-run` exits after printing the plan → confirmation prompt (skipped by `--yes`) → dirty check → in-use check (`lsof`; skipped in `--current` mode, where your own shell is inside) → pre-cleanup hook → `herd unsecure` + `herd unlink`, then *re-checks Herd actually removed them* → database drop → `git worktree remove` → `git worktree prune` → registry entry removed. After the Herd re-check, the removed domain's entries in Herd's PHP CA bundle (`config/php/cacert.pem`) are pruned — along with any entry whose certificate no longer exists in valet's `Certificates/` (orphans of earlier removals) — and `herd.json`'s `lastSite` is repointed at the main repo if it referenced the removed worktree. Setup rollback prunes the CA bundle the same way.

The dirty check ignores the artifacts this tool creates (`.worktree-herd.json`, a generated `herd.yml`); anything else untracked or modified requires `--force` — interactively you're offered the escalation, but `--yes` alone refuses so automation can't destroy work silently.

## PHP version

Read from the main `herd.yml` `php:` field (used for `herd link --isolate`). Default: `8.4`.

## Node package manager

Auto-detected from the lockfile:

| Lockfile | Command |
| --- | --- |
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| `yarn.lock` | `yarn install --frozen-lockfile` |
| `package-lock.json` / `package.json` | `npm ci` |

Skipped if there is no `package.json`. `composer`/`artisan` run through `herd composer` / `herd php` when the Herd CLI is available.

## Editor tasks (per project)

`worktree-herd-install-tasks <project>` writes `.vscode/tasks.json` with four tasks (set up / clean up × chosen branch / current workspace). `.vscode` is often gitignored — tasks are local to your machine.

## Re-install / update

Run from this skill's directory:

```bash
scripts/install.sh
```

Symlinks in `~/.local/bin` are updated in place.
