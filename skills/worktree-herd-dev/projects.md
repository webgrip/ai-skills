# Worktree Herd Dev — Project Recipes

The tool is project-agnostic; everything project-specific lives **in the project's own repo** and is committed there, so every developer (and Claude) gets it on checkout:

- `worktree-herd.yml` — config in the main repo root ([reference.md](reference.md) has the full key list)
- `.worktree-herd/post-setup` and `.worktree-herd/pre-cleanup` — executable hooks (`chmod +x`), run with the worktree as working directory and `WHD_*` variables exported (see the hook contract in [reference.md](reference.md))

This document is the place to record how each project archetype is set up. When you onboard a new project, work through the checklist, copy the closest recipe, and add a section here for anything project-specific you had to figure out.

## Onboarding checklist for a new project

1. **Single-domain or subdomain-routing?** Look for route registration bound to hostnames (e.g. a `config/domains.php`, `Route::domain(...)`, `DOMAINS_*`-style env vars). If the app routes across its own subdomains, you need `site_separator: "-"` **and** a post-setup hook that rewrites those env vars — see the multi-domain recipe. If unconfigured, the symptom is: the worktree URL redirects or 404s into the **main** checkout's app.
2. **What do features branch from?** Set `base_branch` (e.g. `development`).
3. **Can worktrees share the main database?** If branches carry diverging migrations or destructive seeds, set `database: per-worktree` and do any seeding in the post-setup hook.
4. **Does a page render without a Vite dev server?** A fresh worktree has no built assets — Laravel 500s with *"Vite manifest not found"*. Set `build_assets: true` so the site is browsable immediately; a dev server is only needed for hot reload.
5. **Anything else in `.env` that is per-instance?** Session domain/cookie scoping beyond what the tool sets, callback URLs for external services, feature flags.
6. **Anything to detach on teardown?** Queues, scheduled jobs, webhooks pointing at the worktree URL — handle in `pre-cleanup` (the site and database still exist inside it).

Verify the result end-to-end: run `worktree-herd-setup`, open the printed URL, and log in. A `curl --fail` check at the end of the post-setup hook makes every future setup self-verifying — a non-zero hook exit fails the setup and rolls everything back.

Hooks run on macOS (Herd is macOS-only), so BSD `sed -i ''` is safe to use in them.

## Recipe: single-domain Laravel app

The default case — the app lives on one host, so the derived `slug.project.test` site just works. No hooks needed; a minimal config is still worth committing:

```yaml
# worktree-herd.yml
base_branch: development
build_assets: true
```

## Recipe: multi-domain Laravel app (Chugoku)

Chugoku binds route groups to hosts via `config/domains.php`, fed by seven `DOMAINS_*` env vars (`shared.`, `sqs.`, `tca.`, …), and redirects unknown hosts to the shared domain. Two things are required:

**1. Flat site names.** Herd resolves a host by exact link name or by the *last* label only, so with a dotted site `slug.chugoku`, a request to `shared.slug.chugoku.test` falls back to the `chugoku` link — the main checkout. `site_separator: "-"` fixes the naming (full explanation in [reference.md](reference.md)); Herd's wildcard nginx config and certificate already cover one level of subdomains below the flat site.

```yaml
# worktree-herd.yml
base_branch: development
site_separator: "-"   # shared.slug-chugoku.test resolves to this worktree; shared.slug.chugoku.test would not
build_assets: true
```

**2. Domain rewrites in the post-setup hook.** Point every `DOMAINS_*` var at a subdomain of the worktree's own domain and scope the session cookie to them:

```bash
#!/usr/bin/env bash
# .worktree-herd/post-setup  (chmod +x)
set -euo pipefail

# Route every app domain (keys of config/domains.php) to a subdomain of this
# worktree, and share the session across those subdomains. The autoload require
# matters: config/domains.php calls env(), which plain `php -r` doesn't define.
for key in $(php -r "require 'vendor/autoload.php'; echo implode(' ', array_keys(require 'config/domains.php'));"); do
    upper=$(echo "$key" | tr '[:lower:]' '[:upper:]')
    sed -i '' "s|^DOMAINS_${upper}=.*|DOMAINS_${upper}=${key}.${WHD_HERD_DOMAIN}|" .env
done
sed -i '' "s|^SESSION_DOMAIN=.*|SESSION_DOMAIN=.${WHD_HERD_DOMAIN}|" .env

php artisan optimize:clear

# Self-check: the shared login page must come up, or the setup rolls back.
curl --fail -sk -o /dev/null "https://shared.${WHD_HERD_DOMAIN}/login" \
    || { echo "shared.${WHD_HERD_DOMAIN}/login is not reachable" >&2; exit 1; }
```

The worktree shares the main database by default; sessions stay isolated because the tool already sets a unique `SESSION_COOKIE` per worktree.

## Recipe fragment: per-worktree database with review data

For any project where worktrees need their own data (set `database: per-worktree` — the tool creates the DB and runs `migrate` before the hook fires), append to the post-setup hook:

```bash
php artisan db:seed --force
php artisan tinker --execute="
    \$u = App\Models\User::where('email', 'admin@example.test')->firstOrFail();
    \$u->password = Illuminate\Support\Facades\Hash::make('admin');
    \$u->saveQuietly();
"
```

Adjust seeder classes and the known admin login to the project. Cleanup drops the database automatically (`--keep-db` preserves it).
