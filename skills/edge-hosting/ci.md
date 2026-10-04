# CI deploys, previews and smoke tests

Contents: [pipeline](#pipeline) · [previews](#previews) · [staging and production](#staging-and-production) · [smoke test](#smoke-test) · [CI traps](#ci-traps)

## Pipeline

```
install (lockfile) → build → wrangler types --check → edge_check.py config → quality gates (Lighthouse, axe)
  → wrangler deploy [--env staging] → wait for edge → smoke test → edge_check.py live
```

- Cloudflare's own git integration (Workers Builds, deploy button) connects GitHub and GitLab only; Forgejo, Gitea and Codeberg deploy from their own Actions with `wrangler deploy`.
- Env: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` (skips the `/memberships` lookup account tokens can fail). Token scopes → [dns.md](dns.md#api-tokens).
- Pin reusable deploy workflows by commit SHA, and move every consumer together; a mutable tag pin changes under you.
- `wrangler deploy --strict` in CI refuses to clobber dashboard edits.

## Previews

| Mechanism | URL | Fits |
|---|---|---|
| `wrangler versions upload --preview-alias <branch>` | `<alias>-<worker>.<subdomain>.workers.dev` (Version URL) | PR previews of a static site; needs `preview_urls: true` |
| `wrangler preview` (open beta, ≥ 4.135) | per-branch Preview with its own vars, secrets, bindings | previews that need their own data; currently ignores `404-page` and `_headers`, drops secrets each deploy (pass `--secrets-file`) |
| `[env.preview]` Worker on `preview.example.org/*` | your own hostname | previews behind a hostname Access app, with zone rules applied |

Previews are public on workers.dev unless the Worker is behind Worker-level Access. Parse the preview URL from wrangler's output and **fail the step when none is printed** — a green job with no URL usually means `preview_urls` is off.

## Staging and production

- `env.staging` = separate Worker (`name: "<site>-staging"`), own route (`staging.example.org/*`), **own** KV/D1/R2. Bindings are not inherited; copying the production `database_id` into staging makes staging write production data.
- Release-driven: release-candidate tag → `--env staging`; stable tag → production. Scheduled rebuilds deploy the **latest release tag**, never `main` HEAD, and run the same smoke test.
- Gate staging with Access; staging indexed by search engines is duplicate content.

## Smoke test

1. Poll the production hostname until it serves the new build (a build id or asset hash in the HTML), up to ~2 minutes; a fresh route 522s briefly.
2. Assert 200 on the key paths, 404 on a random path (a 200 means a SPA fallback is swallowing misses).
3. Assert every `_redirects` rule: status and `Location`, generated from the file.
4. `python3 scripts/edge_check.py live example.org --fail-on error`: canonical host, `www`, headers, 522s.

## CI traps

- `pnpm dlx wrangler` can hang on pnpm's build-script approval prompt; use the pinned devDependency (`pnpm exec wrangler`).
- `compatibility_date` newer than the pinned wrangler's bundled runtime fails the deploy: bump wrangler first.
- In Forgejo Actions, a `uses:` job without its own `runs-on` can report success when its child job was skipped, and `with:` expressions referencing outputs of a skipped job fail the run; keep gate jobs unskippable.
- A step that ends with `exit 0` inside a conditional ends only that step, not the job; guard later steps on an output.
