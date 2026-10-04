# edge_check.py

Stdlib Python 3.11+. Two modes:

```bash
python3 scripts/edge_check.py config [repo-or-config …] [--json] [--fail-on error|warn|note|never]
python3 scripts/edge_check.py live example.org [more hosts …] [--no-www] [--timeout 20] [--json] [--fail-on …]
```

`config` reads `wrangler.jsonc`, `wrangler.json` or `wrangler.toml` (a directory finds the first). `live` follows redirects over HTTPS and, for a two-label host, also probes `www.`. Exit 1 when a finding at or above `--fail-on` (default `error`) exists.

## Config rules

| Rule | Severity | Fires when | Fix |
|---|---|---|---|
| `no-public-target` | error | `workers_dev: false`, no route/custom domain, no cron | add the route |
| `misplaced-top-level-key` | error | TOML: `routes`, `workers_dev`, `name`, … under a `[table]` | move above the first table header |
| `shared-binding-across-envs` | error | same KV id / D1 database / R2 bucket in production and an `env.*` | give the environment its own resource |
| `env-name-collision` | error | two environments resolve to one Worker name | distinct `name` per env |
| `compat-date-future` | error | `compatibility_date` after today | today or earlier, within the pinned runtime |
| `compat-date-invalid` | error | not `YYYY-MM-DD` | |
| `workers-dev-alongside-routes` | warn | `workers_dev: true` with routes | `false`, or Worker-level Access |
| `run-worker-first-all` | warn | `run_worker_first: true` | array of the paths that need code |
| `binding-not-inherited` | warn | a top-level binding missing from an `env.*` | declare it in the env (with its own resource) |
| `secret-in-vars` | warn | a `vars` key named like a token/secret/key | `wrangler secret put` |
| `compat-date-missing` | warn | no `compatibility_date` | pin one |
| `preview-urls-implicit` | note | routes set, `preview_urls` absent | set it explicitly |
| `assets-404-unset` | note | assets-only Worker without `not_found_handling` | `"404-page"` or `"single-page-application"` |
| `assets-binding-missing` | note | `run_worker_first` set but no `assets.binding` | `"binding": "ASSETS"` |
| `compat-date-stale` | note | date older than 18 months | read the flags changelog, bump |
| `config-not-found` | error | no config in the given directory | |

## Live rules

| Rule | Severity | Fires when |
|---|---|---|
| `origin-unreachable` | error | 520–527 or 530: proxied hostname with no claimant (route, custom domain, redirect) |
| `no-response` | error | no answer within the timeout |
| `unreachable` | error | DNS, TLS or connection failure |
| `www-apex-both-serve` | warn | apex and `www` both 200 |
| `soft-404` | warn | a random path answers 200 |
| `hsts-missing` | warn | no HSTS, TLD not HSTS-preloaded |
| `canonical-redirect-temporary` | note | `www`↔apex redirect is 302/303/307 |
| `not-on-cloudflare` | note | `server` header isn't `cloudflare` |
| `nosniff-missing` | note | no `X-Content-Type-Options: nosniff` |
| `framing-unprotected` | note | neither CSP `frame-ancestors` nor `X-Frame-Options` |
